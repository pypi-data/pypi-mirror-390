pub use super::applied_symb_interp::complete::{immutable, mutable, owned};
use super::{Precision, TypeInterps, partial::PartialStructure};
use crate::vocabulary::{PfuncIndex, Vocabulary};
use sli_collections::iterator::Iterator as SIterator;
use sli_collections::rc::Rc;

/// A comp core complete structure.
#[repr(transparent)]
#[derive(Debug, Clone)]
pub struct CompleteStructure(pub(super) PartialStructure);

impl AsRef<PartialStructure> for CompleteStructure {
    fn as_ref(&self) -> &PartialStructure {
        &self.0
    }
}

impl Eq for CompleteStructure {}

impl PartialEq for CompleteStructure {
    fn eq(&self, other: &Self) -> bool {
        if self.rc_type_interps() == other.rc_type_interps() {
            return false;
        }
        self.iter().all(|a| {
            let b = other.get(a.pfunc_index());
            a.iter().all(|(arg, value)| b.get_i(arg) == value)
        })
    }
}

impl PartialEq<PartialStructure> for CompleteStructure {
    fn eq(&self, other: &PartialStructure) -> bool {
        <PartialStructure as PartialEq<Self>>::eq(other, self)
    }
}

impl Precision for CompleteStructure {
    fn is_more_precise(&self, rhs: &CompleteStructure) -> bool {
        self.eq(rhs)
    }

    fn is_strictly_more_precise(&self, _rhs: &CompleteStructure) -> bool {
        false
    }

    fn is_strictly_less_precise(&self, _rhs: &CompleteStructure) -> bool {
        false
    }
}

impl Precision<PartialStructure> for CompleteStructure {
    fn is_more_precise(&self, rhs: &PartialStructure) -> bool {
        if self.rc_type_interps() != rhs.rc_type_interps() {
            return false;
        }
        rhs.iter_known().all(|a| {
            let b = self.get(a.pfunc_index());
            a.iter().all(|(arg, value)| value == b.get_i(arg))
        })
    }

    fn is_strictly_less_precise(&self, _rhs: &PartialStructure) -> bool {
        false
    }
}

impl AsRef<TypeInterps> for CompleteStructure {
    fn as_ref(&self) -> &TypeInterps {
        self.type_interps()
    }
}

impl TryFrom<PartialStructure> for CompleteStructure {
    type Error = PartialStructure;

    fn try_from(value: PartialStructure) -> Result<Self, Self::Error> {
        value.try_into_complete()
    }
}

impl CompleteStructure {
    /// The [Vocabulary] of the structure.
    pub fn vocab(&self) -> &Vocabulary {
        self.0.vocab()
    }

    /// The [Vocabulary] of the structure, as a pointer to an [Rc].
    pub fn rc_vocab(&self) -> &Rc<Vocabulary> {
        self.0.rc_vocab()
    }

    /// The [TypeInterps] of the structure.
    pub fn type_interps(&self) -> &TypeInterps {
        self.0.type_interps()
    }

    /// The [TypeInterps] of the structure, as a pointer to an [Rc].
    pub fn rc_type_interps(&self) -> &Rc<TypeInterps> {
        self.0.rc_type_interps()
    }

    /// An iterator over all interpretations.
    pub fn iter(&self) -> impl SIterator<Item = immutable::SymbolInterp> {
        self.vocab().iter_pfuncs().map(|i| self.get(i))
    }

    /// Converts this [CompleteStructure] to a [PartialStructure].
    pub fn into_partial(self) -> PartialStructure {
        self.into()
    }

    /// Get the interpretation of the given pfunc.
    pub fn get(&self, index: PfuncIndex) -> immutable::SymbolInterp {
        self.0.get(index).try_into_complete().unwrap()
    }

    /// Get the mutable interpretation of the given pfunc.
    pub fn get_mut(&mut self, index: PfuncIndex) -> mutable::SymbolInterp {
        self.0.get_mut(index).try_into_complete().unwrap()
    }
}
