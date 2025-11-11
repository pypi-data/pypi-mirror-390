//! # Store implementation
//!
//! Choosing the backend store implementation is done via the `SLI_BACKEND_STORE`
//! environment variable.
//! Valid values for this env variable are:
//! - `hash`: hashing based backend.
//! - `roaring`: roaring bitmap based backend.
//!
//! # Crate Feature Flags
//!
//! - `std`: link with rust standard library (enabled by default) (currently does not actually
//! remove std crate)
//! - [`32-bit`, `64-bit`]: sets minimum size of indices, integers and floating point numbers used. If both
//! 32-bit and 64-bit features are enabled the minimum would be 64-bit. If none of these feature
//! flags are enabled the standard size is the size of a pointer on the targeted platform.

mod comp_core;
pub mod solver;
pub mod transform;
pub use comp_core::*;
pub mod interp_structures;
mod utils;
