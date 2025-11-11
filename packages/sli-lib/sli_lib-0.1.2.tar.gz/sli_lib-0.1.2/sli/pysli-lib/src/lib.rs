use pyo3::prelude::*;
use std::ffi::OsString;

pub mod fodot;
mod interior_mut;
pub mod solver;

#[pyo3::pyfunction]
/// Runs the SLI command line interface.
///
/// If `do_exit` is true this function does not return.
/// If `add_name` is true the first argument is not regarded as the name of the executable, but as
/// the first argument of the cli.
/// If `abort_on_sig_int` is true, the current SIG_INT signal handler is overridden with
/// the default signal handler which aborts, the previous signal handler is restored if it is set
/// from python.
/// This function's behaviour is not covered by the version of this library.
#[pyo3(signature = (args, do_exit=false, add_name=true, abort_on_sig_int=true))]
fn sli_cli_main(
    args: Bound<PyAny>,
    do_exit: bool,
    add_name: bool,
    abort_on_sig_int: bool,
    py: Python,
) -> PyResult<i32> {
    let mut args = args
        .try_iter()?
        .map(|value| value.and_then(|f| f.extract::<OsString>()))
        .collect::<Result<Vec<_>, _>>()?;
    if add_name {
        args.insert(0, "sli".into());
    }
    let do_the_thing = || py.detach(|| Ok(sli_cli::main_from(do_exit, args.into_iter())));
    if abort_on_sig_int {
        let signal = py.import("signal")?;
        let sig_int = signal.getattr("SIGINT")?;
        let cur_signal = signal.getattr("getsignal")?.call1((sig_int,))?;
        // Set SIGINT to have the default action
        signal
            .getattr("signal")?
            .call1((signal.getattr("SIGINT")?, signal.getattr("SIG_DFL")?))?;
        let ret = do_the_thing();
        if !cur_signal.is_none() {
            // Revert signal if it was set from python, otherwise we can't do much
            signal
                .getattr("signal")?
                .call1((signal.getattr("SIGINT")?, cur_signal))?;
        }
        ret
    } else {
        do_the_thing()
    }
}

mod python_module {
    use super::*;

    #[pymodule]
    fn sli_lib(m: &Bound<'_, PyModule>) -> PyResult<()> {
        let fodot = fodot::submodule(m.py())?;
        m.gil_used(false)?;
        m.add_submodule(&fodot)?;
        m.py()
            .import("sys")?
            .getattr("modules")?
            .set_item("sli_lib._fodot", &fodot)?;
        let solver = solver::submodule(m.py())?;
        m.add_submodule(&solver)?;
        m.py()
            .import("sys")?
            .getattr("modules")?
            .set_item("sli_lib._solver", &solver)?;
        m.add_function(pyo3::wrap_pyfunction!(sli_cli_main, m)?)?;
        Ok(())
    }
}
