use core::fmt::Debug;

#[derive(Default)]
pub struct Cell<T>(
    #[cfg(feature = "std_sync")] crossbeam_utils::atomic::AtomicCell<T>,
    #[cfg(not(feature = "std_sync"))] core::cell::Cell<T>,
);

#[cfg(feature = "std_sync")]
#[doc(hidden)]
mod atomic_impls {
    use super::*;
    impl<T> Cell<T> {
        #[inline]
        pub fn new(value: T) -> Self {
            Cell(value.into())
        }

        #[inline]
        pub fn as_ptr(&self) -> *mut T {
            self.0.as_ptr()
        }

        #[inline]
        pub fn get_mut(&mut self) -> &mut T {
            // This is safe since we have a mutable reference to self.
            unsafe { self.as_ptr().as_mut().unwrap() }
        }

        #[inline]
        pub fn into_inner(self) -> T {
            // This is safe since we have ownership of self
            let ptr = self.as_ptr();
            let new_value = unsafe { ptr.read() };
            core::mem::forget(self);
            new_value
        }
    }

    impl<T: Default> Cell<T> {
        #[inline]
        pub fn take(&self) -> T {
            self.0.take()
        }
    }

    impl<T: Copy> Cell<T> {
        #[inline]
        pub fn get(&self) -> T {
            self.0.load()
        }

        #[inline]
        pub fn set(&self, value: T) {
            self.0.store(value)
        }

        #[inline]
        pub fn update<F: FnOnce(T) -> T>(&self, f: F) -> T {
            let new = f(self.get());
            self.set(new);
            new
        }
    }
}

#[cfg(not(feature = "std_sync"))]
#[doc(hidden)]
mod non_sync_impls {
    use super::*;
    impl<T> Cell<T> {
        #[inline]
        pub fn new(value: T) -> Self {
            Cell(value.into())
        }

        #[inline]
        pub fn as_ptr(&self) -> *mut T {
            self.0.as_ptr()
        }

        #[inline]
        pub fn get_mut(&mut self) -> &mut T {
            self.0.get_mut()
        }

        #[inline]
        pub fn into_inner(self) -> T {
            self.0.into_inner()
        }
    }

    impl<T: Default> Cell<T> {
        #[inline]
        pub fn take(&self) -> T {
            self.0.take()
        }
    }

    impl<T: Copy> Cell<T> {
        #[inline]
        pub fn get(&self) -> T {
            self.0.get()
        }

        #[inline]
        pub fn set(&self, value: T) {
            self.0.set(value)
        }

        #[inline]
        pub fn update<F: FnOnce(T) -> T>(&self, f: F) -> T {
            let new = f(self.get());
            self.set(new);
            new
        }
    }
}

impl<T: Copy> Clone for Cell<T> {
    #[inline]
    fn clone(&self) -> Self {
        Self::new(self.get())
    }
}

impl<T> From<T> for Cell<T> {
    #[inline]
    fn from(value: T) -> Self {
        Cell::new(value)
    }
}

impl<T: PartialEq + Copy> PartialEq for Cell<T> {
    #[inline]
    fn eq(&self, other: &Self) -> bool {
        self.get() == other.get()
    }
}

impl<T: Eq + Copy> Eq for Cell<T> {}

impl<T: PartialOrd + Copy> PartialOrd for Cell<T> {
    #[inline]
    fn partial_cmp(&self, other: &Self) -> Option<core::cmp::Ordering> {
        self.get().partial_cmp(&other.get())
    }
}

impl<T: Copy + Debug> Debug for Cell<T> {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.debug_tuple("Cell").field(&self.get()).finish()
    }
}
