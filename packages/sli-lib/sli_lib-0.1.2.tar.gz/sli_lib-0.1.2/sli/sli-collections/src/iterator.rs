use cfg_if::cfg_if;
cfg_if! {
    if #[cfg(feature = "std_sync")] {
        pub use sync::Iterator;
    } else {
        pub use norm::Iterator;
    }
}

#[cfg(not(feature = "std_sync"))]
#[doc(hidden)]
mod norm {
    pub trait Iterator: core::iter::Iterator {}

    impl<T: core::iter::Iterator> Iterator for T {}
}

#[cfg(feature = "std_sync")]
#[doc(hidden)]
mod sync {
    pub trait Iterator: core::iter::Iterator + Sync + Send {}

    impl<T: core::iter::Iterator + Sync + Send> Iterator for T {}
}
