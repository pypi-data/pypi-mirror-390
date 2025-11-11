use super::{
    IntInterp, RealInterp, StrInterp, TypeElement, TypeInterps,
    backend::{complete_interp, partial_interp},
    traits::{self, CodomainInterp, SymbolInfo, ToOwnedStore, TypeInterp, TypeInterpMethods},
};
use crate::{
    Int, Real,
    structure::TypeFull,
    vocabulary::{
        Domain, DomainEnum, DomainSlice, PfuncIndex, Type, TypeElementIndex, TypeEnum, TypeIndex,
        Vocabulary,
    },
};
use algebraic_errors::algebraic_errors;
use duplicate::duplicate_item;
use itertools::Either;
use paste::paste;
use sli_collections::iterator::Iterator as SIterator;
use std::ops::Deref;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct DomainError;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct CodomainError;

algebraic_errors! {
    #[derive(Clone, Debug, PartialEq, Eq)]
    pub sum PfuncError {
        DomainError,
        CodomainError,
    },
}

pub trait SymbolInfoHolder<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a>;
}

trait CustomCodomainHolder {
    type Interp;
    fn codomain_interp(&self) -> &Self::Interp;
}

/// Primitive nullary information.
#[derive(Debug, Clone)]
pub struct PrimNullaryCommon<'a> {
    pub vocabulary: &'a Vocabulary,
    pub type_interps: &'a TypeInterps,
    pub index: PfuncIndex,
}

impl<'a> PrimNullaryCommon<'a> {
    pub fn domain(&self) -> &'static DomainSlice {
        &Domain([])
    }
}

/// Custom nullary information.
#[derive(Debug, Clone)]
pub struct CustomNullaryCommon<'a, S> {
    pub vocabulary: &'a Vocabulary,
    pub type_interps: &'a TypeInterps,
    pub index: PfuncIndex,
    pub type_index: TypeIndex,
    pub codomain_interp: &'a S,
}

impl<'a, S> CustomNullaryCommon<'a, S> {
    pub fn domain(&self) -> &'static DomainSlice {
        &Domain([])
    }
}

#[derive(Debug, Clone)]
pub struct PropCommon<'a>(pub PrimNullaryCommon<'a>);

impl<'a> Deref for PropCommon<'a> {
    type Target = PrimNullaryCommon<'a>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> SymbolInfoHolder<'a> for PropCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain(),
            codomain: CodomainInterp::Bool,
        }
    }
}

#[derive(Debug, Clone)]
pub struct IntConstCommon<'a>(pub PrimNullaryCommon<'a>);

impl<'a> Deref for IntConstCommon<'a> {
    type Target = PrimNullaryCommon<'a>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> SymbolInfoHolder<'a> for IntConstCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain(),
            codomain: CodomainInterp::Int(None),
        }
    }
}

#[derive(Debug, Clone)]
pub struct RealConstCommon<'a>(pub PrimNullaryCommon<'a>);

impl<'a> Deref for RealConstCommon<'a> {
    type Target = PrimNullaryCommon<'a>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> SymbolInfoHolder<'a> for RealConstCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain(),
            codomain: CodomainInterp::Real(None),
        }
    }
}

#[derive(Debug, Clone)]
pub struct IntTypeConstCommon<'a>(pub CustomNullaryCommon<'a, IntInterp>);

impl<'a> Deref for IntTypeConstCommon<'a> {
    type Target = CustomNullaryCommon<'a, IntInterp>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> SymbolInfoHolder<'a> for IntTypeConstCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain(),
            codomain: CodomainInterp::Int(Some(self.codomain_interp)),
        }
    }
}

impl<'a> CustomCodomainHolder for IntTypeConstCommon<'a> {
    type Interp = IntInterp;
    fn codomain_interp(&self) -> &Self::Interp {
        self.codomain_interp
    }
}

#[derive(Debug, Clone)]
pub struct RealTypeConstCommon<'a>(pub CustomNullaryCommon<'a, RealInterp>);

impl<'a> Deref for RealTypeConstCommon<'a> {
    type Target = CustomNullaryCommon<'a, RealInterp>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> SymbolInfoHolder<'a> for RealTypeConstCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain(),
            codomain: CodomainInterp::Real(Some(self.codomain_interp)),
        }
    }
}

impl<'a> CustomCodomainHolder for RealTypeConstCommon<'a> {
    type Interp = RealInterp;
    fn codomain_interp(&self) -> &Self::Interp {
        self.codomain_interp
    }
}

#[derive(Debug, Clone)]
pub struct StrConstCommon<'a>(pub CustomNullaryCommon<'a, StrInterp>);

impl<'a> Deref for StrConstCommon<'a> {
    type Target = CustomNullaryCommon<'a, StrInterp>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> SymbolInfoHolder<'a> for StrConstCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain(),
            codomain: CodomainInterp::Str(self.codomain_interp),
        }
    }
}

impl<'a> CustomCodomainHolder for StrConstCommon<'a> {
    type Interp = StrInterp;
    fn codomain_interp(&self) -> &Self::Interp {
        self.codomain_interp
    }
}

#[derive(Debug, Clone)]
pub struct PrimFuncCommon<'a> {
    pub(super) vocabulary: &'a Vocabulary,
    pub(super) type_interps: &'a TypeInterps,
    pub(super) index: PfuncIndex,
    pub(super) domain: &'a DomainSlice,
}

impl<'a> PrimFuncCommon<'a> {
    pub fn domain(&self) -> &'a DomainSlice {
        self.domain
    }
}

#[derive(Clone, Debug)]
pub struct CustomFuncCommon<'a, S> {
    pub(super) vocabulary: &'a Vocabulary,
    pub(super) type_interps: &'a TypeInterps,
    pub(super) index: PfuncIndex,
    pub(super) type_index: TypeIndex,
    pub(super) domain: &'a DomainSlice,
    pub(super) codomain_interp: &'a S,
}

impl<'a, S> CustomFuncCommon<'a, S> {
    pub fn domain(&self) -> &'a DomainSlice {
        self.domain
    }
}

#[derive(Debug, Clone)]
pub struct PredCommon<'a>(pub PrimFuncCommon<'a>);

impl<'a> Deref for PredCommon<'a> {
    type Target = PrimFuncCommon<'a>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> SymbolInfoHolder<'a> for PredCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain,
            codomain: CodomainInterp::Bool,
        }
    }
}

#[derive(Debug, Clone)]
pub struct IntFuncCommon<'a>(pub PrimFuncCommon<'a>);

impl<'a> Deref for IntFuncCommon<'a> {
    type Target = PrimFuncCommon<'a>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> SymbolInfoHolder<'a> for IntFuncCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain,
            codomain: CodomainInterp::Int(None),
        }
    }
}

#[derive(Debug, Clone)]
pub struct RealFuncCommon<'a>(pub PrimFuncCommon<'a>);

impl<'a> Deref for RealFuncCommon<'a> {
    type Target = PrimFuncCommon<'a>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> SymbolInfoHolder<'a> for RealFuncCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain,
            codomain: CodomainInterp::Real(None),
        }
    }
}

#[derive(Debug, Clone)]
pub struct IntTypeFuncCommon<'a>(pub CustomFuncCommon<'a, IntInterp>);

impl<'a> Deref for IntTypeFuncCommon<'a> {
    type Target = CustomFuncCommon<'a, IntInterp>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> SymbolInfoHolder<'a> for IntTypeFuncCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain,
            codomain: CodomainInterp::Int(Some(self.codomain_interp)),
        }
    }
}

impl<'a> CustomCodomainHolder for IntTypeFuncCommon<'a> {
    type Interp = IntInterp;
    fn codomain_interp(&self) -> &Self::Interp {
        self.codomain_interp
    }
}

#[derive(Debug, Clone)]
pub struct RealTypeFuncCommon<'a>(pub CustomFuncCommon<'a, RealInterp>);

impl<'a> Deref for RealTypeFuncCommon<'a> {
    type Target = CustomFuncCommon<'a, RealInterp>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> SymbolInfoHolder<'a> for RealTypeFuncCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain,
            codomain: CodomainInterp::Real(Some(self.codomain_interp)),
        }
    }
}

impl<'a> CustomCodomainHolder for RealTypeFuncCommon<'a> {
    type Interp = RealInterp;
    fn codomain_interp(&self) -> &Self::Interp {
        self.codomain_interp
    }
}

#[derive(Debug, Clone)]
pub struct StrFuncCommon<'a>(pub CustomFuncCommon<'a, StrInterp>);

impl<'a> Deref for StrFuncCommon<'a> {
    type Target = CustomFuncCommon<'a, StrInterp>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a> CustomCodomainHolder for StrFuncCommon<'a> {
    type Interp = StrInterp;
    fn codomain_interp(&self) -> &Self::Interp {
        self.codomain_interp
    }
}

impl<'a> SymbolInfoHolder<'a> for StrFuncCommon<'a> {
    fn symbol_info(&self) -> SymbolInfo<'a> {
        SymbolInfo {
            type_interps: self.type_interps,
            domain: self.domain,
            codomain: CodomainInterp::Str(self.codomain_interp),
        }
    }
}

fn partial_set_custom_const<'a, S, T, C>(
    store: &mut S,
    common: &C,
    value: Option<T>,
) -> Result<(), CodomainError>
where
    S: traits::partial::MutNullary<T>,
    T: Copy + TypeInterp,
    C: SymbolInfoHolder<'a> + CustomCodomainHolder<Interp = <T as TypeInterp>::InterpType>,
{
    let symbol_info = common.symbol_info();
    if value
        .as_ref()
        .map(|f| common.codomain_interp().contains(f))
        .unwrap_or(true)
    {
        traits::partial::MutNullary::set(store, symbol_info, value);
        Ok(())
    } else {
        Err(CodomainError)
    }
}

fn partial_get_custom_func<'a, S, T, C>(
    store: &S,
    common: &C,
    domain_enum: DomainEnum,
) -> Result<Option<T>, DomainError>
where
    S: traits::partial::ImFunc<T>,
    T: Copy,
    C: SymbolInfoHolder<'a>,
{
    let symbol_info = common.symbol_info();
    if symbol_info
        .domain
        .iter_index(symbol_info.type_interps)
        .contains(domain_enum)
    {
        Ok(traits::partial::ImFunc::get(
            store,
            symbol_info,
            domain_enum,
        ))
    } else {
        Err(DomainError)
    }
}

fn partial_set_custom_func<'a, S, T, C>(
    store: &mut S,
    common: &C,
    domain_enum: DomainEnum,
    value: Option<T>,
) -> Result<(), PfuncError>
where
    S: traits::partial::MutFunc<T>,
    T: Copy + TypeInterp,
    C: SymbolInfoHolder<'a> + CustomCodomainHolder<Interp = <T as TypeInterp>::InterpType>,
{
    let symbol_info = common.symbol_info();
    if !symbol_info
        .domain
        .iter_index(symbol_info.type_interps)
        .contains(domain_enum)
    {
        Err(PfuncError::DomainError(DomainError))
    } else if !value
        .as_ref()
        .map(|f| common.codomain_interp().contains(f))
        .unwrap_or(true)
    {
        Err(CodomainError.into())
    } else {
        Ok(traits::partial::MutFunc::set(
            store,
            symbol_info,
            domain_enum,
            value,
        ))
    }
}

#[duplicate_item(
    common_ty codomain_ty;
    [PropCommon] [bool];
    [IntConstCommon] [Int];
    [RealConstCommon] [Real];
    [IntTypeConstCommon] [Int];
    [RealTypeConstCommon] [Real];

    [PredCommon] [bool];
    [IntFuncCommon] [Int];
    [RealFuncCommon] [Real];
    [IntTypeFuncCommon] [Int];
    [RealTypeFuncCommon] [Real];
)]
impl<'a> common_ty<'a> {
    pub(super) fn symbol_to_type_element_func(
        &self,
    ) -> impl Fn(codomain_ty) -> TypeElement + use<> {
        |value| value.into()
    }

    pub(super) fn symbol_to_type_element(&self, value: codomain_ty) -> TypeElement {
        value.into()
    }

    pub(super) fn symbol_codomain_from_type_element(
        &self,
        value: TypeElement,
    ) -> Result<codomain_ty, CodomainError> {
        value.try_into().map_err(|_| CodomainError)
    }
}

#[duplicate_item(
    common_ty;
    [StrConstCommon];
    [StrFuncCommon];
)]
impl<'a> common_ty<'a> {
    fn symbol_to_type_element_func(&self) -> impl Fn(TypeEnum) -> TypeElement + use<'a> {
        let type_index = self.type_index;
        move |value| TypeElementIndex(type_index, value).into()
    }

    fn symbol_to_type_element(&self, value: TypeEnum) -> TypeElement {
        TypeElementIndex(self.type_index, value).into()
    }

    fn symbol_codomain_from_type_element(
        &self,
        value: TypeElement,
    ) -> Result<TypeEnum, CodomainError> {
        TypeElementIndex::try_from(value)
            .map_err(|_| CodomainError)
            .and_then(|f| {
                if f.0 != self.type_index {
                    Err(CodomainError)
                } else {
                    Ok(f.1)
                }
            })
    }
}

#[duplicate_item(
    prim_nullary(prefix) custom_nullary(prefix) prim_func(prefix) custom_func(prefix);
    [
        [prefix::PropInterp] [bool];
        [prefix::IntConstInterp] [Int];
        [prefix::RealConstInterp] [Real];
    ]
    [
        [prefix::IntTypeConstInterp] [Int];
        [prefix::RealTypeConstInterp] [Real];
        [prefix::StrConstInterp] [TypeEnum];
    ]
    [
        [prefix::PredInterp] [bool];
        [prefix::IntFuncInterp] [Int];
        [prefix::RealFuncInterp] [Real];
    ]
    [
        [prefix::IntTypeFuncInterp] [Int];
        [prefix::RealTypeFuncInterp] [Real];
        [prefix::StrFuncInterp] [TypeEnum];
    ];
)]
pub mod partial {
    use super::*;
    #[duplicate_item(
        module interp_mod BigEnumName BigNullaryName BigFuncName lifetime derives;
        [owned] [owned] [SymbolInterp] [NullaryInterp] [FuncInterp] [] [Clone, Debug];
        [immutable] [immutable_view] [SymbolInterp] [NullaryInterp] [FuncInterp] ['a] [Clone, Debug];
        [mutable] [mutable_view] [SymbolInterp] [NullaryInterp] [FuncInterp] ['a] [Debug];
    )]
    pub mod module {
        use super::*;
        paste! {
            pub use [<partial_symbol_ module>]::BigEnumName;
        }
        paste! {
            pub use [<partial_nullary_ module>]::BigNullaryName;
        }
        paste! {
            pub use [<partial_func_ module>]::BigFuncName;
        }
        #[duplicate_item(
            name_ty common_ty interp_name;
            [PropInterp] [PropCommon] [Prop];
            [IntConstInterp] [IntConstCommon] [IntConst];
            [RealConstInterp] [RealConstCommon] [RealConst];
            [IntTypeConstInterp] [IntTypeConstCommon] [IntTypeConst];
            [RealTypeConstInterp] [RealTypeConstCommon] [RealTypeConst];
            [StrConstInterp] [StrConstCommon] [StrConst];

            [PredInterp] [PredCommon] [Pred];
            [IntFuncInterp] [IntFuncCommon] [IntFunc];
            [RealFuncInterp] [RealFuncCommon] [RealFunc];
            [IntTypeFuncInterp] [IntTypeFuncCommon] [IntTypeFunc];
            [RealTypeFuncInterp] [RealTypeFuncCommon] [RealTypeFunc];
            [StrFuncInterp] [StrFuncCommon] [StrFunc];
        )]
        /// A wrapped view around the partial backend, ensuring proper usage.
        #[derive(derives)]
        pub struct name_ty<'a> {
            pub store: partial_interp::interp_mod::interp_name<lifetime>,
            pub common: common_ty<'a>,
        }

        #[duplicate_item(
            name_ty Var1 ty_1 Var2 ty_2 big_special big_postfix;
            [IntCoConstInterp] [Int] [IntConstInterp] [IntType] [IntTypeConstInterp]
                [BigNullaryName] [Const];
            [RealCoConstInterp] [Real] [RealConstInterp] [RealType] [RealTypeConstInterp]
                [BigNullaryName] [Const];

            [IntCoFuncInterp] [Int] [IntFuncInterp] [IntType] [IntTypeFuncInterp]
                [BigFuncName] [Func];
            [RealCoFuncInterp]  [Real] [RealFuncInterp] [RealType] [RealTypeFuncInterp]
                [BigFuncName] [Func];
        )]
        mod combined {
            #![doc(hidden)]
            use super::*;
            #[derive(derives)]
            pub enum name_ty<'a> {
                Var1(ty_1<'a>),
                Var2(ty_2<'a>),
            }

            paste! {
                impl<'a> From<ty_1<'a>> for BigEnumName<'a> {
                    fn from(value: ty_1<'a>) -> Self {
                        Self::[<Var1 big_postfix>](value.into())
                    }
                }
            }

            paste! {
                impl<'a> From<ty_2<'a>> for BigEnumName<'a> {
                    fn from(value: ty_2<'a>) -> Self {
                        Self::[<Var1 big_postfix>](value.into())
                    }
                }
            }

            paste! {
                impl<'a> From<ty_1<'a>> for big_special<'a> {
                    fn from(value: ty_1<'a>) -> Self {
                        Self::[<Var1 big_postfix>](value.into())
                    }
                }
            }

            paste! {
                impl<'a> From<ty_2<'a>> for big_special<'a> {
                    fn from(value: ty_2<'a>) -> Self {
                        Self::[<Var1 big_postfix>](value.into())
                    }
                }
            }

            impl<'a> From<ty_1<'a>> for name_ty<'a> {
                fn from(value: ty_1<'a>) -> Self {
                    Self::Var1(value)
                }
            }

            impl<'a> From<ty_2<'a>> for name_ty<'a> {
                fn from(value: ty_2<'a>) -> Self {
                    Self::Var2(value)
                }
            }
        }
        pub use combined_int_co_const_interp::*;
        pub use combined_int_co_func_interp::*;
        pub use combined_real_co_const_interp::*;
        pub use combined_real_co_func_interp::*;
    }

    #[duplicate_item(
        kind name_ty codomain_ty codomain_type;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            [kinds] [PropInterp] [bool] [Type::Bool];
            [kinds] [IntConstInterp] [Int] [Type::Int];
            [kinds] [RealConstInterp] [Real] [Type::Real];
            [kinds] [IntTypeConstInterp] [Int] [Type::IntType(self.codomain_index())];
            [kinds] [RealTypeConstInterp] [Real] [Type::RealType(self.codomain_index())];
            [kinds] [StrConstInterp] [TypeEnum] [Type::Str(self.codomain_index())];
            [kinds] [PredInterp] [bool] [Type::Bool];
            [kinds] [IntFuncInterp] [Int] [Type::Int];
            [kinds] [RealFuncInterp] [Real] [Type::Real];
            [kinds] [IntTypeFuncInterp] [Int] [Type::IntType(self.codomain_index())];
            [kinds] [RealTypeFuncInterp] [Real] [Type::RealType(self.codomain_index())];
            [kinds] [StrFuncInterp] [TypeEnum] [Type::Str(self.codomain_index())];
        }
    )]
    impl<'a> kind::name_ty<'a> {
        /// Create an owned copy of the interpretation.
        pub fn to_owned(&self) -> owned::name_ty<'a> {
            owned::name_ty {
                store: ToOwnedStore::to_owned(&self.store, self.common.symbol_info()),
                common: self.common.clone(),
            }
        }

        /// The domain of the symbol.
        pub fn domain(&self) -> &'a DomainSlice {
            self.common.domain()
        }

        /// The vocabulary of the symbol.
        pub fn vocab(&self) -> &'a Vocabulary {
            self.common.vocabulary
        }

        /// The type interpretations of the symbol.
        pub fn type_interps(&self) -> &'a TypeInterps {
            self.common.type_interps
        }

        /// The [PfuncIndex] of the symbol.
        pub fn pfunc_index(&self) -> PfuncIndex {
            self.common.index
        }

        pub(super) fn symbol_codomain(&self) -> Type {
            codomain_type
        }

        pub(super) fn symbol_to_type_element_func(
            &self,
        ) -> impl Fn(codomain_ty) -> TypeElement + use<'a> {
            self.common.symbol_to_type_element_func()
        }

        pub(super) fn symbol_to_type_element(&self, value: codomain_ty) -> TypeElement {
            self.common.symbol_to_type_element(value)
        }

        #[allow(unused)]
        pub(super) fn symbol_codomain_from_type_element(
            &self,
            value: TypeElement,
        ) -> Result<codomain_ty, CodomainError> {
            self.common.symbol_codomain_from_type_element(value)
        }
    }

    #[duplicate_item(
        kind name_ty codomain_ty codomain_interp_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            [kinds] [IntCoConstInterp] [Int] [IntInterp];
            [kinds] [RealCoConstInterp] [Real] [RealInterp];
            [kinds] [IntCoFuncInterp] [Int] [IntInterp];
            [kinds] [RealCoFuncInterp] [Real] [RealInterp];
        }
    )]
    impl<'a> kind::name_ty<'a> {
        /// Create an owned copy of the interpretation.
        pub fn to_owned(&self) -> owned::name_ty<'a> {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.to_owned().into(),
                    Self::[<codomain_ty Type>](value) => value.to_owned().into(),
                }
            }
        }

        /// The domain of the symbol.
        pub fn domain(&self) -> &'a DomainSlice {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.domain(),
                    Self::[<codomain_ty Type>](value) => value.domain(),
                }
            }
        }

        /// The vocabulary of the symbol.
        pub fn vocab(&self) -> &'a Vocabulary {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.vocab(),
                    Self::[<codomain_ty Type>](value) => value.vocab(),
                }
            }
        }

        /// The type interpretations of the symbol.
        pub fn type_interps(&self) -> &'a TypeInterps {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.type_interps(),
                    Self::[<codomain_ty Type>](value) => value.type_interps(),
                }
            }
        }

        /// The [PfuncIndex] of the symbol.
        pub fn pfunc_index(&self) -> PfuncIndex {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.pfunc_index(),
                    Self::[<codomain_ty Type>](value) => value.pfunc_index(),
                }
            }
        }

        pub(super) fn symbol_codomain(&self) -> Type {
            paste! {
                match self {
                    Self::codomain_ty(interp) => interp.symbol_codomain(),
                    Self::[<codomain_ty Type>](interp) => interp.symbol_codomain(),
                }
            }
        }

        /// The codomain interpretation of the symbol if there is one.
        pub fn codomain_interp(&self) -> Option<&'a codomain_interp_ty> {
            paste! {
                match self {
                    Self::codomain_ty(_) => None,
                    Self::[<codomain_ty Type>](value) => Some(value.common.codomain_interp),
                }
            }
        }

        /// The codomain [TypeIndex] of the symbol if there is one.
        pub fn codomain_index(&self) -> Option<TypeIndex> {
            paste! {
                match self {
                    Self::codomain_ty(_) => None,
                    Self::[<codomain_ty Type>](value) => Some(value.common.type_index),
                }
            }
        }

        pub(super) fn symbol_to_type_element_func(
            &self,
        ) -> impl Fn(codomain_ty) -> TypeElement + use<'a> {
            let function = paste! {
                match self {
                    Self::codomain_ty(value) => Either::Left(value.symbol_to_type_element_func()),
                    Self::[<codomain_ty Type>](value) => Either::Right(value.symbol_to_type_element_func()),
                }
            };
            move |value| match &function {
                Either::Left(fun) => fun(value),
                Either::Right(fun) => fun(value),
            }
        }

        pub(super) fn symbol_to_type_element(&self, value: codomain_ty) -> TypeElement {
            paste! {
                match self {
                    Self::codomain_ty(interp) => interp.symbol_to_type_element(value),
                    Self::[<codomain_ty Type>](interp) => interp.symbol_to_type_element(value),
                }
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_codomain_from_type_element(
            &self,
            value: TypeElement,
        ) -> Result<codomain_ty, CodomainError> {
            paste! {
                match self {
                    Self::codomain_ty(interp) => interp.symbol_codomain_from_type_element(value),
                    Self::[<codomain_ty Type>](interp) => interp.symbol_codomain_from_type_element(value),
                }
            }
        }
    }

    #[duplicate_item(
        name_ty codomain_ty codomain_interp_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            [kinds::IntTypeConstInterp] [Int] [IntInterp];
            [kinds::RealTypeConstInterp] [Real] [RealInterp];
            [kinds::StrConstInterp] [TypeEnum] [StrInterp];

            [kinds::IntTypeFuncInterp] [Int] [IntInterp];
            [kinds::RealTypeFuncInterp] [Real] [RealInterp];
            [kinds::StrFuncInterp] [TypeEnum] [StrInterp];
        }
    )]
    impl<'a> name_ty<'a> {
        /// The codomain interpretation of the symbol.
        pub fn codomain_interp(&self) -> &'a codomain_interp_ty {
            self.common.codomain_interp
        }

        /// The codomain [TypeIndex] of the symbol.
        pub fn codomain_index(&self) -> TypeIndex {
            self.common.type_index
        }
    }

    //
    // Nullaries
    //

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            prim_nullary([kinds])
            custom_nullary([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        /// Get the interpretation of the nullary.
        pub fn get(&self) -> Option<codomain_ty> {
            traits::partial::ImNullary::get(&self.store, self.common.symbol_info())
        }

        pub fn has_interp(&self) -> bool {
            self.get().is_some()
        }

        #[allow(unused)]
        pub(super) fn symbol_get(
            &self,
            domain_enum: DomainEnum,
        ) -> Result<Option<codomain_ty>, DomainError> {
            if domain_enum == DomainEnum::from(0) {
                Ok(self.get())
            } else {
                Err(DomainError)
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_amount_known(&self) -> usize {
            if self.get().is_some() { 1 } else { 0 }
        }

        #[allow(unused)]
        pub(super) fn iter<'b>(&'b self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'b {
            self.get().map(|f| (DomainEnum::from(0), f)).into_iter()
        }

        #[allow(unused)]
        pub(super) fn into_iter(self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'a {
            self.get().map(|f| (DomainEnum::from(0), f)).into_iter()
        }

        #[allow(unused)]
        pub(super) fn iter_unknown(&self) -> impl SIterator<Item = DomainEnum> + use<> {
            if self.get().is_none() {
                Some(0.into()).into_iter()
            } else {
                None.into_iter()
            }
        }

        #[allow(unused)]
        pub(super) fn into_iter_unknown(self) -> impl SIterator<Item = DomainEnum> {
            self.iter_unknown()
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            [kinds::IntCoConstInterp] [Int];
            [kinds::RealCoConstInterp] [Real];
        }
    )]
    impl<'a> name_ty<'a> {
        /// Get the interpretation of the nullary.
        pub fn get(&self) -> Option<codomain_ty> {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.get(),
                    Self::[<codomain_ty Type>](value) =>  value.get(),
                }
            }
        }

        pub fn has_interp(&self) -> bool {
            self.get().is_some()
        }

        pub(super) fn symbol_get(
            &self,
            domain_enum: DomainEnum,
        ) -> Result<Option<codomain_ty>, DomainError> {
            if domain_enum == DomainEnum::from(0) {
                Ok(self.get())
            } else {
                Err(DomainError)
            }
        }

        pub(super) fn symbol_amount_known(&self) -> usize {
            if self.get().is_some() { 1 } else { 0 }
        }

        pub(super) fn iter<'b>(&'b self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'b {
            self.get().map(|f| (DomainEnum::from(0), f)).into_iter()
        }

        pub(super) fn into_iter(self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'a {
            self.get().map(|f| (DomainEnum::from(0), f)).into_iter()
        }

        pub(super) fn iter_unknown(&self) -> impl SIterator<Item = DomainEnum> + use<> {
            if self.get().is_none() {
                Some(0.into()).into_iter()
            } else {
                None.into_iter()
            }
        }

        pub(super) fn into_iter_unknown(self) -> impl SIterator<Item = DomainEnum> {
            self.iter_unknown()
        }
    }

    #[duplicate_item(
        name_ty im_complete_ty complete_ty into_thingy;
        duplicate! {
            [
                kinds into_thingy;
                [owned] [ImNullary::try_into_im_complete];
                [immutable] [ImNullary::try_into_im_complete];
                [mutable] [MutNullary::try_into_mut_complete];
            ]
            [kinds::PropInterp]
                [complete::immutable::PropInterp] [complete::kinds::PropInterp]
                [into_thingy];
            [kinds::IntConstInterp]
                [complete::immutable::IntConstInterp] [complete::kinds::IntConstInterp]
                [into_thingy];
            [kinds::RealConstInterp]
                [complete::immutable::RealConstInterp] [complete::kinds::RealConstInterp]
                [into_thingy];
            [kinds::IntTypeConstInterp]
                [complete::immutable::IntTypeConstInterp] [complete::kinds::IntTypeConstInterp]
                [into_thingy];
            [kinds::RealTypeConstInterp]
                [complete::immutable::RealTypeConstInterp] [complete::kinds::RealTypeConstInterp]
                [into_thingy];
            [kinds::StrConstInterp]
                [complete::immutable::StrConstInterp] [complete::kinds::StrConstInterp]
                [into_thingy];
        }
    )]
    impl<'a> name_ty<'a> {
        /// Try viewing the interpretation as a complete interpretation
        pub fn try_as_im_complete<'b>(&'b self) -> Result<im_complete_ty<'b>, ()> {
            match traits::partial::ImNullary::try_as_im_complete(
                &self.store,
                self.common.symbol_info(),
            ) {
                Ok(complete) => Ok(im_complete_ty {
                    store: complete,
                    common: self.common.clone(),
                }),
                Err(value) => Err(value),
            }
        }

        pub fn is_complete(&self) -> bool {
            self.try_as_im_complete().is_ok()
        }

        /// Try converting the interpretation into a complete interpretation.
        pub fn try_into_complete(self) -> Result<complete_ty<'a>, Self> {
            match traits::partial::into_thingy(self.store, self.common.symbol_info()) {
                Ok(complete) => Ok(complete_ty {
                    store: complete,
                    common: self.common,
                }),
                Err(value) => Err(Self {
                    store: value,
                    common: self.common,
                }),
            }
        }
    }

    #[duplicate_item(
        name_ty im_complete_ty complete_ty codomain;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            [kinds::IntCoConstInterp]
                [complete::immutable::IntCoConstInterp] [complete::kinds::IntCoConstInterp] [Int];
            [kinds::RealCoConstInterp]
                [complete::immutable::RealCoConstInterp] [complete::kinds::RealCoConstInterp] [Real];
            [kinds::IntCoFuncInterp]
                [complete::immutable::IntCoFuncInterp] [complete::kinds::IntCoFuncInterp] [Int];
            [kinds::RealCoFuncInterp]
                [complete::immutable::RealCoFuncInterp] [complete::kinds::RealCoFuncInterp] [Real];
        }
    )]
    impl<'a> name_ty<'a> {
        /// Try viewing the interpretation as a complete interpretation
        pub fn try_as_im_complete<'b>(&'b self) -> Result<im_complete_ty<'b>, ()> {
            paste! {
                match self {
                    Self::codomain(value) => value.try_as_im_complete().map(im_complete_ty::codomain),
                    Self::[<codomain Type>](value) => value.try_as_im_complete().map(im_complete_ty::[<codomain Type>]),
                }
            }
        }

        pub fn is_complete(&self) -> bool {
            self.try_as_im_complete().is_ok()
        }

        /// Try converting the interpretation into a complete interpretation.
        pub fn try_into_complete(self) -> Result<complete_ty<'a>, Self> {
            paste! {
                match self {
                    Self::codomain(value) => value.try_into_complete()
                        .map(complete_ty::codomain)
                        .map_err(Self::codomain),
                    Self::[<codomain Type>](value) => value.try_into_complete()
                        .map(complete_ty::[<codomain Type>])
                        .map_err(Self::[<codomain Type>]),
                }
            }
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            prim_nullary([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(&mut self, value: Option<codomain_ty>) {
            traits::partial::MutNullary::set(&mut self.store, self.common.symbol_info(), value)
        }

        /// Set the interpretation if the interpretation is unknown.
        ///
        /// Returns a [bool] signifying if the interpretation was set.
        pub fn set_if_unknown(&mut self, value: codomain_ty) -> bool {
            if self.get().is_none() {
                self.set(Some(value));
                true
            } else {
                false
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_set_if_unknown(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<bool, PfuncError> {
            if domain_enum == DomainEnum::from(0) {
                Ok(self.set_if_unknown(value))
            } else {
                Err(DomainError)?
            }
        }

        #[allow(unused)]
        pub(super) fn nullary_set_if_unknown(
            &mut self,
            value: codomain_ty,
        ) -> Result<bool, CodomainError> {
            Ok(self.set_if_unknown(value))
        }

        #[allow(unused)]
        pub(super) fn nullary_set(
            &mut self,
            value: Option<codomain_ty>,
        ) -> Result<(), CodomainError> {
            Ok(self.set(value))
        }

        #[allow(unused)]
        pub(super) fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: Option<codomain_ty>,
        ) -> Result<(), DomainError> {
            if domain_enum == DomainEnum::from(0) {
                Ok(self.set(value))
            } else {
                Err(DomainError)
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_fill_unknown_with(
            &mut self,
            value: codomain_ty,
        ) -> Result<(), DomainError> {
            if self.get().is_none() {
                self.set(Some(value));
            }
            Ok(())
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            custom_nullary([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(&mut self, value: Option<codomain_ty>) -> Result<(), CodomainError> {
            partial_set_custom_const(&mut self.store, &self.common, value)
        }

        /// Set the interpretation if the interpretation is unknown.
        ///
        /// Returns a [bool] signifying if the interpretation was set.
        pub fn set_if_unknown(&mut self, value: codomain_ty) -> Result<bool, CodomainError> {
            if self.get().is_none() {
                if !self.common.codomain_interp.contains(&value) {
                    return Err(CodomainError);
                }
                traits::partial::MutNullary::set(
                    &mut self.store,
                    self.common.symbol_info(),
                    Some(value),
                );
                Ok(true)
            } else {
                Ok(false)
            }
        }

        #[allow(unused)]
        pub(super) fn nullary_set_if_unknown(
            &mut self,
            value: codomain_ty,
        ) -> Result<bool, CodomainError> {
            self.set_if_unknown(value)
        }

        #[allow(unused)]
        pub(super) fn symbol_set_if_unknown(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<bool, PfuncError> {
            if domain_enum == DomainEnum::from(0) {
                Ok(self.set_if_unknown(value)?)
            } else {
                Err(DomainError)?
            }
        }

        pub fn set_i(&mut self, value: Option<codomain_ty>) {
            self.set(value).unwrap()
        }

        #[allow(unused)]
        pub(super) fn nullary_set(
            &mut self,
            value: Option<codomain_ty>,
        ) -> Result<(), CodomainError> {
            self.set(value)
        }

        #[allow(unused)]
        pub(super) fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: Option<codomain_ty>,
        ) -> Result<(), PfuncError> {
            if domain_enum == DomainEnum::from(0) {
                Ok(self.set(value)?)
            } else {
                Err(DomainError.into())
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_fill_unknown_with(
            &mut self,
            value: codomain_ty,
        ) -> Result<(), CodomainError> {
            if self.get().is_none() {
                self.set(Some(value))?;
            }
            Ok(())
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            [kinds::IntCoConstInterp] [Int];
            [kinds::RealCoConstInterp] [Real];
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(&mut self, value: Option<codomain_ty>) -> Result<(), CodomainError> {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Ok(interp.set(value)),
                    Self::[<codomain_ty Type>](interp) => interp.set(value),
                }
            }
        }

        /// Set the interpretation if the interpretation is unknown.
        ///
        /// Returns a [bool] signifying if the interpretation was set.
        pub fn set_if_unknown(&mut self, value: codomain_ty) -> Result<bool, CodomainError> {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Ok(interp.set_if_unknown(value)),
                    Self::[<codomain_ty Type>](interp) => interp.set_if_unknown(value),
                }
            }
        }

        pub(super) fn symbol_set_if_unknown(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<bool, PfuncError> {
            if domain_enum == DomainEnum::from(0) {
                Ok(self.set_if_unknown(value)?)
            } else {
                Err(DomainError)?
            }
        }

        pub(super) fn nullary_set_if_unknown(
            &mut self,
            value: codomain_ty,
        ) -> Result<bool, CodomainError> {
            self.set_if_unknown(value)
        }

        /// Panicking version of [Self::set].
        pub fn set_i(&mut self, value: Option<codomain_ty>) {
            self.set(value).unwrap()
        }

        pub(super) fn nullary_set(
            &mut self,
            value: Option<codomain_ty>,
        ) -> Result<(), CodomainError> {
            self.set(value)
        }

        pub(super) fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: Option<codomain_ty>,
        ) -> Result<(), PfuncError> {
            if domain_enum == DomainEnum::from(0) {
                Ok(self.set(value)?)
            } else {
                Err(DomainError.into())
            }
        }

        pub(super) fn symbol_fill_unknown_with(
            &mut self,
            value: codomain_ty,
        ) -> Result<(), CodomainError> {
            if self.get().is_none() {
                self.set(Some(value))?;
            }
            Ok(())
        }
    }

    //
    // Functions
    //

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            prim_func([kinds])
            custom_func([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn get(&self, domain_enum: DomainEnum) -> Result<Option<codomain_ty>, DomainError> {
            partial_get_custom_func(&self.store, &self.common, domain_enum)
        }

        pub fn has_interp(&self, domain_enum: DomainEnum) -> Result<bool, DomainError> {
            self.get(domain_enum).map(|f| f.is_some())
        }

        /// Panicking version of [Self::get].
        pub fn get_i(&self, domain_enum: DomainEnum) -> Option<codomain_ty> {
            self.get(domain_enum).unwrap()
        }

        #[allow(unused)]
        pub(super) fn symbol_get(
            &self,
            domain_enum: DomainEnum,
        ) -> Result<Option<codomain_ty>, DomainError> {
            self.get(domain_enum)
        }

        pub fn amount_known(&self) -> usize {
            traits::partial::ImFunc::len_partial(&self.store, self.common.symbol_info())
        }

        pub fn amount_unknown(&self) -> usize {
            self.domain().domain_len(self.type_interps()) - self.amount_known()
        }

        pub fn any_known(&self) -> bool {
            self.amount_known() != 0
        }

        #[allow(unused)]
        pub(super) fn symbol_amount_known(&self) -> usize {
            self.amount_known()
        }

        pub fn iter<'b>(&'b self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'b {
            traits::partial::ImFunc::iter_partial(&self.store, self.common.symbol_info())
        }

        pub fn into_iter(self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'a {
            traits::partial::ImFunc::into_iter_partial(self.store, self.common.symbol_info())
        }

        pub fn iter_unknown<'b>(&'b self) -> impl SIterator<Item = DomainEnum> + 'b {
            traits::partial::ImFunc::iter_unknown(&self.store, self.common.symbol_info())
        }

        pub fn into_iter_unknown(self) -> impl SIterator<Item = DomainEnum> + 'a {
            traits::partial::ImFunc::into_iter_unknown(self.store, self.common.symbol_info())
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            [kinds::IntCoFuncInterp] [Int];
            [kinds::RealCoFuncInterp] [Real];
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn get(&self, domain_enum: DomainEnum) -> Result<Option<codomain_ty>, DomainError> {
            paste! {
                match self {
                    Self::codomain_ty(interp) => interp.get(domain_enum),
                    Self::[<codomain_ty Type>](interp) => interp.get(domain_enum),
                }
            }
        }

        /// Panicking version of [Self::get].
        pub fn get_i(&self, domain_enum: DomainEnum) -> Option<codomain_ty> {
            self.get(domain_enum).unwrap()
        }

        pub fn has_interp(&self, domain_enum: DomainEnum) -> Result<bool, DomainError> {
            self.get(domain_enum).map(|f| f.is_some())
        }

        pub(super) fn symbol_get(
            &self,
            domain_enum: DomainEnum,
        ) -> Result<Option<codomain_ty>, DomainError> {
            self.get(domain_enum)
        }

        pub fn amount_known(&self) -> usize {
            paste! {
                match self {
                    Self::codomain_ty(interp) => interp.amount_known(),
                    Self::[<codomain_ty Type>](interp) => interp.amount_known(),
                }
            }
        }

        pub fn amount_unknown(&self) -> usize {
            self.domain().domain_len(self.type_interps()) - self.amount_known()
        }

        pub(super) fn symbol_amount_known(&self) -> usize {
            self.amount_known()
        }

        pub(super) fn iter<'b>(&'b self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'b {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Either::Left(interp.iter()),
                    Self::[<codomain_ty Type>](interp) => Either::Right(interp.iter()),
                }
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_iter<'b>(
            &'b self,
        ) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'b {
            self.iter()
        }

        pub fn into_iter(self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'a {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Either::Left(interp.into_iter()),
                    Self::[<codomain_ty Type>](interp) => Either::Right(interp.into_iter()),
                }
            }
        }

        pub fn iter_unknown<'b>(&'b self) -> impl SIterator<Item = DomainEnum> + 'b {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Either::Left(interp.iter_unknown()),
                    Self::[<codomain_ty Type>](interp) => Either::Right(interp.iter_unknown()),
                }
            }
        }

        pub fn into_iter_unknown(self) -> impl SIterator<Item = DomainEnum> + 'a {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Either::Left(interp.into_iter_unknown()),
                    Self::[<codomain_ty Type>](interp) =>
                        Either::Right(interp.into_iter_unknown()),
                }
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_into_iter(
            self,
        ) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'a {
            self.into_iter()
        }
    }

    #[duplicate_item(
        name_ty im_complete_ty complete_ty into_thingy;
        duplicate! {
            [
                kinds into_thingy;
                [owned] [ImFunc::try_into_im_complete];
                [immutable] [ImFunc::try_into_im_complete];
                [mutable] [MutFunc::try_into_mut_complete];
            ]
            [kinds::PredInterp]
                [complete::immutable::PredInterp] [complete::kinds::PredInterp]
                [into_thingy];
            [kinds::IntFuncInterp]
                [complete::immutable::IntFuncInterp] [complete::kinds::IntFuncInterp]
                [into_thingy];
            [kinds::RealFuncInterp]
                [complete::immutable::RealFuncInterp] [complete::kinds::RealFuncInterp]
                [into_thingy];
            [kinds::IntTypeFuncInterp]
                [complete::immutable::IntTypeFuncInterp] [complete::kinds::IntTypeFuncInterp]
                [into_thingy];
            [kinds::RealTypeFuncInterp]
                [complete::immutable::RealTypeFuncInterp] [complete::kinds::RealTypeFuncInterp]
                [into_thingy];
            [kinds::StrFuncInterp]
                [complete::immutable::StrFuncInterp] [complete::kinds::StrFuncInterp]
                [into_thingy];
        }
    )]
    impl<'a> name_ty<'a> {
        /// Try viewing the interpretation as a complete interpretation
        pub fn try_as_im_complete<'b>(&'b self) -> Result<im_complete_ty<'b>, ()> {
            match traits::partial::ImFunc::try_as_im_complete(
                &self.store,
                self.common.symbol_info(),
            ) {
                Ok(complete) => Ok(im_complete_ty {
                    store: complete,
                    common: self.common.clone(),
                }),
                Err(value) => Err(value),
            }
        }

        pub fn is_complete(&self) -> bool {
            self.try_as_im_complete().is_ok()
        }

        /// Try converting the interpretation into a complete interpretation.
        pub fn try_into_complete(self) -> Result<complete_ty<'a>, Self> {
            match traits::partial::into_thingy(self.store, self.common.symbol_info()) {
                Ok(complete) => Ok(complete_ty {
                    store: complete,
                    common: self.common,
                }),
                Err(value) => Err(Self {
                    store: value,
                    common: self.common,
                }),
            }
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            prim_func([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(
            &mut self,
            domain_enum: DomainEnum,
            value: Option<codomain_ty>,
        ) -> Result<(), DomainError> {
            if self
                .common
                .domain
                .iter_index(self.common.type_interps)
                .contains(domain_enum)
            {
                Ok(traits::partial::MutFunc::set(
                    &mut self.store,
                    self.common.symbol_info(),
                    domain_enum,
                    value,
                ))
            } else {
                Err(DomainError)
            }
        }

        /// Set the interpretation if the interpretation is unknown.
        ///
        /// Returns a [bool] signifying if the interpretation was set.
        pub fn set_if_unknown(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<bool, DomainError> {
            if self.get(domain_enum)?.is_none() {
                traits::partial::MutFunc::set(
                    &mut self.store,
                    self.common.symbol_info(),
                    domain_enum,
                    Some(value),
                );
                Ok(true)
            } else {
                Ok(false)
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_set_if_unknown(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<bool, PfuncError> {
            Ok(self.set_if_unknown(domain_enum, value)?)
        }

        /// Panicking version of [Self::set].
        pub fn set_i(&mut self, domain_enum: DomainEnum, value: Option<codomain_ty>) {
            self.set(domain_enum, value).unwrap()
        }

        #[allow(unused)]
        pub(super) fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: Option<codomain_ty>,
        ) -> Result<(), DomainError> {
            self.set(domain_enum, value)
        }

        /// Sets all unknown interpretations with the given value.
        pub fn fill_unknown_with(&mut self, value: codomain_ty) {
            traits::partial::MutFunc::fill_unknown_with(
                &mut self.store,
                self.common.symbol_info(),
                value,
            )
        }

        #[allow(unused)]
        pub(super) fn symbol_fill_unknown_with(
            &mut self,
            value: codomain_ty,
        ) -> Result<(), DomainError> {
            traits::partial::MutFunc::fill_unknown_with(
                &mut self.store,
                self.common.symbol_info(),
                value,
            );
            Ok(())
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            custom_func([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(
            &mut self,
            domain_enum: DomainEnum,
            value: Option<codomain_ty>,
        ) -> Result<(), PfuncError> {
            partial_set_custom_func(&mut self.store, &self.common, domain_enum, value)
        }

        /// Panicking version of [Self::set].
        pub fn set_if_unknown(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<bool, PfuncError> {
            if self.get(domain_enum)?.is_none() {
                if !self.common.codomain_interp.contains(&value) {
                    return Err(CodomainError.into());
                }
                traits::partial::MutFunc::set(
                    &mut self.store,
                    self.common.symbol_info(),
                    domain_enum,
                    Some(value),
                );
                Ok(true)
            } else {
                Ok(false)
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_set_if_unknown(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<bool, PfuncError> {
            self.set_if_unknown(domain_enum, value)
        }

        /// Panicking version of [Self::set].
        pub fn set_i(&mut self, domain_enum: DomainEnum, value: Option<codomain_ty>) {
            self.set(domain_enum, value).unwrap()
        }

        #[allow(unused)]
        pub(super) fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: Option<codomain_ty>,
        ) -> Result<(), PfuncError> {
            Ok(self.set(domain_enum, value)?)
        }

        /// Sets all unknown interpretations with the given value.
        pub fn fill_unknown_with(&mut self, value: codomain_ty) -> Result<(), CodomainError> {
            if self.common.codomain_interp.contains(&value) {
                traits::partial::MutFunc::fill_unknown_with(
                    &mut self.store,
                    self.common.symbol_info(),
                    value,
                );
                Ok(())
            } else {
                Err(CodomainError)
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_fill_unknown_with(
            &mut self,
            value: codomain_ty,
        ) -> Result<(), CodomainError> {
            self.fill_unknown_with(value)
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            [kinds::IntCoFuncInterp] [Int];
            [kinds::RealCoFuncInterp] [Real];
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(
            &mut self,
            domain_enum: DomainEnum,
            value: Option<codomain_ty>,
        ) -> Result<(), PfuncError> {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Ok(interp.set(domain_enum, value)?),
                    Self::[<codomain_ty Type>](interp) => interp.set(domain_enum, value),
                }
            }
        }

        /// Set the interpretation if the interpretation is unknown.
        ///
        /// Returns a [bool] signifying if the interpretation was set.
        pub fn set_if_unknown(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<bool, PfuncError> {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Ok(interp.set_if_unknown(domain_enum, value)?),
                    Self::[<codomain_ty Type>](interp) => interp.set_if_unknown(domain_enum, value),
                }
            }
        }

        pub(super) fn symbol_set_if_unknown(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<bool, PfuncError> {
            self.set_if_unknown(domain_enum, value)
        }

        /// Panicking version of [Self::set].
        pub fn set_i(&mut self, domain_enum: DomainEnum, value: Option<codomain_ty>) {
            self.set(domain_enum, value).unwrap()
        }

        pub(super) fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: Option<codomain_ty>,
        ) -> Result<(), PfuncError> {
            Ok(self.set(domain_enum, value)?)
        }

        /// Sets all unknown interpretations with the given value.
        pub fn fill_unknown_with(&mut self, value: codomain_ty) -> Result<(), CodomainError> {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Ok(interp.fill_unknown_with(value)),
                    Self::[<codomain_ty Type>](interp) => interp.fill_unknown_with(value),
                }
            }
        }

        pub(super) fn symbol_fill_unknown_with(
            &mut self,
            value: codomain_ty,
        ) -> Result<(), CodomainError> {
            self.fill_unknown_with(value)
        }
    }

    #[duplicate_item(
        kinds;
        [owned];
        [immutable];
        [mutable];
    )]
    impl<'a> kinds::PredInterp<'a> {
        pub fn iter_true<'b>(&'b self) -> impl SIterator<Item = DomainEnum> + 'b {
            traits::partial::ImPred::iter_true(&self.store, self.common.symbol_info())
        }

        pub fn into_iter_true(self) -> impl SIterator<Item = DomainEnum> + 'a {
            traits::partial::ImPred::into_iter_true(self.store, self.common.symbol_info())
        }

        pub fn iter_false<'b>(&'b self) -> impl SIterator<Item = DomainEnum> + 'b {
            traits::partial::ImPred::iter_false(&self.store, self.common.symbol_info())
        }

        pub fn into_iter_false(self) -> impl SIterator<Item = DomainEnum> + 'a {
            traits::partial::ImPred::into_iter_false(self.store, self.common.symbol_info())
        }
    }

    #[duplicate_item(
        kinds;
        [owned];
        [immutable];
    )]
    impl<'a> kinds::PredInterp<'a> {
        pub fn split_ct_cf(
            self,
        ) -> Result<
            (
                complete::kinds::PredInterp<'a>,
                complete::kinds::PredInterp<'a>,
            ),
            Self,
        > {
            match traits::partial::ImPred::split_ct_cf(self.store, self.common.symbol_info()) {
                Ok(value) => Ok((
                    complete::kinds::PredInterp {
                        store: value.0,
                        common: self.common.clone(),
                    },
                    complete::kinds::PredInterp {
                        store: value.1,
                        common: self.common,
                    },
                )),
                Err(value) => Err(Self {
                    store: value,
                    common: self.common,
                }),
            }
        }
    }
}

#[duplicate_item(
    prim_nullary(prefix) custom_nullary(prefix) prim_func(prefix) custom_func(prefix);
    [
        [prefix::PropInterp] [bool];
        [prefix::IntConstInterp] [Int];
        [prefix::RealConstInterp] [Real];
    ]
    [
        [prefix::IntTypeConstInterp] [Int];
        [prefix::RealTypeConstInterp] [Real];
        [prefix::StrConstInterp] [TypeEnum];
    ]
    [
        [prefix::PredInterp] [bool];
        [prefix::IntFuncInterp] [Int];
        [prefix::RealFuncInterp] [Real];
    ]
    [
        [prefix::IntTypeFuncInterp] [Int];
        [prefix::RealTypeFuncInterp] [Real];
        [prefix::StrFuncInterp] [TypeEnum];
    ];
)]
pub mod complete {
    use super::*;
    #[duplicate_item(
        module interp_mod BigEnumName BigNullaryName BigFuncName lifetime derives;
        [owned] [owned] [SymbolInterp] [NullaryInterp] [FuncInterp] [] [Clone, Debug];
        [immutable] [immutable_view] [SymbolInterp] [NullaryInterp] [FuncInterp] ['a] [Clone, Debug];
        [mutable] [mutable_view] [SymbolInterp] [NullaryInterp] [FuncInterp] ['a] [Debug];
    )]
    pub mod module {
        paste! {
            pub use [<complete_symbol_ module>]::BigEnumName;
        }
        paste! {
            pub use [<complete_nullary_ module>]::BigNullaryName;
        }
        paste! {
            pub use [<complete_func_ module>]::BigFuncName;
        }
        use super::*;
        #[duplicate_item(
            name_ty common_ty interp_name;
            [PropInterp] [PropCommon] [Prop];
            [IntConstInterp] [IntConstCommon] [IntConst];
            [RealConstInterp] [RealConstCommon] [RealConst];
            [IntTypeConstInterp] [IntTypeConstCommon] [IntTypeConst];
            [RealTypeConstInterp] [RealTypeConstCommon] [RealTypeConst];
            [StrConstInterp] [StrConstCommon] [StrConst];

            [PredInterp] [PredCommon] [Pred];
            [IntFuncInterp] [IntFuncCommon] [IntFunc];
            [RealFuncInterp] [RealFuncCommon] [RealFunc];
            [IntTypeFuncInterp] [IntTypeFuncCommon] [IntTypeFunc];
            [RealTypeFuncInterp] [RealTypeFuncCommon] [RealTypeFunc];
            [StrFuncInterp] [StrFuncCommon] [StrFunc];
        )]
        /// A wrapped view around the complete backend, ensuring proper usage.
        #[derive(derives)]
        pub struct name_ty<'a> {
            pub store: complete_interp::interp_mod::interp_name<lifetime>,
            pub common: common_ty<'a>,
        }

        #[duplicate_item(
            name_ty Var1 ty_1 Var2 ty_2 big_special big_postfix;
            [IntCoConstInterp] [Int] [IntConstInterp] [IntType] [IntTypeConstInterp]
                [BigNullaryName] [Const];
            [RealCoConstInterp] [Real] [RealConstInterp] [RealType] [RealTypeConstInterp]
                [BigNullaryName] [Const];

            [IntCoFuncInterp] [Int] [IntFuncInterp] [IntType] [IntTypeFuncInterp]
                [BigFuncName] [Func];
            [RealCoFuncInterp]  [Real] [RealFuncInterp] [RealType] [RealTypeFuncInterp]
                [BigFuncName] [Func];
        )]
        mod combined {
            #![doc(hidden)]
            use super::*;
            #[derive(derives)]
            pub enum name_ty<'a> {
                Var1(ty_1<'a>),
                Var2(ty_2<'a>),
            }

            paste! {
                impl<'a> From<ty_1<'a>> for BigEnumName<'a> {
                    fn from(value: ty_1<'a>) -> Self {
                        Self::[<Var1 big_postfix>](value.into())
                    }
                }
            }

            paste! {
                impl<'a> From<ty_2<'a>> for BigEnumName<'a> {
                    fn from(value: ty_2<'a>) -> Self {
                        Self::[<Var1 big_postfix>](value.into())
                    }
                }
            }

            paste! {
                impl<'a> From<ty_1<'a>> for big_special<'a> {
                    fn from(value: ty_1<'a>) -> Self {
                        Self::[<Var1 big_postfix>](value.into())
                    }
                }
            }

            paste! {
                impl<'a> From<ty_2<'a>> for big_special<'a> {
                    fn from(value: ty_2<'a>) -> Self {
                        Self::[<Var1 big_postfix>](value.into())
                    }
                }
            }

            impl<'a> From<ty_1<'a>> for name_ty<'a> {
                fn from(value: ty_1<'a>) -> Self {
                    Self::Var1(value)
                }
            }

            impl<'a> From<ty_2<'a>> for name_ty<'a> {
                fn from(value: ty_2<'a>) -> Self {
                    Self::Var2(value)
                }
            }
        }

        pub use combined_int_co_const_interp::*;
        pub use combined_int_co_func_interp::*;
        pub use combined_real_co_const_interp::*;
        pub use combined_real_co_func_interp::*;
    }

    #[duplicate_item(
        kind name_ty codomain_ty codomain_type;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            [kinds] [PropInterp] [bool] [Type::Bool];
            [kinds] [IntConstInterp] [Int] [Type::Int];
            [kinds] [RealConstInterp] [Real] [Type::Real];
            [kinds] [IntTypeConstInterp] [Int] [Type::IntType(self.codomain_index())];
            [kinds] [RealTypeConstInterp] [Real] [Type::RealType(self.codomain_index())];
            [kinds] [StrConstInterp] [TypeEnum] [Type::Str(self.codomain_index())];
            [kinds] [PredInterp] [bool] [Type::Bool];
            [kinds] [IntFuncInterp] [Int] [Type::Int];
            [kinds] [RealFuncInterp] [Real] [Type::Real];
            [kinds] [IntTypeFuncInterp] [Int] [Type::IntType(self.codomain_index())];
            [kinds] [RealTypeFuncInterp] [Real] [Type::RealType(self.codomain_index())];
            [kinds] [StrFuncInterp] [TypeEnum] [Type::Str(self.codomain_index())];
        }
    )]
    impl<'a> kind::name_ty<'a> {
        /// Create an owned copy of the interpretation.
        pub fn to_owned(&self) -> owned::name_ty<'a> {
            owned::name_ty {
                store: ToOwnedStore::to_owned(&self.store, self.common.symbol_info()),
                common: self.common.clone(),
            }
        }

        /// The domain of the symbol.
        pub fn domain(&self) -> &'a DomainSlice {
            self.common.domain()
        }

        /// The vocabulary of the symbol.
        pub fn vocab(&self) -> &'a Vocabulary {
            self.common.vocabulary
        }

        /// The type interpretations of the symbol.
        pub fn type_interps(&self) -> &'a TypeInterps {
            self.common.type_interps
        }

        /// The [PfuncIndex] of the symbol.
        pub fn pfunc_index(&self) -> PfuncIndex {
            self.common.index
        }

        pub(super) fn symbol_codomain(&self) -> Type {
            codomain_type
        }

        pub(super) fn symbol_to_type_element_func(
            &self,
        ) -> impl Fn(codomain_ty) -> TypeElement + use<'a> {
            self.common.symbol_to_type_element_func()
        }

        pub(super) fn symbol_to_type_element(&self, value: codomain_ty) -> TypeElement {
            self.common.symbol_to_type_element(value)
        }

        #[allow(unused)]
        pub(super) fn symbol_codomain_from_type_element(
            &self,
            value: TypeElement,
        ) -> Result<codomain_ty, CodomainError> {
            self.common.symbol_codomain_from_type_element(value)
        }
    }

    #[duplicate_item(
        kind name_ty codomain_ty codomain_interp_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            [kinds] [IntCoConstInterp] [Int] [IntInterp];
            [kinds] [RealCoConstInterp] [Real] [RealInterp];
            [kinds] [IntCoFuncInterp] [Int] [IntInterp];
            [kinds] [RealCoFuncInterp] [Real] [RealInterp];
        }
    )]
    impl<'a> kind::name_ty<'a> {
        /// Create an owned copy of the interpretation.
        pub fn to_owned(&self) -> owned::name_ty<'a> {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.to_owned().into(),
                    Self::[<codomain_ty Type>](value) => value.to_owned().into(),
                }
            }
        }

        /// The domain of the symbol.
        pub fn domain(&self) -> &'a DomainSlice {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.domain(),
                    Self::[<codomain_ty Type>](value) => value.domain(),
                }
            }
        }

        /// The vocabulary of the symbol.
        pub fn vocab(&self) -> &'a Vocabulary {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.vocab(),
                    Self::[<codomain_ty Type>](value) => value.vocab(),
                }
            }
        }

        /// The type interpretations of the symbol.
        pub fn type_interps(&self) -> &'a TypeInterps {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.type_interps(),
                    Self::[<codomain_ty Type>](value) => value.type_interps(),
                }
            }
        }

        /// The [PfuncIndex] of the symbol.
        pub fn pfunc_index(&self) -> PfuncIndex {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.pfunc_index(),
                    Self::[<codomain_ty Type>](value) => value.pfunc_index(),
                }
            }
        }

        /// The codomain interpretation of the symbol if there is one.
        pub fn codomain_interp(&self) -> Option<&'a codomain_interp_ty> {
            paste! {
                match self {
                    Self::codomain_ty(_) => None,
                    Self::[<codomain_ty Type>](value) => Some(value.common.codomain_interp),
                }
            }
        }

        /// The codomain [TypeIndex] of the symbol if there is one.
        pub fn codomain_index(&self) -> Option<TypeIndex> {
            paste! {
                match self {
                    Self::codomain_ty(_) => None,
                    Self::[<codomain_ty Type>](value) => Some(value.common.type_index),
                }
            }
        }

        pub(super) fn symbol_codomain(&self) -> Type {
            paste! {
                match self {
                    Self::codomain_ty(interp) => interp.symbol_codomain(),
                    Self::[<codomain_ty Type>](interp) => interp.symbol_codomain(),
                }
            }
        }

        pub(super) fn symbol_to_type_element_func(
            &self,
        ) -> impl Fn(codomain_ty) -> TypeElement + use<'a> {
            let function = paste! {
                match self {
                    Self::codomain_ty(value) => Either::Left(value.symbol_to_type_element_func()),
                    Self::[<codomain_ty Type>](value) => Either::Right(value.symbol_to_type_element_func()),
                }
            };
            move |value| match &function {
                Either::Left(fun) => fun(value),
                Either::Right(fun) => fun(value),
            }
        }

        pub(super) fn symbol_to_type_element(&self, value: codomain_ty) -> TypeElement {
            paste! {
                match self {
                    Self::codomain_ty(interp) => interp.symbol_to_type_element(value),
                    Self::[<codomain_ty Type>](interp) => interp.symbol_to_type_element(value),
                }
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_codomain_from_type_element(
            &self,
            value: TypeElement,
        ) -> Result<codomain_ty, CodomainError> {
            paste! {
                match self {
                    Self::codomain_ty(interp) => interp.symbol_codomain_from_type_element(value),
                    Self::[<codomain_ty Type>](interp) => interp.symbol_codomain_from_type_element(value),
                }
            }
        }
    }

    #[duplicate_item(
        name_ty codomain_ty codomain_interp_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            [kinds::IntTypeConstInterp] [Int] [IntInterp];
            [kinds::RealTypeConstInterp] [Real] [RealInterp];
            [kinds::StrConstInterp] [TypeEnum] [StrInterp];

            [kinds::IntTypeFuncInterp] [Int] [IntInterp];
            [kinds::RealTypeFuncInterp] [Real] [RealInterp];
            [kinds::StrFuncInterp] [TypeEnum] [StrInterp];
        }
    )]
    impl<'a> name_ty<'a> {
        /// The codomain interpretation of the symbol.
        pub fn codomain_interp(&self) -> &'a codomain_interp_ty {
            self.common.codomain_interp
        }

        /// The codomain [TypeIndex] of the symbol.
        pub fn codomain_index(&self) -> TypeIndex {
            self.common.type_index
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            prim_nullary([kinds])
            custom_nullary([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn get(&self) -> codomain_ty {
            traits::complete::ImNullary::get(&self.store, self.common.symbol_info())
        }

        #[allow(unused)]
        pub(super) fn symbol_get(
            &self,
            domain_enum: DomainEnum,
        ) -> Result<codomain_ty, DomainError> {
            if domain_enum == DomainEnum::from(0) {
                Ok(self.get())
            } else {
                Err(DomainError)
            }
        }

        #[allow(unused)]
        pub(super) fn symbol_iter<'b>(
            &'b self,
        ) -> impl SIterator<Item = (DomainEnum, codomain_ty)> {
            core::iter::once((DomainEnum::from(0), self.get()))
        }

        #[allow(unused)]
        pub(super) fn symbol_into_iter(
            self,
        ) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'a {
            core::iter::once((DomainEnum::from(0), self.get()))
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            [kinds::IntCoConstInterp] [Int];
            [kinds::RealCoConstInterp] [Real];
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn get(&self) -> codomain_ty {
            paste! {
                match self {
                    Self::codomain_ty(value) => value.get(),
                    Self::[<codomain_ty Type>](value) =>  value.get(),
                }
            }
        }

        pub(super) fn symbol_get(
            &self,
            domain_enum: DomainEnum,
        ) -> Result<codomain_ty, DomainError> {
            if domain_enum == DomainEnum::from(0) {
                Ok(self.get())
            } else {
                Err(DomainError)
            }
        }

        pub(super) fn symbol_iter<'b>(
            &'b self,
        ) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'b {
            core::iter::once((DomainEnum::from(0), self.get()))
        }

        pub(super) fn symbol_into_iter(
            self,
        ) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'a {
            core::iter::once((DomainEnum::from(0), self.get()))
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            prim_nullary([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(&mut self, value: codomain_ty) {
            traits::complete::MutNullary::set(&mut self.store, self.common.symbol_info(), value)
        }

        #[allow(unused)]
        pub(super) fn nullary_set(&mut self, value: codomain_ty) -> Result<(), CodomainError> {
            Ok(self.set(value))
        }

        pub fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<(), PfuncError> {
            if domain_enum == DomainEnum::from(0) {
                self.set(value);
                Ok(())
            } else {
                Err(DomainError.into())
            }
        }
        // TODO: as complete
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            custom_nullary([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(&mut self, value: codomain_ty) -> Result<(), CodomainError> {
            if self.common.codomain_interp.contains(&value) {
                traits::complete::MutNullary::set(
                    &mut self.store,
                    self.common.symbol_info(),
                    value,
                );
                Ok(())
            } else {
                Err(CodomainError)
            }
        }

        /// Panicking version of [Self::set].
        pub fn set_i(&mut self, value: codomain_ty) {
            self.set(value).unwrap()
        }

        #[allow(unused)]
        pub(super) fn nullary_set(&mut self, value: codomain_ty) -> Result<(), CodomainError> {
            self.set(value)
        }

        pub fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<(), PfuncError> {
            if domain_enum == DomainEnum::from(0) {
                self.set(value)?;
                Ok(())
            } else {
                Err(DomainError.into())
            }
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            [kinds::IntCoConstInterp] [Int];
            [kinds::RealCoConstInterp] [Real];
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(&mut self, value: codomain_ty) -> Result<(), CodomainError> {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Ok(interp.set(value)),
                    Self::[<codomain_ty Type>](interp) => interp.set(value),
                }
            }
        }

        /// Panicking version of [Self::set].
        pub fn set_i(&mut self, value: codomain_ty) {
            self.set(value).unwrap()
        }

        pub(super) fn nullary_set(&mut self, value: codomain_ty) -> Result<(), CodomainError> {
            self.set(value)
        }

        pub(super) fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<(), PfuncError> {
            if domain_enum == DomainEnum::from(0) {
                Ok(self.set(value)?)
            } else {
                Err(DomainError.into())
            }
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            prim_func([kinds])
            custom_func([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn get(&self, domain_enum: DomainEnum) -> Result<codomain_ty, DomainError> {
            if self
                .common
                .domain
                .iter_index(self.common.type_interps)
                .contains(domain_enum)
            {
                Ok(traits::complete::ImFunc::get(
                    &self.store,
                    self.common.symbol_info(),
                    domain_enum,
                ))
            } else {
                Err(DomainError)
            }
        }

        /// Panicking version of [Self::get].
        pub fn get_i(&self, domain_enum: DomainEnum) -> codomain_ty {
            self.get(domain_enum).unwrap()
        }

        pub fn symbol_get(&self, domain_enum: DomainEnum) -> Result<codomain_ty, DomainError> {
            self.get(domain_enum)
        }

        pub fn iter<'b>(&'b self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'b {
            traits::complete::ImFunc::iter_complete(&self.store, self.common.symbol_info())
        }

        #[allow(unused)]
        pub(super) fn symbol_iter<'b>(
            &'b self,
        ) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'b {
            self.iter()
        }

        pub fn into_iter(self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'a {
            traits::complete::ImFunc::into_iter_complete(self.store, self.common.symbol_info())
        }

        #[allow(unused)]
        pub(super) fn symbol_into_iter(
            self,
        ) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'a {
            self.into_iter()
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [immutable];
                [mutable];
            ]
            [kinds::IntCoFuncInterp] [Int];
            [kinds::RealCoFuncInterp] [Real];
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn get(&self, domain_enum: DomainEnum) -> Result<codomain_ty, DomainError> {
            paste! {
                match self {
                    Self::codomain_ty(interp) => interp.get(domain_enum),
                    Self::[<codomain_ty Type>](interp) => interp.get(domain_enum),
                }
            }
        }

        /// Panicking version of [Self::get].
        pub fn get_i(&self, domain_enum: DomainEnum) -> codomain_ty {
            self.get(domain_enum).unwrap()
        }

        pub(super) fn symbol_get(
            &self,
            domain_enum: DomainEnum,
        ) -> Result<codomain_ty, DomainError> {
            self.get(domain_enum)
        }

        pub fn iter<'b>(&'b self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'b {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Either::Left(interp.iter()),
                    Self::[<codomain_ty Type>](interp) => Either::Right(interp.iter()),
                }
            }
        }

        pub(super) fn symbol_iter<'b>(
            &'b self,
        ) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'b {
            self.iter()
        }

        pub fn into_iter(self) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'a {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Either::Left(interp.into_iter()),
                    Self::[<codomain_ty Type>](interp) => Either::Right(interp.into_iter()),
                }
            }
        }

        pub(super) fn symbol_into_iter(
            self,
        ) -> impl SIterator<Item = (DomainEnum, codomain_ty)> + 'a {
            self.into_iter()
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            prim_func([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<(), DomainError> {
            if self
                .common
                .domain
                .iter_index(self.common.type_interps)
                .contains(domain_enum)
            {
                Ok(traits::complete::MutFunc::set(
                    &mut self.store,
                    self.common.symbol_info(),
                    domain_enum,
                    value,
                ))
            } else {
                Err(DomainError)
            }
        }

        /// Panicking version of [Self::set].
        pub fn set_i(&mut self, domain_enum: DomainEnum, value: codomain_ty) {
            self.set(domain_enum, value).unwrap()
        }

        pub fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<(), PfuncError> {
            self.set(domain_enum, value)?;
            Ok(())
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            custom_func([kinds])
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<(), PfuncError> {
            if !self
                .common
                .domain
                .iter_index(self.common.type_interps)
                .contains(domain_enum)
            {
                Err(PfuncError::DomainError(DomainError))
            } else if !self.common.codomain_interp.contains(&value) {
                Err(PfuncError::CodomainError(CodomainError))
            } else {
                Ok(traits::complete::MutFunc::set(
                    &mut self.store,
                    self.common.symbol_info(),
                    domain_enum,
                    value,
                ))
            }
        }

        /// Panicking version of [Self::set].
        pub fn set_i(&mut self, domain_enum: DomainEnum, value: codomain_ty) {
            self.set(domain_enum, value).unwrap()
        }

        #[allow(unused)]
        pub(super) fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<(), PfuncError> {
            Ok(self.set(domain_enum, value)?)
        }
    }

    #[duplicate_item(
        name_ty codomain_ty;
        duplicate! {
            [
                kinds;
                [owned];
                [mutable];
            ]
            [kinds::IntCoFuncInterp] [Int];
            [kinds::RealCoFuncInterp] [Real];
        }
    )]
    impl<'a> name_ty<'a> {
        pub fn set(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<(), PfuncError> {
            paste! {
                match self {
                    Self::codomain_ty(interp) => Ok(interp.set(domain_enum, value)?),
                    Self::[<codomain_ty Type>](interp) => interp.set(domain_enum, value),
                }
            }
        }

        /// Panicking version of [Self::set].
        pub fn set_i(&mut self, domain_enum: DomainEnum, value: codomain_ty) {
            self.set(domain_enum, value).unwrap()
        }

        pub(super) fn symbol_set(
            &mut self,
            domain_enum: DomainEnum,
            value: codomain_ty,
        ) -> Result<(), PfuncError> {
            Ok(self.set(domain_enum, value)?)
        }
    }

    //
    // predicates
    //

    #[duplicate_item(
        kinds;
        [owned];
        [immutable];
        [mutable];
    )]
    impl<'a> kinds::PredInterp<'a> {
        pub fn iter_true<'b>(&'b self) -> impl SIterator<Item = DomainEnum> + 'b {
            traits::complete::ImPred::iter_true(&self.store, self.common.symbol_info())
        }

        pub fn into_iter_true(self) -> impl SIterator<Item = DomainEnum> + 'a {
            traits::complete::ImPred::into_iter_true(self.store, self.common.symbol_info())
        }
    }
}

macro_rules! create_big_enum {
    (
        $partial_owned:ident,
        $partial_im:ident,
        $partial_mut:ident,
        $partial_nullary_owned:ident,
        $partial_nullary_immutable:ident,
        $partial_nullary_mutable:ident,
        $partial_func_owned:ident,
        $partial_func_immutable:ident,
        $partial_func_mutable:ident,
        $complete_owned:ident,
        $complete_im:ident,
        $complete_mut:ident,
        $complete_nullary_owned:ident,
        $complete_nullary_immutable:ident,
        $complete_nullary_mutable:ident,
        $complete_func_owned:ident,
        $complete_func_immutable:ident,
        $complete_func_mutable:ident,
        $(
            $e_interp:ident: [
                {
                    $(nullary: $nullary_tag:literal,)?
                    $(func: $func_tag:literal,)?
                },
                $interp_codomain:ident,
                $part_owned_interp_ty:ty,
                $part_im_interp_ty:ty,
                $part_mut_interp_ty:ty,
                $complete_owned_interp_ty:ty,
                $complete_im_interp_ty:ty,
                $complete_mut_interp_ty:ty,
                $unwrap_func:ident,
            ]
        ),* $(,)?
    ) => {
        create_big_enum! {
            create_iterator:
            SymbolIter,
            $(
                $e_interp: (true),
            )*
        }
        create_big_enum! {
            create_iterator:
            FuncIter,
            $($(
                $e_interp: ($func_tag),
            )?)*
        }

        // Partial owned
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $partial_owned,
            partial_symbol_owned,
            $(
                $e_interp: (true, $part_owned_interp_ty),
            )*
        }
        create_big_enum! {
            partial_symbol_im_impls:
            partial_symbol_owned::$partial_owned<'a>,
            complete_symbol_immutable::$complete_im,
            complete_symbol_owned::$complete_owned,
            partial_nullary_owned::$partial_nullary_owned,
            partial_func_owned::$partial_func_owned,
            partial_symbol_owned::$partial_owned,
            SymbolIter,
            $($(
                $e_interp: ($nullary_tag, $part_owned_interp_ty, partial_nullary_owned::$partial_nullary_owned, Left),
            )?)*
            $($(
                $e_interp: ($func_tag, $part_owned_interp_ty, partial_func_owned::$partial_func_owned, Right),
            )?)*
        }
        create_big_enum! {
            partial_mut_impls:
            partial_symbol_owned::$partial_owned<'a>,
            $(
                $e_interp: (true, $part_owned_interp_ty),
            )*
        }

        // partial nullary owned
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $partial_nullary_owned,
            partial_nullary_owned,
            $($(
                $e_interp: ($nullary_tag, $part_owned_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_nullary_im_impls:
            partial_nullary_owned::$partial_nullary_owned<'a>,
            complete_nullary_immutable::$complete_nullary_immutable,
            complete_nullary_owned::$complete_nullary_owned,
            $($(
                $e_interp: ($nullary_tag, $part_owned_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_nullary_mut_impls:
            partial_nullary_owned::$partial_nullary_owned<'a>,
            $($(
                $e_interp: ($nullary_tag, $part_owned_interp_ty),
            )?)*
        }

        // partial func owned
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $partial_func_owned,
            partial_func_owned,
            $($(
                $e_interp: ($func_tag, $part_owned_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_im_impls:
            partial_func_owned::$partial_func_owned<'a>,
            complete_func_immutable::$complete_func_immutable,
            complete_func_owned::$complete_func_owned,
            partial_func_owned::$partial_func_owned,
            FuncIter,
            $($(
                $e_interp: ($func_tag, $part_owned_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_mut_impls:
            partial_func_owned::$partial_func_owned<'a>,
            $($(
                $e_interp: ($func_tag, $part_owned_interp_ty),
            )?)*
        }

        // Partial immutable
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $partial_im,
            partial_symbol_immutable,
            $(
                $e_interp: (true, $part_im_interp_ty),
            )*
        }
        create_big_enum! {
            partial_symbol_im_impls:
            partial_symbol_immutable::$partial_im<'a>,
            complete_symbol_immutable::$complete_im,
            complete_symbol_immutable::$complete_im,
            partial_nullary_immutable::$partial_nullary_immutable,
            partial_func_immutable::$partial_func_immutable,
            partial_symbol_owned::$partial_owned,
            SymbolIter,
            $($(
                $e_interp: (
                    $nullary_tag, $part_im_interp_ty, partial_nullary_immutable::$partial_nullary_immutable, Left
                ),
            )?)*
            $($(
                $e_interp: ($func_tag, $part_im_interp_ty, partial_func_immutable::$partial_func_immutable, Right),
            )?)*
        }

        // partial nullary immutable
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $partial_nullary_immutable,
            partial_nullary_immutable,
            $($(
                $e_interp: ($nullary_tag, $part_im_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_nullary_im_impls:
            partial_nullary_immutable::$partial_nullary_immutable<'a>,
            complete_nullary_immutable::$complete_nullary_immutable,
            complete_nullary_immutable::$complete_nullary_immutable,
            $($(
                $e_interp: ($nullary_tag, $part_im_interp_ty),
            )?)*
        }

        // partial func immutable
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $partial_func_immutable,
            partial_func_immutable,
            $($(
                $e_interp: ($func_tag, $part_im_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_im_impls:
            partial_func_immutable::$partial_func_immutable<'a>,
            complete_func_immutable::$complete_func_immutable,
            complete_func_immutable::$complete_func_immutable,
            partial_func_owned::$partial_func_owned,
            FuncIter,
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty),
            )?)*
        }

        // Partial mutable
        create_big_enum! {
            create:
            #[derive(Debug)]
            $partial_mut,
            partial_symbol_mutable,
            $(
                $e_interp: (true, $part_mut_interp_ty),
            )*
        }
        create_big_enum! {
            partial_symbol_im_impls:
            partial_symbol_mutable::$partial_mut<'a>,
            complete_symbol_immutable::$complete_im,
            complete_symbol_mutable::$complete_mut,
            partial_nullary_mutable::$partial_nullary_mutable,
            partial_func_mutable::$partial_func_mutable,
            partial_symbol_owned::$partial_owned,
            SymbolIter,
            $($(
                $e_interp: (
                    $nullary_tag, $part_mut_interp_ty, partial_nullary_mutable::$partial_nullary_mutable, Left
                ),
            )?)*
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty, partial_func_mutable::$partial_func_mutable, Right),
            )?)*
        }
        create_big_enum! {
            partial_mut_impls:
            partial_symbol_mutable::$partial_mut<'a>,
            $(
                $e_interp: (true, $part_mut_interp_ty),
            )*
        }

        // partial nullary mutable
        create_big_enum! {
            create:
            #[derive(Debug)]
            $partial_nullary_mutable,
            partial_nullary_mutable,
            $($(
                $e_interp: ($nullary_tag, $part_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_nullary_im_impls:
            partial_nullary_mutable::$partial_nullary_mutable<'a>,
            complete_nullary_immutable::$complete_nullary_immutable,
            complete_nullary_mutable::$complete_nullary_mutable,
            $($(
                $e_interp: ($nullary_tag, $part_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_nullary_mut_impls:
            partial_nullary_mutable::$partial_nullary_mutable<'a>,
            $($(
                $e_interp: ($nullary_tag, $part_mut_interp_ty),
            )?)*
        }

        // partial func immutable
        create_big_enum! {
            create:
            #[derive(Debug)]
            $partial_func_mutable,
            partial_func_mutable,
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_im_impls:
            partial_func_mutable::$partial_func_mutable<'a>,
            complete_func_immutable::$complete_func_immutable,
            complete_func_mutable::$complete_func_mutable,
            partial_func_owned::$partial_func_owned,
            FuncIter,
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_mut_impls:
            partial_func_mutable::$partial_func_mutable<'a>,
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty),
            )?)*
        }

        // Complete owned
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $complete_owned,
            complete_symbol_owned,
            $(
                $e_interp: (true, $complete_owned_interp_ty),
            )*
        }
        create_big_enum! {
            complete_symbol_im_impls:
            complete_symbol_owned::$complete_owned<'a>,
            complete_nullary_owned::$partial_nullary_owned,
            complete_func_owned::$partial_func_owned,
            SymbolIter,
            $($(
                $e_interp: (
                    $nullary_tag, $part_owned_interp_ty, complete_nullary_owned::$complete_nullary_owned, Left
                ),
            )?)*
            $($(
                $e_interp: ($func_tag, $part_owned_interp_ty, complete_func_owned::$complete_func_owned, Right),
            )?)*
        }
        create_big_enum! {
            complete_mut_impls:
            complete_symbol_owned::$complete_owned<'a>,
            $(
                $e_interp: (true, $complete_owned_interp_ty),
            )*
        }

        // complete nullary owned
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $complete_nullary_owned,
            complete_nullary_owned,
            $($(
                $e_interp: ($nullary_tag, $complete_owned_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_nullary_im_impls:
            complete_nullary_owned::$complete_nullary_owned<'a>,
            $($(
                $e_interp: ($nullary_tag, $complete_owned_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_nullary_mut_impls:
            complete_nullary_owned::$complete_nullary_owned<'a>,
            $($(
                $e_interp: ($nullary_tag, $complete_owned_interp_ty),
            )?)*
        }

        // complete func owned
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $complete_func_owned,
            complete_func_owned,
            $($(
                $e_interp: ($func_tag, $complete_owned_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_im_impls:
            complete_func_owned::$complete_func_owned<'a>,
            FuncIter,
            $($(
                $e_interp: ($func_tag, $complete_owned_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_mut_impls:
            complete_func_owned::$complete_func_owned<'a>,
            $($(
                $e_interp: ($func_tag, $complete_owned_interp_ty),
            )?)*
        }

        // Complete immutable
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $complete_im,
            complete_symbol_immutable,
            $(
                $e_interp: (true, $complete_im_interp_ty),
            )*
        }
        create_big_enum! {
            complete_symbol_im_impls:
            complete_symbol_immutable::$complete_im<'a>,
            complete_nullary_immutable::$partial_nullary_immutable,
            complete_func_immutable::$partial_func_immutable,
            SymbolIter,
            $($(
                $e_interp: (
                    $nullary_tag, $part_im_interp_ty, complete_nullary_immutable::$complete_nullary_immutable, Left
                ),
            )?)*
            $($(
                $e_interp: ($func_tag, $part_im_interp_ty, complete_func_immutable::$complete_func_immutable, Right),
            )?)*
        }

        // complete nullary immutable
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $complete_nullary_immutable,
            complete_nullary_immutable,
            $($(
                $e_interp: ($nullary_tag, $complete_im_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_nullary_im_impls:
            complete_nullary_immutable::$complete_nullary_immutable<'a>,
            $($(
                $e_interp: ($nullary_tag, $complete_im_interp_ty),
            )?)*
        }

        // complete func immutable
        create_big_enum! {
            create:
            #[derive(Clone, Debug)]
            $complete_func_immutable,
            complete_func_immutable,
            $($(
                $e_interp: ($func_tag, $complete_im_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_im_impls:
            complete_func_immutable::$complete_func_immutable<'a>,
            FuncIter,
            $($(
                $e_interp: ($func_tag, $complete_im_interp_ty),
            )?)*
        }

        // Complete mutable
        create_big_enum! {
            create:
            #[derive(Debug)]
            $complete_mut,
            complete_symbol_mutable,
            $(
                $e_interp: (true, $complete_mut_interp_ty),
            )*
        }
        create_big_enum! {
            complete_symbol_im_impls:
            complete_symbol_mutable::$complete_mut<'a>,
            complete_nullary_mutable::$partial_nullary_mutable,
            complete_func_mutable::$partial_func_mutable,
            SymbolIter,
            $($(
                $e_interp: (
                    $nullary_tag, $part_mut_interp_ty, complete_nullary_mutable::$complete_nullary_mutable, Left
                ),
            )?)*
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty, complete_func_mutable::$complete_func_mutable, Right),
            )?)*
        }
        create_big_enum! {
            complete_mut_impls:
            complete_symbol_mutable::$complete_mut<'a>,
            $(
                $e_interp: (true, $complete_mut_interp_ty),
            )*
        }

        // complete nullary mutable
        create_big_enum! {
            create:
            #[derive(Debug)]
            $complete_nullary_mutable,
            complete_nullary_mutable,
            $($(
                $e_interp: ($nullary_tag, $complete_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_nullary_im_impls:
            complete_nullary_mutable::$complete_nullary_mutable<'a>,
            $($(
                $e_interp: ($nullary_tag, $complete_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_nullary_mut_impls:
            complete_nullary_mutable::$complete_nullary_mutable<'a>,
            $($(
                $e_interp: ($nullary_tag, $complete_mut_interp_ty),
            )?)*
        }

        // complete func mutable
        create_big_enum! {
            create:
            #[derive(Debug)]
            $complete_func_mutable,
            complete_func_mutable,
            $($(
                $e_interp: ($func_tag, $complete_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_im_impls:
            complete_func_mutable::$complete_func_mutable<'a>,
            FuncIter,
            $($(
                $e_interp: ($func_tag, $complete_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_mut_impls:
            complete_func_mutable::$complete_func_mutable<'a>,
            $($(
                $e_interp: ($func_tag, $complete_mut_interp_ty),
            )?)*
        }
    };
    (
        create:
        $(#[$($derives:tt)*])*
        $name:ident,
        $name_mod:ident,
        $($variants:ident: ($($tag:literal)?, $var_ty:ty)),* $(,)?
    ) => {
        mod $name_mod {
            use super::*;
            $(#[$($derives)*])*
            pub enum $name<'a> {
                $(
                    $variants($var_ty),
                )*
            }

            $(
                impl<'a> From<$var_ty> for $name<'a> {
                    fn from(value: $var_ty) -> $name<'a> {
                        $name::$variants(value)
                    }
                }
            )*
        }
        create_big_enum! {
            common_impls:
            $name_mod::$name<'a>,
            $(
                $variants: ($($tag)?, $var_ty),
            )*
        }
    };
    (
        create_iterator:
        $name:ident,
        $($variants:ident: ($($tag:literal)?)),* $(,)?
    ) => {
        pub enum $name<
            $(
                $variants,
            )*
        > {
            $(
                $variants($variants),
            )*
        }

        impl<
            I,
            $(
                $variants: Iterator<Item = I>,
            )*
        > Iterator for $name<
            $(
                $variants,
            )*
        > {
            type Item = I;

            fn next(&mut self) -> Option<Self::Item> {
                match self {
                    $(
                        Self::$variants(value) => value.next(),
                    )*
                }
            }
        }
    };
    (
        common_impls:
        $symbol_ty:ty,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            pub fn domain(&self) -> &'a DomainSlice {
                match self {
                    $(
                        Self::$variants(value) => value.domain(),
                    )*
                }
            }

            pub fn vocab(&self) -> &'a Vocabulary {
                match self {
                    $(
                        Self::$variants(value) => value.vocab(),
                    )*
                }
            }

            pub fn type_interps(&self) -> &'a TypeInterps {
                match self {
                    $(
                        Self::$variants(value) => value.type_interps(),
                    )*
                }
            }

            pub fn codomain(&self) -> Type {
                match self {
                    $(
                        Self::$variants(value) => value.symbol_codomain(),
                    )*
                }
            }

            pub fn codomain_full(&self) -> TypeFull<'a> {
                self.codomain().with_interps(self.type_interps())
            }

            pub fn pfunc_index(&self) -> PfuncIndex {
                match self {
                    $(
                        Self::$variants(value) => value.pfunc_index(),
                    )*
                }
            }
        }
    };
    (
        partial_symbol_im_impls:
        $symbol_ty:ty,
        $as_prefix:ident :: $as_complete_ty:ident,
        $into_prefix:ident :: $into_complete_ty:ident,
        $nullary_prefix:ident :: $nullary:ident,
        $func_prefix:ident :: $func:ident,
        $owned_prefix:ident :: $owned_ty:ident,
        $iterator_name:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty, $cor_prefix:ident::$cor_split:ident, $either_var:ident)),* $(,)?
    ) => {
        create_big_enum! {
            partial_im_impls:
            $symbol_ty,
            $as_prefix::$as_complete_ty,
            $into_prefix::$into_complete_ty,
            $owned_prefix::$owned_ty,
            $iterator_name,
            $(
                $variants: ($($tag,)? $var_ty),
            )*
        }
        impl<'a> $symbol_ty {
            pub fn split(self) -> Either<$nullary_prefix::$nullary<'a>, $func_prefix::$func<'a>> {
                match self {
                    $(
                        Self::$variants(interp) => Either::$either_var($cor_prefix::$cor_split::$variants(interp)),
                    )*
                }
            }
        }
    };
    (
        partial_im_impls:
        $symbol_ty:ty,
        $as_prefix:ident :: $as_complete_ty:ident,
        $into_prefix:ident :: $into_complete_ty:ident,
        $owned_prefix:ident :: $owned_ty:ident,
        $iterator_name:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        create_big_enum! {
            try_into_impls:
            $symbol_ty,
            $as_prefix::$as_complete_ty,
            $into_prefix::$into_complete_ty,
            $(
                $variants: ($($tag,)? $var_ty),
            )*
        }
        impl<'a> $symbol_ty {
            pub fn get(&self, domain_enum: DomainEnum) -> Result<Option<TypeElement>, DomainError> {
                match self {
                    $(
                        Self::$variants(value) => {
                            let ret = value.symbol_get(domain_enum)?;
                            Ok(ret.map(|f| value.symbol_to_type_element(f)))
                        },
                    )*
                }
            }

            pub fn has_interp(&self, domain_enum: DomainEnum) -> Result<bool, DomainError> {
                self.get(domain_enum).map(|f| f.is_some())
            }


            /// Panicking version of [Self::get].
            pub fn get_i(&self, domain_enum: DomainEnum) -> Option<TypeElement> {
                self.get(domain_enum).unwrap()
            }

            pub fn amount_known(&self) -> usize {
                match self {
                    $(
                        Self::$variants(value) => value.symbol_amount_known(),
                    )*
                }
            }

            pub fn amount_unknown(&self) -> usize {
                self.domain().domain_len(self.type_interps()) - self.amount_known()
            }

            pub fn any_known(&self) -> bool {
                self.amount_known() != 0
            }

            pub fn iter<'b>(&'b self) -> impl SIterator<Item = (DomainEnum, TypeElement)> + 'b {
                match self {
                    $(
                        Self::$variants(value) => {
                            let to_type_el_func = value.symbol_to_type_element_func();
                            $iterator_name::$variants(
                                value.iter()
                                    .map(move |(dom, val)| (dom, to_type_el_func(val)))
                            )
                        }
                    )*
                }
            }

            pub fn into_iter(self) -> impl SIterator<Item = (DomainEnum, TypeElement)> + 'a {
                match self {
                    $(
                        Self::$variants(value) => {
                            let to_type_el_func = value.symbol_to_type_element_func();
                            $iterator_name::$variants(
                                value.into_iter()
                                    .map(move |(dom, val)| (dom, to_type_el_func(val)))
                            )
                        }
                    )*
                }
            }

            pub fn iter_unknown<'b>(&'b self) -> impl SIterator<Item = DomainEnum> + 'b {
                match self {
                    $(
                        Self::$variants(interp) => $iterator_name::$variants(
                            interp.iter_unknown()
                        ),
                    )*
                }
            }

            pub fn into_iter_unknown(self) -> impl SIterator<Item = DomainEnum> + 'a {
                match self {
                    $(
                        Self::$variants(interp) => $iterator_name::$variants(
                            interp.into_iter_unknown()
                        ),
                    )*
                }
            }

            /// Create an owned copy of the interpretation.
            pub fn to_owned(&self) -> $owned_prefix::$owned_ty<'a> {
                match self {
                    $(
                        Self::$variants(interp) => $owned_prefix::$owned_ty::$variants(interp.to_owned()),
                    )*
                }
            }
        }
    };
    (
        partial_nullary_im_impls:
        $symbol_ty:ty,
        $as_prefix:ident :: $as_complete_ty:ident,
        $into_prefix:ident :: $into_complete_ty:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        create_big_enum! {
            try_into_impls:
            $symbol_ty,
            $as_prefix::$as_complete_ty,
            $into_prefix::$into_complete_ty,
            $(
                $variants: ($($tag,)? $var_ty),
            )*
        }
        impl<'a> $symbol_ty {
            pub fn get(&self) -> Option<TypeElement> {
                match self {
                    $(
                        Self::$variants(value) => {
                            let ret = value.get();
                            ret.map(|f| value.symbol_to_type_element(f))
                        },
                    )*
                }
            }
        }
    };
    (
        try_into_impls:
        $symbol_ty:ty,
        $as_prefix:ident :: $as_complete_ty:ident,
        $into_prefix:ident :: $into_complete_ty:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            /// Try viewing the interpretation as a complete interpretation
            pub fn try_as_complete<'b>(&'b self) -> Result<$as_prefix::$as_complete_ty<'b>, ()> {
                match self {
                    $(
                        Self::$variants(value) => Ok(
                            $as_prefix::$as_complete_ty::$variants(value.try_as_im_complete()?)
                        ),
                    )*
                }
            }

            pub fn is_complete(&self) -> bool {
                self.try_as_complete().is_ok()
            }

            /// Try converting the interpretation into a complete interpretation.
            pub fn try_into_complete(self) -> Result<$into_prefix::$into_complete_ty<'a>, Self> {
                match self {
                    $(
                        Self::$variants(value) => Ok(
                            $into_prefix::$into_complete_ty::$variants(
                                value.try_into_complete()
                                .map_err(|f| Self::$variants(f))?
                            )
                        ),
                    )*
                }
            }
        }
    };
    (
        partial_mut_impls:
        $symbol_ty:ty,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            pub fn set(
                &mut self,
                domain_enum: DomainEnum,
                value: Option<TypeElement>
            ) -> Result<(), PfuncError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            interp.symbol_set(
                                domain_enum,
                                value.map(|f| interp.symbol_codomain_from_type_element(f))
                                    .transpose()?
                            )?;
                            Ok(())
                        },
                    )*
                }
            }

            /// Panicking version of [Self::set].
            pub fn set_i(
                &mut self,
                domain_enum: DomainEnum,
                value: Option<TypeElement>,
            ) {
                self.set(domain_enum, value).unwrap()
            }

            /// Set the interpretation if the interpretation is unknown.
            ///
            /// Returns a [bool] signifying if the interpretation was set.
            pub fn set_if_unknown(
                &mut self,
                domain_enum: DomainEnum,
                value: TypeElement
            ) -> Result<bool, PfuncError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            interp.symbol_set_if_unknown(
                                domain_enum,
                                interp.symbol_codomain_from_type_element(value)?
                            )
                        },
                    )*
                }
            }

            /// Sets all unknown interpretations with the given value.
            pub fn fill_unknown_with(
                &mut self,
                value: TypeElement
            ) -> Result<(), PfuncError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            interp.symbol_fill_unknown_with(
                                interp.symbol_codomain_from_type_element(value)?
                            )?;
                            Ok(())
                        },
                    )*
                }
            }
        }
    };
    (
        partial_nullary_mut_impls:
        $symbol_ty:ty,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            pub fn set(&mut self, value: Option<TypeElement>) -> Result<(), CodomainError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            interp.nullary_set(
                                value.map(|f| interp.symbol_codomain_from_type_element(f))
                                    .transpose()?
                            )
                        },
                    )*
                }
            }

            /// Panicking version of [Self::set].
            pub fn set_i(&mut self, value: Option<TypeElement>) {
                self.set(value).unwrap()
            }

            /// Set the interpretation if the interpretation is unknown.
            ///
            /// Returns a [bool] signifying if the interpretation was set.
            pub fn set_if_unknown(&mut self, value: TypeElement) -> Result<bool, CodomainError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            interp.nullary_set_if_unknown(
                                interp.symbol_codomain_from_type_element(value)?
                            )
                        },
                    )*
                }
            }
        }
    };
    (
        complete_symbol_im_impls:
        $symbol_ty:ty,
        $nullary_prefix:ident :: $nullary:ident,
        $func_prefix:ident :: $func:ident,
        $iterator_name:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty, $cor_prefix:ident::$cor_split:ident, $either_var:ident)),* $(,)?
    ) => {
        create_big_enum! {
            complete_im_impls:
            $symbol_ty,
            $iterator_name,
            $(
                $variants: ($($tag,)? $var_ty),
            )*
        }
        impl<'a> $symbol_ty {
            /// Splits the enum, into a nullary and a function part.
            pub fn split(self) -> Either<$nullary_prefix::$nullary<'a>, $func_prefix::$func<'a>> {
                match self {
                    $(
                        Self::$variants(interp) => Either::$either_var($cor_prefix::$cor_split::$variants(interp)),
                    )*
                }
            }
        }
    };
    (
        complete_im_impls:
        $symbol_ty:ty,
        $iterator_name:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            pub fn get(
                &self,
                domain_enum: DomainEnum,
            ) -> Result<TypeElement, PfuncError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            Ok(interp.symbol_to_type_element(
                                interp.symbol_get(
                                    domain_enum,
                                )?
                            ))
                        },
                    )*
                }
            }

            /// Panicking version of [Self::get].
            pub fn get_i(&self, domain_enum: DomainEnum) -> TypeElement {
                self.get(domain_enum).unwrap()
            }

            pub fn iter<'b>(&'b self) -> impl SIterator<Item = (DomainEnum, TypeElement)> + 'b {
                match self {
                    $(
                        Self::$variants(value) => {
                            let to_type_el_func = value.symbol_to_type_element_func();
                            $iterator_name::$variants(
                                value.symbol_iter()
                                    .map(move |(dom, val)| (dom, to_type_el_func(val)))
                            )
                        }
                    )*
                }
            }

            pub fn into_iter(self) -> impl SIterator<Item = (DomainEnum, TypeElement)> + use<'a> {
                match self {
                    $(
                        Self::$variants(value) => {
                            let to_type_el_func = value.symbol_to_type_element_func();
                            $iterator_name::$variants(
                                value.symbol_into_iter()
                                    .map(move |(dom, val)| (dom, to_type_el_func(val)))
                            )
                        }
                    )*
                }
            }
        }
    };
    (
        complete_nullary_im_impls:
        $symbol_ty:ty,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            pub fn get(&self) -> TypeElement {
                match self {
                    $(
                        Self::$variants(value) => {
                            let ret = value.get();
                            value.symbol_to_type_element(ret)
                        },
                    )*
                }
            }
        }
    };
    (
        complete_mut_impls:
        $symbol_ty:ty,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            pub fn set(
                &mut self,
                domain_enum: DomainEnum,
                value: TypeElement,
            ) -> Result<(), PfuncError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            interp.symbol_set(
                                domain_enum,
                                interp.symbol_codomain_from_type_element(value)?
                            )?;
                            Ok(())
                        },
                    )*
                }
            }

            /// Panicking version of [Self::set].
            pub fn set_i(
                &mut self,
                domain_enum: DomainEnum,
                value: TypeElement,
            ) {
                self.set(domain_enum, value).unwrap()
            }
        }
    };
    (
        complete_nullary_mut_impls:
        $symbol_ty:ty,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            pub fn set(
                &mut self,
                value: TypeElement,
            ) -> Result<(), CodomainError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            interp.nullary_set(
                                interp.symbol_codomain_from_type_element(value)?
                            )?;
                            Ok(())
                        },
                    )*
                }
            }

            /// Panicking version of [Self::set].
            pub fn set_i(&mut self, value: TypeElement) {
                self.set(value).unwrap()
            }
        }
    };
}

create_big_enum! {
    SymbolInterp,
    SymbolInterp,
    SymbolInterp,
    NullaryInterp,
    NullaryInterp,
    NullaryInterp,
    FuncInterp,
    FuncInterp,
    FuncInterp,
    SymbolInterp,
    SymbolInterp,
    SymbolInterp,
    NullaryInterp,
    NullaryInterp,
    NullaryInterp,
    FuncInterp,
    FuncInterp,
    FuncInterp,
    Prop: [
        {
            nullary: true,
        },
        bool,
        partial::owned::PropInterp<'a>,
        partial::immutable::PropInterp<'a>,
        partial::mutable::PropInterp<'a>,
        complete::owned::PropInterp<'a>,
        complete::immutable::PropInterp<'a>,
        complete::mutable::PropInterp<'a>,
        unwrap_prop,
    ],
    IntConst: [
        {
            nullary: true,
        },
        Int,
        partial::owned::IntCoConstInterp<'a>,
        partial::immutable::IntCoConstInterp<'a>,
        partial::mutable::IntCoConstInterp<'a>,
        complete::owned::IntCoConstInterp<'a>,
        complete::immutable::IntCoConstInterp<'a>,
        complete::mutable::IntCoConstInterp<'a>,
        unwrap_int_const,
    ],
    RealConst: [
        {
            nullary: true,
        },
        Real,
        partial::owned::RealCoConstInterp<'a>,
        partial::immutable::RealCoConstInterp<'a>,
        partial::mutable::RealCoConstInterp<'a>,
        complete::owned::RealCoConstInterp<'a>,
        complete::immutable::RealCoConstInterp<'a>,
        complete::mutable::RealCoConstInterp<'a>,
        unwrap_real_const,
    ],
    StrConst: [
        {
            nullary: true,
        },
        TypeEnum,
        partial::owned::StrConstInterp<'a>,
        partial::immutable::StrConstInterp<'a>,
        partial::mutable::StrConstInterp<'a>,
        complete::owned::StrConstInterp<'a>,
        complete::immutable::StrConstInterp<'a>,
        complete::mutable::StrConstInterp<'a>,
        unwrap_str_const,
    ],
    Pred: [
        {
            func: true,
        },
        bool,
        partial::owned::PredInterp<'a>,
        partial::immutable::PredInterp<'a>,
        partial::mutable::PredInterp<'a>,
        complete::owned::PredInterp<'a>,
        complete::immutable::PredInterp<'a>,
        complete::mutable::PredInterp<'a>,
        unwrap_pred,
    ],
    IntFunc: [
        {
            func: true,
        },
        Int,
        partial::owned::IntCoFuncInterp<'a>,
        partial::immutable::IntCoFuncInterp<'a>,
        partial::mutable::IntCoFuncInterp<'a>,
        complete::owned::IntCoFuncInterp<'a>,
        complete::immutable::IntCoFuncInterp<'a>,
        complete::mutable::IntCoFuncInterp<'a>,
        unwrap_int_func,
    ],
    RealFunc: [
        {
            func: true,
        },
        Real,
        partial::owned::RealCoFuncInterp<'a>,
        partial::immutable::RealCoFuncInterp<'a>,
        partial::mutable::RealCoFuncInterp<'a>,
        complete::owned::RealCoFuncInterp<'a>,
        complete::immutable::RealCoFuncInterp<'a>,
        complete::mutable::RealCoFuncInterp<'a>,
        unwrap_real_func,
    ],
    StrFunc: [
        {
            func: true,
        },
        Typenum,
        partial::owned::StrFuncInterp<'a>,
        partial::immutable::StrFuncInterp<'a>,
        partial::mutable::StrFuncInterp<'a>,
        complete::owned::StrFuncInterp<'a>,
        complete::immutable::StrFuncInterp<'a>,
        complete::mutable::StrFuncInterp<'a>,
        unwrap_str_func,
    ],
}
