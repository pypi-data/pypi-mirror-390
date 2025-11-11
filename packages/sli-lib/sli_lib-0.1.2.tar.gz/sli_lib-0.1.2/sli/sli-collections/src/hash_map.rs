//! Module that reexports a hash map implementation in 2 flavours.
//!
//! The first flavour is the traditional hash map.
//! This is either the std hash map if std is given, or the default [hashbrown] hash map.
//! Note that the [hashbrown] hash map uses the default hashing algorithm that [hashbrown]
//! provides, this hashing algorithm (at the time of writing) is notably not as resistant
//! to HashDos as SipHash.
//!
//! The second flavour is a deterministic hash map that should only be used when the keys are
//! integer indexes.

use super::hash::IdBuildHasher;
use cfg_if::cfg_if;

cfg_if! {
    if #[cfg(feature = "std")] {
        pub use std::collections::HashMap;
    } else {
        pub use hashbrown::HashMap;
    }
}

cfg_if! {
    if #[cfg(feature = "std")] {
        pub type IdHashMap<K, V> = std::collections::HashMap<K, V, IdBuildHasher>;
    } else {
        pub type IdHashMap<K, V> = hashbrown::HashMap<K, V, IdBuildHasher>;
    }
}
