use cfg_if::cfg_if;
cfg_if! {
    if #[cfg(feature = "std_sync")] {
        pub use sync::Auto;
    } else {
        pub use norm::Auto;
    }
}

#[cfg(not(feature = "std_sync"))]
#[doc(hidden)]
mod norm {
    pub trait Auto {}

    impl<T> Auto for T {}
}

#[cfg(feature = "std_sync")]
#[doc(hidden)]
mod sync {
    pub trait Auto: Sync + Send {}

    impl<T: Sync + Send> Auto for T {}
}
