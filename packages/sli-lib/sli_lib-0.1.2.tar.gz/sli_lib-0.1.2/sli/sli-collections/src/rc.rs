use alloc::borrow::{Cow, ToOwned};
use alloc::boxed::Box;
use alloc::string::String;
use alloc::vec::Vec;
use cfg_if::cfg_if;
use core::fmt;
use core::mem::ManuallyDrop;
use core::ptr::NonNull;
use core::{
    borrow::Borrow,
    fmt::{Display, Pointer},
    ops::Deref,
    panic::{RefUnwindSafe, UnwindSafe},
};

cfg_if! {
    if #[cfg(feature = "std_sync")] {
        type CRc<T> = std::sync::Arc<T>;
    } else {
        type CRc<T> = alloc::rc::Rc<T>;
    }
}

#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Default, Hash)]
#[repr(transparent)]
pub struct Rc<T: ?Sized>(CRc<T>);

impl<T: ?Sized> Deref for Rc<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        self.0.deref()
    }
}

impl<T: ?Sized> AsRef<T> for Rc<T> {
    fn as_ref(&self) -> &T {
        self.0.as_ref()
    }
}

impl<T: ?Sized + Display> Display for Rc<T> {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        Display::fmt(&self.0, f)
    }
}

impl<T> From<T> for Rc<T> {
    fn from(value: T) -> Self {
        Self(value.into())
    }
}

impl From<&str> for Rc<str> {
    fn from(value: &str) -> Self {
        Self(value.into())
    }
}

impl From<String> for Rc<str> {
    fn from(value: String) -> Self {
        Self(value.into())
    }
}

impl<T> From<Box<T>> for Rc<T> {
    fn from(value: Box<T>) -> Self {
        Self(value.into())
    }
}

impl<T> From<Vec<T>> for Rc<[T]> {
    fn from(value: Vec<T>) -> Self {
        Self(value.into())
    }
}

impl<'a, B: ToOwned + ?Sized> From<alloc::borrow::Cow<'a, B>> for Rc<B>
where
    Rc<B>: From<&'a B> + From<<B as ToOwned>::Owned>,
{
    fn from(value: Cow<'a, B>) -> Self {
        match value {
            Cow::Borrowed(value) => value.into(),
            Cow::Owned(value) => value.into(),
        }
    }
}

impl<T: ?Sized> Pointer for Rc<T> {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        Pointer::fmt(&self.0, f)
    }
}

impl<T: ?Sized> Clone for Rc<T> {
    fn clone(&self) -> Self {
        Self(self.0.clone())
    }
}

impl<T: ?Sized> Borrow<T> for Rc<T> {
    fn borrow(&self) -> &T {
        self.as_ref()
    }
}

impl<T: RefUnwindSafe + ?Sized> RefUnwindSafe for Rc<T> {}

impl<T: ?Sized> Unpin for Rc<T> {}

impl<T: RefUnwindSafe + ?Sized> UnwindSafe for Rc<T> {}

impl<T> Rc<T> {
    pub fn new(value: T) -> Rc<T> {
        Self(CRc::new(value))
    }

    pub fn ptr_eq(this: &Rc<T>, other: &Rc<T>) -> bool {
        CRc::ptr_eq(&this.0, &other.0)
    }

    pub fn as_ptr(this: &Rc<T>) -> *const T {
        CRc::as_ptr(&this.0)
    }

    /// Manually increment the reference count.
    ///
    /// # Safety
    ///
    /// The pointer must have been obtained through [Rc::into_raw] and the
    /// associated [Rc] instance must be valid (i.e. the strong count must be at
    /// least 1) for the duration of this method.
    pub unsafe fn increment_count(ptr: *const T) {
        unsafe {
            CRc::increment_strong_count(ptr);
        }
    }

    /// Manually decrement the reference count.
    ///
    /// # Safety
    ///
    /// The pointer must have been obtained through [Rc::into_raw] and the
    /// associated [Rc] instance must be valid (i.e. the strong count must be at
    /// least 1). This method can be used to release the final `Rc` and
    /// backing storage, but **should not** be called after the final `Rc` has been released.
    pub unsafe fn decrement_count(ptr: *const T) {
        unsafe {
            CRc::decrement_strong_count(ptr);
        }
    }

    pub fn count(this: &Rc<T>) -> usize {
        CRc::strong_count(&this.0)
    }

    #[must_use = "losing the pointer will leak memory"]
    pub fn into_raw(this: Rc<T>) -> *const T {
        CRc::into_raw(this.0)
    }

    /// Constructs a `Rc<T>`from a raw pointer.
    ///
    /// # Safety
    ///
    /// The raw pointer must come from [`Rc<T>::into_raw`].
    /// The same requirements as [std::rc::Rc::from_raw] from [std] hold.
    pub unsafe fn from_raw(ptr: *const T) -> Rc<T> {
        unsafe { Self(CRc::from_raw(ptr)) }
    }
}

impl<T: Clone> Rc<T> {
    pub fn make_mut(this: &mut Rc<T>) -> &mut T {
        CRc::make_mut(&mut this.0)
    }

    pub fn unwrap_or_clone(this: Rc<T>) -> T {
        CRc::unwrap_or_clone(this.0)
    }

    pub fn into_inner(this: Rc<T>) -> Option<T> {
        CRc::into_inner(this.0)
    }
}

/// Trait for any (smart) pointer that has that same representation as a pointer to `T`.
///
/// # Safety
///
/// The implementer must be have the exact same representation as a [NonNull].
/// And as such same representation as a reference.
pub unsafe trait PtrRepr<T>: core::ops::Deref<Target = T> + Sized {
    /// 'standard' container for the pointer.
    ///
    /// This container is not obligated to make any promises about its representation.
    ///
    /// i.e. [Rc] makes no promises about it's representation, but [RcA] does.
    type Ctx: Into<Self> + core::ops::Deref<Target = T>;
}

unsafe impl<'a, T> PtrRepr<T> for &'a T {
    type Ctx = &'a T;
}

unsafe impl<T> PtrRepr<T> for RcA<T> {
    type Ctx = Rc<T>;
}

/// An aligned [Rc] to a `T`.
///
/// This struct is a smart pointer like [Rc], except that is guaranteed to point straight to `T`,
/// instead of pointing to something else first, such as the reference counters.
///
/// For datastructures generic over pointers this struct can cause better code to be generated by
/// the compiler, because this has the same behaviour as a reference except that it must do extra
/// work when dropped.
#[repr(transparent)]
pub struct RcA<T>(core::ptr::NonNull<T>);

// Safety:
// Feature "std_sync" guarentees that backed Rc is thread safe.
#[cfg(feature = "std_sync")]
unsafe impl<T: Send + Sync> Send for RcA<T> {}
// Safety:
// Feature "std_sync" guarentees that backed Rc is thread safe.
#[cfg(feature = "std_sync")]
unsafe impl<T: Send + Sync> Sync for RcA<T> {}

impl<T> RcA<T> {
    pub fn new(rc: Rc<T>) -> Self {
        Self(unsafe { core::ptr::NonNull::new_unchecked(Rc::into_raw(rc) as *mut _) })
    }

    pub fn into_rc(this: Self) -> Rc<T> {
        this.into()
    }

    pub fn ptr_eq(this: &Self, other: &Self) -> bool {
        core::ptr::addr_eq(this.0.as_ptr(), other.0.as_ptr())
    }

    #[must_use = "losing the pointer will leak memory"]
    pub fn into_raw(this: Self) -> *const T {
        let this = ManuallyDrop::new(this);
        this.0.as_ptr() as *const _
    }

    /// Constructs an `RcA<T>`from a raw pointer.
    ///
    /// # Safety
    ///
    /// The raw pointer must come from [`RcA<T>::into_raw`].
    /// The same requirements as [Rc::from_raw] hold.
    pub unsafe fn from_raw(ptr: *const T) -> Self {
        Self(NonNull::new(ptr as *mut T).unwrap())
    }
}

impl<T> From<Rc<T>> for RcA<T> {
    fn from(value: Rc<T>) -> Self {
        Self::new(value)
    }
}

impl<T> From<RcA<T>> for Rc<T> {
    fn from(value: RcA<T>) -> Self {
        unsafe { Rc::from_raw(value.0.as_ptr() as *mut _) }
    }
}

impl<T> core::ops::Deref for RcA<T> {
    type Target = T;
    fn deref(&self) -> &Self::Target {
        unsafe { self.0.as_ref() }
    }
}

impl<T> core::ops::Drop for RcA<T> {
    fn drop(&mut self) {
        unsafe { Rc::decrement_count(self.0.as_ptr() as *const _) }
    }
}

impl<T> Clone for RcA<T> {
    fn clone(&self) -> Self {
        unsafe {
            Rc::increment_count(self.0.as_ptr() as *mut _);
        }
        Self(self.0)
    }
}

impl<T> AsRef<T> for RcA<T> {
    fn as_ref(&self) -> &T {
        unsafe { self.0.as_ref() }
    }
}

impl<T> core::borrow::Borrow<T> for RcA<T> {
    fn borrow(&self) -> &T {
        self.as_ref()
    }
}

impl<T> core::hash::Hash for RcA<T>
where
    T: core::hash::Hash,
{
    fn hash<H: core::hash::Hasher>(&self, state: &mut H) {
        self.as_ref().hash(state)
    }
}

impl<T> PartialEq for RcA<T>
where
    T: PartialEq,
{
    fn eq(&self, other: &Self) -> bool {
        self.as_ref().eq(other.as_ref())
    }
}

impl<T> Eq for RcA<T> where T: Eq {}

impl<T> PartialOrd for RcA<T>
where
    T: PartialOrd,
{
    fn partial_cmp(&self, other: &Self) -> Option<core::cmp::Ordering> {
        self.as_ref().partial_cmp(other.as_ref())
    }
}

impl<T> Ord for RcA<T>
where
    T: Ord,
{
    fn cmp(&self, other: &Self) -> core::cmp::Ordering {
        self.as_ref().cmp(other.as_ref())
    }
}

impl<T> fmt::Display for RcA<T>
where
    T: fmt::Display,
{
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        fmt::Display::fmt(self.as_ref(), f)
    }
}

impl<T> fmt::Debug for RcA<T>
where
    T: fmt::Debug,
{
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        fmt::Debug::fmt(self.as_ref(), f)
    }
}
