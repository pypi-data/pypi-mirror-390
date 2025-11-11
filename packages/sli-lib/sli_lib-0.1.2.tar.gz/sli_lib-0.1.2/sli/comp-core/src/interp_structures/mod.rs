//! A collection of structures to represent comp core interpretations.
mod layout;
mod natural_join;
pub use layout::*;
// TODO: make these modules not visible
pub mod btree_func;
pub mod roaring;
pub mod satisfying_set;

use crate::comp_core::{expression::TypeMap, structure::TypeInterps, theory::Theory};

pub type LayoutSymbol = satisfying_set::LayoutSymbol<btree_func::Alias>;
pub type LayoutSatSet = satisfying_set::LayoutSatSet<btree_func::Alias>;
pub type LayoutIntFunc = satisfying_set::LayoutIntFunc<btree_func::Alias>;
pub type LayoutRealFunc = satisfying_set::LayoutRealFunc<btree_func::Alias>;
pub type LayoutTypeEnumFunc = satisfying_set::LayoutTypeEnumFunc<btree_func::Alias>;

#[derive(Debug, Clone)]
pub struct InterpContext<'a> {
    type_map: &'a TypeMap,
    type_interps: &'a TypeInterps,
}

impl<'a> InterpContext<'a> {
    pub fn new(type_map: &'a TypeMap, type_interps: &'a TypeInterps) -> Self {
        Self {
            type_map,
            type_interps,
        }
    }

    pub fn from_theory(theory: &'a Theory) -> Self {
        let type_map = theory.expressions().get_type_map();
        let structure = &theory.structure;
        Self::new(type_map, structure.type_interps())
    }

    pub fn get_type_map(&self) -> &TypeMap {
        self.type_map
    }

    pub fn type_interps(&self) -> &TypeInterps {
        self.type_interps
    }
}
