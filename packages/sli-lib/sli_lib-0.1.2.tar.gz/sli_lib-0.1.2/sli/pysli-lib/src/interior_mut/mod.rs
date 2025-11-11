use core::{
    fmt::Display,
    ops::{Deref, DerefMut},
};
use itertools::Itertools;
use pyo3::{
    Bound, Py, PyClass, Python, marker::Ungil, pyclass::boolean_struct::True, sync::MutexExt,
};
use std::{
    convert::Infallible,
    marker::PhantomData,
    ptr::NonNull,
    sync::{Mutex, MutexGuard, RwLock},
};

/// Provides inner mutability for T + method for passing around datastructures that reference T.
///
/// The main idea is as follows, we provide a RwLock as the main synchronization primitive.
/// After locking T with RwLock, we must then invalidate all datastructure that have an
/// incompatible reference to T. When creating a shared reference we must invalidate the
/// (optional) mutable reference. When creating a exclusive reference we must invalidate all other
/// possible references.
pub struct InnerMut<T>(RwLock<_InnerMut<T>>);

impl<T: Clone> Clone for InnerMut<T> {
    fn clone(&self) -> Self {
        Self(self.0.read().unwrap().clone().into())
    }
}

impl<T: PartialEq> PartialEq for InnerMut<T> {
    fn eq(&self, other: &Self) -> bool {
        self.0.read().unwrap().deref() == other.0.read().unwrap().deref()
    }
}

impl<T: Eq> Eq for InnerMut<T> {}

impl<T: Display> Display for InnerMut<T> {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        Display::fmt(InnerMut::get(self).deref(), f)
    }
}

pub struct InnerMutReadGuard<'a, T>(std::sync::RwLockReadGuard<'a, _InnerMut<T>>);

impl<'a, T> Deref for InnerMutReadGuard<'a, T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.0.inner
    }
}

struct EnsureUngil<T>(T);

impl<T> EnsureUngil<T> {
    /// # Safety
    ///
    /// `value` must be [Ungil] safe.
    unsafe fn new(value: T) -> Self {
        Self(value)
    }

    pub fn inner(self) -> T {
        self.0
    }
}

/// Safety:
unsafe impl<T> Send for EnsureUngil<T> {}

pub struct InnerMutWriteGuard<'a, T>(std::sync::RwLockWriteGuard<'a, _InnerMut<T>>);

impl<'a, T> Deref for InnerMutWriteGuard<'a, T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.0.inner
    }
}

impl<'a, T> DerefMut for InnerMutWriteGuard<'a, T> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0.inner
    }
}

impl<T> InnerMut<T> {
    pub fn new(inner: T) -> Self {
        let inner_inner = _InnerMut::new(inner);
        Self(inner_inner.into())
    }

    pub fn get(this: &Self) -> InnerMutReadGuard<T> {
        let guard = this.0.read().unwrap();
        // Safety:
        // All pointers are valid for as long as this lives.
        unsafe { guard.referrers.lock().unwrap().immutable_invalidate() };
        InnerMutReadGuard(guard)
    }

    pub fn get_mut(this: &Self) -> InnerMutWriteGuard<T> {
        let guard = this.0.write().unwrap();
        // Safety:
        // All pointers are valid for as long as this lives.
        unsafe { guard.referrers.lock().unwrap().mutable_invalidate() };
        InnerMutWriteGuard(guard)
    }
}

impl<T: Sync + Send + Ungil> InnerMut<T> {
    fn add_immutable_referrer(this: &_InnerMut<T>, py: Python, referrer: NonNull<dyn Referer>) {
        this.referrers
            .lock_py_attached(py)
            .unwrap()
            .add_immutable_referrer(referrer);
    }

    fn set_mutable_referrer(this: &_InnerMut<T>, py: Python, referrer: NonNull<dyn Referer>) {
        let mut referrers = this.referrers.lock_py_attached(py).unwrap();
        referrers.set_mutable_referrer(referrer);
    }

    fn remove_immutable_referrer_py(
        this: &_InnerMut<T>,
        py: Python,
        referrer: NonNull<dyn Referer>,
    ) {
        let mut referrers = this.referrers.lock_py_attached(py).unwrap();
        referrers.remove_immutable_referrer(referrer);
    }

    fn remove_immutable_referrer(this: &_InnerMut<T>, referrer: NonNull<dyn Referer>) {
        let mut referrers = this.referrers.lock().unwrap();
        referrers.remove_immutable_referrer(referrer);
    }

    fn remove_mutable_referrer_py(this: &_InnerMut<T>, py: Python) {
        let mut referrers = this.referrers.lock_py_attached(py).unwrap();
        referrers.remove_mutable_referrer();
    }

    fn remove_mutable_referrer(this: &_InnerMut<T>) {
        let mut referrers = this.referrers.lock().unwrap();
        referrers.remove_mutable_referrer();
    }

    #[allow(unused)]
    fn read_py(&self, py: Python) -> InnerMutReadGuard<T> {
        // After locking self, we guarantee no mutations are possible.
        match self.0.try_read() {
            Ok(inner) => return InnerMutReadGuard(inner),
            Err(std::sync::TryLockError::Poisoned(_)) => panic!("poisoned lock!"),
            Err(std::sync::TryLockError::WouldBlock) => {}
        }
        let guard = py
            .detach(|| {
                let guard = self.0.read().unwrap();
                // Safety:
                // T implements ungil as such the write guard is also ok to ungil
                unsafe { EnsureUngil::new(guard) }
            })
            .inner();
        InnerMutReadGuard(guard)
    }

    fn write_py(&self, py: Python) -> InnerMutWriteGuard<T> {
        // After locking self, we guarantee no mutations are possible.
        match self.0.try_write() {
            Ok(inner) => return InnerMutWriteGuard(inner),
            Err(std::sync::TryLockError::Poisoned(_)) => panic!("poisoned lock!"),
            Err(std::sync::TryLockError::WouldBlock) => {}
        }
        let guard = py
            .detach(|| {
                let guard = self.0.write().unwrap();
                // Safety:
                // T implements ungil as such the write guard is also ok to ungil
                unsafe { EnsureUngil::new(guard) }
            })
            .inner();
        InnerMutWriteGuard(guard)
    }

    pub fn get_py(&self, py: Python) -> InnerMutReadGuard<T> {
        // After locking self, we guarantee no mutations are possible.
        match self.0.try_read() {
            Ok(inner) => return InnerMutReadGuard(inner),
            Err(std::sync::TryLockError::Poisoned(_)) => panic!("poisoned lock!"),
            Err(std::sync::TryLockError::WouldBlock) => {}
        }
        let guard = py
            .detach(|| {
                let guard = self.0.read().unwrap();
                // Safety:
                // All pointers must be valid for as long as this lives.
                unsafe { guard.referrers.lock().unwrap().immutable_invalidate() };
                // Safety:
                // T implements ungil as such the write guard is also ok to ungil
                unsafe { EnsureUngil::new(guard) }
            })
            .inner();
        InnerMutReadGuard(guard)
    }

    pub fn get_mut_py(&self, py: Python) -> InnerMutWriteGuard<T> {
        // After locking self, we guarantee no mutations are possible.
        match self.0.try_write() {
            Ok(inner) => return InnerMutWriteGuard(inner),
            Err(std::sync::TryLockError::Poisoned(_)) => panic!("poisoned lock!"),
            Err(std::sync::TryLockError::WouldBlock) => {}
        }
        let guard = py
            .detach(|| {
                let guard = self.0.write().unwrap();
                // Safety:
                // All pointers must be valid for as long as this lives.
                unsafe { guard.referrers.lock().unwrap().mutable_invalidate() };
                // Safety:
                // T implements ungil as such the write guard is also ok to ungil
                unsafe { EnsureUngil::new(guard) }
            })
            .inner();
        InnerMutWriteGuard(guard)
    }
}

enum Referrers {
    None {
        buf: Vec<NonNull<dyn Referer>>,
    },
    Immutable(Vec<NonNull<dyn Referer>>),
    Mutable {
        mutable_ref: NonNull<dyn Referer>,
        buf: Vec<NonNull<dyn Referer>>,
    },
}

impl Default for Referrers {
    fn default() -> Self {
        Self::None { buf: Vec::new() }
    }
}

impl Referrers {
    /// # Safety
    ///
    /// All NonNull pointers must be valid.
    unsafe fn immutable_invalidate(&mut self) {
        match self {
            Self::None { .. } => (),
            Self::Immutable(_) => (),
            Self::Mutable { mutable_ref, buf } => {
                // Safety:
                // Covered by method safety.
                unsafe { mutable_ref.as_ref() }.invalidate();
                *self = Self::None {
                    buf: core::mem::take(buf),
                };
            }
        }
    }

    /// # Safety
    ///
    /// All NonNull pointers must be valid.
    unsafe fn mutable_invalidate(&mut self) {
        match self {
            Self::None { .. } => (),
            Self::Immutable(immutable) => {
                immutable.iter().for_each(|refer| {
                    // Safety:
                    // Covered by method safety.
                    unsafe { refer.as_ref() }.invalidate();
                });
                immutable.clear();
                *self = Self::None {
                    buf: core::mem::take(immutable),
                };
            }
            Self::Mutable { mutable_ref, buf } => {
                // Safety:
                // Covered by method safety.
                unsafe { mutable_ref.as_ref() }.invalidate();
                *self = Self::None {
                    buf: core::mem::take(buf),
                };
            }
        }
    }

    /// Referrers must be in a [Self::None] or [Self::Immutable] state.
    fn add_immutable_referrer(&mut self, referer: NonNull<dyn Referer>) {
        match self {
            Self::None { buf } => {
                buf.push(referer);
                *self = Self::Immutable(core::mem::take(buf));
            }
            Self::Immutable(referrers) => {
                referrers.push(referer);
            }
            Self::Mutable { .. } => panic!("Invalid state of referrers"),
        }
    }

    /// Remove the given referrer, does not invalidate it.
    fn remove_immutable_referrer(&mut self, referrer: NonNull<dyn Referer>) {
        match self {
            Self::Immutable(referrers) => {
                let pos = referrers
                    .iter()
                    .find_position(|p| NonNull::addr(**p) == NonNull::addr(referrer))
                    .expect("tried to invalidate non existent referrer")
                    .0;
                referrers.remove(pos);
                referrers.push(referrer);
            }
            Self::None { .. } | Self::Mutable { .. } => {}
        }
    }

    /// Removes the referrer, but does invalidate it.
    fn remove_mutable_referrer(&mut self) {
        match self {
            Self::Mutable { buf, .. } => {
                *self = Self::None {
                    buf: core::mem::take(buf),
                };
            }
            Self::None { .. } | Self::Immutable { .. } => {}
        }
    }

    /// Referrers must be in a [Self::None].
    fn set_mutable_referrer(&mut self, referrer: NonNull<dyn Referer>) {
        match self {
            Self::None { buf } => {
                *self = Self::Mutable {
                    mutable_ref: referrer,
                    buf: core::mem::take(buf),
                };
            }
            Self::Immutable(_) | Self::Mutable { .. } => {
                panic!("Invalid state of referrers")
            }
        }
    }
}

struct _InnerMut<T> {
    inner: T,
    referrers: Mutex<Referrers>,
}

// Safety:
// T and pointers are all Sync.
unsafe impl<T: Sync> Sync for _InnerMut<T> {}
// Safety:
// T and pointers are all Send.
unsafe impl<T: Send> Send for _InnerMut<T> {}

impl<T: Clone> Clone for _InnerMut<T> {
    fn clone(&self) -> Self {
        Self {
            inner: self.inner.clone(),
            referrers: Default::default(),
        }
    }
}

impl<T: PartialEq> PartialEq for _InnerMut<T> {
    fn eq(&self, other: &Self) -> bool {
        self.inner == other.inner
    }
}

impl<T: Eq> Eq for _InnerMut<T> {}

impl<T: Display> Display for _InnerMut<T> {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        Display::fmt(&self.inner, f)
    }
}

impl<T> _InnerMut<T> {
    fn new(inner: T) -> Self {
        Self {
            inner,
            referrers: Default::default(),
        }
    }
}

trait Referer: Sync + Send {
    fn invalidate(&self);
    fn stable_pointer(self: &Box<Self>) -> NonNull<dyn Referer>
    where
        Self: Sized + 'static,
    {
        NonNull::from(self.as_ref())
    }
}

pub struct InnerImIter<
    I: 'static,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static = Box<
        dyn Iterator<Item = I> + Sync + Send + 'static,
    >,
>(
    // NB: A pointer is used here because this inner field may be shared somewhere else, whilst a
    // box is considered to have unique access to its inner field.
    NonNull<_InnerImIter<I, H, In, Iter>>,
);

// Safety:
// All underlying datastructure are Sync, we must do this manually because of raw pointer usage
unsafe impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Sync for InnerImIter<I, H, In, Iter>
{
}

// Safety:
// All underlying datastructure are Send, we must do this manually because of raw pointer usage
unsafe impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Send for InnerImIter<I, H, In, Iter>
{
}

struct _InnerImIter<
    I: 'static,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static = Box<
        dyn Iterator<Item = I> + Sync + Send + 'static,
    >,
> {
    inner: Mutex<Option<Iter>>,
    // The datastructure that Iter may contain a shared reference to, we hold it here so that it is
    // guaranteed to live as long as Iter.
    holder: Py<H>,
    _marker: PhantomData<In>,
}

impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Ungil + Sync + Send + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Referer for _InnerImIter<I, H, In, Iter>
{
    fn invalidate(&self) {
        match self.inner.lock() {
            Ok(mut value) => *value = None,
            // Even if this value is poisoned dropping the iterator is still safe.
            // See https://doc.rust-lang.org/nomicon/poisoning.html.
            Err(mut poisoned) => {
                *poisoned.get_mut().deref_mut() = None;
                self.inner.clear_poison();
            }
        }
    }
}

pub struct Invalid;

impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Ungil + Sync + Send + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> InnerImIter<I, H, In, Iter>
{
    /// The value returned from `f` is only allowed to contain references to the first argument.
    /// These references are allowed to be transmuted soundly to 'static.
    pub unsafe fn try_construct<E: Send + Sync>(
        holder: &Bound<'_, H>,
        f: impl FnOnce(&In) -> Result<Iter, E>,
    ) -> Result<Self, E> {
        let guard = holder.get().as_ref().get_py(holder.py());
        let inner = f(&guard)?;
        let inner = Box::new(_InnerImIter {
            inner: Mutex::new(Some(inner)),
            holder: holder.clone().unbind(),
            _marker: PhantomData,
        });
        InnerMut::add_immutable_referrer(guard.0.deref(), holder.py(), inner.stable_pointer());
        drop(guard);
        Ok(Self(NonNull::new(Box::into_raw(inner)).unwrap()))
    }

    /// The value returned from `f` is only allowed to contain references to the first argument.
    /// These references are allowed to be transmuted soundly to 'static.
    pub unsafe fn construct(holder: &Bound<'_, H>, f: impl FnOnce(&In) -> Iter) -> Self {
        let Ok(value) =
            unsafe { Self::try_construct(holder, |value| Ok::<_, Infallible>(f(value))) };
        value
    }

    fn as_ref(&self) -> &_InnerImIter<I, H, In, Iter> {
        // Safety:
        // It is always safe to have shared references to this _InnerImIter
        unsafe { self.0.as_ref() }
    }

    pub fn holder(&self) -> &Py<H> {
        &self.as_ref().holder
    }

    pub fn aquire_iter<'a>(&'a self, py: Python<'a>) -> InnerImIterGuard<'a, I, H, In, Iter> {
        InnerImIterGuard {
            iter: self,
            holder_guard: self.as_ref().holder.bind(py).get().as_ref().get_py(py),
            py,
        }
    }
}

pub struct InnerImIterGuard<
    'a,
    I: 'static,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static = Box<
        dyn Iterator<Item = I> + Sync + Send + 'static,
    >,
> {
    iter: &'a InnerImIter<I, H, In, Iter>,
    #[expect(unused)]
    holder_guard: InnerMutReadGuard<'a, In>,
    py: Python<'a>,
}

impl<
    'a,
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> InnerImIterGuard<'a, I, H, In, Iter>
{
    #[allow(unused)]
    pub fn is_valid(&self) -> bool {
        self.iter.as_ref().inner.lock().unwrap().is_some()
    }

    pub fn next<'py>(&self) -> Result<Option<I>, Invalid> {
        let mut guard = self.iter.as_ref().inner.lock_py_attached(self.py).unwrap();
        if let Some(inner) = guard.deref_mut() {
            Ok(inner.next())
        } else {
            Err(Invalid)
        }
    }
}

impl<
    'a,
    I: Sync + Send + Ungil,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> InnerImIterGuard<'a, I, H, In, Iter>
{
    #[allow(unused)]
    pub fn next_detached(&self) -> Result<Option<I>, Invalid> {
        let mut guard = self.iter.as_ref().inner.lock_py_attached(self.py).unwrap();
        if let Some(inner) = guard.deref_mut() {
            self.py.detach(|| Ok(inner.next()))
        } else {
            Err(Invalid)
        }
    }
}

// Safety:
// All underlying datastructure are Sync, we must do this manually because of raw pointer usage
unsafe impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Sync for _InnerImIter<I, H, In, Iter>
{
}

// Safety:
// All underlying datastructure are Send, we must do this manually because of raw pointer usage
unsafe impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Send for _InnerImIter<I, H, In, Iter>
{
}

impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Drop for InnerImIter<I, H, In, Iter>
{
    fn drop(&mut self) {
        // pointer still exists, so we must still be valid
        // Get read access to holder to invalidate pointer
        //
        // We invalidate from `self` to uphold rust aliasing rules.
        Python::try_attach(|py| {
            InnerMut::remove_immutable_referrer_py(
                self.as_ref().holder.get().as_ref().get_py(py).0.deref(),
                py,
                self.0,
            );
            py.detach(|| self.as_ref().invalidate());
        })
        .unwrap_or_else(|| {
            InnerMut::remove_immutable_referrer(
                InnerMut::get(self.as_ref().holder.get().as_ref()).0.deref(),
                self.0,
            );
            self.as_ref().invalidate();
        });
        // Safety:
        // At this point self.0 must be a unique pointer, coming from Box::into_raw
        drop(unsafe { Box::from_raw(self.0.as_ptr()) });
    }
}

pub struct InnerMutIter<
    I: 'static,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static = Box<
        dyn Iterator<Item = I> + Sync + Send + 'static,
    >,
>(
    // NB: A pointer is used here because this inner field may be shared somewhere else, whilst a
    // box is considered to have unique access to its inner field.
    NonNull<_InnerMutIter<I, H, In, Iter>>,
);

// Safety:
// All underlying datastructure are Sync, we must do this manually because of raw pointer usage
unsafe impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Sync for InnerMutIter<I, H, In, Iter>
{
}

// Safety:
// All underlying datastructure are Send, we must do this manually because of raw pointer usage
unsafe impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Send for InnerMutIter<I, H, In, Iter>
{
}

struct _InnerMutIter<
    I: 'static,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static = Box<
        dyn Iterator<Item = I> + Sync + Send + 'static,
    >,
> {
    inner: Mutex<Option<Iter>>,
    // We contain a Py reference to H, which Iter is allowed to have an exclusive reference to.
    holder: Py<H>,
    _marker: PhantomData<In>,
}

impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Ungil + Sync + Send + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Referer for _InnerMutIter<I, H, In, Iter>
{
    fn invalidate(&self) {
        match self.inner.lock() {
            Ok(mut value) => *value = None,
            // Even if this value is poisoned dropping the iterator is still safe.
            // See https://doc.rust-lang.org/nomicon/poisoning.html.
            Err(mut poisoned) => {
                *poisoned.get_mut().deref_mut() = None;
                self.inner.clear_poison();
            }
        }
    }
}

impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Ungil + Sync + Send + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> InnerMutIter<I, H, In, Iter>
{
    /// The value returned from `f` is only allowed to contain references to the first argument.
    /// These references are allowed to be transmuted soundly to 'static.
    pub unsafe fn try_construct<E: Send + Sync>(
        holder: &Bound<'_, H>,
        f: impl FnOnce(&mut In) -> Result<Iter, E>,
    ) -> Result<Self, E> {
        let mut guard = holder.get().as_ref().get_mut_py(holder.py());
        let inner = f(&mut guard)?;
        let inner = Box::new(_InnerMutIter {
            inner: Mutex::new(Some(inner)),
            holder: holder.clone().unbind(),
            _marker: PhantomData,
        });
        InnerMut::set_mutable_referrer(guard.0.deref(), holder.py(), inner.stable_pointer());
        drop(guard);
        Ok(Self(NonNull::new(Box::into_raw(inner)).unwrap()))
    }

    /// The value returned from `f` is only allowed to contain references to the first argument.
    /// These references are allowed to be transmuted soundly to 'static.
    pub unsafe fn construct(holder: &Bound<'_, H>, f: impl FnOnce(&mut In) -> Iter) -> Self {
        let Ok(value) =
            unsafe { Self::try_construct(holder, |value| Ok::<_, Infallible>(f(value))) };
        value
    }

    fn inner_ref(&self) -> &_InnerMutIter<I, H, In, Iter> {
        // Safety:
        // This NonNull can be 'owned' somewhere else, but a shared reference is always ok.
        unsafe { self.0.as_ref() }
    }

    #[allow(unused)]
    pub fn holder(&self) -> &Py<H> {
        &self.inner_ref().holder
    }

    pub fn aquire_iter<'a>(&'a self, py: Python<'a>) -> InnerMutIterGuard<'a, I, H, In, Iter> {
        InnerMutIterGuard {
            iter: self,
            // Aquire the iter using a get_mut!
            holder_guard: self
                .inner_ref()
                .holder
                .bind(py)
                .get()
                .as_ref()
                .get_mut_py(py),
            py,
        }
    }
}

pub struct InnerMutIterGuard<
    'a,
    I: 'static,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static = Box<
        dyn Iterator<Item = I> + Sync + Send + 'static,
    >,
> {
    iter: &'a InnerMutIter<I, H, In, Iter>,
    #[expect(unused)]
    holder_guard: InnerMutWriteGuard<'a, In>,
    py: Python<'a>,
}

impl<
    'a,
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> InnerMutIterGuard<'a, I, H, In, Iter>
{
    #[allow(unused)]
    pub fn is_valid(&self) -> bool {
        self.iter.inner_ref().inner.lock().unwrap().is_some()
    }

    #[allow(unused)]
    pub fn next<'py>(&self) -> Result<Option<I>, Invalid> {
        let mut guard = self
            .iter
            .inner_ref()
            .inner
            .lock_py_attached(self.py)
            .unwrap();
        if let Some(inner) = guard.deref_mut() {
            Ok(inner.next())
        } else {
            Err(Invalid)
        }
    }

    pub fn inner_mut(&self) -> MutexGuard<Option<Iter>> {
        self.iter
            .inner_ref()
            .inner
            .lock_py_attached(self.py)
            .unwrap()
    }
}

impl<
    'a,
    I: Sync + Send + Ungil,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> InnerMutIterGuard<'a, I, H, In, Iter>
{
    pub fn next_detached(&self) -> Result<Option<I>, Invalid> {
        let mut guard = self.iter.inner_ref().inner.lock().unwrap();
        if let Some(inner) = guard.deref_mut() {
            self.py.detach(|| Ok(inner.next()))
        } else {
            Err(Invalid)
        }
    }
}

// Safety:
// All underlying datastructure are Sync, we must do this manually because of raw pointer usage
unsafe impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Sync for _InnerMutIter<I, H, In, Iter>
{
}

// Safety:
// All underlying datastructure are Send, we must do this manually because of raw pointer usage
unsafe impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Send for _InnerMutIter<I, H, In, Iter>
{
}

impl<
    I,
    H: PyClass<Frozen = True> + AsRef<InnerMut<In>> + Sync,
    In: Sync + Send + Ungil + 'static,
    Iter: Iterator<Item = I> + Sync + Send + 'static,
> Drop for InnerMutIter<I, H, In, Iter>
{
    fn drop(&mut self) {
        Python::try_attach(|py| {
            InnerMut::remove_mutable_referrer_py(
                self.inner_ref()
                    .holder
                    .get()
                    .as_ref()
                    .write_py(py)
                    .0
                    .deref(),
                py,
            );
            py.detach(|| self.inner_ref().invalidate());
        })
        .unwrap_or_else(|| {
            InnerMut::remove_mutable_referrer(
                self.inner_ref()
                    .holder
                    .get()
                    .as_ref()
                    .0
                    .write()
                    .unwrap()
                    .deref(),
            );
            self.inner_ref().invalidate();
        });
        // Lastly we deallocate the iterator now that we are sure this is the last remaining
        // instance of this pointer.
        // Safety:
        // This pointer came from Box::into_raw
        drop(unsafe { Box::from_raw(self.0.as_ptr()) });
    }
}
