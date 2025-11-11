use std::fmt::Debug;

use crate::comp_core::structure::{TypeFull, TypeInterps};

use super::{DomainSlice, PfuncIndex, Type, Vocabulary};

/// A collection of all information of a comp core symbol without type enumerations.
#[derive(Clone)]
pub struct Symbol<'a> {
    pub index: PfuncIndex,
    pub domain: &'a DomainSlice,
    pub codomain: Type,
    pub vocabulary: &'a Vocabulary,
}

impl<'a> Debug for Symbol<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Symbol")
            .field("index", &self.index)
            .field("domain", &self.domain)
            .field("codomain", &self.codomain)
            .finish()
    }
}

/// A collection of all information of a comp core symbol with type enumerations.
pub struct SymbolFull<'a> {
    pub index: PfuncIndex,
    pub domain: &'a DomainSlice,
    pub codomain: TypeFull<'a>,
    pub vocabulary: &'a Vocabulary,
    pub type_interps: &'a TypeInterps,
}

impl<'a> Symbol<'a> {
    pub fn with_interps(self, type_interps: &'a TypeInterps) -> SymbolFull<'a> {
        SymbolFull {
            index: self.index,
            domain: self.domain,
            codomain: self.codomain.with_interps(type_interps),
            vocabulary: self.vocabulary,
            type_interps,
        }
    }

    pub fn arity(&self) -> usize {
        return self.domain.len();
    }
}

impl<'a> SymbolFull<'a> {
    pub fn arity(&self) -> usize {
        return self.domain.len();
    }
}
