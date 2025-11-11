//! Datastructures for representing FO(·).
//!
//! FO(·) vocabulary can be found in [vocabulary].
//!
//! FO(·) structure can be found in [structure].
//! A SLI FO(·) structure must be valid according to its corresponding vocabulary.
//! i.e. it is not possible to create a structure where a constant has a value that is not part of
//! its codomain.
//!
//! Lastly datastructures for an FO(·) theory can be found in [theory].
//!
//! The [fmt] module contains configuration and helper functions for displaying these datastructures
//! in an FO(·) format.
//!
//! # Examples
//!
//! Creating a [Theory](self::theory::Theory) from a string using
//! [Theory::from_specifiation](self::theory::Theory::from_specification).
//!
//! ```
//! use sli_lib::fodot::theory::Theory;
//!
//! let theory = Theory::from_specification(
//! "
//! vocabulary {
//!     p: -> Bool
//!     q: -> Bool
//! }
//!
//! theory {
//!     p() => q().
//! }
//!
//! structure {}
//! "
//! ).expect("Specification error!");
//!
//! println!("{}", theory.assertions());
//! ```
//!
//! Programmatically creating a [Vocabulary](self::vocabulary::Vocabulary)
//! and a [PartialStructure](self::structure::PartialStructure) for this vocabulary.
//! Note: most functions are fallible, as such the usage of the [`?` operator](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#a-shortcut-for-propagating-errors-the--operator).
//!
//! ```
//! # use std::error::Error;
//! # fn main() -> Result<(), Box<dyn Error>> {
//! use sli_lib::fodot::{
//!     TryIntoCtx,
//!     vocabulary::Vocabulary,
//!     structure::{
//!          TypeInterps,
//!          PartialStructure,
//!          StrInterp,
//!          partial,
//!     }
//! };
//!
//! let mut vocab = Vocabulary::new("V");
//! vocab.add_type_decl_with_interp(
//!     "T",
//!     StrInterp::from_iter(
//!         ["a", "b", "c"]
//!     ).into()
//! )?;
//! // Codomain of the pfunc
//! vocab.build_pfunc_decl("Bool")?
//!     // domain of the pfunc
//!     .set_domain(["T", "T"])?
//!     // we add a symbol with the signature we built with the name "p"
//!     .complete_with_name("p")?;
//! let (vocab, part_type_interps) = vocab.complete_vocab();
//! // Complete the type interpretations, and wrap it in an Rc with .into()
//! let type_interps = TypeInterps::try_from(part_type_interps)?.into();
//! let mut structure = PartialStructure::new(type_interps);
//!
//! // TODO: allow get_mut to receive any value that can be converted to a Pfunc
//! let pred_decl = vocab.parse_pfunc("p")?;
//! let partial::mutable::SymbolInterp::Pred(mut pred) = structure.get_mut(pred_decl) else {
//!     unreachable!()
//! };
//! // Expects an Option wrapped value since setting to unknown is allowed in a partial structure.
//! pred.set(["a", "a"].try_into_ctx(pred.domain_full())?, Some(true))?;
//! pred.set(["a", "b"].try_into_ctx(pred.domain_full())?, Some(true))?;
//! // Sets everything else that is unknown to false.
//! pred.set_all_unknown_to_value(false);
//! println!("{}", structure);
//! # Ok(())
//! # }
//! ```

pub mod collections;
pub mod error;
pub mod fmt;
pub mod idp_spec;
mod lower;
pub mod structure;
pub mod theory;
pub mod vocabulary;

/// A [TryFrom] variant where a context is needed for the operation.
pub trait TryFromCtx<I>: Sized {
    type Ctx;
    type Error;

    fn try_from_ctx(value: I, ctx: Self::Ctx) -> Result<Self, Self::Error>;
}

/// A [TryInto] variant where a context is needed for the operation.
///
/// See also [TryFromCtx].
pub trait TryIntoCtx<I>: Sized {
    type Ctx;
    type Error;

    fn try_into_ctx(self, ctx: Self::Ctx) -> Result<I, Self::Error>;
}

impl<T, U: TryFromCtx<T>> TryIntoCtx<U> for T {
    type Ctx = U::Ctx;
    type Error = U::Error;

    fn try_into_ctx(self, ctx: U::Ctx) -> Result<U, U::Error> {
        U::try_from_ctx(self, ctx)
    }
}

/// Contains metadata information about things in FO(·).
///
/// This metadata contains things such as the corresponding span in a FO(·) source specification.
#[non_exhaustive]
#[derive(Debug, Clone, Default, Hash, PartialEq, Eq)]
pub struct Metadata {
    span: Option<Span>,
}

impl AsRef<Metadata> for Metadata {
    fn as_ref(&self) -> &Metadata {
        self
    }
}

impl AsMut<Metadata> for Metadata {
    fn as_mut(&mut self) -> &mut Metadata {
        self
    }
}

impl Metadata {
    pub fn with_span(mut self, span: Span) -> Self {
        self.span = Some(span);
        self
    }
}

pub trait MetadataIm: Sized {
    type Metadata: AsRef<Metadata> + AsMut<Metadata>;
    /// Returns a reference to the [Metadata].
    fn metadata(&self) -> Option<&Self::Metadata>;

    fn span(&self) -> Option<Span> {
        self.metadata().and_then(|f| f.as_ref().span)
    }
}

pub trait MetadataMut: MetadataIm {
    /// Returns the mutable reference to the current [Metadata] or initializes one using
    /// [Default::default].
    fn metadata_mut(&mut self) -> &mut Self::Metadata;

    /// Sets the span in the [Metadata].
    fn with_span(mut self, span: Span) -> Self {
        self.metadata_mut().as_mut().span = Some(span);
        self
    }

    /// Set a new [Metadata].
    fn with_new_metadata(mut self, metadata: Metadata) -> Self {
        *self.metadata_mut().as_mut() = metadata;
        self
    }
}

macro_rules! display_as_debug {
    (
        $ty_name:ty $(, gen: ($($tt:tt)*))? $(, where: ($($bound:tt)*))?
    ) => {
        impl<$($($tt)*)?> core::fmt::Debug for $ty_name
            where $($($bound)*)?
        {
            fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
                write!(f, "{}", self)
            }
        }
    };
}

pub(self) use display_as_debug;

use crate::ast::Span;

mod architecture {
    //! This is the user facing layer of sli.
    //!
    //! See [crate::architecture] for an overview.
    //!
    //! # Implementation
    //!
    //! This layer is implemented by storing every corresponding datastructure from
    //! [comp_core] in the corresponding datastructure of this layer
    //! and using it for as much as it can be used.
    //!
    //! For instance in a [Vocabulary](vocabulary::Vocabulary) domains and
    //! codomains of pfuncs are stored in the embedded
    //! [comp_core Vocabulary](comp_core::vocabulary::Vocabulary).
    //! Usage of these embedded elements than requires translation back to the [fodot](crate::fodot)
    //! layer.
    //!
    //! These translations back to [fodot](crate::fodot) should exist inside each module
    //! as a sub module called `translation_layer` (e.g. [vocabulary::translation_layer],
    //! [structure::translation_layer]).
    //!
    //! This type of implementation has some implication, such as:
    //! - Each pfunc in fodot layer corresponds to 1 pfunc in comp core layer.
    //! - Each type in fodot layer corresponds to 1 type in comp core layer.
    //! - Possibly others.
    //!
    //! ## About genericness of [Pfunc](vocabulary::Pfunc), [Type](vocabulary::Type), ...
    //!
    //! These types are generic over `Borrow<UnderlyingType>` where `UnderlyingType` is the type
    //! they depend on, e.g. [Vocabulary](vocabulary::Vocabulary),
    //! [TypeInterps](structure::TypeInterps).
    //! We do this cause these types can appear in 2 forms: their normal selves, or wrapped in an
    //! [Rc](sli_collections::rc::Rc).
    //! So we want these types to be generic over a [reference] and an [Rc](sli_collections::rc::Rc) to reduce
    //! code duplication.
    //!
    //! This causes certain methods to be over restrictive for a [reference], e.g.
    //! [Domain::get](vocabulary::Domain::get).
    //! For this we provide reference only methods with less restrictive lifetimes.
    //! These unfortunately have a different name since having the same name is not allowed.
    //! These methods have a `_ref` postfix in their name.

    #[cfg(doc)]
    use super::*;
}
