use crate::fodot::vocabulary::Real;
use crate::interior_mut::{InnerImIter, InnerMut};
use itertools::Itertools;
use pyo3::{
    IntoPyObjectExt,
    exceptions::{PyRuntimeError, PyTypeError, PyValueError},
    prelude::*,
    types::{PyBool, PyInt, PyNone, PyString, PyTuple},
};
use sli_collections::rc::Rc;
use sli_lib::fodot::TryFromCtx;
use sli_lib::fodot::{
    structure::{self, ArgsRef, TypeElement, TypeFull},
    vocabulary::{self, Int},
};
use std::cell::Cell;
use std::fmt::{self, Display};

#[pyclass(frozen)]
/// A set of integers.
pub struct IntInterp(pub(crate) InnerMut<Rc<structure::IntInterp>>);

impl IntInterp {
    pub(crate) fn construct(value: Rc<structure::IntInterp>) -> Self {
        Self(InnerMut::new(value))
    }
}

impl AsRef<InnerMut<Rc<structure::IntInterp>>> for IntInterp {
    fn as_ref(&self) -> &InnerMut<Rc<structure::IntInterp>> {
        &self.0
    }
}

#[pymethods]
impl IntInterp {
    #[new]
    #[pyo3(signature = (values=None))]
    fn new(values: Option<Bound<'_, PyAny>>) -> PyResult<Self> {
        match values {
            Some(values) => {
                let b: structure::IntInterp = values
                    .try_iter()?
                    .map(|f| f.and_then(|f| f.extract::<Int>().map_err(|f| PyErr::from(f))))
                    .collect::<PyResult<_>>()?;
                Ok(IntInterp(InnerMut::new(b.into())))
            }
            None => Ok(IntInterp(InnerMut::new(structure::IntInterp::new().into()))),
        }
    }

    fn __str__(slf: &Bound<'_, Self>) -> String {
        format!("{}", slf.get().0.get_py(slf.py()).as_ref())
    }

    fn __repr__(slf: &Bound<'_, Self>) -> String {
        format!(
            "IntInterp({{{}}})",
            slf.get()
                .0
                .get_py(slf.py())
                .as_ref()
                .into_iter()
                .format(", ")
        )
    }

    fn __len__(slf: &Bound<'_, Self>) -> usize {
        slf.get().0.get_py(slf.py()).len()
    }

    fn __iter__(slf: Bound<'_, Self>) -> IntInterpIter {
        // Safety:
        // We only hold references to slf
        let inner = unsafe {
            InnerImIter::construct(&slf, |f| {
                let a = f.into_iter();
                // Safety:
                // InnerImIter ensure this iterator is valid for the entire lifetime
                core::mem::transmute::<
                    structure::int_interp::Iter<'_>,
                    structure::int_interp::Iter<'static>,
                >(a)
            })
        };
        IntInterpIter(inner)
    }
}

type IntInterpIterInner =
    InnerImIter<Int, IntInterp, Rc<structure::IntInterp>, structure::int_interp::Iter<'static>>;

#[pyclass(frozen)]
pub struct IntInterpIter(pub(crate) IntInterpIterInner);

#[pymethods]
impl IntInterpIter {
    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn __next__(slf: Bound<'_, Self>) -> PyResult<Option<Int>> {
        let iter = slf.get().0.aquire_iter(slf.py());
        Ok(iter
            .next()
            .map_err(|_| PyRuntimeError::new_err("StrInterp changed during iteration"))?
            .map(|f| f))
    }
}

#[pyclass(frozen)]
/// A set of reals.
pub struct RealInterp(pub(crate) InnerMut<Rc<structure::RealInterp>>);

impl RealInterp {
    pub(crate) fn construct(value: Rc<structure::RealInterp>) -> Self {
        Self(InnerMut::new(value))
    }
}

impl AsRef<InnerMut<Rc<structure::RealInterp>>> for RealInterp {
    fn as_ref(&self) -> &InnerMut<Rc<structure::RealInterp>> {
        &self.0
    }
}

#[pymethods]
impl RealInterp {
    #[new]
    #[pyo3(signature = (values=None))]
    fn new(values: Option<Bound<'_, PyAny>>) -> PyResult<Self> {
        match values {
            Some(values) => {
                let b: structure::RealInterp = values
                    .try_iter()?
                    .map(|f| {
                        f.and_then(|f| Real::from_py_exact(f.as_borrowed()))
                            .map(|f| f.0)
                    })
                    .collect::<PyResult<_>>()?;
                Ok(RealInterp(InnerMut::new(b.into())))
            }
            None => Ok(RealInterp(InnerMut::new(
                structure::RealInterp::new().into(),
            ))),
        }
    }

    fn __str__(slf: &Bound<'_, Self>) -> String {
        format!("{}", slf.get().0.get_py(slf.py()).as_ref())
    }

    fn __repr__(slf: &Bound<'_, Self>) -> String {
        format!(
            "IntInterp({{{}}})",
            slf.get()
                .0
                .get_py(slf.py())
                .as_ref()
                .into_iter()
                .format(", ")
        )
    }

    fn __len__(slf: &Bound<'_, Self>) -> usize {
        slf.get().0.get_py(slf.py()).len()
    }

    fn __iter__(slf: Bound<'_, Self>) -> RealInterpIter {
        // Safety:
        // We only hold references to slf
        let inner = unsafe {
            InnerImIter::construct(&slf, |f| {
                let a = f.into_iter();
                // Safety:
                // InnerImIter ensure this iterator is valid for the entire lifetime
                core::mem::transmute::<
                    structure::real_interp::Iter<'_>,
                    structure::real_interp::Iter<'static>,
                >(a)
            })
        };
        RealInterpIter(inner)
    }
}

#[pyclass(frozen)]
pub struct RealInterpIter(
    InnerImIter<
        &'static vocabulary::Real,
        RealInterp,
        Rc<structure::RealInterp>,
        structure::real_interp::Iter<'static>,
    >,
);

#[pymethods]
impl RealInterpIter {
    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn __next__(slf: Bound<'_, Self>) -> PyResult<Option<Real>> {
        let iter = slf.get().0.aquire_iter(slf.py());
        Ok(iter
            .next()
            .map_err(|_| PyRuntimeError::new_err("StrInterp changed during iteration"))?
            // Safety:
            // f lives as long as the iterator, which is longer than this clone call
            .map(|f| Real(f.clone())))
    }
}

#[pyclass(frozen)]
/// A set of named objects.
pub struct StrInterp(pub(crate) InnerMut<Rc<structure::StrInterp>>);

impl StrInterp {
    pub(crate) fn construct(value: Rc<structure::StrInterp>) -> Self {
        Self(InnerMut::new(value))
    }
}

impl AsRef<InnerMut<Rc<structure::StrInterp>>> for StrInterp {
    fn as_ref(&self) -> &InnerMut<Rc<structure::StrInterp>> {
        &self.0
    }
}

#[pymethods]
impl StrInterp {
    #[new]
    #[pyo3(signature = (values=None))]
    fn new(values: Option<Bound<'_, PyAny>>) -> PyResult<Self> {
        match values {
            Some(values) => {
                let b: structure::StrInterp = values
                    .try_iter()?
                    .map(|f| {
                        f.and_then(|f| {
                            f.cast::<PyString>()
                                .map_err(|f| PyErr::from(f))
                                .and_then(|f| f.to_cow().map(|f| Rc::from(f.as_ref())))
                        })
                    })
                    .collect::<PyResult<_>>()?;
                Ok(StrInterp(InnerMut::new(b.into())))
            }
            None => Ok(StrInterp(InnerMut::new(structure::StrInterp::new().into()))),
        }
    }

    fn __str__(&self, py: Python) -> String {
        format!("{}", self.0.get_py(py).as_ref())
    }

    fn __repr__(&self, py: Python) -> String {
        format!(
            "StrInterp({{{}}})",
            self.0
                .get_py(py)
                .as_ref()
                .into_iter()
                .map(|val| display_fn(move |f| write!(f, "\"{}\"", val)))
                .format(", ")
        )
    }

    fn __len__(&self, py: Python) -> usize {
        self.0.get_py(py).len()
    }

    fn __iter__(slf: Bound<'_, Self>) -> StrInterpIter {
        // Safety:
        // We only hold references to slf
        let inner = unsafe {
            InnerImIter::construct(&slf, |f| {
                let a = f.into_iter();
                // Safety:
                // InnerImIter ensure this iterator is valid for the entire lifetime
                core::mem::transmute::<
                    <&'_ structure::StrInterp as IntoIterator>::IntoIter,
                    <&'static structure::StrInterp as IntoIterator>::IntoIter,
                >(a)
            })
        };
        StrInterpIter(inner)
    }
}

#[pyclass(frozen)]
pub struct StrInterpIter(
    InnerImIter<
        &'static Rc<str>,
        StrInterp,
        Rc<structure::StrInterp>,
        <&'static structure::StrInterp as IntoIterator>::IntoIter,
    >,
);

#[pymethods]
impl StrInterpIter {
    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn __next__<'a>(slf: Bound<'a, Self>) -> PyResult<Option<&'a str>> {
        let iter = slf.get().0.aquire_iter(slf.py());
        Ok(iter
            .next()
            .map_err(|_| PyRuntimeError::new_err("StrInterp changed during iteration"))?
            // Safety:
            // f lives as long as the iterator, which is as long as Bound<'_, Self>
            .map(|f| f.as_ref()))
    }
}

pub fn type_element_to_pyobject(py: Python, element: TypeElement) -> PyResult<Py<PyAny>> {
    match element {
        TypeElement::Bool(value) => PyBool::new(py, value).into_py_any(py),
        TypeElement::Int(value) => value.into_pyobject(py)?.into_py_any(py),
        TypeElement::Real(value) => Real(value).into_py_any(py),
        TypeElement::Str(value) => Ok(PyString::new(py, &value).into_any().unbind()),
    }
}

pub fn pyobject_to_type_element<'a>(
    value: Borrowed<'_, '_, PyAny>,
    type_full: TypeFull<'a>,
) -> PyResult<TypeElement<'a>> {
    if let Ok(value) = value.downcast::<PyBool>() {
        return Ok(TypeElement::Bool(value.is_true()));
    } else if let Ok(_) = value.downcast::<PyInt>() {
        return value.extract::<Int>().map(|f| TypeElement::Int(f));
    } else if let Ok(value) = Real::from_py_exact(value) {
        return Ok(TypeElement::Real(value.0));
    } else if let Ok(value) = value.downcast::<PyString>() {
        TypeElement::try_from_ctx(value.to_cow()?.as_ref(), type_full)
            .map_err(|f| PyValueError::new_err(format!("{}", f)))
            .and_then(|f| match f {
                value @ TypeElement::Str(_) => Ok(value),
                _ => Err(PyTypeError::new_err(format!(
                    "Expected a str, found a {}",
                    value.get_type().repr()?
                ))),
            })
    } else {
        return Err(match value.get_type().str() {
            Ok(value) => PyValueError::new_err(format!(
                "Expected a bool, int, real or string, found a {}",
                value
            )),
            Err(value) => value,
        });
    }
}

pub fn opt_type_element_to_pyobject(
    py: Python,
    element: Option<TypeElement>,
) -> PyResult<Py<PyAny>> {
    match element {
        Some(value) => type_element_to_pyobject(py, value),
        None => PyNone::get(py).into_py_any(py),
    }
}

pub fn py_type_interp_to_interp(
    interp: Borrowed<'_, '_, PyAny>,
) -> PyResult<structure::TypeInterp> {
    if let Ok(int) = interp.cast::<IntInterp>() {
        Ok(structure::TypeInterp::Int(
            int.get().0.get_py(interp.py()).clone(),
        ))
    } else if let Ok(real) = interp.cast::<RealInterp>() {
        Ok(structure::TypeInterp::Real(
            real.get().0.get_py(interp.py()).clone(),
        ))
    } else if let Ok(str) = interp.cast::<StrInterp>() {
        Ok(structure::TypeInterp::Str(
            str.get().0.get_py(interp.py()).clone(),
        ))
    } else {
        Err(PyTypeError::new_err(format!(
            "expected an 'IntInterp', a 'RealInterp' or a 'StrInterp', found a '{}'",
            interp.get_type().str()?
        )))
    }
}

pub fn args_to_py_tuple<'a>(py: Python<'a>, args: ArgsRef) -> PyResult<Bound<'a, PyTuple>> {
    PyTuple::new(
        py,
        args.iter()
            .map(|f| type_element_to_pyobject(py, f))
            .collect::<Result<Vec<_>, _>>()?,
    )
}

pub(crate) fn display_fn(f: impl FnOnce(&mut fmt::Formatter<'_>) -> fmt::Result) -> impl Display {
    struct WithFormatter<F>(Cell<Option<F>>);

    impl<F> Display for WithFormatter<F>
    where
        F: FnOnce(&mut fmt::Formatter<'_>) -> fmt::Result,
    {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            (self.0.take()).unwrap()(f)
        }
    }

    WithFormatter(Cell::new(Some(f)))
}
