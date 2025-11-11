use super::{
    AppliedSymbol, FreeVariableIter, FreeVariables, Metadata, WellDefinedCondition,
    display_as_debug,
};
use crate::fodot::{
    MetadataIm, MetadataMut,
    fmt::{Fmt, FodotDisplay, FodotOptions, FormatOptions},
    vocabulary::{TypeRef, Vocabulary},
};
use sli_collections::rc::RcA;
use std::fmt::Display;

#[derive(Clone)]
pub struct IsEnumerated {
    pub applied_symbol: AppliedSymbol,
    metadata: Option<Box<Metadata>>,
}

impl PartialEq for IsEnumerated {
    fn eq(&self, other: &Self) -> bool {
        self.applied_symbol == other.applied_symbol
    }
}

impl Eq for IsEnumerated {}

impl FodotOptions for IsEnumerated {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for IsEnumerated {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "{} is enumerated",
            fmt.with_format_opts(&fmt.value.applied_symbol)
        )
    }
}

impl Display for IsEnumerated {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        Display::fmt(&self.display(), f)
    }
}

display_as_debug!(IsEnumerated);

impl IsEnumerated {
    pub fn new(applied_symbol: AppliedSymbol) -> Self {
        Self {
            applied_symbol,
            metadata: Default::default(),
        }
    }

    pub fn codomain(&self) -> TypeRef<'static> {
        TypeRef::Bool
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition> {
        self.applied_symbol.collect_wdcs()
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.applied_symbol.vocab_rc()
    }
}

impl FreeVariables for IsEnumerated {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        for arg in self.applied_symbol.args() {
            iter.add_expr(arg.into());
        }
    }
}

impl MetadataIm for IsEnumerated {
    type Metadata = Metadata;
    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }
}

impl MetadataMut for IsEnumerated {
    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_default()
    }
}

#[cfg(test)]
mod test {
    use crate::Rc;
    use crate::fodot::TryIntoCtx;
    use crate::fodot::structure::{ArgsRef, PartialStructure};
    use crate::fodot::theory::{Assertions, Theory};
    use crate::fodot::vocabulary::Vocabulary;
    use crate::solver::{Solver, SolverIter, Z3Solver};

    #[test]
    fn const_is_enumerated_test() {
        let mut vocab = Vocabulary::new("V");
        vocab.parse("p: -> Bool t: -> Int").unwrap();
        let (vocab, type_interps) = vocab.complete_vocab();
        let type_interps = Rc::new(type_interps.try_complete().unwrap());
        let mut structure = PartialStructure::new(type_interps.clone());
        let mut p_interp = structure.get_mut(vocab.parse_pfunc("p").unwrap());
        p_interp
            .set(
                ArgsRef::empty(p_interp.domain_full()).unwrap(),
                Some(true.into()),
            )
            .unwrap();
        let mut assertions = Assertions::new(vocab.clone());
        assertions
            .parse("p() is enumerated. ~t() is enumerated.")
            .unwrap();
        let assertions = Rc::new(assertions);
        let theory = Theory::new(assertions.clone(), structure).unwrap();
        assert!(Z3Solver::initialize(&theory).check().is_sat());
        let mut structure = PartialStructure::new(type_interps.clone());
        let mut t_interp = structure.get_mut(vocab.parse_pfunc("t").unwrap());
        t_interp
            .set(
                ArgsRef::empty(t_interp.domain_full()).unwrap(),
                Some(2.into()),
            )
            .unwrap();
        let theory = Theory::new(assertions, structure).unwrap();
        assert!(Z3Solver::initialize(&theory).check().is_unsat());
    }

    #[test]
    fn pfunc_is_enumerated_test() {
        let mut vocab = Vocabulary::new("V");
        vocab
            .parse("type A := {a,b,c} p: A -> Bool t: A -> Int")
            .unwrap();
        let (vocab, type_interps) = vocab.complete_vocab();
        let type_interps = Rc::new(type_interps.try_complete().unwrap());
        let mut structure = PartialStructure::new(type_interps.clone());
        let mut p_interp = structure.get_mut(vocab.parse_pfunc("p").unwrap());
        p_interp
            .set(
                ["a"].try_into_ctx(p_interp.domain_full()).unwrap(),
                Some(true.into()),
            )
            .unwrap();
        let mut assertions = Assertions::new(vocab.clone());
        assertions
            .parse("!x in A: if p(x) is enumerated then 1 else 2 = t(x).")
            .unwrap();
        let assertions = Rc::new(assertions);
        let theory = Theory::new(assertions.clone(), structure).unwrap();
        let mut solver = Z3Solver::initialize(&theory);
        let t_symb = vocab.parse_pfunc("t").unwrap();
        for model in solver.iter_models().complete().take(4) {
            let t_interp = model.as_ref().get(t_symb);
            assert_eq!(
                t_interp
                    .get(["a"].try_into_ctx(t_interp.domain_full()).unwrap())
                    .unwrap(),
                1.into()
            );
            assert_eq!(
                t_interp
                    .get(["b"].try_into_ctx(t_interp.domain_full()).unwrap())
                    .unwrap(),
                2.into()
            );
            assert_eq!(
                t_interp
                    .get(["c"].try_into_ctx(t_interp.domain_full()).unwrap())
                    .unwrap(),
                2.into()
            );
        }
    }

    #[test]
    fn pfunc_is_enumerated_test_2() {
        let mut vocab = Vocabulary::new("V");
        vocab
            .parse("type A := {a,b,c} p: A -> Int t: A -> Int")
            .unwrap();
        let (vocab, type_interps) = vocab.complete_vocab();
        let type_interps = Rc::new(type_interps.try_complete().unwrap());
        let mut structure = PartialStructure::new(type_interps.clone());
        let mut p_interp = structure.get_mut(vocab.parse_pfunc("p").unwrap());
        p_interp
            .set(
                ["a"].try_into_ctx(p_interp.domain_full()).unwrap(),
                Some(420.into()),
            )
            .unwrap();
        let mut assertions = Assertions::new(vocab.clone());
        assertions
            .parse("!x in A: if p(x) is enumerated then 1 else 2 = t(x).")
            .unwrap();
        let assertions = Rc::new(assertions);
        let theory = Theory::new(assertions.clone(), structure).unwrap();
        let mut solver = Z3Solver::initialize(&theory);
        let t_symb = vocab.parse_pfunc("t").unwrap();
        for model in solver.iter_models().complete().take(4) {
            let t_interp = model.as_ref().get(t_symb);
            assert_eq!(
                t_interp
                    .get(["a"].try_into_ctx(t_interp.domain_full()).unwrap())
                    .unwrap(),
                1.into()
            );
            assert_eq!(
                t_interp
                    .get(["b"].try_into_ctx(t_interp.domain_full()).unwrap())
                    .unwrap(),
                2.into()
            );
            assert_eq!(
                t_interp
                    .get(["c"].try_into_ctx(t_interp.domain_full()).unwrap())
                    .unwrap(),
                2.into()
            );
        }
    }
}
