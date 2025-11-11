//! This module contains datastructures and their respective code for comp core.
//!
//! The computational core (comp core) is a subset of full FO(.) where all computationally
//! intensive procedures are defined.
//! This format is also what gets grounded to external solvers.
//!
//! ## [Primitive types](types)
//!
//! Primitive types live in [types]. Currently types are hardcoded to be a
//! fixed size representation, where [Reals](Real) are represented using IEEE 754 floating point
//! numbers.
//!
//! The size of all these types must currently be the same. But this is quite stupid so eventually
//! this should be changed.
//!
//! The size of these types can be set using the `*-bit` feature-flags see [crate] for
//! more info.
//!
//! ## [Vocabulary](vocabulary)
//!
//! Contains datastructures for comp core vocabulary and others that live inside of vocabularies,
//! such as types, predicates and functions (Pfunc) and domains.
//!
//! ## [Structure](structure)
//!
//! Contains datastructures for comp core structure and others that live inside of structures.
//! Such as predicate and function (Pfunc) interpretations, type interpretations, type elements
//! and type interpretations.
//!
//! ## [Expressions](expression), [Constraints](constraints) and [nodes](node)
//!
//! These 3 modules contain all code needed to represent comp core expressions and constraints.
//! The module [node] contains each node in the AST, each node type must
//! specify how to be serialized and deserialized in the [Expressions](expression::Expressions)
//! datastructure.
//! The difference between [expression] and [constraints] is that expressions are just a
//! collection of expressions, while constraints keep track of assertions (constraints).
//!
//! In comp core variables are represented using [BoundVarID](self::constraints::BoundVarId).
//! Quantifying over the same variable multiple times is not allowed. i.e. `!x: P(x) | ?x: T(x).`
//! where `x` represents the same [BoundVarId](self::constraints::BoundVarId).
//!
//! ## [Theory](theory)
//!
//! Contains the combination of a vocabulary, some constraints over this vocabulary and a
//! structure.
//! You can think of this as a complete knowledge base, ready for use.
//!
pub mod constraints;
pub mod expression;
pub mod node;
pub mod structure;
pub mod theory;
mod types;
pub mod vocabulary;
pub use types::*;
// TODO decide if exposing fodot structure to outside code is ok

pub use sli_collections::rc::Rc;
