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

pub mod ast;
pub mod fodot;
mod sli_entrance;
pub mod solver;
pub use sli_collections::rc::Rc;

include!(concat!(env!("OUT_DIR"), "/sli_version.rs"));

mod architecture {
    //! # SLI architecture
    //!
    //! SLI is split into 3 parts that are part of a pipeline.
    //! - [FO(·)](fodot)
    //! - [comp_core]
    //! - [Solvers](solver)
    //!
    //! ## FO(·)
    //!
    //! The first part represents full FO(·) which gets transformed to FO(·) [comp_core].
    //! See [fodot] for more info.
    //!
    //! ## [comp_core]
    //!
    //! The comp core part is the second part of the pipeline, simplification using satisfying sets and
    //! others such as ?relevance? and symbolic propagation live here
    //! (relevance and symb prop don't exist yet).
    //! Mainly any kind of performance intensive procedure is implementation in this layer.
    //!
    //! Transformations and tools for easing transformations of comp core can be found in [transform].
    //! Such as the satisfying set transform in [comp_core::transform::satisfying_set_transform]
    //! and the naive transform in [comp_core::transform::naive_transform].
    //!
    //! ## Solvers
    //!
    //! Lastly in the [solver](comp_core::solver) module comp core is translated
    //! (grounded) to a format for use with a solver. Such as [solver::z3](comp_core::solver::z3).
    //!
    //! Note: a pipeline is not a good mental model of this process since data must also be
    //! translated in the opposite direction (this is currently lacking).
    //! e.g. solver results must be represented in FO(·) and as such flow backwards in the pipeline.

    #[cfg(doc)]
    use super::fodot;
    #[cfg(doc)]
    use super::solver;
    #[cfg(doc)]
    use comp_core;
    #[cfg(doc)]
    use comp_core::transform;
}
