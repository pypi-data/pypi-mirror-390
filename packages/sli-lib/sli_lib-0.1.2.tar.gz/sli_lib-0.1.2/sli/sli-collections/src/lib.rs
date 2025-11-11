//! Contains wrapped datastructures of things such as [alloc::rc::Rc] and [core::cell::Cell], with
//! that implement [Sync] and [Send] if any of the `sync` feature flags are set.
//!
//! # Feature flags
//!
//! - `std_sync`: Ensures [Sync] and [Send] are implemented for all datastructures making use of
//! `std`.
#![no_std]

extern crate alloc;
#[cfg(feature = "std")]
extern crate std;

pub mod auto;
pub mod cell;
pub mod hash;
pub mod hash_map;
pub mod hash_set;
pub mod iterator;
pub mod rc;
