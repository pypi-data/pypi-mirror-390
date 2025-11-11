//! Home of datastructures needed for comp core vocabularies.
//! And some lose bits and bobs.
use super::structure::{RawTypeInterps, TypeFull, TypeInterps};
use super::{IndexRange, Real};
use crate::comp_core::Int;
use crate::comp_core::create_index;
use sli_collections::{auto, iterator::Iterator as SIterator};
use std::hash::Hash;
use std::mem::transmute;
use std::ops::Index;
use std::slice::Iter;
use std::unimplemented;
use typed_index_collections::TiVec;

mod applied_symbol;
pub use applied_symbol::*;

type Types = TiVec<TypeIndex, TypeDecl>;
type Pfuncs = TiVec<PfuncIndex, PfuncDecl>;

create_index!(TypeIndex, "This is the type of an FO[.] type identifier");
create_index!(PfuncIndex, "This is the type of an FO[.] symbol identifier");
create_index!(DomainIndex, "This is the type of a domain identifier");

/// A struct representing an FO[.] type declaration.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TypeDecl {
    pub super_type: BaseType,
}

/// A struct representing an FO[.] Vocabulary block
#[derive(Debug)]
pub struct Vocabulary {
    pub types: Types,
    pfuncs: Pfuncs,
    domains: domains::Domains,
}

impl PartialEq for Vocabulary {
    fn eq(&self, other: &Self) -> bool {
        self.types == other.types && self.pfuncs == other.pfuncs
    }
}

impl Eq for Vocabulary {}

impl Clone for Vocabulary {
    fn clone(&self) -> Self {
        Vocabulary {
            types: self.types.clone(),
            pfuncs: self.pfuncs.clone(),
            domains: self.domains.clone(),
        }
    }
}

impl Vocabulary {
    /// Creates an empty vocabulary.
    pub fn new() -> Self {
        Self {
            types: Types::new(),
            pfuncs: Pfuncs::new(),
            domains: domains::Domains::new(),
        }
    }

    /// Returns an iterator over all Pfunc **indices**.
    pub fn iter_pfuncs(&self) -> IndexRange<PfuncIndex> {
        PfuncIndex::range(0..self.pfuncs.len())
    }

    pub fn add_domain<'a, T: Into<Box<DomainSlice>>>(&self, domain: T) -> DomainIndex {
        self.domains.add_domain(domain.into())
    }

    pub fn empty_domain(&self) -> &DomainSlice {
        &Domain([])
    }

    pub fn get_domain(&self, domain_id: DomainIndex) -> &DomainSlice {
        self.domains.get_domain(domain_id)
    }

    pub fn add_type_decl(&mut self, type_decl: TypeDecl) -> TypeIndex {
        let index: TypeIndex = self.types.len().into();
        self.types.push(type_decl);
        return index;
    }

    pub fn add_pfunc_decl(&mut self, decl: PfuncDecl) -> PfuncIndex {
        let index: PfuncIndex = self.pfuncs.len().into();
        self.pfuncs.push(decl);
        return index;
    }

    pub fn get_pfunc_domain<'a>(&'a self, pfunc: &PfuncDecl) -> &'a DomainSlice {
        &self.get_domain(pfunc.domain)
    }

    pub fn get_pfunc_domain_id<'a>(&'a self, pfunc_index: PfuncIndex) -> &'a DomainSlice {
        self.get_pfunc_domain(&self.pfuncs[pfunc_index])
    }

    pub fn get_type(&self, type_index: TypeIndex) -> Type {
        let type_decl = &self.types[type_index];
        match type_decl.super_type {
            BaseType::Int => Type::IntType(type_index),
            BaseType::Real => Type::RealType(type_index),
            BaseType::Str => Type::Str(type_index),
        }
    }

    pub fn get_pfunc_decl(&self, index: PfuncIndex) -> &PfuncDecl {
        &self.pfuncs[index]
    }

    /// Returns an iterator over _all_ symbols (functions, predicates, constants, propositions)
    pub fn iter_symbols<'a>(
        &'a self,
    ) -> impl Iterator<Item = Symbol<'a>> + ExactSizeIterator + DoubleEndedIterator + 'a {
        self.pfuncs.iter_enumerated().map(|f| Symbol {
            index: f.0,
            domain: self.get_domain(f.1.domain),
            codomain: f.1.codomain,
            vocabulary: self,
        })
    }

    /// Returns an iterator over all symbols with an empty domain (constants, propositions)
    pub fn iter_consts_symbols<'a>(
        &'a self,
    ) -> impl Iterator<Item = Symbol<'a>> + DoubleEndedIterator + 'a {
        self.pfuncs
            .iter_enumerated()
            .filter_map(|f| match self.get_domain(f.1.domain) {
                domain @ Domain([]) => Some(Symbol {
                    index: f.0,
                    domain,
                    codomain: f.1.codomain,
                    vocabulary: self,
                }),
                _ => None,
            })
    }

    /// Returns an iterator over all symbols with a non-empty domain (functions, predicates)
    pub fn iter_funcs_symbols<'a>(
        &'a self,
    ) -> impl Iterator<Item = Symbol<'a>> + DoubleEndedIterator + 'a {
        self.pfuncs
            .iter_enumerated()
            .filter_map(|f| match self.get_domain(f.1.domain) {
                domain @ Domain([_, ..]) => Some(Symbol {
                    index: f.0,
                    domain,
                    codomain: f.1.codomain,
                    vocabulary: self,
                }),
                _ => None,
            })
    }

    pub fn pfuncs(&self, index: PfuncIndex) -> Symbol {
        Symbol {
            index,
            codomain: self.pfuncs[index].codomain,
            domain: self.get_domain(self.pfuncs[index].domain),
            vocabulary: self,
        }
    }
}

/// A struct representing an FO[.] symbol.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PfuncDecl {
    pub codomain: Type,
    /// Domain of a symbol.
    pub domain: DomainIndex,
}

create_index!(
    DomainEnum,
    "This type represents the arguments of symbols. \
See [DomainEnumBuilder][crate::comp_core::structure::DomainEnumBuilder] for more information."
);
create_index!(TypeEnum, "This type represents the enumerations of types");

impl Default for TypeEnum {
    fn default() -> Self {
        TypeEnum(0)
    }
}

impl TypeEnum {
    pub fn with_type(self, type_index: TypeIndex) -> TypeElementIndex {
        TypeElementIndex(type_index, self)
    }
}

/// A struct representing an FO[.] domain.
#[derive(Debug, Clone)]
#[repr(transparent)]
pub struct Domain<T: AsRef<[Type]> + ?Sized>(pub T);

pub type DomainSlice = Domain<[Type]>;

impl Clone for Box<DomainSlice> {
    fn clone(&self) -> Self {
        let ret: Box<[Type]> = Box::from_iter(self.iter().copied());
        ret.into()
    }
}

impl<'a, T: AsRef<[Type]> + ?Sized> IntoIterator for &'a Domain<T> {
    type IntoIter = Iter<'a, Type>;
    type Item = &'a Type;

    fn into_iter(self) -> Self::IntoIter {
        self.0.as_ref().iter()
    }
}

impl<T: AsRef<[Type]> + ?Sized, T2: AsRef<[Type]> + ?Sized> PartialEq<Domain<T>> for Domain<T2> {
    fn eq(&self, other: &Domain<T>) -> bool {
        self.0.as_ref() == other.0.as_ref()
    }
}

impl<T: AsRef<[Type]> + ?Sized> Eq for Domain<T> {}

impl<T: AsRef<[Type]> + ?Sized> AsRef<[Type]> for Domain<T> {
    fn as_ref(&self) -> &[Type] {
        self.0.as_ref()
    }
}

impl<S: AsRef<[Type]> + ?Sized> Domain<S> {
    /// Arity of the domain.
    /// For example the arity of the domain of symbol `T` with the following
    /// declaration: `T: A * A -> Bool` would be 2.
    pub fn len(&self) -> usize {
        self.0.as_ref().len()
    }

    /// Returns an Iterator over all the types of the domain.
    pub fn iter(&self) -> Iter<Type> {
        self.0.as_ref().iter()
    }

    /// Length of the domain.
    pub fn domain_len<T: AsRef<RawTypeInterps>>(&self, type_interps: &T) -> usize {
        DomainSlice::type_iter_domain_len(self.iter(), type_interps)
    }

    pub fn iter_index<T: AsRef<RawTypeInterps>>(&self, type_interps: &T) -> IndexRange<DomainEnum> {
        IndexRange::new(0..DomainSlice::type_iter_domain_len(self.iter(), type_interps))
    }

    /// Length of the each type in the domain.
    pub fn domains_len<'a, T: AsRef<TypeInterps> + auto::Auto>(
        &'a self,
        type_interps: &'a T,
    ) -> impl SIterator<Item = usize> + ExactSizeIterator + DoubleEndedIterator + 'a {
        DomainSlice::type_iter_domains_len(self.iter(), type_interps)
    }

    /// Length of each type in the domain. Where the domain is an iterator of [Type]s.
    pub(crate) fn type_iter_domains_len<'a, I, T: AsRef<TypeInterps> + auto::Auto>(
        types: I,
        type_interps: &'a T,
    ) -> impl SIterator<Item = usize> + ExactSizeIterator + DoubleEndedIterator + 'a
    where
        I: SIterator<Item = &'a Type> + ExactSizeIterator + DoubleEndedIterator + 'a,
    {
        types.map(|t| match t {
            Type::Bool => 2,
            Type::Int => unimplemented!(),
            Type::Real => unimplemented!(),
            Type::Str(type_id) | Type::IntType(type_id) | Type::RealType(type_id) => {
                let type_interp = &type_interps.as_ref()[*type_id];
                type_interp.len()
            }
        })
    }

    /// Length of the domain where the domain is represented as an iterator of [Type]s.
    pub(crate) fn type_iter_domain_len<'a, T: AsRef<RawTypeInterps>>(
        types: impl Iterator<Item = &'a Type>,
        type_interps: &'a T,
    ) -> usize {
        let mut size = 1;
        for t in types {
            match t {
                Type::Bool => size *= 2,
                Type::Int => unimplemented!(),
                Type::Real => unimplemented!(),
                Type::Str(type_id) | Type::IntType(type_id) | Type::RealType(type_id) => {
                    let type_interp = &type_interps.as_ref()[*type_id];
                    size *= type_interp.len();
                }
            }
        }
        size
    }
}

impl<T: AsRef<[Type]> + ?Sized> Index<usize> for Domain<T> {
    type Output = Type;

    fn index(&self, index: usize) -> &Self::Output {
        &self.0.as_ref()[index]
    }
}

impl<'a> From<&'a [Type]> for &'a DomainSlice {
    fn from(value: &'a [Type]) -> Self {
        unsafe { transmute(value) }
    }
}

impl<const N: usize> From<[Type; N]> for Box<DomainSlice> {
    fn from(value: [Type; N]) -> Self {
        Box::new(Domain(value))
    }
}

impl From<Box<[Type]>> for Box<DomainSlice> {
    fn from(value: Box<[Type]>) -> Self {
        // Safe since Domain<T> is repr transparent
        unsafe { transmute(value) }
    }
}

impl From<Box<DomainSlice>> for Domain<Box<[Type]>> {
    fn from(value: Box<DomainSlice>) -> Self {
        // Safe since Domain<T> is repr transparent
        unsafe { transmute(value) }
    }
}

impl From<Vec<Type>> for Box<DomainSlice> {
    fn from(value: Vec<Type>) -> Self {
        value.into_boxed_slice().into()
    }
}

/// A [TypeElement](super::structure::TypeElement) of a custom type.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct TypeElementIndex(pub TypeIndex, pub TypeEnum);

impl From<(TypeIndex, TypeEnum)> for TypeElementIndex {
    fn from(value: (TypeIndex, TypeEnum)) -> Self {
        TypeElementIndex(value.0, value.1)
    }
}

impl From<TypeElementIndex> for TypeIndex {
    fn from(value: TypeElementIndex) -> Self {
        value.0
    }
}

impl From<(usize, usize)> for TypeElementIndex {
    fn from(value: (usize, usize)) -> Self {
        TypeElementIndex(value.0.into(), value.1.into())
    }
}

impl From<TypeElementIndex> for TypeEnum {
    fn from(value: TypeElementIndex) -> Self {
        value.1
    }
}

/// The index of a declaration. This declaration is either a symbol,
/// a type, or a type enumeration
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DeclIndex {
    Pfunc(PfuncIndex),
    Type(TypeIndex),
    Enum(TypeElementIndex),
}

impl From<TypeIndex> for DeclIndex {
    fn from(value: TypeIndex) -> Self {
        Self::Type(value)
    }
}

impl From<PfuncIndex> for DeclIndex {
    fn from(value: PfuncIndex) -> Self {
        Self::Pfunc(value)
    }
}

impl From<TypeElementIndex> for DeclIndex {
    fn from(value: TypeElementIndex) -> Self {
        Self::Enum(value)
    }
}

/// An enum representing an FO[.] type.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash)]
/// Represents a type.
/// Types can be either built-in (`Bool`, `Int`, `Real`) or user-defined.
/// Note that `Int` and `Real` logically represent infinite ranges, from -inf to +inf.
/// `IntType` and `RealType` present finite subsets of resp. integer and real numbers.
/// `Str` represents an enumeration of strings.
pub enum Type {
    /// FO[.] Bool
    Bool,
    /// FO[.] Int
    Int,
    /// FO[.] Real
    Real,
    /// FO[.] custom subtype of int
    IntType(TypeIndex),
    /// FO[.] custom subtype of Real
    RealType(TypeIndex),
    /// A custom FO[.] type
    Str(TypeIndex),
}

impl Type {
    pub fn len(&self, type_interps: &TypeInterps) -> usize {
        match self {
            Type::Bool => 2,
            Type::Int => unimplemented!(),
            Type::Real => unimplemented!(),
            Type::Str(type_id) | Type::IntType(type_id) | Type::RealType(type_id) => {
                type_interps[*type_id].len()
            }
        }
    }

    pub fn subtype_eq(self, other: &Type) -> bool {
        match (self, other) {
            (Type::Bool, Type::Bool)
            | (Type::Int, Type::Int | Type::IntType(_))
            | (Type::Real, Type::Real | Type::RealType(_)) => true,
            (Type::Str(a), Type::Str(b)) if a == *b => true,
            _ => false,
        }
    }

    pub fn with_interps<T: AsRef<TypeInterps>>(self, type_interps: &T) -> TypeFull {
        TypeFull::from_type(self, type_interps)
    }

    pub fn type_index(&self) -> Option<TypeIndex> {
        match self {
            Self::Bool | Self::Int | Self::Real => None,
            Self::IntType(id) | Self::RealType(id) | Self::Str(id) => Some(*id),
        }
    }
}

#[derive(Debug, Copy, Clone, Eq, PartialEq)]
pub enum BaseType {
    Int,
    Real,
    Str,
}

impl BaseType {
    pub fn parse(str_slice: &str) -> Self {
        if let Ok(_) = str_slice.parse::<Int>() {
            return Self::Int;
        } else if let Ok(_) = str_slice.parse::<Real>() {
            return Self::Real;
        } else {
            return Self::Str;
        }
    }
}

#[cfg(not(feature = "std_sync"))]
#[doc(hidden)]
mod domains {
    use super::*;
    use core::cell::UnsafeCell;
    type DomainsVec = TiVec<DomainIndex, Box<DomainSlice>>;

    pub struct Domains {
        domains: UnsafeCell<DomainsVec>,
    }

    impl core::fmt::Debug for Domains {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            f.debug_struct("Domains").finish_non_exhaustive()
        }
    }

    impl Clone for Domains {
        fn clone(&self) -> Self {
            Self {
                domains: UnsafeCell::new(unsafe { self.domains.get().as_ref().unwrap() }.clone()),
            }
        }
    }

    impl Domains {
        pub fn new() -> Self {
            Self {
                domains: UnsafeCell::new(Default::default()),
            }
        }

        pub fn add_domain(&self, domain: Box<DomainSlice>) -> DomainIndex {
            if let Some(i) = unsafe { &*self.domains.get() }
                .iter()
                .position(|x| *x == domain)
            {
                i.into()
            } else {
                let index = unsafe { &*self.domains.get() }.len();
                unsafe { &mut *self.domains.get() }.push(domain);
                index.into()
            }
        }

        pub fn get_domain(&self, domain_id: DomainIndex) -> &DomainSlice {
            (unsafe { &*self.domains.get() })[domain_id].as_ref()
        }
    }
}

#[cfg(feature = "std_sync")]
#[doc(hidden)]
mod domains {
    use super::*;
    use std::sync::RwLock;
    type DomainsVec = TiVec<DomainIndex, Box<DomainSlice>>;

    pub struct Domains {
        domains: RwLock<DomainsVec>,
    }

    impl core::fmt::Debug for Domains {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            f.debug_struct("Domains").finish_non_exhaustive()
        }
    }

    impl Clone for Domains {
        fn clone(&self) -> Self {
            Self {
                domains: RwLock::new(self.domains.read().unwrap().clone()),
            }
        }
    }

    impl Domains {
        pub fn new() -> Self {
            Self {
                domains: RwLock::new(Default::default()),
            }
        }

        pub fn add_domain(&self, domain: Box<DomainSlice>) -> DomainIndex {
            let mut domains = self.domains.write().unwrap();
            if let Some(i) = domains.iter().position(|x| *x == domain) {
                i.into()
            } else {
                let index = domains.len();
                domains.push(domain);
                index.into()
            }
        }

        pub fn get_domain<'a>(&'a self, domain_id: DomainIndex) -> &'a DomainSlice {
            let guareded = &self.domains.read().unwrap()[domain_id];
            let a = guareded.as_ref();
            // This extends the lifetime.
            // This is safe since we never allow mutation of the Box<DomainSlice>.
            // The only thing that can be mutated is the TiVec that holds all the
            // Box<DomainSlice>s.
            unsafe { core::mem::transmute::<&DomainSlice, &'a DomainSlice>(a) }
        }
    }
}
