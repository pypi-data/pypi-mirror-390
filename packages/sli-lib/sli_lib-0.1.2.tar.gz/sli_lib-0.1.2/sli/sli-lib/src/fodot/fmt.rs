//! Displaying datastructures in FO(·) format.
//!
//! The main idea of this module is for datastructures to implement [Display] for `Fmt<&'a T>`
//! where `T` is the datastructure in question, if needed `Fmt<T>` can also be implemented.
//! Then [FodotDisplay] should be implemented for `T`, at which point [Display] can be implemented
//! using the provided [FodotDisplay::display] method.
//!
//! For example:
//! ```
//! use sli_lib::fodot::fmt::{Fmt, FodotOptions, FodotDisplay, FormatOptions};
//! use std::fmt::Display;
//!
//! struct Thing;
//!
//! impl FodotOptions for Thing {
//!     type Options<'a> = FormatOptions where Self: 'a;
//! }
//!
//! impl FodotDisplay for Thing {
//!     fn fmt(
//!         fmt: Fmt<&Self, Self::Options<'_>>,
//!         f: &mut std::fmt::Formatter<'_>
//!     ) -> std::fmt::Result {
//!         todo!()
//!     }
//! }
//!
//! impl Display for Thing {
//!     fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
//!         // Here we call the `Display` impl for `Fmt<&'a Thing>` using the display method.
//!         write!(f, "{}", self.display())
//!     }
//! }
//!
//! ```
//!
//! The [Fmt] struct takes a second generic argument which is a custom options type.
//! This custom options type must implement [FodotFmtOpts], which has an auto impl.
//! The idea boils down to that we have some common format options which are relevant for all
//! datastructures ([FormatOptions]), which we would like to extend if needed.
//!

use super::{
    structure::{ArgsRef, PartialStructure, TypeElement},
    vocabulary::DomainRef,
};
use itertools::Itertools;
use std::{
    cell::Cell,
    fmt::{self, Display, Write},
    ops::{Deref, DerefMut},
};

pub const BOOL_ASCII: &str = "Bool";
pub const BOOL_UNI_CHAR: char = '𝔹';
pub const BOOL_UNI: &str = "𝔹";

pub const INT_ASCII: &str = "Int";
pub const INT_UNI_CHAR: char = 'ℤ';
pub const INT_UNI: &str = "ℤ";

pub const REAL_ASCII: &str = "Real";
pub const REAL_UNI_CHAR: char = 'ℝ';
pub const REAL_UNI: &str = "ℝ";

pub const TRUE: &str = "true";
pub const FALSE: &str = "false";

pub const IMAGE_ASCII: &str = "->";
pub const IMAGE_UNI_CHAR: char = '→';
pub const IMAGE_UNI: &str = "→";

pub const PRODUCT_ASCII: &str = "*";
pub const PRODUCT_UNI_CHAR: char = '⨯';
pub const PRODUCT_UNI: &str = "⨯";

pub const SUPERSET_ASCII: &str = ":>";
pub const SUPERSET_UNI_CHAR: char = '⊇';
pub const SUPERSET_UNI: &str = "⊇";

pub const SUBSET_ASCII: &str = "<:";
pub const SUBSET_UNI_CHAR: char = '⊆';
pub const SUBSET_UNI: &str = "⊆";

pub const DEF_EQ_ASCII: &str = ":=";
pub const DEF_EQ_UNI_CHAR: char = '≜';
pub const DEF_EQ_UNI: &str = "≜";

pub const AND_ASCII: &str = "&";
pub const AND_UNI_CHAR: char = '∧';
pub const AND_UNI: &str = "∧";

pub const OR_ASCII: &str = "|";
pub const OR_UNI_CHAR: char = '∨';
pub const OR_UNI: &str = "∨";

pub const RIMPL_ASCII: &str = "=>";
pub const RIMPL_UNI_CHAR: char = '⇒';
pub const RIMPL_UNI: &str = "⇒";

pub const LIMPL_ASCII: &str = "<=";
pub const LIMPL_UNI_CHAR: char = '⇐';
pub const LIMPL_UNI: &str = "⇐";

pub const EQV_ASCII: &str = "<=>";
pub const EQV_UNI_CHAR: char = '⇔';
pub const EQV_UNI: &str = "⇔";

pub const NEQ_ASCII: &str = "~=";
pub const NEQ_UNI_CHAR: char = '≠';
pub const NEQ_UNI: &str = "≠";

pub const LE_ASCII: &str = "=<";
pub const LE_UNI_CHAR: char = '≤';
pub const LE_UNI: &str = "≤";

pub const GE_ASCII: &str = ">=";
pub const GE_UNI_CHAR: char = '≥';
pub const GE_UNI: &str = "≥";

pub const IN_ASCII: &str = "in";
pub const IN_UNI_CHAR: char = '∈';
pub const IN_UNI: &str = "∈";

pub const NEG_ASCII: &str = "~";
pub const NEG_UNI_CHAR: char = '¬';
pub const NEG_UNI: &str = "¬";

pub const UNI_QUANT_ASCII: &str = "!";
pub const UNI_QUANT_UNI_CHAR: char = '∀';
pub const UNI_QUANT_UNI: &str = "∀";

pub const EX_QUANT_ASCII: &str = "?";
pub const EX_QUANT_UNI_CHAR: char = '∃';
pub const EX_QUANT_UNI: &str = "∃";

pub const DEF_LIMPL_ASCII: &str = "<-";
pub const DEF_LIMPL_UNI_CHAR: char = '←';
pub const DEF_LIMPL_UNI: &str = "←";

pub const CONJ_GUARD_LEFT: &str = "[[";
pub const CONJ_GUARD_RIGHT: &str = "]]";

pub const IMPL_GUARD_LEFT_ASCII: &str = "<<";
pub const IMPL_GUARD_RIGHT_ASCII: &str = ">>";
pub const IMPL_GUARD_LEFT_UNI: &str = "⟨⟨";
pub const IMPL_GUARD_RIGHT_UNI: &str = "⟩⟩";

pub trait FodotFmtOpts: AsRef<FormatOptions> + AsMut<FormatOptions> + Default + Clone {
    fn set_format_options(&mut self, options: &FormatOptions) {
        *self.as_mut() = options.clone();
    }
}

impl<T> FodotFmtOpts for T where T: AsRef<FormatOptions> + AsMut<FormatOptions> + Default + Clone {}

impl AsRef<FormatOptions> for FormatOptions {
    fn as_ref(&self) -> &FormatOptions {
        self
    }
}

impl AsMut<FormatOptions> for FormatOptions {
    fn as_mut(&mut self) -> &mut FormatOptions {
        self
    }
}

/// The format options for this type.
///
/// Note: the associated type [FodotOptions::Options] is not extendable because of the lifetime
/// GAT.
/// see: [this blog post](https://sabrinajewson.org/blog/the-better-alternative-to-lifetime-gats)
/// by Sabrina Jewson.
pub trait FodotOptions {
    type Options<'a>: FodotFmtOpts;
}

/// The display implementation.
///
/// Adds a provided [FodotDisplay::display], which returns a [Fmt] which implements [Display] for
/// and get be used to edit the default [FodotOptions::Options].
pub trait FodotDisplay: FodotOptions {
    fn fmt(fmt: Fmt<&Self, Self::Options<'_>>, f: &mut std::fmt::Formatter<'_>)
    -> std::fmt::Result;

    /// Returns the formatter options for this value.
    /// The options are populated with default values.
    fn display<'a>(&'a self) -> Fmt<&'a Self, Self::Options<'a>> {
        Fmt::with_defaults(self)
    }
}

impl<'a, T: FodotOptions> FodotOptions for &'a T {
    type Options<'b> = T::Options<'b>;
}

pub trait FodotPrecDisplay: FodotOptions {
    fn fmt_with_prec(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
        super_prec: u32,
    ) -> std::fmt::Result;
}

impl<'a, T> FodotPrecDisplay for &'a T
where
    T: FodotPrecDisplay,
{
    fn fmt_with_prec(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
        super_prec: u32,
    ) -> std::fmt::Result {
        FodotPrecDisplay::fmt_with_prec(
            Fmt {
                value: *fmt.value,
                options: fmt.options.clone(),
            },
            f,
            super_prec,
        )
    }
}

/// Implements [FodotDisplay] for a type that already implements [Display] and does need any
/// formatting options.
///
/// Usage: call with the type you want to add a [FodotDisplay] implementation for.
/// When the type requires generics these must be given before the type in angled brackets, a where
/// statement is not allowed.
///
/// example: `simple_fodot_display(<T: Display> Type<T>)`
macro_rules! simple_fodot_display {
    (
        $(<$($gen:tt)*>)? $ty:ty $(,)?
    ) => {
        impl<$($($gen)*)?> $crate::fodot::fmt::FodotOptions for $ty {
            type Options<'aaaaloooongliiifeetimmee> = $crate::fodot::fmt::FormatOptions;
        }

        impl<$($($gen)*)?> $crate::fodot::fmt::FodotDisplay for $ty {
            fn fmt(
                fmt: $crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
                f: &mut std::fmt::Formatter<'_>
            ) -> std::fmt::Result {
                write!(f, "{}", fmt.value)
            }
        }
    }
}

pub(crate) use simple_fodot_display;

impl<'a, T> FodotDisplay for &'a T
where
    T: FodotDisplay,
{
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        FodotDisplay::fmt(
            Fmt {
                value: *fmt.value,
                options: fmt.options.clone(),
            },
            f,
        )
    }
}

pub struct Fmt<V, O: FodotFmtOpts = FormatOptions> {
    pub options: O,
    pub value: V,
}

impl<'a, V: FodotDisplay> Display for Fmt<V, V::Options<'a>> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        FodotDisplay::fmt(
            Fmt {
                value: &self.value,
                options: self.options.clone(),
            },
            f,
        )
    }
}

impl<V, O: FodotFmtOpts> Deref for Fmt<V, O> {
    type Target = O;

    fn deref(&self) -> &Self::Target {
        &self.options
    }
}

impl<V, O: FodotFmtOpts> DerefMut for Fmt<V, O> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.options
    }
}

impl<V, O: FodotFmtOpts> Fmt<V, O> {
    pub fn with_defaults(value: V) -> Fmt<V, O> {
        Fmt {
            value,
            options: Default::default(),
        }
    }

    /// Copies the inner [FormatOptions], other format options are inherited from [Default].
    pub fn with_format_opts<W: FodotDisplay>(&self, value: W) -> Fmt<W, W::Options<'_>> {
        let mut options = W::Options::default();
        options.set_format_options(self.options.as_ref());
        Fmt { options, value }
    }

    /// Copies the all format options, can only be called if W has same associated type for
    /// [FodotOptions::Options].
    pub fn with_opts<'a, W: FodotDisplay<Options<'a> = O> + 'a>(&self, value: W) -> Fmt<W, O> {
        Fmt {
            options: self.options.clone(),
            value,
        }
    }

    pub fn with_prec(self, super_prec: u32) -> FmtPrec<V, O>
    where
        V: FodotPrecDisplay,
    {
        FmtPrec {
            fmt: self,
            super_prec,
        }
    }

    pub fn with_extra_indent(mut self, extra: u32) -> Fmt<V, O> {
        self.as_mut().indent_level += extra;
        self
    }

    pub fn with_indent(self) -> Fmt<V, O> {
        self.with_extra_indent(1)
    }

    pub fn with_char_set(mut self, char_set: CharSet) -> Fmt<V, O> {
        self.options.as_mut().char_set = char_set;
        self
    }

    pub fn map_options<F: FnOnce(O) -> O>(mut self, map: F) -> Self {
        self.options = map(self.options);
        self
    }
}

pub struct FmtPrec<V, O: FodotFmtOpts = FormatOptions> {
    pub fmt: Fmt<V, O>,
    pub super_prec: u32,
}

impl<'a, V: FodotPrecDisplay> Display for FmtPrec<V, V::Options<'a>> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        FodotPrecDisplay::fmt_with_prec(
            Fmt {
                value: &self.fmt.value,
                options: self.fmt.options.clone(),
            },
            f,
            self.super_prec,
        )
    }
}

/// Charset option.
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum CharSet {
    Ascii,
    Unicode,
}

impl Default for CharSet {
    fn default() -> Self {
        Self::Ascii
    }
}

/// Standard format options.
#[non_exhaustive]
#[derive(Clone)]
pub struct FormatOptions {
    pub char_set: CharSet,
    pub tab_width: u32,
    pub indent_level: u32,
}

impl Default for FormatOptions {
    fn default() -> Self {
        Self {
            char_set: Default::default(),
            tab_width: 4,
            indent_level: Default::default(),
        }
    }
}

impl FormatOptions {
    pub fn write_tab<W: Write>(&self, writer: &mut W, level: u32) -> fmt::Result {
        let amount = self.tab_width * level;
        if amount == 0 {
            return Ok(());
        }
        write!(
            writer,
            "{:width$}",
            " ",
            width = (amount).try_into().unwrap()
        )
    }

    pub fn write_indent<W: Write>(&self, writer: &mut W) -> fmt::Result {
        Self::write_tab(&self, writer, self.indent_level)
    }

    pub fn write_indent_extra<W: Write>(&self, writer: &mut W, extra: u32) -> fmt::Result {
        Self::write_tab(&self, writer, self.indent_level)?;
        Self::write_tab(&self, writer, extra)
    }

    pub fn write_bool_type<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(BOOL_ASCII),
            CharSet::Unicode => writer.write_char(BOOL_UNI_CHAR),
        }
    }

    pub fn write_int_type<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(INT_ASCII),
            CharSet::Unicode => writer.write_char(INT_UNI_CHAR),
        }
    }

    pub fn write_real_type<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(REAL_ASCII),
            CharSet::Unicode => writer.write_char(REAL_UNI_CHAR),
        }
    }

    pub fn write_image_sign<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(IMAGE_ASCII),
            CharSet::Unicode => writer.write_char(IMAGE_UNI_CHAR),
        }
    }

    pub fn write_product<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(PRODUCT_ASCII),
            CharSet::Unicode => writer.write_char(PRODUCT_UNI_CHAR),
        }
    }

    pub fn write_superset<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(SUPERSET_ASCII),
            CharSet::Unicode => writer.write_char(SUPERSET_UNI_CHAR),
        }
    }

    pub fn write_subset<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(SUBSET_ASCII),
            CharSet::Unicode => writer.write_char(SUBSET_UNI_CHAR),
        }
    }

    pub fn write_def_eq<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(DEF_EQ_ASCII),
            CharSet::Unicode => writer.write_char(DEF_EQ_UNI_CHAR),
        }
    }

    pub fn write_and<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(AND_ASCII),
            CharSet::Unicode => writer.write_char(AND_UNI_CHAR),
        }
    }

    pub fn write_or<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(OR_ASCII),
            CharSet::Unicode => writer.write_char(OR_UNI_CHAR),
        }
    }

    pub fn write_rimpl<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(RIMPL_ASCII),
            CharSet::Unicode => writer.write_char(RIMPL_UNI_CHAR),
        }
    }

    pub fn write_limpl<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(LIMPL_ASCII),
            CharSet::Unicode => writer.write_char(LIMPL_UNI_CHAR),
        }
    }

    pub fn write_eqv<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(EQV_ASCII),
            CharSet::Unicode => writer.write_char(EQV_UNI_CHAR),
        }
    }

    pub fn write_neq<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(NEQ_ASCII),
            CharSet::Unicode => writer.write_char(NEQ_UNI_CHAR),
        }
    }

    pub fn write_le<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(LE_ASCII),
            CharSet::Unicode => writer.write_char(LE_UNI_CHAR),
        }
    }

    pub fn write_ge<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(GE_ASCII),
            CharSet::Unicode => writer.write_char(GE_UNI_CHAR),
        }
    }

    pub fn write_in<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(IN_ASCII),
            CharSet::Unicode => writer.write_char(IN_UNI_CHAR),
        }
    }

    pub fn write_neg<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(NEG_ASCII),
            CharSet::Unicode => writer.write_char(NEG_UNI_CHAR),
        }
    }

    pub fn write_uni_quant<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(UNI_QUANT_ASCII),
            CharSet::Unicode => writer.write_char(UNI_QUANT_UNI_CHAR),
        }
    }

    pub fn write_ex_quant<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(EX_QUANT_ASCII),
            CharSet::Unicode => writer.write_char(EX_QUANT_UNI_CHAR),
        }
    }

    pub fn write_def_limpl<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(DEF_LIMPL_ASCII),
            CharSet::Unicode => writer.write_char(DEF_LIMPL_UNI_CHAR),
        }
    }

    pub fn write_conj_guard_left<W: Write>(&self, writer: &mut W) -> fmt::Result {
        writer.write_str(CONJ_GUARD_LEFT)
    }

    pub fn write_conj_guard_right<W: Write>(&self, writer: &mut W) -> fmt::Result {
        writer.write_str(CONJ_GUARD_RIGHT)
    }

    pub fn write_impl_guard_left<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(IMPL_GUARD_LEFT_ASCII),
            CharSet::Unicode => writer.write_str(IMPL_GUARD_LEFT_UNI),
        }
    }

    pub fn write_impl_guard_right<W: Write>(&self, writer: &mut W) -> fmt::Result {
        match self.char_set {
            CharSet::Ascii => writer.write_str(IMPL_GUARD_RIGHT_ASCII),
            CharSet::Unicode => writer.write_str(IMPL_GUARD_RIGHT_UNI),
        }
    }

    /// Write a function enumeration display to the writer.
    ///
    /// e.g. `(a, b, c) -> d, (e, f, g) -> h, ...`
    pub fn write_image_arg<'a, W: Write, T: Display>(
        &self,
        f: &mut W,
        values: impl Iterator<Item = (ArgsRef<'a>, T)>,
    ) -> fmt::Result {
        let arg_fmt = values
            .map(|(arg, value)| {
                display_fn(move |f| -> std::fmt::Result {
                    write!(
                        f,
                        "{} ",
                        Fmt {
                            options: self.clone(),
                            value: arg,
                        }
                    )?;
                    self.write_image_sign(f)?;
                    write!(f, " {}", value)
                })
            })
            .format(", ");
        write!(f, "{}", arg_fmt)
    }
}

/// Custom format options for structures.
#[derive(Clone)]
pub enum StructFmt<'a> {
    Full,
    PFuncOnly,
    Diff(&'a PartialStructure),
}

impl<'a> Default for StructFmt<'a> {
    fn default() -> Self {
        Self::PFuncOnly
    }
}

/// Format options for structures with [StructFmt].
#[derive(Clone)]
pub struct StructureOptions<'a> {
    pub opts: FormatOptions,
    pub struct_opts: StructFmt<'a>,
}

impl<'a> Default for StructureOptions<'a> {
    fn default() -> Self {
        Self {
            opts: Default::default(),
            struct_opts: Default::default(),
        }
    }
}

impl<'a> AsRef<FormatOptions> for StructureOptions<'a> {
    fn as_ref(&self) -> &FormatOptions {
        &self.opts
    }
}

impl<'a> AsMut<FormatOptions> for StructureOptions<'a> {
    fn as_mut(&mut self) -> &mut FormatOptions {
        &mut self.opts
    }
}

/// Formats arguments.
pub struct ArgFormatter<'a, T: Iterator<Item = TypeElement<'a>>>(Cell<Option<T>>, usize);

impl<'a, T: Iterator<Item = TypeElement<'a>>> ArgFormatter<'a, T> {
    pub fn new(args: T, domain: &DomainRef) -> Self {
        Self(Cell::new(Some(args)), domain.arity())
    }
}

impl<'a, T: Iterator<Item = TypeElement<'a>>> FodotOptions for ArgFormatter<'a, T> {
    type Options<'b> = FormatOptions;
}

impl<'a, T: Iterator<Item = TypeElement<'a>>> FodotDisplay for ArgFormatter<'a, T> {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        let arg = match fmt.value.0.take() {
            Some(arg) => arg,
            None => panic!("Reformat of arg formatter!"),
        };
        let arg = arg.map(|f| fmt.with_format_opts(f)).format(", ");
        if fmt.value.1 > 1 {
            write!(f, "({})", arg)
        } else {
            write!(f, "{}", arg)
        }
    }
}

pub(crate) fn display_fn(f: impl FnOnce(&mut fmt::Formatter<'_>) -> fmt::Result) -> impl Display {
    struct WithFormatter<F>(Cell<Option<F>>);

    impl<F> Display for WithFormatter<F>
    where
        F: FnOnce(&mut fmt::Formatter<'_>) -> fmt::Result,
    {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            (self.0.take()).unwrap()(f)
        }
    }

    WithFormatter(Cell::new(Some(f)))
}

/// Options for symbols.
///
/// Adds option to only display the name instead of the default display of the declaration.
#[derive(Clone)]
pub struct SymbolOptions {
    pub options: FormatOptions,
    pub name_only: bool,
}

impl Default for SymbolOptions {
    fn default() -> Self {
        Self {
            options: Default::default(),
            name_only: false,
        }
    }
}

impl<V> Fmt<V, SymbolOptions> {
    pub fn with_name_only(mut self) -> Self {
        self.name_only = true;
        self
    }
}

impl AsRef<FormatOptions> for SymbolOptions {
    fn as_ref(&self) -> &FormatOptions {
        &self.options
    }
}

impl AsMut<FormatOptions> for SymbolOptions {
    fn as_mut(&mut self) -> &mut FormatOptions {
        &mut self.options
    }
}

impl Deref for SymbolOptions {
    type Target = FormatOptions;

    fn deref(&self) -> &Self::Target {
        &self.options
    }
}

impl<'a> DerefMut for SymbolOptions {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.options
    }
}
