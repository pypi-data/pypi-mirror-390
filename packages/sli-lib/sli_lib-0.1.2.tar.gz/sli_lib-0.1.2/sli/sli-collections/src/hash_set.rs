//! Module that reexports a hash set implementation in 2 flavours.
//!
//! The first flavour is the traditional hash set.
//! This is either the std hash set if std is given, or the default [hashbrown] hash set.
//! Note that the [hashbrown] hash set uses the default hashing algorithm that [hashbrown]
//! provides, this hashing algorithm (at the time of writing) is notably not as resistant
//! to HashDos as SipHash.
//!
//! The second flavour is a deterministic hash set that should only be used when the keys are
//! integer indexes.

use super::hash::IdBuildHasher;
use cfg_if::cfg_if;

cfg_if! {
    if #[cfg(feature = "std")] {
        pub use std::collections::HashSet;
    } else {
        pub use hashbrown::HashSet;
    }
}

cfg_if! {
    if #[cfg(feature = "std")] {
        pub type IdHashSet<T> = std::collections::HashSet<T, IdBuildHasher>;
    } else {
        pub type IdHashSet<T> = hashbrown::HashSet<T, IdBuildHasher>;
    }
}
