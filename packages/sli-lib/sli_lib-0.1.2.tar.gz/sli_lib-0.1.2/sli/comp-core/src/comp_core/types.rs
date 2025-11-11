//! Module for primitive types.
//! Types must currently be the same size.
//! Size can be chosen via `*-bit` feature flag see [crate] for more info.
use cfg_if::cfg_if;
use num_traits::{CheckedAdd, CheckedDiv, CheckedMul, CheckedSub, FromPrimitive};
use std::{
    error::Error,
    fmt::Display,
    hash::Hash,
    ops::{Add, AddAssign, Mul, MulAssign, Neg, Range, Rem, Sub, SubAssign},
    str::FromStr,
};

macro_rules! index_repr {
    () => {
        "Backing datatype for indices."
    };
}

macro_rules! int_repr {
    () => {
        "Backing datatype for integers in comp_core."
    };
}

cfg_if! {
    if #[cfg(feature = "64-bit")] {
        #[doc = index_repr!()]
        pub type IndexRepr = u64;
        #[doc = int_repr!()]
        pub type IntRepr = i64;
    } else if #[cfg(feature = "32-bit")] {
        #[doc = index_repr!()]
        pub type IndexRepr = u32;
        #[doc = int_repr!()]
        pub type IntRepr = i32;
    } else {
        // These are the default sizes
        #[doc = index_repr!()]
        pub type IndexRepr = usize;
        #[doc = int_repr!()]
        pub type IntRepr = isize;
    }
}

macro_rules! real_repr {
    () => {
        "Backing datatype for reals in comp core."
    };
}

macro_rules! discrete_size {
    () => {
        "Discete size type for current size."
    };
}

cfg_if! {
    if #[cfg(feature = "64-bit")] {
        #[doc = real_repr!()]
        pub type RealRepr = num_rational::Rational64;
        #[doc = discrete_size!()]
        pub type DiscreteSize = u64;
        pub type DiscreteInt = i64;
    } else if #[cfg(feature = "32-bit")] {
        #[doc = real_repr!()]
        pub type RealRepr = num_rational::Rational32;
        #[doc = discrete_size!()]
        pub type DiscreteSize = u32;
        pub type DiscreteInt = i32;
    } else if #[cfg(target_pointer_width = "32")] {
        #[doc = real_repr!()]
        pub type RealRepr = num_rational::Rational32;
        #[doc = discrete_size!()]
        pub type DiscreteSize = u32;
        pub type DiscreteInt = i32;
    } else if #[cfg(target_pointer_width = "64")] {
        #[doc = real_repr!()]
        pub type RealRepr = num_rational::Rational64;
        #[doc = discrete_size!()]
        pub type DiscreteSize = u64;
        pub type DiscreteInt = i64;
    } else {
        std::compile_error!("Architecture pointer size does not align with \
                            float pointing number size.
                            Please specify one of the bit size features.");
    }
}

#[macro_export]
macro_rules! create_index {
    ($index:ident $(, $doc:literal)?) => {
        $(
            #[doc=$doc]
        )?
        #[repr(transparent)]
        #[derive(Debug, Hash, PartialEq, Eq, PartialOrd, Ord, Clone, Copy)]
        pub struct $index(pub(super) $crate::IndexRepr);
        impl $index {
            pub fn into_opt_usize(value: Option<$index>) -> Option<usize> {
                match value {
                    Some(s) => Some(s.into()),
                    None => None,
                }
            }

            pub fn from_opt_usize(value: Option<usize>) -> Option<$index> {
                match value {
                    Some(s) => Some(s.into()),
                    None => None,
                }
            }

            pub fn range(r: std::ops::Range<usize>) -> $crate::IndexRange<$index> {
                $crate::IndexRange {
                    start: r.start.into(),
                    end: r.end.into(),
                }
            }
        }

        #[cfg(any(feature = "32-bit", feature = "64-bit"))]
        impl From<usize> for $index {
            fn from(value: usize) -> Self {
                $index(value.try_into().expect("Reached memory address limit! (or a bug)"))
            }
        }

        impl From<$crate::IndexRepr> for $index {
            fn from(value: $crate::IndexRepr) -> Self {
                $index(value)
            }
        }

        impl From<$index> for $crate::IndexRepr {
            fn from(value: $index) -> Self {
                value.0
            }
        }

        #[cfg(not(any(feature = "32-bit", feature = "64-bit")))]
        impl From<$index> for $crate::DiscreteSize {
            fn from(value: $index) -> Self {
                $crate::IndexRepr::from(value.0).try_into().unwrap()
            }
        }

        impl From<i32> for $index {
            fn from(value: i32) -> Self {
                $index(value as $crate::IndexRepr)
            }
        }

        #[cfg(any(feature = "32-bit", feature = "64-bit"))]
        impl From<$index> for usize {
            fn from(value: $index) -> Self {
                value.0.try_into().expect("Reached memory address limit! (or a bug)")
            }
        }
    };
}

/// Reimplementation of [std::ops::Range] for custom indices.
#[derive(Debug, Clone)]
pub struct IndexRange<T>
where
    T: From<IndexRepr> + Copy + PartialOrd,
    IndexRepr: From<T>,
{
    pub start: T,
    pub end: T,
}

impl<T> IndexRange<T>
where
    T: From<IndexRepr> + Copy + PartialOrd + From<usize>,
    IndexRepr: From<T>,
{
    pub fn new(r: Range<usize>) -> Self {
        IndexRange {
            start: r.start.into(),
            end: r.end.into(),
        }
    }

    pub fn contains(&self, value: T) -> bool {
        IndexRepr::from(self.start) <= IndexRepr::from(value)
            && IndexRepr::from(value) < IndexRepr::from(self.end)
    }
}

impl<T> Iterator for IndexRange<T>
where
    T: From<IndexRepr> + Copy + PartialOrd,
    IndexRepr: From<T>,
{
    type Item = T;
    fn next(&mut self) -> Option<Self::Item> {
        if self.start < self.end {
            let ret = Some(self.start);
            self.start = (IndexRepr::from(self.start) + 1).into();
            ret
        } else {
            None
        }
    }
}

impl<T> ExactSizeIterator for IndexRange<T>
where
    T: From<IndexRepr> + Copy + PartialOrd,
    IndexRepr: From<T>,
{
    fn len(&self) -> usize {
        (IndexRepr::from(self.end) - IndexRepr::from(self.start))
            .try_into()
            .expect("numbers too big")
    }
}

impl<T> From<Range<usize>> for IndexRange<T>
where
    T: From<IndexRepr> + Copy + PartialOrd + From<usize>,
    IndexRepr: From<T>,
{
    fn from(value: Range<usize>) -> Self {
        Self::new(value)
    }
}

pub(crate) use create_index;

// Size of Ints used in FO[.] spec
// Architecture dependent
/// Represents an FO(·) Int.
pub type Int = IntRepr;

/// Represents an FO(·) Real.
#[repr(transparent)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Real(RealRepr);

impl Default for Real {
    fn default() -> Self {
        Real(Default::default())
    }
}

impl Display for Real {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NotRealError {
    IsInf,
    IsNan,
}

#[derive(Debug, Clone, Copy)]
pub struct RealOverflow();

pub enum DivError {
    RealOverflow(RealOverflow),
    IsNan,
}

impl Real {
    pub(crate) fn new(value: RealRepr) -> Self {
        Real(value)
    }

    pub(crate) fn inner_ref(&self) -> &RealRepr {
        &self.0
    }

    pub fn from_fraction(denom: IntRepr, num: IntRepr) -> Option<Self> {
        if num == 0 {
            None
        } else {
            Some(Self(RealRepr::new(
                denom.try_into().unwrap(),
                num.try_into().unwrap(),
            )))
        }
    }

    pub fn add(self, other: Self) -> Result<Self, RealOverflow> {
        if let Some(value) = self.0.checked_add(&other.0) {
            Ok(Self(value))
        } else {
            Err(RealOverflow())
        }
    }

    pub fn round(self) -> Self {
        Self(self.0.round())
    }

    pub fn floor(self) -> Self {
        Self(self.0.floor())
    }

    pub fn ceil(self) -> Self {
        Self(self.0.ceil())
    }

    pub fn sub(self, other: Self) -> Result<Self, RealOverflow> {
        if let Some(value) = self.0.checked_sub(&other.0) {
            Ok(Self(value))
        } else {
            Err(RealOverflow())
        }
    }

    pub fn mult(self, other: Self) -> Result<Self, RealOverflow> {
        if let Some(value) = self.0.checked_mul(&other.0) {
            Ok(Self(value))
        } else {
            Err(RealOverflow())
        }
    }

    pub fn div(self, other: &Self) -> Result<Self, DivError> {
        if other.0 == RealRepr::ZERO {
            return Err(DivError::IsNan);
        }
        if let Some(value) = self.0.checked_div(&other.0) {
            Ok(Self(value))
        } else {
            Err(DivError::RealOverflow(RealOverflow()))
        }
    }

    pub(crate) fn div_cc(self, other: &Self) -> Self {
        match self.div(other) {
            Ok(value) => value,
            Err(DivError::RealOverflow(_)) => panic!("real overflow"),
            Err(DivError::IsNan) => Default::default(),
        }
    }

    pub fn rem(self, other: &Self) -> Result<Self, DivError> {
        if other.0 == RealRepr::ZERO {
            return Err(DivError::IsNan);
        }
        Ok(Self(self.0.rem(&other.0)))
    }

    pub(crate) fn rem_cc(self, other: &Self) -> Self {
        match self.rem(other) {
            Ok(value) => value,
            Err(DivError::RealOverflow(_)) => panic!("real overflow"),
            Err(DivError::IsNan) => Default::default(),
        }
    }

    pub fn negate_inplace(&mut self) {
        *self = -(self.clone())
    }

    pub fn to_string(&self) -> String {
        self.0.to_string()
    }

    pub fn is_integer(&self) -> bool {
        self.0.is_integer()
    }
}

impl PartialEq<Int> for Real {
    fn eq(&self, other: &Int) -> bool {
        *self == Real::from(*other)
    }
}

impl PartialEq<Real> for Int {
    fn eq(&self, other: &Real) -> bool {
        Real::from(*other) == *self
    }
}

impl PartialOrd<Int> for Real {
    fn partial_cmp(&self, other: &Int) -> Option<std::cmp::Ordering> {
        self.partial_cmp(&Real::from(*other))
    }
}

impl PartialOrd<Real> for Int {
    fn partial_cmp(&self, other: &Real) -> Option<std::cmp::Ordering> {
        Real::from(*self).partial_cmp(other)
    }
}

impl Add for Real {
    type Output = Self;

    fn add(self, rhs: Self) -> Self::Output {
        Self::add(self, rhs).unwrap()
    }
}

impl AddAssign for Real {
    fn add_assign(&mut self, rhs: Self) {
        *self = Self::add(*self, rhs).unwrap();
    }
}

impl AddAssign<&Self> for Real {
    fn add_assign(&mut self, rhs: &Self) {
        AddAssign::add_assign(self, *rhs)
    }
}

impl Sub for Real {
    type Output = Self;

    fn sub(self, rhs: Self) -> Self::Output {
        Self::sub(self, rhs).unwrap()
    }
}

impl SubAssign for Real {
    fn sub_assign(&mut self, rhs: Self) {
        *self = Self::sub(*self, rhs).unwrap();
    }
}

impl SubAssign<&Self> for Real {
    fn sub_assign(&mut self, rhs: &Self) {
        SubAssign::sub_assign(self, *rhs)
    }
}

impl Mul for Real {
    type Output = Self;

    fn mul(self, rhs: Self) -> Self::Output {
        Self::mult(self, rhs).unwrap()
    }
}

impl MulAssign for Real {
    fn mul_assign(&mut self, rhs: Self) {
        *self = Self::mult(*self, rhs).unwrap();
    }
}

impl MulAssign<&Self> for Real {
    fn mul_assign(&mut self, rhs: &Self) {
        MulAssign::mul_assign(self, *rhs)
    }
}

impl Neg for Real {
    type Output = Real;

    fn neg(self) -> Self::Output {
        Self(self.0.neg())
    }
}

impl From<Int> for Real {
    fn from(value: Int) -> Self {
        Real::new((value as DiscreteInt).into())
    }
}

impl TryFrom<Real> for Int {
    type Error = ();

    fn try_from(value: Real) -> Result<Self, Self::Error> {
        if *value.0.denom() == 1 {
            return Err(());
        }
        Ok(*value.0.numer() as Int)
    }
}

pub struct FloatToRealError<T> {
    pub value: T,
}

impl<T: Display> Display for FloatToRealError<T> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "could not convert float ({}) to real", self.value)
    }
}

impl TryFrom<f64> for Real {
    type Error = FloatToRealError<f64>;

    fn try_from(value: f64) -> Result<Self, Self::Error> {
        Ok(Real::new(
            RealRepr::from_f64(value).ok_or(FloatToRealError { value })?,
        ))
    }
}

impl From<Real> for f64 {
    fn from(value: Real) -> Self {
        let values = value.0.into_raw();
        values.0 as f64 / values.1 as f64
    }
}

impl TryFrom<f32> for Real {
    type Error = FloatToRealError<f32>;

    fn try_from(value: f32) -> Result<Self, Self::Error> {
        Ok(Real::new(
            RealRepr::from_f32(value).ok_or(FloatToRealError { value })?,
        ))
    }
}

#[cfg(any(not(feature = "32-bit"), feature = "64-bit"))]
impl From<i32> for Real {
    fn from(value: i32) -> Self {
        Real::new((value as DiscreteInt).into())
    }
}

impl TryFrom<usize> for Real {
    type Error = ();
    fn try_from(value: usize) -> Result<Self, Self::Error> {
        Ok(Self(RealRepr::from_usize(value).ok_or(())?))
    }
}

/// An error for parsing a [Real] value.
#[non_exhaustive]
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ParseRealError;

impl Display for ParseRealError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Unable to parse real from provided value.")
    }
}

impl Error for ParseRealError {}

impl FromStr for Real {
    type Err = ParseRealError;

    fn from_str(s: &str) -> Result<Self, ParseRealError> {
        // first try to parse a rational with or without a fraction
        if let Ok(value) = RealRepr::from_str(s) {
            Ok(Self(value))
        } else {
            // Try parsing a floating point number and converting it to a rational
            let dot_loc = s.find('.').ok_or(ParseRealError)?;
            let before_point = DiscreteInt::from_str(&s[..dot_loc]).map_err(|_| ParseRealError)?;
            let (after_point, amount_of_digits) = if dot_loc + 1 >= s.len() {
                return Err(ParseRealError);
            } else {
                (
                    DiscreteInt::from_str(&s[dot_loc + 1..]).map_err(|_| ParseRealError)?,
                    s[dot_loc + 1..].len(),
                )
            };
            if let Some(value) = RealRepr::from(after_point).checked_div(&<RealRepr as From<
                DiscreteInt,
            >>::from(
                (10 as DiscreteInt).pow(amount_of_digits.try_into().map_err(|_| ParseRealError)?),
            )) {
                Ok(Self(
                    RealRepr::from(before_point)
                        .checked_add(&value)
                        .ok_or(ParseRealError)?,
                ))
            } else {
                Err(ParseRealError)
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::Real;
    use crate::comp_core::structure::TypeElement;

    #[test]
    fn test_real_int_cmp() {
        debug_assert!(Real::from(0) == 0);
        debug_assert!(0 == Real::from(0));

        debug_assert!(Real::from(0) != 1);
        debug_assert!(1 != Real::from(0));

        debug_assert!(Real::from(0) < 1);
        debug_assert!(1 > Real::from(0));

        debug_assert!(Real::from(0) <= 1);
        debug_assert!(1 >= Real::from(0));

        use TypeElement::Real as TeReal;

        debug_assert!(TeReal(Real::from(0)) == 0.into());
        debug_assert!(TypeElement::from(0) == TeReal(Real::from(0)));

        debug_assert!(TeReal(Real::from(0)) != 1.into());
        debug_assert!(TypeElement::from(1) != TeReal(Real::from(0)));
    }
}
