//! An efficient set of a specified domain.
use crate::fodot::{
    error::ArgCreationErrorExtension,
    fmt::{ArgFormatter, FodotDisplay, FodotOptions, FormatOptions},
    structure::{ArgsRc, ArgsRef, DomainFullRc, DomainFullRef, PartialTypeInterps, TryIntoArgs},
    vocabulary::{SymbolError, Vocabulary},
};
use comp_core::{IndexRange, structure::backend::complete_interp::owned::Pred};
use itertools::Itertools;
use std::fmt::{Display, Write};

/// A typed FO(·) set.
pub struct Set {
    pub(crate) backing: Pred,
    pub(crate) domain: DomainFullRc,
}

impl FodotOptions for Set {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for Set {
    fn fmt(
        fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        f.write_char('{')?;
        let arg_fmt = fmt
            .value
            .into_iter()
            .map(|f| {
                fmt.with_format_opts(ArgFormatter::new(
                    f.into_iter_ref(),
                    &fmt.value.domain.as_domain(),
                ))
            })
            .format(", ");
        write!(f, "{}", arg_fmt)?;
        f.write_char('}')
    }
}

impl Display for Set {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl Set {
    /// Create an empty set with values of the given domain.
    pub fn new(domain: DomainFullRc) -> Result<Self, SymbolError> {
        if domain.is_infinite() {
            return Err(SymbolError::IDK);
        }
        Ok(Self {
            backing: Default::default(),
            domain,
        })
    }

    /// The [Vocabulary] of the domain of the set.
    pub fn vocab(&self) -> &Vocabulary {
        self.domain.type_interps().vocab()
    }

    /// The [PartialTypeInterps] of the set
    pub fn type_interps(&self) -> &PartialTypeInterps {
        self.domain.type_interps()
    }

    /// The [DomainFullRc] of the set.
    pub fn domain(&self) -> &DomainFullRc {
        &self.domain
    }

    /// Add the given argument to the set.
    pub fn add<'a, I>(
        &'a mut self,
        args: I,
    ) -> Result<(), <I::Error as ArgCreationErrorExtension>::Error>
    where
        I: TryIntoArgs<'a, Error: ArgCreationErrorExtension>,
    {
        let args = args.try_into_ctx((&self.domain).into())?;
        Ok(self.backing.insert(args.domain_enum))
    }

    /// Negate the set of its domain.
    pub fn negate(&mut self) {
        let len = self.domain().len();
        self.backing.negate_over_range(IndexRange::new(0..len));
    }

    pub fn cardinality(&self) -> usize {
        self.backing.len()
    }

    /// Returns true if the value is in the set.
    ///
    /// Returns [Ok] with a boolean value representing if the value is in the set.
    /// Returns [Err] if the value is of the wrong type.
    pub fn contains<'a, I>(
        &'a self,
        args: I,
    ) -> Result<bool, <I::Error as ArgCreationErrorExtension>::Error>
    where
        I: TryIntoArgs<'a, Error: ArgCreationErrorExtension>,
    {
        let args = args.try_into_ctx((&self.domain).into())?;
        Ok(self.backing.contains(args.domain_enum))
    }

    /// Returns an iterator over the values in the set.
    pub fn iter(&self) -> Iter {
        self.into_iter()
    }
}

/// A referencing iterator over a [Set].
pub struct Iter<'a> {
    iter: <&'a Pred as IntoIterator>::IntoIter,
    domain: DomainFullRef<'a>,
}

/// A owning iterator over a [Set].
pub struct IntoIter {
    into_iter: <Pred as IntoIterator>::IntoIter,
    domain: DomainFullRc,
}

impl<'a> IntoIterator for &'a Set {
    type Item = ArgsRef<'a>;
    type IntoIter = Iter<'a>;

    fn into_iter(self) -> Self::IntoIter {
        Iter {
            iter: (&self.backing).into_iter(),
            domain: (&self.domain).into(),
        }
    }
}

impl<'a> Iterator for Iter<'a> {
    type Item = ArgsRef<'a>;

    fn next(&mut self) -> Option<Self::Item> {
        self.iter.next().map(|f| ArgsRef {
            domain_enum: f,
            domain: self.domain.clone(),
        })
    }
}

impl Iterator for IntoIter {
    type Item = ArgsRc;

    fn next(&mut self) -> Option<Self::Item> {
        self.into_iter.next().map(|f| ArgsRc {
            domain_enum: f,
            domain: self.domain.clone(),
        })
    }
}

#[cfg(test)]
mod test {
    use crate::fodot::TryFromCtx;
    use crate::fodot::structure::{Args, DomainFullRef, StrInterp};
    use crate::fodot::vocabulary::BaseType;
    use crate::fodot::vocabulary::DomainRc;
    use crate::fodot::vocabulary::Vocabulary;
    use sli_collections::rc::Rc;
    use std::error::Error;

    use super::Set;

    #[test]
    fn set_1() -> Result<(), Box<dyn Error>> {
        let mut vocab = Vocabulary::new("test");
        vocab
            .add_type_decl("A", BaseType::Str)?
            .add_voc_type_interp("A", StrInterp::from_iter(["a", "b", "c"]).into())?;
        let (vocab, part_type_interps) = vocab.complete_vocab();
        let type_interps: Rc<_> = part_type_interps.try_err_complete()?.into();
        let domain = DomainRc::new(&["A", "A"], vocab.clone())?;
        let domain_full = domain.with_interps(type_interps).unwrap();

        let mut set = Set::new(domain_full)?;
        set.add(["a", "b"])?;
        set.add(["a", "a"])?;

        assert!(set.contains(["a", "b"])?);
        assert!(set.contains(["a", "a"])?);

        let contained_args = [["a", "a"], ["a", "b"]];
        let domain: DomainFullRef = set.domain().into();

        assert!(
            set.iter()
                .find(|f| contained_args
                    .iter()
                    .find(
                        |f1| &Args::try_from_ctx(f1.iter().copied(), domain.clone()).unwrap() == f
                    )
                    .is_some())
                .is_some()
        );

        assert!(set.add(["a", "a", "a"]).is_err());

        let domain: DomainFullRef = set.domain().into();

        assert!(
            set.into_iter()
                .find(|f| contained_args
                    .iter()
                    .find(
                        |f1| &Args::try_from_ctx(f1.iter().copied(), domain.clone()).unwrap() == f
                    )
                    .is_some())
                .is_some()
        );
        Ok(())
    }
}
