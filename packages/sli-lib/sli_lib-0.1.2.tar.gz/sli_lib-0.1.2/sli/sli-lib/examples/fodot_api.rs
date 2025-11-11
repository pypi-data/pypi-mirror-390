use sli_lib::{
    fodot::{
        TryIntoCtx,
        fmt::{BOOL_ASCII, INT_ASCII},
        structure::{IntInterp, PartialStructure, StrInterp, StructureBlock, TypeElement, partial},
        theory::{
            Assertions, BinOp, BinOps, Element, EqualityBinOp, EqualityBinOps, Expr, LogicBinOp,
            LogicBinOps, QuantType, QuanteesBuilder, Quantification, Theory, TheoryBlock,
            VariableDecl,
        },
        vocabulary::{BaseType, Vocabulary},
    },
    solver::{Solver, SolverIter, Z3Solver},
};
use std::error::Error;
use std::str::FromStr;

// Creates the following FO(.) equivalent using the API:
//
// vocabulary {
//   type Foo := {0..10}
//   type Bar := {a, b, c}
//
//   prop: -> Bool
//   const: -> Bar
//   pred: Foo * Foo -> Bool
//   func: Foo -> Int
// }
//
// theory {
//    prop() => const() = a.
//    !x in Foo: pred(x, x) <=> func(x) = 0.
// }
//
// structure {
//    pred := {(1, 1), (2, 3)}.
// }

fn main() -> Result<(), Box<dyn Error>> {
    let mut voc = Vocabulary::new("V");

    ////////////////////////////////////////////
    // Voc
    // Add `Foo := {0..10}` (the long way, as an example)
    voc.add_type_decl("Foo", BaseType::Int)?;
    let foo_interp = IntInterp::try_from(0..10)?;
    voc.add_voc_type_interp("Foo", foo_interp.into())?;

    // Add `Bar := {a, b, c}` (the short way)
    let values: Vec<&str> = vec!["a", "b", "c"];
    let bar_interp = StrInterp::from_iter(values).into();
    voc.add_type_decl_with_interp("Bar", bar_interp)?;

    // Add `prop: -> Bool`
    voc.build_pfunc_decl(BOOL_ASCII)?
        .complete_with_name("prop")?;

    // Add `const: -> Bar`
    voc.build_pfunc_decl("Bar")?.complete_with_name("const")?;

    // Add `pred: Foo * Foo -> Bool`
    voc.build_pfunc_decl(BOOL_ASCII)?
        .set_domain(["Foo", "Foo"])?
        .complete_with_name("pred")?;

    // Add `func: Foo -> Int`
    voc.build_pfunc_decl(INT_ASCII)?
        .set_domain(["Foo"])?
        .complete_with_name("func")?;

    let (voc, part_type_interps) = voc.complete_vocab();

    //////////////////////////////////////////////
    // Theory
    let mut assertions = Assertions::new(voc.clone());

    // prop() => const() = a.
    let prop_symbol = Vocabulary::parse_symbol_rc(&voc, "prop")
        .unwrap()
        .try_apply([])
        .unwrap();
    let const_symbol = Vocabulary::parse_symbol_rc(&voc, "const")
        .unwrap()
        .try_apply([])
        .unwrap();
    let el = Vocabulary::parse_symbol_rc(&voc, "a")?.try_apply([])?;
    let eq = BinOp::new(const_symbol.into(), BinOps::Equal, el.into())?;
    let implication = BinOp::new(prop_symbol.into(), BinOps::Implication, eq.into())?;
    assertions.add_assertion(implication.try_into()?)?;

    // !x in Foo: pred(x, x) <=> func(x) = 0.
    // First, make the quantees.
    let mut quant_builder = QuanteesBuilder::new();
    let type_rc = Vocabulary::parse_type_rc(&voc, "Foo")?;
    let var_decl = VariableDecl::new("x".into(), type_rc.clone()).finish();
    let var_ref = var_decl.create_var_ref();
    quant_builder.add_decl(var_decl);
    //quant_builder.add_new_var("x", type_rc.clone());
    let quantees = quant_builder.finish()?;

    // pred(x, x)
    let pred_args: Vec<Expr> = vec![var_ref.clone().into(), var_ref.clone().into()];
    let pred_symbol = Vocabulary::parse_symbol_rc(&voc, "pred")
        .unwrap()
        .try_apply(pred_args)
        .unwrap();

    // func(x)  = 0
    let func_args: Vec<Expr> = vec![var_ref.clone().into()];
    let func_symbol = Vocabulary::parse_symbol_rc(&voc, "func")
        .unwrap()
        .try_apply(func_args)
        .unwrap();
    let eq = EqualityBinOp::new(
        func_symbol.into(),
        EqualityBinOps::Equal,
        Element::from_str("0")?.into(),
    )?;

    // pred(x, x) <=> func(x) = 0.
    let equiv = LogicBinOp::new(pred_symbol.try_into()?, LogicBinOps::Equivalence, eq.into())?;
    let quantification = Quantification::new(QuantType::Universal, quantees, equiv.into())?;
    assertions.add_assertion(quantification.try_into()?)?;

    let theory_block = TheoryBlock::new("T", assertions);
    println!("{}", theory_block);

    //////////////////////////////////////////////
    // Structure
    let mut structure = PartialStructure::from_partial_interps(part_type_interps)?;

    let pfunc_index = voc.parse_pfunc("pred")?;
    let symbol_interp = structure.get_mut(pfunc_index);
    let mut pred_interp = match symbol_interp {
        partial::mutable::SymbolInterp::Pred(pred) => pred,
        _ => panic!(),
    };
    pred_interp.set(
        [TypeElement::Int(1), TypeElement::Int(1)]
            .try_into_ctx(pred_interp.domain_full())
            .unwrap(),
        true.into(),
    )?;
    pred_interp.set(
        [TypeElement::Int(2), TypeElement::Int(2)]
            .try_into_ctx(pred_interp.domain_full())
            .unwrap(),
        true.into(),
    )?;
    pred_interp.set_all_unknown_to_value(false);

    let struc_block = StructureBlock {
        name: "S".into(),
        structure: structure.into(),
    };

    //////////////////////////////////////////////
    // Solver
    let theory = Theory::from_blocks(theory_block, struc_block)?;
    let mut z3_solver = Z3Solver::initialize(&theory);
    println!("{}", z3_solver.get_smtlib());
    for x in z3_solver.iter_models().complete().take(10) {
        println!("{}", x);
    }

    Ok(())
}
