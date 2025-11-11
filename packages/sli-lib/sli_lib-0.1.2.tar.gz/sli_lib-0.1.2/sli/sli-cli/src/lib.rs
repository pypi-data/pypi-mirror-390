use clap::{Parser, Subcommand, ValueEnum};
use itertools::Itertools;
use sli_lib::fodot::TryIntoCtx;
use sli_lib::fodot::structure::Args;
use sli_lib::fodot::theory::Theory as FODTheory;
use sli_lib::fodot::vocabulary::Vocabulary;
use sli_lib::solver::Z3Solver;
use sli_lib::solver::{InterpMethod, Solver, SolverIter, TimeMeasurements, Timings};
use std::ffi::OsString;
use std::fmt::Display;
use std::io::Read;
use std::time::Duration;
use std::{process::exit, time::Instant};

#[derive(Debug, Parser)]
#[command(name = "sli", version = sli_lib::VERSION, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    inference: Inferences,
    #[arg(long, global = true)]
    /// Print smtlib grounding.
    smt: bool,
    #[arg(long, global=true, value_enum, default_value_t = InterpMode::Satset)]
    /// Processing step.
    interp_mode: InterpMode,
    #[arg(long, global = true)]
    /// Print timings of each step.
    print_timings: bool,
}

#[derive(Debug, Copy, Clone, PartialEq, Eq, PartialOrd, Ord, ValueEnum)]
enum InterpMode {
    /// Use satisfying set interpretation.
    Satset,
    /// Use naive interpretation.
    Naive,
    /// Don't reduce.
    NoReduc,
}

#[derive(Debug, Subcommand)]
enum Inferences {
    /// Model expansion
    Expand {
        #[arg(long, default_value_t = 2)]
        /// Amount of models to expand
        models: usize,
        #[command(flatten)]
        options: InferenceOptions,
    },
    /// Backbone propagation
    Propagate {
        #[command(flatten)]
        options: InferenceOptions,
    },
    /// Complete propagation of single applied symbol
    GetRange {
        /// Applied symbol to propagate.
        applied_symbol: String,
        #[command(flatten)]
        options: InferenceOptions,
    },
}

#[derive(Debug, Parser, Clone)]
struct InferenceOptions {
    /// Path to knowledge base to use.
    ///
    /// With no FILE, or when FILE is -, read standard input.
    file: Option<String>,
}

impl Inferences {
    fn options(&self) -> &InferenceOptions {
        match self {
            Self::Expand { options, .. }
            | Self::Propagate { options, .. }
            | Self::GetRange { options, .. } => &options,
        }
    }
}

pub enum InferenceTask<'a> {
    Expand,
    Propagate,
    GetRange { pfunc: &'a str, args: Vec<&'a str> },
}

struct ErrValue {
    err: Option<Box<dyn Display>>,
    code: i32,
}

impl<T: Display + 'static> From<T> for ErrValue {
    fn from(value: T) -> Self {
        Self {
            err: Some(Box::new(value)),
            code: 1,
        }
    }
}

impl ErrValue {
    fn from_code(code: i32) -> Self {
        Self { err: None, code }
    }
}

pub fn main(do_exit: bool) -> i32 {
    let cli = if do_exit {
        Ok(Cli::parse())
    } else {
        Cli::try_parse()
    };
    _main_catch(cli, do_exit)
}

pub fn main_from<I, T>(do_exit: bool, args: I) -> i32
where
    I: IntoIterator<Item = T>,
    T: Into<OsString> + Clone,
{
    let cli = if do_exit {
        Ok(Cli::parse_from(args))
    } else {
        Cli::try_parse_from(args)
    };
    _main_catch(cli, do_exit)
}

fn _main_catch(cli: Result<Cli, clap::Error>, do_exit: bool) -> i32 {
    let cli = match cli {
        Ok(value) => value,
        Err(value) => {
            eprintln!("sli: {}", value);
            return value.exit_code();
        }
    };
    match _main(cli, do_exit) {
        Ok(_) => exit(0),
        Err(value) => {
            if let Some(err) = value.err {
                eprintln!("sli: {}", err);
            }
            exit(value.code);
        }
    }
}

fn _main(cli: Cli, do_exit: bool) -> Result<(), ErrValue> {
    let mut time_measurer = TimeMeasurer::new();
    let parse_timer = time_measurer.parse.start();
    if let Inferences::GetRange { applied_symbol, .. } = &cli.inference {
        if cli.inference.options().file.is_none() && !applied_symbol.contains('(') {
            eprintln!(
                "Warning: get range applied symbol input '{}', looks like a path.",
                applied_symbol
            );
            eprintln!("Warning: Reading from stdin may not be your intention ...");
        }
    }
    let kb = match cli.inference.options().file.as_deref() {
        Some("-") | None => {
            let mut buffer = String::new();
            std::io::stdin()
                .read_to_string(&mut buffer)
                .map_err(|f| format!("{}", f))?;
            buffer
        }
        Some(path) => std::fs::read_to_string(path).map_err(|f| format!("{}: {}", path, f))?,
    };
    let fodot_theory = match FODTheory::from_specification(&kb) {
        Ok(value) => value,
        Err(err) => {
            eprintln!("{}", err.with_source(&kb.as_ref()));
            let exit_code = 1;
            if do_exit {
                exit(exit_code);
            } else {
                return Err(ErrValue::from_code(exit_code));
            }
        }
    };
    let ground_transform = match cli.interp_mode {
        InterpMode::Satset => InterpMethod::SatisfyingSetInterp,
        InterpMode::Naive => InterpMethod::NaiveInterp,
        InterpMode::NoReduc => InterpMethod::NoInterp,
    };
    let parse_time = parse_timer.end().as_secs_f32();
    if cli.print_timings {
        eprintln!("{} - parse done", parse_time);
    }

    let mut z3_solver =
        Z3Solver::initialize_with_timing(&fodot_theory, ground_transform, &mut time_measurer);
    let ground_time = time_measurer.ground.get_time().as_secs_f32();
    let tranform_time = time_measurer.transform.get_time().as_secs_f32();
    if cli.print_timings {
        eprintln!("{} - transform done", tranform_time);
        eprintln!("{} - ground done", ground_time);
    }
    if cli.smt {
        println!("{:}", z3_solver.get_smtlib());
    }

    let solve_timer = time_measurer.solve.start();
    match &cli.inference {
        Inferences::Expand {
            models: max_models, ..
        } => {
            let max_models = *max_models;
            let complete_model_iter = z3_solver.iter_models().complete().take(max_models);
            let mut number_models = 0;
            for (i, model) in complete_model_iter.enumerate() {
                println!("=== Model {} ===\n{}", i + 1, model);
                number_models = i + 1;
            }
            if number_models == 0 {
                println!("Theory is unsatisfiable.");
            } else if number_models != max_models {
                println!("No more models.");
            } else {
                println!("More models may be available.");
            }
        }
        Inferences::Propagate { .. } => {
            let consequences = z3_solver.propagate();
            match consequences {
                Some(x) => println!("{}", x),
                None => println!("Theory is unsatisfiable."),
            };
        }
        Inferences::GetRange { applied_symbol, .. } => {
            let (pfunc, args) = {
                let l_paran = applied_symbol
                    .find("(")
                    .ok_or_else(|| "error when parsing applied symbol")?;
                let pfunc = applied_symbol[..l_paran].trim();
                let r_paran = applied_symbol
                    .find(")")
                    .ok_or_else(|| "error when parsing applied symbol")?;
                if applied_symbol[r_paran..].trim() != ")" {
                    return Err("error when parsing applied symbol".into());
                }
                let args = applied_symbol[l_paran + 1..r_paran]
                    .split(',')
                    .map(|f| f.trim())
                    .collect::<Vec<_>>();
                let args = if let &[""] = args.as_slice() {
                    Vec::new()
                } else {
                    args
                };
                (pfunc, args)
            };
            let pfunc_rc = Vocabulary::parse_pfunc_rc(z3_solver.theory().vocab_rc(), pfunc)
                .map_err(|f| format!("{}: {}", applied_symbol, f))?;
            let type_interps = z3_solver.theory().type_interps_rc().clone();
            let args = args
                .iter()
                .map(|f| *f)
                .try_into_ctx(
                    pfunc_rc
                        .domain()
                        .with_interps(type_interps.as_ref())
                        .unwrap(),
                )
                .map_err(|f| format!("{}: {}", applied_symbol, f))?;
            let cf = z3_solver
                .get_range(pfunc_rc, Args::clone(&args))
                .map_err(|f| format!("{}", f))?;
            if let Some(cf) = cf {
                println!("{}({})<cf> := {}", pfunc, args.iter().format(","), cf);
            } else {
                println!("Theory is unsatisfiable");
            }
        }
    }
    let solve_time = solve_timer.end().as_secs_f32();

    if cli.print_timings {
        eprintln!(
            "\nParse: {} | Transform: {} | Ground: {} | Solve: {}",
            parse_time, tranform_time, ground_time, solve_time
        );
    }
    if do_exit {
        // exit makes it so we don't have to do any cleanup of resources ourselves which is faster
        exit(0);
    }
    Ok(())
}

#[derive(Debug, Clone, Copy)]
pub enum Timer {
    None,
    Duration(Duration),
    Instant(Instant),
}

impl Timer {
    pub fn start_measurement(&mut self) {
        *self = Timer::Instant(Instant::now());
    }

    pub fn start(&mut self) -> TimerEnder {
        self.start_measurement();
        TimerEnder { timer: self }
    }

    pub fn end(&mut self) -> Duration {
        match self {
            Timer::Instant(inst) => {
                let elapsed = inst.elapsed();
                *self = Timer::Duration(elapsed);
                elapsed
            }
            _ => Default::default(),
        }
    }

    pub fn duration_or(&self, value: Duration) -> Duration {
        match self {
            Timer::Duration(dur) => *dur,
            _ => value,
        }
    }

    pub fn get_time(&self) -> Duration {
        self.duration_or(Default::default())
    }

    pub fn expect_instant(&self, msg: &str) -> Instant {
        match self {
            Timer::Instant(inst) => *inst,
            _ => panic!("{msg}"),
        }
    }
}

pub struct TimerEnder<'a> {
    timer: &'a mut Timer,
}

impl<'a> TimerEnder<'a> {
    /// End timing
    pub fn end(self) -> Duration {
        let ret = self.timer.end();
        std::mem::forget(self);
        ret
    }
}

impl<'a> Drop for TimerEnder<'a> {
    fn drop(&mut self) {
        self.timer.end();
    }
}

impl Default for Timer {
    fn default() -> Self {
        Timer::None
    }
}

#[derive(Debug, Default)]
pub struct TimeMeasurer {
    parse: Timer,
    transform: Timer,
    ground: Timer,
    solve: Timer,
}

impl TimeMeasurer {
    pub fn new() -> Self {
        Default::default()
    }
}

impl Timings for TimeMeasurer {
    fn start_measurement(&mut self, measure: TimeMeasurements) {
        match measure {
            TimeMeasurements::Transform => self.transform.start_measurement(),
            TimeMeasurements::Grounding => self.ground.start_measurement(),
        }
    }

    fn end_measurement(&mut self, measure: TimeMeasurements) {
        match measure {
            TimeMeasurements::Transform => {
                self.transform.end();
            }
            TimeMeasurements::Grounding => {
                self.ground.end();
            }
        }
    }
}

#[test]
fn verify_cli() {
    use clap::CommandFactory;
    Cli::command().debug_assert();
}
