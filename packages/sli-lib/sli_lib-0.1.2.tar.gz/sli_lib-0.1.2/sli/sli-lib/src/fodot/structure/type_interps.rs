use crate::fodot::error::{
    BaseTypeMismatchError, ConvertTypeElementError, MissingTypeElementError, MissingTypeInterps,
    MissingTypeInterpsError, NoBuiltinTypeInterp, OverflowError, ParseIntSubTypeError,
    ParseRealSubTypeError, ParseTypeElementError, SetTypeInterpError, TypeInterpFromStrError,
    TypeMismatch, VocabMismatchError, WithPartialInterpsError,
};
use crate::fodot::fmt::{FALSE, Fmt, FodotDisplay, FodotOptions, FormatOptions, TRUE};
use crate::fodot::vocabulary::{
    BaseType, IntType, RealType, StrType, TypeStr, TypeSymbolIndex, Vocabulary, parse_bool_value,
    parse_int_value, parse_real_value,
};
use crate::fodot::vocabulary::{CustomTypeRef, IntTypeRef, RealTypeRef, StrTypeRef, TypeRef};
use crate::fodot::{TryFromCtx, display_as_debug};
use comp_core::vocabulary::TypeIndex;
use comp_core::{self as cc, IndexRepr, Int, Real};
use core::ops::{Range, RangeInclusive};
use core::panic;
use duplicate::duplicate_item;
use indexmap::IndexSet;
use itertools::Itertools;
use sli_collections::rc::{PtrRepr, RcA};
use sli_collections::{hash_map::IdHashMap, iterator::Iterator as SIterator, rc::Rc};
use std::borrow::Borrow;
use std::fmt::Display;
use std::fmt::Write;
use std::ops::Deref;

/// Parse a builtin [TypeElement] such as `0` or `true`.
pub fn parse_builtin_type_element<'a>(value: &str) -> Result<TypeElement<'a>, ()> {
    match value {
        TRUE => Ok(true.into()),
        FALSE => Ok(false.into()),
        other => {
            if let Ok(int) = other.parse() {
                Ok(TypeElement::Int(int))
            } else if let Ok(real) = other.parse() {
                Ok(TypeElement::Real(real))
            } else {
                Err(())
            }
        }
    }
}

/// Represents an FO(·) element.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TypeElement<'a> {
    Bool(bool),
    Int(Int),
    Real(Real),
    Str(StrElement<'a>),
}

impl<'a> FodotOptions for TypeElement<'a> {
    type Options<'b> = FormatOptions;
}

impl<'a> FodotDisplay for TypeElement<'a> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            TypeElement::Bool(value) => write!(f, "{}", value),
            TypeElement::Int(value) => write!(f, "{}", value),
            TypeElement::Real(value) => write!(f, "{}", value),
            TypeElement::Str(value) => write!(f, "{}", value),
        }
    }
}

impl<'a> Display for TypeElement<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl<'a> From<bool> for TypeElement<'a> {
    fn from(value: bool) -> Self {
        TypeElement::Bool(value)
    }
}

impl<'a> From<Int> for TypeElement<'a> {
    fn from(value: Int) -> Self {
        TypeElement::Int(value)
    }
}

impl<'a> From<Real> for TypeElement<'a> {
    fn from(value: Real) -> Self {
        TypeElement::Real(value)
    }
}

impl<'a> TypeElement<'a> {
    /// Returns the corresponding [TypeInterps] if there is one.
    pub fn type_interps(&self) -> Option<&'a PartialTypeInterps> {
        match self {
            Self::Bool(_) | Self::Int(_) | Self::Real(_) => None,
            Self::Str(value) => Some(value.type_interps),
        }
    }

    pub fn codomain(&self) -> TypeRef<'a> {
        match self {
            Self::Bool(_) => TypeRef::Bool,
            Self::Int(_) => TypeRef::Int,
            Self::Real(_) => TypeRef::Real,
            Self::Str(value) => TypeRef::StrType(value.decl()),
        }
    }
}

impl<'a, I: Borrow<str>> TryFromCtx<I> for TypeElement<'a> {
    type Ctx = TypeFull<'a>;
    type Error = ParseTypeElementError;

    fn try_from_ctx(value: I, ctx: Self::Ctx) -> Result<Self, Self::Error> {
        match ctx {
            TypeFull::Bool => Ok(parse_bool_value(value.borrow())?.into()),
            TypeFull::Int => Ok(parse_int_value(value.borrow())?.into()),
            TypeFull::Real => Ok(parse_real_value(value.borrow())?.into()),
            TypeFull::IntType(interp) => Ok(interp.parse_value(value.borrow())?.into()),
            TypeFull::RealType(interp) => Ok(interp.parse_value(value.borrow())?.into()),
            TypeFull::Str(interp) => Ok(interp.parse_value(value.borrow())?.into()),
        }
    }
}

impl<'a, 'b> TryFromCtx<TypeElement<'a>> for TypeElement<'b> {
    type Ctx = TypeFull<'b>;
    type Error = ConvertTypeElementError;

    fn try_from_ctx(value: TypeElement<'a>, ctx: Self::Ctx) -> Result<Self, Self::Error> {
        match (value, ctx) {
            (TypeElement::Bool(value), TypeFull::Bool) => Ok(value.into()),
            (TypeElement::Int(value), TypeFull::Int) => Ok(value.into()),
            (TypeElement::Real(value), TypeFull::Real) => Ok(value.into()),
            (TypeElement::Int(value), TypeFull::IntType(interp)) => {
                if interp.contains(value) {
                    Ok(value.into())
                } else {
                    Err(MissingTypeElementError.into())
                }
            }
            (TypeElement::Real(value), TypeFull::RealType(interp)) => {
                if interp.contains(value) {
                    Ok(value.into())
                } else {
                    Err(MissingTypeElementError.into())
                }
            }
            (TypeElement::Str(value), TypeFull::Str(interp)) => {
                if core::ptr::eq(value.type_interps, interp.type_interps) {
                    // This is safe since we confirmed above that type_interps of 'a does
                    // infact live for atleast 'b
                    Ok(
                        unsafe { core::mem::transmute::<StrElement<'a>, StrElement<'b>>(value) }
                            .into(),
                    )
                } else {
                    Err(MissingTypeElementError.into())
                }
            }
            (val, ty) => Err(TypeMismatch {
                found: val.codomain().into(),
                expected: ty.into(),
            }
            .into()),
        }
    }
}

/// Represents an non-builtin element.
pub enum CustomElement<'a> {
    Str(StrElement<'a>),
}

impl<'a> From<StrElement<'a>> for CustomElement<'a> {
    fn from(value: StrElement<'a>) -> Self {
        Self::Str(value)
    }
}

impl<'a> From<CustomElement<'a>> for TypeElement<'a> {
    fn from(value: CustomElement<'a>) -> Self {
        match value {
            CustomElement::Str(value) => value.into(),
        }
    }
}

/// Represents a str element.
#[derive(Clone)]
pub struct StrElement<'a> {
    // this value field MUST come from the type interps below (or any reference that points to
    // the same type_interps)
    pub(crate) value: &'a str,
    pub(crate) type_decl_index: TypeSymbolIndex,
    pub(crate) type_interps: &'a PartialTypeInterps,
}

impl<'a> FodotOptions for StrElement<'a> {
    type Options<'b> = FormatOptions;
}

impl<'a> FodotDisplay for StrElement<'a> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        f.write_str(fmt.value.value)
    }
}

display_as_debug!(StrElement<'a>, gen: ('a));

impl<'a> Display for StrElement<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl<'a> PartialEq for StrElement<'a> {
    fn eq(&self, other: &Self) -> bool {
        core::ptr::eq(self.type_interps, other.type_interps)
            && self.type_decl_index == other.type_decl_index
            && self.value == other.value
    }
}

impl<'a> Eq for StrElement<'a> {}

impl<'a> Deref for StrElement<'a> {
    type Target = str;

    fn deref(&self) -> &Self::Target {
        self.value
    }
}

impl<'a> From<StrElement<'a>> for TypeElement<'a> {
    fn from(value: StrElement<'a>) -> Self {
        Self::Str(value)
    }
}

impl<'a> StrElement<'a> {
    /// Returns the corresponding type declaration.
    pub fn decl(&self) -> StrTypeRef<'a> {
        StrType(self.type_decl_index, self.type_interps.vocab())
    }

    pub fn type_interps(&self) -> &'a PartialTypeInterps {
        self.type_interps
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum StrTypeElement {
    Bool(bool),
    Int(Int),
    Real(Real),
    Str(Box<str>),
}

impl<'a> From<TypeElement<'a>> for StrTypeElement {
    fn from(value: TypeElement<'a>) -> Self {
        match value {
            TypeElement::Bool(value) => Self::Bool(value),
            TypeElement::Int(value) => Self::Int(value),
            TypeElement::Real(value) => Self::Real(value),
            TypeElement::Str(value) => Self::Str(value.value.to_owned().into_boxed_str()),
        }
    }
}

impl Display for StrTypeElement {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Bool(value) => write!(f, "{}", value),
            Self::Int(value) => write!(f, "{}", value),
            Self::Real(value) => write!(f, "{}", value),
            Self::Str(value) => write!(f, "{}", value),
        }
    }
}

#[repr(transparent)]
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct IntInterp(pub(crate) cc::structure::IntInterp);

impl IntInterp {
    pub fn len(&self) -> usize {
        self.0.len()
    }

    pub fn new() -> IntInterp {
        Self(cc::structure::IntInterp::new())
    }

    pub fn try_from_iterator<T>(value: T) -> Result<Self, OverflowError>
    where
        T: IntoIterator<Item = Int>,
    {
        Ok(Self(
            cc::structure::IntInterp::try_from_iterator(value).map_err(|_| OverflowError)?,
        ))
    }

    pub fn contains(&self, value: Int) -> bool {
        self.0.contains(&value)
    }

    pub(crate) fn rc_to_cc(value: Rc<IntInterp>) -> Rc<cc::structure::IntInterp> {
        // Safety:
        // IntInterp is repr(transparent) over cc::structure::IntInterp.
        unsafe { core::mem::transmute::<Rc<IntInterp>, Rc<cc::structure::IntInterp>>(value) }
    }
}

impl From<IntInterp> for cc::structure::IntInterp {
    fn from(value: IntInterp) -> Self {
        value.0
    }
}

impl FromIterator<Int> for IntInterp {
    fn from_iter<T: IntoIterator<Item = Int>>(iter: T) -> Self {
        Self::try_from_iterator(iter).expect("Number too big")
    }
}

pub mod int_interp {
    use super::Int;
    use comp_core::structure::IntInterpIter;
    #[repr(transparent)]
    #[derive(Clone, Debug)]
    pub struct Iter<'a>(pub(crate) IntInterpIter<'a>);

    impl<'a> Iterator for Iter<'a> {
        type Item = Int;

        fn next(&mut self) -> Option<Self::Item> {
            self.0.next()
        }
    }
}

impl TryFrom<Range<Int>> for IntInterp {
    type Error = OverflowError;

    fn try_from(value: Range<Int>) -> Result<Self, Self::Error> {
        Ok(Self(value.try_into().map_err(|_| OverflowError)?))
    }
}

impl TryFrom<RangeInclusive<Int>> for IntInterp {
    type Error = OverflowError;

    fn try_from(value: RangeInclusive<Int>) -> Result<Self, Self::Error> {
        Ok(Self(value.try_into().map_err(|_| OverflowError)?))
    }
}

impl<'a> IntoIterator for &'a IntInterp {
    type Item = Int;
    type IntoIter = int_interp::Iter<'a>;

    fn into_iter(self) -> Self::IntoIter {
        int_interp::Iter(self.0.into_iter())
    }
}

impl FodotOptions for IntInterp {
    type Options<'b> = FormatOptions;
}

impl FodotDisplay for IntInterp {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        f.write_char('{')?;
        if fmt.value.len() != 0 {
            write!(f, "{}", fmt.value.into_iter().format(", "))?;
        }
        f.write_char('}')
    }
}

impl Display for IntInterp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

#[repr(transparent)]
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct RealInterp(cc::structure::RealInterp);

impl RealInterp {
    pub fn new() -> Self {
        Self(cc::structure::RealInterp::new())
    }

    pub fn len(&self) -> usize {
        self.0.len()
    }

    pub fn contains(&self, value: Real) -> bool {
        self.0.contains(&value)
    }

    pub fn insert(&mut self, value: Real) {
        self.0.insert(value);
    }

    pub(crate) fn rc_to_cc(value: Rc<RealInterp>) -> Rc<cc::structure::RealInterp> {
        // Safety:
        // RealInterp is repr(transparent) over cc::structure::RealInterp.
        unsafe { core::mem::transmute::<Rc<RealInterp>, Rc<cc::structure::RealInterp>>(value) }
    }
}

pub mod real_interp {
    use super::Real;
    use comp_core::structure::RealInterp;
    #[derive(Clone, Debug)]
    pub struct Iter<'a>(pub(crate) <&'a RealInterp as IntoIterator>::IntoIter);

    impl<'a> Iterator for Iter<'a> {
        type Item = &'a Real;

        fn next(&mut self) -> Option<Self::Item> {
            self.0.next()
        }
    }
}

impl<'a> IntoIterator for &'a RealInterp {
    type Item = &'a Real;
    type IntoIter = real_interp::Iter<'a>;

    fn into_iter(self) -> Self::IntoIter {
        real_interp::Iter(self.0.into_iter())
    }
}

impl FromIterator<Real> for RealInterp {
    fn from_iter<T: IntoIterator<Item = Real>>(iter: T) -> Self {
        Self(cc::structure::RealInterp::from_iter(iter))
    }
}

impl FodotOptions for RealInterp {
    type Options<'b> = FormatOptions;
}

impl FodotDisplay for RealInterp {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        f.write_char('{')?;
        if fmt.value.len() != 0 {
            write!(f, "{}", fmt.value.into_iter().format(", "))?;
        }
        f.write_char('}')
    }
}

impl Display for RealInterp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

/// Represents a type interpretation of str elements.
/// i.e. `type A := { a, b, c }`
#[derive(PartialEq, Eq, Clone)]
pub struct StrInterp(pub(crate) IndexSet<Rc<str>>);

impl StrInterp {
    /// Create an empty [StrInterp].
    pub fn new() -> Self {
        StrInterp(Default::default())
    }

    /// Returns the amount of items in the type interpretation.
    pub fn len(&self) -> usize {
        self.0.len()
    }

    pub fn iter<'a>(&'a self) -> <&'a IndexSet<Rc<str>> as IntoIterator>::IntoIter {
        self.into_iter()
    }
}

impl FodotOptions for StrInterp {
    type Options<'b> = FormatOptions;
}

impl FodotDisplay for StrInterp {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        f.write_char('{')?;
        if fmt.value.len() != 0 {
            write!(f, "{}", fmt.value.into_iter().format(", "))?;
        }
        f.write_char('}')
    }
}

impl Display for StrInterp {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(StrInterp);

impl<'a> IntoIterator for &'a StrInterp {
    type Item = <&'a IndexSet<Rc<str>> as IntoIterator>::Item;
    type IntoIter = <&'a IndexSet<Rc<str>> as IntoIterator>::IntoIter;

    fn into_iter(self) -> Self::IntoIter {
        self.0.borrow().into_iter()
    }
}

impl FromIterator<Rc<str>> for StrInterp {
    fn from_iter<T: IntoIterator<Item = Rc<str>>>(iter: T) -> Self {
        Self(IndexSet::from_iter(iter))
    }
}

impl<'a> FromIterator<&'a str> for StrInterp {
    fn from_iter<T: IntoIterator<Item = &'a str>>(iter: T) -> Self {
        Self(IndexSet::from_iter(iter.into_iter().map(|f| f.into())))
    }
}

/// An enum of type interpretations.
#[derive(Debug, Clone)]
pub enum TypeInterp {
    Int(Rc<IntInterp>),
    Real(Rc<RealInterp>),
    Str(Rc<StrInterp>),
}

impl From<IntInterp> for TypeInterp {
    fn from(value: IntInterp) -> Self {
        Self::Int(value.into())
    }
}

impl From<Rc<IntInterp>> for TypeInterp {
    fn from(value: Rc<IntInterp>) -> Self {
        Self::Int(value)
    }
}

impl From<RealInterp> for TypeInterp {
    fn from(value: RealInterp) -> Self {
        Self::Real(value.into())
    }
}

impl From<Rc<RealInterp>> for TypeInterp {
    fn from(value: Rc<RealInterp>) -> Self {
        Self::Real(value)
    }
}

impl From<StrInterp> for TypeInterp {
    fn from(value: StrInterp) -> Self {
        Self::Str(value.into())
    }
}

impl From<Rc<StrInterp>> for TypeInterp {
    fn from(value: Rc<StrInterp>) -> Self {
        Self::Str(value)
    }
}

impl TypeInterp {
    pub fn base_type(&self) -> BaseType {
        match self {
            Self::Int(_) => BaseType::Int,
            Self::Real(_) => BaseType::Real,
            Self::Str(_) => BaseType::Str,
        }
    }
}

#[derive(Default, Clone)]
pub(crate) struct _PartialTypeInterps(IdHashMap<TypeSymbolIndex, TypeInterp>);

impl _PartialTypeInterps {
    pub fn add_interp(&mut self, index: TypeSymbolIndex, interp: TypeInterp) {
        self.0.insert(index, interp);
    }

    pub fn get_interp(&self, index: TypeSymbolIndex) -> Option<&TypeInterp> {
        self.0.get(&index)
    }
}

/// A collection of type interpretations where a type is allowed to not have an interpretation.
///
/// After ensuring that all types declared in the underlying vocabulary have been given an
/// interpretation calling [Self::try_complete] returns a [TypeInterps].
#[derive(Clone)]
pub struct PartialTypeInterps {
    pub(crate) vocab: Rc<Vocabulary>,
    /// Incomplete types are represented using empty types on the comp-core side.
    pub(crate) cc: Rc<cc::structure::TypeInterps>,
    pub(crate) str_interps: IdHashMap<TypeSymbolIndex, Rc<StrInterp>>,
    pub(crate) complete: Box<[bool]>,
}

impl FodotOptions for PartialTypeInterps {
    type Options<'b> = FormatOptions;
}

impl FodotDisplay for PartialTypeInterps {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        for type_interp in fmt.value.iter() {
            fmt.options.write_indent(f)?;
            writeln!(f, "{}.", fmt.with_format_opts(&type_interp))?;
        }
        Ok(())
    }
}

impl Display for PartialTypeInterps {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(PartialTypeInterps);

impl PartialEq for PartialTypeInterps {
    fn eq(&self, other: &Self) -> bool {
        Rc::ptr_eq(&self.vocab, &other.vocab)
            && self.complete == other.complete
            && self.cc.interps() == other.cc.interps()
    }
}

impl PartialEq<TypeInterps> for PartialTypeInterps {
    fn eq(&self, other: &TypeInterps) -> bool {
        Rc::ptr_eq(&self.vocab, other.vocab_rc())
            && self.is_complete()
            && self.cc.interps() == other.0.cc.interps()
    }
}

impl PartialEq<PartialTypeInterps> for TypeInterps {
    fn eq(&self, other: &PartialTypeInterps) -> bool {
        PartialEq::<TypeInterps>::eq(other, self)
    }
}

impl PartialTypeInterps {
    pub(crate) fn for_vocab(vocab: Rc<Vocabulary>) -> Self {
        let (raw, complete): (Vec<_>, Vec<_>) = vocab
            .id_iter_types()
            .map(|i| {
                let cc_id = vocab.type_decl_to_cc(i);
                if let Some(value) = vocab.part_type_interps.get_interp(i) {
                    return (
                        match value {
                            TypeInterp::Int(value) => IntInterp::rc_to_cc(value.clone()).into(),
                            TypeInterp::Real(value) => RealInterp::rc_to_cc(value.clone()).into(),
                            TypeInterp::Str(value) => {
                                cc::structure::StrInterp::new(value.len()).into()
                            }
                        },
                        true,
                    );
                }
                let cc_decl = &vocab.comp_core_symbs.types[cc_id];
                // type interp not known yet, insert empty interpretations on comp-core side.
                (
                    match cc_decl.super_type {
                        cc::vocabulary::BaseType::Int => {
                            cc::structure::IntInterp::try_from_iterator([])
                                .unwrap()
                                .into()
                        }
                        cc::vocabulary::BaseType::Real => cc::structure::RealInterp::new().into(),
                        cc::vocabulary::BaseType::Str => cc::structure::StrInterp::new(0).into(),
                    },
                    false,
                )
            })
            .unzip();
        Self {
            cc: Rc::new(
                cc::structure::TypeInterps::try_from_raw(vocab.comp_core_symbs.clone(), raw.into())
                    .unwrap(),
            ),
            str_interps: vocab
                .part_type_interps
                .0
                .iter()
                .filter_map(|f| match f.1 {
                    TypeInterp::Str(interp) => Some((*f.0, interp.clone())),
                    TypeInterp::Int(_) | TypeInterp::Real(_) => None,
                })
                .collect(),
            complete: complete.into_boxed_slice(),
            vocab,
        }
    }

    pub(crate) fn ensured_get_interp(&self, custom_type: CustomTypeRef) -> _TypeInterpRef {
        self._get_interp(custom_type).unwrap()
    }

    pub(crate) fn _get_interp(&self, custom_type: CustomTypeRef) -> Option<_TypeInterpRef> {
        use cc::structure::TypeInterp as TI;
        if !self.complete[usize::from(custom_type.type_id())] {
            return None;
        }
        Some(
            match (
                &self.cc[TypeIndex::from(IndexRepr::from(custom_type.type_id()))],
                custom_type.super_type(),
            ) {
                (TI::Int(int_interp), BaseType::Int) => _TypeInterpRef::Int(unsafe {
                    core::mem::transmute::<&cc::structure::IntInterp, &IntInterp>(
                        int_interp.as_ref(),
                    )
                }),
                (TI::Real(real_interp), BaseType::Real) => _TypeInterpRef::Real(unsafe {
                    core::mem::transmute::<&cc::structure::RealInterp, &RealInterp>(
                        real_interp.as_ref(),
                    )
                }),
                (TI::Custom(_), BaseType::Str) => {
                    _TypeInterpRef::Str(&self.str_interps[&custom_type.type_id()])
                }
                _ => unreachable!(),
            },
        )
    }

    pub(crate) fn _get_interp_cloned(&self, custom_type: CustomTypeRef) -> Option<TypeInterp> {
        use cc::structure::TypeInterp as TI;
        if !self.complete[usize::from(custom_type.type_id())] {
            return None;
        }
        Some(
            match (
                &self.cc[TypeIndex::from(IndexRepr::from(custom_type.type_id()))],
                custom_type.super_type(),
            ) {
                (TI::Int(int_interp), BaseType::Int) => {
                    let raw = Rc::into_raw(Rc::clone(int_interp));
                    // Safety:
                    // IntInterp is repr(transparent) of comp-core IntInterp
                    TypeInterp::Int(unsafe { Rc::from_raw(raw as *const IntInterp) })
                }
                (TI::Real(real_interp), BaseType::Real) => {
                    let raw = Rc::into_raw(Rc::clone(real_interp));
                    // Safety:
                    // RealInterp is repr(transparent) of comp-core RealInterp
                    TypeInterp::Real(unsafe { Rc::from_raw(raw as *const RealInterp) })
                }
                (TI::Custom(_), BaseType::Str) => {
                    TypeInterp::Str(Rc::clone(&self.str_interps[&custom_type.type_id()]))
                }
                _ => unreachable!(),
            },
        )
    }

    pub fn vocab(&self) -> &Vocabulary {
        &self.vocab
    }

    pub fn vocab_rc(&self) -> &Rc<Vocabulary> {
        &self.vocab
    }

    pub fn set_interp(
        &mut self,
        custom_type: CustomTypeRef,
        interp: TypeInterp,
    ) -> Result<(), SetTypeInterpError> {
        if !custom_type.vocab().exact_eq(self.vocab()) {
            return Err(VocabMismatchError.into());
        }
        let cc_id = self.vocab().type_decl_to_cc(custom_type.type_id());
        match (custom_type, interp) {
            (CustomTypeRef::Int(_), TypeInterp::Int(interp)) => {
                Rc::make_mut(&mut self.cc).mut_interps()[cc_id] =
                    IntInterp::rc_to_cc(interp).into();
            }
            (CustomTypeRef::Real(_), TypeInterp::Real(interp)) => {
                Rc::make_mut(&mut self.cc).mut_interps()[cc_id] =
                    RealInterp::rc_to_cc(interp).into();
            }
            (CustomTypeRef::Str(value), TypeInterp::Str(interp)) => {
                Rc::make_mut(&mut self.cc).mut_interps()[cc_id] =
                    cc::structure::StrInterp::new(interp.len()).into();
                self.str_interps.insert(value.0, interp);
            }
            (cust, interp) => {
                let declared_base = match cust {
                    CustomTypeRef::Int(_) => BaseType::Int,
                    CustomTypeRef::Real(_) => BaseType::Real,
                    CustomTypeRef::Str(_) => BaseType::Str,
                };
                return Err(BaseTypeMismatchError {
                    found: interp.base_type(),
                    expected: declared_base,
                }
                .into());
            }
        };
        self.complete[usize::from(custom_type.type_id())] = true;
        Ok(())
    }

    pub fn get_interp_from_str(
        &self,
        type_name: &str,
    ) -> Result<Option<TypeInterpRef>, TypeInterpFromStrError> {
        let type_ = self.vocab.parse_type(type_name)?;
        match type_ {
            TypeRef::Bool => Err(NoBuiltinTypeInterp.into()),
            TypeRef::Int => Err(NoBuiltinTypeInterp.into()),
            TypeRef::Real => Err(NoBuiltinTypeInterp.into()),
            TypeRef::IntType(int_type) => self
                ._get_interp(int_type.into())
                .map(|interp| {
                    Ok(IntInterpRef {
                        decl: int_type,
                        interp: interp.unwrap_int(),
                    }
                    .into())
                })
                .transpose(),
            TypeRef::RealType(real_type) => self
                ._get_interp(real_type.into())
                .map(|interp| {
                    Ok(RealInterpRef {
                        decl: real_type,
                        interp: interp.unwrap_real(),
                    }
                    .into())
                })
                .transpose(),
            TypeRef::StrType(str_type) => self
                ._get_interp(str_type.into())
                .map(|interp| {
                    Ok(StrInterpRef {
                        decl: str_type,
                        interp: interp.unwrap_str(),
                    }
                    .into())
                })
                .transpose(),
        }
    }

    pub fn get_interp<'a>(
        &'a self,
        type_: CustomTypeRef<'a>,
    ) -> Result<Option<CustomTypeFull<'a>>, VocabMismatchError> {
        if !self.vocab.exact_eq(type_.vocab()) {
            return Err(VocabMismatchError.into());
        }
        match (self._get_interp(type_), type_) {
            (Some(_TypeInterpRef::Int(interp)), CustomTypeRef::Int(decl)) => Ok(Some(
                IntTypeFull {
                    type_decl_index: decl.0,
                    type_interps: self,
                    interp,
                }
                .into(),
            )),
            (Some(_TypeInterpRef::Real(interp)), CustomTypeRef::Real(decl)) => Ok(Some(
                RealTypeFull {
                    type_decl_index: decl.0,
                    type_interps: self,
                    interp,
                }
                .into(),
            )),
            (Some(_TypeInterpRef::Str(interp)), CustomTypeRef::Str(decl)) => Ok(Some(
                StrTypeFull {
                    type_decl_index: decl.0,
                    type_interps: self,
                    interp,
                }
                .into(),
            )),
            (None, _) => Ok(None),
            _ => unreachable!(),
        }
    }

    pub fn get_interp_cloned(
        &self,
        custom_type: CustomTypeRef,
    ) -> Result<Option<TypeInterp>, VocabMismatchError> {
        if !self.vocab.exact_eq(custom_type.vocab()) {
            return Err(VocabMismatchError.into());
        }
        Ok(self._get_interp_cloned(custom_type))
    }

    pub fn is_complete(&self) -> bool {
        self.complete.iter().all(|f| *f)
    }

    pub fn try_complete(self) -> Result<TypeInterps, Self> {
        if self.is_complete() {
            Ok(TypeInterps(self))
        } else {
            Err(self)
        }
    }

    pub fn try_rc_into_complete(this: Rc<Self>) -> Result<Rc<TypeInterps>, Rc<Self>> {
        if this.is_complete() {
            // Safety:
            // Self is repr transparent of PartialTypeInterps.
            Ok(unsafe { Rc::from_raw(Rc::into_raw(this) as *const TypeInterps) })
        } else {
            Err(this)
        }
    }

    pub fn missing_type_error(&self) -> MissingTypeInterps {
        MissingTypeInterps {
            missing: self.iter_missing().map(|f| f.name().to_string()).collect(),
        }
    }

    /// Tries to convert `self` to a [TypeInterps].
    ///
    /// Returns a [MissingTypeInterpsError] on failure.
    ///
    /// See also [Self::try_complete], which returns this [PartialTypeInterps] instead of an actual
    /// error.
    pub fn try_err_complete(self) -> Result<TypeInterps, MissingTypeInterpsError> {
        self.try_into()
    }

    pub fn from_rc_complete(type_interps: Rc<TypeInterps>) -> Rc<Self> {
        // Safety:
        // type_interps is repr transparent of PartialTypeInterps.
        unsafe { Rc::from_raw(Rc::into_raw(type_interps) as *const Self) }
    }

    pub fn has_interp(&self, type_: CustomTypeRef) -> Result<bool, VocabMismatchError> {
        if !self.vocab().exact_eq(type_.vocab()) {
            return Err(VocabMismatchError);
        }
        Ok(self.complete[usize::from(type_.type_id())])
    }

    pub fn iter(&self) -> impl SIterator<Item = CustomTypeFull> {
        self.vocab
            .iter_types()
            .filter_map(|f| self.get_interp(f).unwrap())
    }

    pub fn iter_missing<'a>(&'a self) -> impl Iterator<Item = CustomTypeRef<'a>> + use<'a> {
        self.complete.iter().enumerate().filter(|f| *f.1).map(|f| {
            let type_id = TypeSymbolIndex::from(f.0);
            self.vocab._get_type(type_id)
        })
    }
}

#[allow(unused)]
#[repr(transparent)]
pub struct TypeInterps(pub(crate) PartialTypeInterps);

pub trait IntoPtr<I> {
    type Target: PtrRepr<I>;
    fn into_ptr(self) -> Self::Target;
}

impl<'a> IntoPtr<PartialTypeInterps> for &'a TypeInterps {
    type Target = &'a PartialTypeInterps;
    fn into_ptr(self) -> Self::Target {
        self.into()
    }
}

impl IntoPtr<PartialTypeInterps> for RcA<TypeInterps> {
    type Target = RcA<PartialTypeInterps>;
    fn into_ptr(self) -> Self::Target {
        TypeInterps::into_partial_rca(self)
    }
}

impl IntoPtr<PartialTypeInterps> for Rc<TypeInterps> {
    type Target = RcA<PartialTypeInterps>;
    fn into_ptr(self) -> Self::Target {
        TypeInterps::into_partial_rca(self.into())
    }
}

impl TryFrom<PartialTypeInterps> for TypeInterps {
    type Error = MissingTypeInterpsError;

    fn try_from(value: PartialTypeInterps) -> Result<Self, Self::Error> {
        if value.is_complete() {
            Ok(Self(value))
        } else {
            Err(value.missing_type_error().into())
        }
    }
}

impl From<TypeInterps> for PartialTypeInterps {
    fn from(value: TypeInterps) -> Self {
        value.into_partial()
    }
}

impl<'a> From<&'a TypeInterps> for &'a PartialTypeInterps {
    fn from(value: &'a TypeInterps) -> Self {
        // Safety:
        // This is safe since TypeInterps is repr(transparent) of PartialTypeInterps
        unsafe { core::mem::transmute::<&'a TypeInterps, &'a PartialTypeInterps>(value) }
    }
}

impl FodotOptions for TypeInterps {
    type Options<'b> = FormatOptions;
}

impl FodotDisplay for TypeInterps {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        for type_interp in fmt.value.iter() {
            fmt.options.write_indent(f)?;
            writeln!(f, "{}.", fmt.with_format_opts(&type_interp))?;
        }
        Ok(())
    }
}

impl Display for TypeInterps {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

display_as_debug!(TypeInterps);

impl TypeInterps {
    pub(crate) fn cc(&self) -> &Rc<comp_core::structure::TypeInterps> {
        &self.0.cc
    }

    pub fn vocab(&self) -> &Vocabulary {
        &self.0.vocab
    }

    pub fn vocab_rc(&self) -> &Rc<Vocabulary> {
        &self.0.vocab
    }

    pub fn get_interp_from_str(
        &self,
        type_name: &str,
    ) -> Result<TypeInterpRef, TypeInterpFromStrError> {
        self.0.get_interp_from_str(type_name).map(|f| f.unwrap())
    }

    pub fn get_interp<'a>(
        &'a self,
        type_: CustomTypeRef<'a>,
    ) -> Result<CustomTypeFull<'a>, VocabMismatchError> {
        self.0.get_interp(type_).map(|f| f.unwrap())
    }

    pub fn iter(&self) -> impl SIterator<Item = CustomTypeFull> {
        self.0
            .vocab
            .iter_types()
            .map(|f| self.get_interp(f).unwrap())
    }

    pub fn into_partial(self) -> PartialTypeInterps {
        // Safety:
        // Self is repr transparent of PartialTypeInterps.
        unsafe { core::mem::transmute::<Self, PartialTypeInterps>(self) }
    }

    pub fn into_partial_rc(this: Rc<Self>) -> Rc<PartialTypeInterps> {
        // Safety:
        // Self is repr transparent of PartialTypeInterps.
        unsafe { Rc::from_raw(Rc::into_raw(this) as *const PartialTypeInterps) }
    }

    pub(crate) fn into_partial_rca(this: RcA<Self>) -> RcA<PartialTypeInterps> {
        // Safety:
        // Self is repr transparent of PartialTypeInterps.
        unsafe { RcA::from_raw(RcA::into_raw(this) as *const PartialTypeInterps) }
    }

    pub fn try_from_partial(partial: PartialTypeInterps) -> Result<Self, MissingTypeInterpsError> {
        partial.try_into()
    }
}

pub(crate) enum _TypeInterpRef<'a> {
    Int(&'a IntInterp),
    Real(&'a RealInterp),
    Str(&'a StrInterp),
}

impl<'a> _TypeInterpRef<'a> {
    pub fn unwrap_int(self) -> &'a IntInterp {
        match self {
            Self::Int(value) => value,
            _ => panic!("unwrap on _TypeInterpRef"),
        }
    }

    pub fn unwrap_real(self) -> &'a RealInterp {
        match self {
            Self::Real(value) => value,
            _ => panic!("unwrap on _TypeInterpRef"),
        }
    }

    pub fn unwrap_str(self) -> &'a StrInterp {
        match self {
            Self::Str(value) => value,
            _ => panic!("unwrap on _TypeInterpRef"),
        }
    }
}

/// A [Type](crate::fodot::vocabulary::Type) bundled with a [TypeInterps] reference.
#[derive(Clone)]
pub enum TypeFull<'a> {
    Bool,
    Int,
    Real,
    IntType(IntTypeFull<'a>),
    RealType(RealTypeFull<'a>),
    Str(StrTypeFull<'a>),
}

impl<'a> TypeFull<'a> {
    pub fn as_type(&self) -> TypeRef<'a> {
        match self {
            Self::Bool => TypeRef::Bool,
            Self::Int => TypeRef::Int,
            Self::Real => TypeRef::Real,
            Self::IntType(value) => {
                TypeRef::IntType(IntType(value.type_decl_index, value.type_interps.vocab()))
            }
            Self::RealType(value) => {
                TypeRef::RealType(RealType(value.type_decl_index, value.type_interps.vocab()))
            }
            Self::Str(value) => {
                TypeRef::StrType(StrType(value.type_decl_index, value.type_interps.vocab()))
            }
        }
    }

    pub fn into_type(self) -> TypeRef<'a> {
        match self {
            Self::Bool => TypeRef::Bool,
            Self::Int => TypeRef::Int,
            Self::Real => TypeRef::Real,
            Self::IntType(value) => {
                TypeRef::IntType(IntType(value.type_decl_index, value.type_interps.vocab()))
            }
            Self::RealType(value) => {
                TypeRef::RealType(RealType(value.type_decl_index, value.type_interps.vocab()))
            }
            Self::Str(value) => {
                TypeRef::StrType(StrType(value.type_decl_index, value.type_interps.vocab()))
            }
        }
    }
}

impl<'a> TypeRef<'a> {
    pub fn with_interps(
        self,
        type_interps: &'a TypeInterps,
    ) -> Result<TypeFull<'a>, VocabMismatchError> {
        match self {
            Self::Bool => Ok(TypeFull::Bool),
            Self::Int => Ok(TypeFull::Int),
            Self::Real => Ok(TypeFull::Real),
            Self::IntType(type_) => type_.with_interps(type_interps).map(|f| f.into()),
            Self::RealType(type_) => type_.with_interps(type_interps).map(|f| f.into()),
            Self::StrType(type_) => type_.with_interps(type_interps).map(|f| f.into()),
        }
    }

    pub fn with_partial_interps(
        self,
        type_interps: &'a PartialTypeInterps,
    ) -> Result<TypeFull<'a>, WithPartialInterpsError> {
        match self {
            Self::Bool => Ok(TypeFull::Bool),
            Self::Int => Ok(TypeFull::Int),
            Self::Real => Ok(TypeFull::Real),
            Self::IntType(type_) => type_.with_partial_interps(type_interps).map(|f| f.into()),
            Self::RealType(type_) => type_.with_partial_interps(type_interps).map(|f| f.into()),
            Self::StrType(type_) => type_.with_partial_interps(type_interps).map(|f| f.into()),
        }
    }
}

/// A [CustomType](crate::fodot::vocabulary::CustomType) bundled with a [TypeInterps] reference.
#[non_exhaustive]
#[derive(Clone)]
pub enum CustomTypeFull<'a> {
    Int(IntTypeFull<'a>),
    Real(RealTypeFull<'a>),
    Str(StrTypeFull<'a>),
}

impl<'a> FodotOptions for CustomTypeFull<'a> {
    type Options<'b> = FormatOptions;
}

impl<'a> FodotDisplay for CustomTypeFull<'a> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "{}",
            fmt.with_format_opts(&TypeInterpRef::from(fmt.value.clone()))
        )
    }
}

impl<'a> Display for CustomTypeFull<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl PartialEq<TypeInterp> for CustomTypeFull<'_> {
    fn eq(&self, other: &TypeInterp) -> bool {
        match (self, other) {
            (Self::Int(left), TypeInterp::Int(right)) => left.interp() == right.as_ref(),
            (Self::Real(left), TypeInterp::Real(right)) => left.interp() == right.as_ref(),
            (Self::Str(left), TypeInterp::Str(right)) => left.interp() == right.as_ref(),
            _ => false,
        }
    }
}

impl<'a> CustomTypeFull<'a> {
    /// Returns the contained [CustomTypeFull::Int].
    ///
    /// # panics
    ///
    /// If self is not a [CustomTypeFull::Int] variant.
    pub fn unwrap_int(self) -> IntTypeFull<'a> {
        match self {
            Self::Int(value) => value,
            _ => panic!("unwrap on non int type!"),
        }
    }

    /// Returns the contained [CustomTypeFull::Real].
    ///
    /// # panics
    ///
    /// If self is not a [CustomTypeFull::Real] variant.
    pub fn unwrap_real(self) -> RealTypeFull<'a> {
        match self {
            Self::Real(value) => value,
            _ => panic!("unwrap on non real type!"),
        }
    }

    /// Returns the contained [CustomTypeFull::Str].
    ///
    /// # panics
    ///
    /// If self is not a [CustomTypeFull::Str] variant.
    pub fn unwrap_str(self) -> StrTypeFull<'a> {
        match self {
            Self::Str(value) => value,
            _ => panic!("unwrap on non str type!"),
        }
    }
}

/// A [IntType] bundled with a [TypeInterps] reference and the type's [IntInterp].
#[derive(Clone)]
pub struct IntTypeFull<'a> {
    pub(crate) type_decl_index: TypeSymbolIndex,
    pub(crate) type_interps: &'a PartialTypeInterps,
    pub(crate) interp: &'a IntInterp,
}

impl<'a> From<CustomTypeFull<'a>> for TypeInterpRef<'a> {
    fn from(value: CustomTypeFull<'a>) -> Self {
        match value {
            CustomTypeFull::Int(interp) => IntInterpRef::from(interp).into(),
            CustomTypeFull::Real(interp) => RealInterpRef::from(interp).into(),
            CustomTypeFull::Str(interp) => StrInterpRef::from(interp).into(),
        }
    }
}

impl<'a> From<IntTypeFull<'a>> for TypeFull<'a> {
    fn from(value: IntTypeFull<'a>) -> Self {
        Self::IntType(value)
    }
}

impl<'a> From<IntTypeFull<'a>> for CustomTypeFull<'a> {
    fn from(value: IntTypeFull<'a>) -> Self {
        Self::Int(value)
    }
}

impl<'a> From<IntTypeFull<'a>> for IntInterpRef<'a> {
    fn from(value: IntTypeFull<'a>) -> Self {
        IntInterpRef {
            decl: IntType(value.type_decl_index, value.type_interps.vocab()),
            interp: value.interp,
        }
    }
}

impl<'a> IntTypeFull<'a> {
    /// Returns the reference to the [IntInterp] of the type.
    pub fn interp(&self) -> &'a IntInterp {
        self.interp
    }

    /// Returns true if the [Int] value is contained in the custom type.
    pub fn contains(&self, value: Int) -> bool {
        self.interp.contains(value)
    }

    /// Parses a &[str] to an [Int] that is contained in this type.
    pub fn parse_value(&self, value: &str) -> Result<Int, ParseIntSubTypeError> {
        let value = parse_int_value(value)?;
        if self.contains(value) {
            Ok(value)
        } else {
            Err(MissingTypeElementError.into())
        }
    }
}

/// A [RealType] bundled with a [TypeInterps] reference and the type's [RealInterp].
#[derive(Clone)]
pub struct RealTypeFull<'a> {
    pub(crate) type_decl_index: TypeSymbolIndex,
    pub(crate) type_interps: &'a PartialTypeInterps,
    pub(crate) interp: &'a RealInterp,
}

impl<'a> From<RealTypeFull<'a>> for TypeFull<'a> {
    fn from(value: RealTypeFull<'a>) -> Self {
        Self::RealType(value)
    }
}

impl<'a> From<RealTypeFull<'a>> for CustomTypeFull<'a> {
    fn from(value: RealTypeFull<'a>) -> Self {
        Self::Real(value)
    }
}

impl<'a> From<RealTypeFull<'a>> for RealInterpRef<'a> {
    fn from(value: RealTypeFull<'a>) -> Self {
        RealInterpRef {
            decl: RealType(value.type_decl_index, value.type_interps.vocab()),
            interp: value.interp,
        }
    }
}

impl<'a> RealTypeFull<'a> {
    /// Returns the reference to the [RealInterp] of the type.
    pub fn interp(&self) -> &'a RealInterp {
        self.interp
    }

    /// Returns true if the [Real] value is contained in the custom type.
    pub fn contains(&self, value: Real) -> bool {
        self.interp.contains(value)
    }

    /// Parses a [str] to an [Real] that is contained in this type.
    pub fn parse_value(&self, value: &str) -> Result<Real, ParseRealSubTypeError> {
        let value = parse_real_value(value)?;
        if self.contains(value) {
            Ok(value)
        } else {
            Err(MissingTypeElementError.into())
        }
    }
}

/// A [StrType] bundled with a [TypeInterps] reference and the type's [StrInterp].
#[derive(Clone)]
pub struct StrTypeFull<'a> {
    pub(crate) type_decl_index: TypeSymbolIndex,
    pub(crate) type_interps: &'a PartialTypeInterps,
    pub(crate) interp: &'a StrInterp,
}

impl<'a> From<StrTypeFull<'a>> for TypeFull<'a> {
    fn from(value: StrTypeFull<'a>) -> Self {
        Self::Str(value)
    }
}

impl<'a> From<StrTypeFull<'a>> for CustomTypeFull<'a> {
    fn from(value: StrTypeFull<'a>) -> Self {
        Self::Str(value)
    }
}

impl<'a> From<StrTypeFull<'a>> for StrInterpRef<'a> {
    fn from(value: StrTypeFull<'a>) -> Self {
        StrInterpRef {
            decl: StrType(value.type_decl_index, value.type_interps.vocab()),
            interp: value.interp,
        }
    }
}

impl<'a> StrTypeFull<'a> {
    /// Returns the reference to the [StrInterp] of the type.
    pub fn interp(&self) -> &'a StrInterp {
        self.interp
    }

    /// Parses a [str] to an [StrElement] that is contained in this type.
    pub fn parse_value(&self, value: &str) -> Result<StrElement<'a>, MissingTypeElementError> {
        if let Some(value) = self.interp.0.get(value) {
            Ok(StrElement {
                value,
                type_decl_index: self.type_decl_index,
                type_interps: self.type_interps,
            })
        } else {
            Err(MissingTypeElementError.into())
        }
    }
}

/// An enum reference for a type with an for it interpretation.
///
/// The main difference between this and [CustomTypeFull] is that this type does not keep track of
/// where it comes from whilst a [CustomTypeFull] keeps track of the [TypeInterps] where it is
/// contained.
/// This makes it useful to use for a referencing a [TypeInterp] in a [Vocabulary].
#[non_exhaustive]
#[derive(Clone)]
pub enum TypeInterpRef<'a> {
    Int(IntInterpRef<'a>),
    Real(RealInterpRef<'a>),
    Str(StrInterpRef<'a>),
}

impl<'a> TypeInterpRef<'a> {
    pub fn unwrap_int(self) -> IntInterpRef<'a> {
        if let Self::Int(value) = self {
            value
        } else {
            panic!("Unwrap on TypeInterpRef")
        }
    }

    pub fn unwrap_real(self) -> RealInterpRef<'a> {
        if let Self::Real(value) = self {
            value
        } else {
            panic!("Unwrap on TypeInterpRef")
        }
    }

    pub fn unwrap_str(self) -> StrInterpRef<'a> {
        if let Self::Str(value) = self {
            value
        } else {
            panic!("Unwrap on TypeInterpRef")
        }
    }
}

impl<'a> FodotOptions for TypeInterpRef<'a> {
    type Options<'b> = FormatOptions;
}

impl<'a> FodotDisplay for TypeInterpRef<'a> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match fmt.value {
            TypeInterpRef::Int(value) => write!(f, "{}", fmt.with_format_opts(value)),
            TypeInterpRef::Real(value) => write!(f, "{}", fmt.with_format_opts(value)),
            TypeInterpRef::Str(value) => write!(f, "{}", fmt.with_format_opts(value)),
        }
    }
}

impl<'a> Display for TypeInterpRef<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

/// An [IntTypeRef] with an [IntInterp].
///
/// See [TypeInterpRef] for difference between [IntTypeFull].
#[derive(Clone)]
pub struct IntInterpRef<'a> {
    pub(crate) decl: IntTypeRef<'a>,
    pub(crate) interp: &'a IntInterp,
}

impl<'a> IntTypeRef<'a> {
    pub fn with_interps(
        self,
        type_interp: &'a TypeInterps,
    ) -> Result<IntTypeFull<'a>, VocabMismatchError> {
        match type_interp.get_interp(self.into())? {
            CustomTypeFull::Int(value) => Ok(value),
            _ => unreachable!(),
        }
    }

    pub fn with_partial_interps(
        self,
        type_interp: &'a PartialTypeInterps,
    ) -> Result<IntTypeFull<'a>, WithPartialInterpsError> {
        match type_interp.get_interp(self.into())? {
            Some(CustomTypeFull::Int(value)) => Ok(value),
            None => Err(MissingTypeInterps {
                missing: vec![self.name().to_string()],
            }
            .into()),
            _ => unreachable!(),
        }
    }

    pub(crate) fn interp_from_partial(
        self,
        interps_partial: &'a _PartialTypeInterps,
    ) -> Option<IntInterpRef<'a>> {
        match interps_partial.get_interp(self.0) {
            Some(TypeInterp::Int(interp)) => IntInterpRef { interp, decl: self }.into(),
            None => None,
            _ => panic!("Cannot find interp!"),
        }
    }
}

impl<'a> IntInterpRef<'a> {
    /// Returns a reference to this [IntInterp].
    pub fn interp(&self) -> &'a IntInterp {
        self.interp
    }

    pub fn contains(&self, value: Int) -> bool {
        self.interp.contains(value)
    }

    pub fn parse_value(&self, value: &str) -> Result<Int, ParseIntSubTypeError> {
        let value = parse_int_value(value)?;
        if self.contains(value) {
            Ok(value)
        } else {
            Err(MissingTypeElementError.into())
        }
    }
}

impl<'a> From<IntInterpRef<'a>> for TypeInterpRef<'a> {
    fn from(value: IntInterpRef<'a>) -> Self {
        Self::Int(value)
    }
}

impl<'a> Deref for IntInterpRef<'a> {
    type Target = IntTypeRef<'a>;

    fn deref(&self) -> &Self::Target {
        &self.decl
    }
}

/// An [RealTypeRef] with an [RealInterp].
///
/// See [TypeInterpRef] for difference between [RealTypeFull].
#[derive(Clone)]
pub struct RealInterpRef<'a> {
    pub(crate) decl: RealTypeRef<'a>,
    pub(crate) interp: &'a RealInterp,
}

impl<'a> RealTypeRef<'a> {
    pub fn with_interps(
        self,
        type_interp: &'a TypeInterps,
    ) -> Result<RealTypeFull<'a>, VocabMismatchError> {
        match type_interp.get_interp(self.into())? {
            CustomTypeFull::Real(value) => Ok(value),
            _ => unreachable!(),
        }
    }

    pub fn with_partial_interps(
        self,
        type_interp: &'a PartialTypeInterps,
    ) -> Result<RealTypeFull<'a>, WithPartialInterpsError> {
        match type_interp.get_interp(self.into())? {
            Some(CustomTypeFull::Real(value)) => Ok(value),
            None => Err(MissingTypeInterps {
                missing: vec![self.name().to_string()],
            }
            .into()),
            _ => unreachable!(),
        }
    }

    pub fn get_vocab_interp(&self) -> Option<RealInterpRef<'a>> {
        match self.vocab_ref().get_interp((*self).into()).unwrap() {
            Some(TypeInterpRef::Real(value)) => Some(value),
            None => None,
            _ => unreachable!(),
        }
    }

    pub(crate) fn interp_from_partial(
        self,
        interps_partial: &'a _PartialTypeInterps,
    ) -> Option<RealInterpRef<'a>> {
        match interps_partial.get_interp(self.0) {
            Some(TypeInterp::Real(interp)) => RealInterpRef { interp, decl: self }.into(),
            None => None,
            _ => panic!("Cannot find interp!"),
        }
    }
}

impl<'a> RealInterpRef<'a> {
    pub fn interp(&self) -> &'a RealInterp {
        self.interp
    }

    pub fn contains(&self, value: Real) -> bool {
        self.interp.contains(value)
    }

    pub fn parse_value(&self, value: &str) -> Result<Real, ParseRealSubTypeError> {
        let value = parse_real_value(value)?;
        if self.contains(value) {
            Ok(value)
        } else {
            Err(MissingTypeElementError.into())
        }
    }
}

impl<'a> From<RealInterpRef<'a>> for TypeInterpRef<'a> {
    fn from(value: RealInterpRef<'a>) -> Self {
        Self::Real(value)
    }
}

impl<'a> Deref for RealInterpRef<'a> {
    type Target = RealTypeRef<'a>;

    fn deref(&self) -> &Self::Target {
        &self.decl
    }
}

/// An [StrTypeRef] with an [StrInterp].
///
/// See [TypeInterpRef] for difference between [StrTypeFull].
#[derive(Clone)]
pub struct StrInterpRef<'a> {
    pub(crate) decl: StrTypeRef<'a>,
    pub(crate) interp: &'a StrInterp,
}
impl<'a> StrTypeRef<'a> {
    pub fn with_interps(
        self,
        type_interp: &'a TypeInterps,
    ) -> Result<StrTypeFull<'a>, VocabMismatchError> {
        match type_interp.get_interp(self.into())? {
            CustomTypeFull::Str(value) => Ok(value),
            _ => unreachable!(),
        }
    }

    pub fn with_partial_interps(
        self,
        type_interp: &'a PartialTypeInterps,
    ) -> Result<StrTypeFull<'a>, WithPartialInterpsError> {
        match type_interp.get_interp(self.into())? {
            Some(CustomTypeFull::Str(value)) => Ok(value),
            None => Err(MissingTypeInterps {
                missing: vec![self.name().to_string()],
            }
            .into()),
            _ => unreachable!(),
        }
    }

    pub fn get_vocab_interp(&self) -> Option<StrInterpRef<'a>> {
        match self.vocab_ref().get_interp((*self).into()).unwrap() {
            Some(TypeInterpRef::Str(value)) => Some(value),
            None => None,
            _ => unreachable!(),
        }
    }

    pub(crate) fn interp_from_partial(
        self,
        interps_partial: &'a _PartialTypeInterps,
    ) -> Option<StrInterpRef<'a>> {
        match interps_partial.get_interp(self.0) {
            Some(TypeInterp::Str(interp)) => StrInterpRef { interp, decl: self }.into(),
            None => None,
            _ => panic!("Cannot find interp!"),
        }
    }
}

impl<'a> StrInterpRef<'a> {
    pub fn interp(&self) -> &'a StrInterp {
        self.interp
    }

    pub fn contains(&self, value: &str) -> bool {
        self.interp.0.get_index_of(value).is_some()
    }
}

#[duplicate_item(
    name;
    [IntInterpRef];
    [RealInterpRef];
    [StrInterpRef];
)]
mod interp_ref_display {
    #![doc(hidden)]
    use super::*;

    impl<'a> FodotOptions for name<'a> {
        type Options<'b> = FormatOptions;
    }

    impl<'a> FodotDisplay for name<'a> {
        fn fmt(
            fmt: Fmt<&Self, Self::Options<'_>>,
            f: &mut std::fmt::Formatter<'_>,
        ) -> std::fmt::Result {
            write!(f, "{} ", fmt.with_format_opts(&fmt.value.decl))?;
            fmt.options.write_def_eq(f)?;
            write!(f, " {}", fmt.with_format_opts(fmt.value.interp))
        }
    }

    impl<'a> Display for name<'a> {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "{}", self.display())
        }
    }

    display_as_debug!(name<'a>, gen: ('a));
}

impl<'a> From<StrInterpRef<'a>> for TypeInterpRef<'a> {
    fn from(value: StrInterpRef<'a>) -> Self {
        Self::Str(value)
    }
}

impl<'a> Deref for StrInterpRef<'a> {
    type Target = StrTypeRef<'a>;

    fn deref(&self) -> &Self::Target {
        &self.decl
    }
}

impl<'a> From<TypeFull<'a>> for TypeStr {
    fn from(value: TypeFull<'a>) -> Self {
        value.into_type().into()
    }
}
