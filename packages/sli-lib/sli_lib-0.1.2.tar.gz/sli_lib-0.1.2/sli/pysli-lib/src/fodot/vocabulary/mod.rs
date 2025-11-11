use crate::{
    fodot::structure::py_type_interp_to_interp,
    interior_mut::{InnerImIter, InnerMut},
};
use pyo3::{
    exceptions::{
        PyNotImplementedError, PyRuntimeError, PyTypeError, PyValueError, PyZeroDivisionError,
    },
    prelude::*,
    types::PyString,
};
use sli_collections::rc::Rc;
use sli_lib::fodot::vocabulary::{
    self, BaseType, CustomTypeRef, Int, PfuncBuilder, PfuncRef, PrimitiveType,
};
use std::{
    ops::{Deref, DerefMut},
    str::FromStr,
};
mod types;
pub use types::*;
mod symbols;
pub use symbols::*;

#[pyclass(frozen)]
/// Python class representing an FO(·) vocabulary.
pub struct Vocabulary(pub(crate) InnerMut<Rc<vocabulary::Vocabulary>>);

impl AsRef<InnerMut<Rc<vocabulary::Vocabulary>>> for Vocabulary {
    fn as_ref(&self) -> &InnerMut<Rc<vocabulary::Vocabulary>> {
        &self.0
    }
}

impl Vocabulary {
    pub(crate) fn construct(vocabulary: Rc<vocabulary::Vocabulary>) -> Self {
        Self(InnerMut::new(vocabulary))
    }

    fn py_with_mut<T, F: FnOnce(&mut vocabulary::Vocabulary) -> T>(&self, py: Python, f: F) -> T {
        let mut b = self.0.get_mut_py(py);
        let a = Rc::make_mut(b.deref_mut());
        f(a)
    }
}

#[pymethods]
impl Vocabulary {
    #[new]
    fn new(name: &str) -> Self {
        Self(InnerMut::new(vocabulary::Vocabulary::new(name).into()))
    }

    /// Returns the name of this vocabulary.
    fn name(&self, py: Python) -> String {
        self.0.get_py(py).name().to_owned()
    }

    /// Parses vocabulary declarations and adds them to this vocabulary.
    ///
    /// ```python
    /// from sli_lib.fodot.vocabulary import Vocabulary
    /// # Vocabulary.parse returns the vocabulary so it can be chained.
    /// vocab = Vocabulary("V").parse("""
    ///     type T
    /// """)
    /// # Already existing symbols can be referenced
    /// vocab.parse("""
    ///     p: T -> Bool
    /// """)
    /// print(vocab.parse_type("T"))
    /// print(vocab.parse_pfunc("p"))
    /// ```
    fn parse<'a>(
        slf: &'a Bound<'a, Self>,
        source: &Bound<'_, PyString>,
    ) -> PyResult<&'a Bound<'a, Self>> {
        slf.get().py_with_mut(slf.py(), |f| {
            let source_cow = source.to_cow()?;
            let source_str = source_cow.deref();
            f.parse(source_str)
                .map(|_| ())
                .map_err(|f| PyValueError::new_err(format!("{}", f.with_source(&source_str))))
        })?;
        Ok(slf)
    }

    /// Adds the given type to the vocabulary, with no super set or the given super set.
    ///
    /// # Raises
    ///
    /// - `TypeError` if any of the given arguments don't conform to the type annotations.
    /// - `ValueError` if the given name already exists in the vocabulary.
    #[pyo3(signature = (name, super_set = None))]
    fn add_type(
        slf: &Bound<'_, Self>,
        name: &str,
        super_set: Option<Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        let super_set = if let Some(super_set) = super_set {
            match convert_or_parse_builtin_type(super_set.as_borrowed()) {
                Ok(PrimitiveType::Bool) => {
                    return Err(PyNotImplementedError::new_err(
                        "Subtype of `Bool` is unimplemented",
                    ));
                }
                Ok(PrimitiveType::Int) => BaseType::Int,
                Ok(PrimitiveType::Real) => BaseType::Real,
                Err(_) => {
                    let interp = py_type_interp_to_interp(super_set.as_borrowed())
                        .map_err(|_| {
                            let super_set_type = match super_set.get_type().str() {
                                Ok(value) => value,
                                Err(err) => return err,
                            };
                            PyTypeError::new_err(
                                format!(
                                    "'super_set' must be either a 'ExtType' or a type interpretation, found '{}'",
                                    super_set_type
                                )
                            )
                        })?;
                    return slf
                        .get()
                        .py_with_mut(slf.py(), |voc| {
                            voc.add_type_decl_with_interp(name, interp).map(|_| ())
                        })
                        .map_err(|f| pyo3::exceptions::PyValueError::new_err(format!("{}", f)));
                }
            }
        } else {
            BaseType::Str
        };
        slf.get()
            .py_with_mut(slf.py(), |voc| {
                voc.add_type_decl(name, super_set.into()).map(|_| ())
            })
            .map_err(|f| pyo3::exceptions::PyValueError::new_err(format!("{}", f)))
    }

    /// Adds the given interpretation to the given type at a vocabulary level.
    ///
    /// # Raises
    ///
    /// - `ValueError` if a string was given but this string is not a type in the given vocabulary,
    ///     if a symbol type was given with the wrong vocabulary, or if an invalid symbol was given.
    /// - `TypeError` if an unexpected type was given.
    fn add_voc_type_interp(
        slf: &Bound<'_, Self>,
        type_: &Bound<'_, PyAny>,
        interp: Bound<'_, PyAny>,
    ) -> PyResult<()> {
        let type_name = convert_or_parse_type_from_python(type_.as_borrowed(), slf.as_borrowed())?
            .name()
            .to_string();
        let interpp = py_type_interp_to_interp(interp.as_borrowed())?;
        slf.get()
            .py_with_mut(slf.py(), |f| {
                f.add_voc_type_interp(&type_name, interpp).map(|_| ())
            })
            .map_err(|f| PyValueError::new_err(format!("{}", f)))
    }

    /// Adds one or many pfuncs with the given signature to the vocabulary.
    ///
    /// # Raises
    ///
    /// - `ValueError` if a type was given as a string but this string is not a type
    ///     in the given vocabulary, if a symbol type was given with the wrong vocabulary,
    ///     if an invalid symbol was given or if a symbol with the same name as the given name(s)
    ///     already exists.
    /// - `TypeError` if an unexpected type was given.
    fn add_pfunc(
        slf: &Bound<'_, Self>,
        name: &Bound<'_, PyAny>,
        domain: &Bound<'_, PyAny>,
        codomain: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        let borrowed_slf = slf.as_borrowed();
        let codomain = convert_or_parse_type_from_python(codomain.as_borrowed(), borrowed_slf)?
            .name()
            .to_owned();
        let domain: Result<Vec<_>, (usize, PyErr)> = domain
            .try_iter()?
            .enumerate()
            .map(|(i, f)| {
                Ok(convert_or_parse_type_from_python(
                    f.map_err(|f| (i, f))?.as_borrowed(),
                    borrowed_slf,
                )
                .map_err(|f| (i, f))?
                .name()
                .to_owned())
            })
            .collect();
        let domain = domain.map_err(|f| {
            let pyobj = f.1.into_pyobject(slf.py()).unwrap();
            pyobj
                .call_method1("add_note", (format!("At domain {}", f.0),))
                .unwrap();
            pyobj
        })?;
        slf.get().py_with_mut(slf.py(), |voc| {
            let mut builder = voc.build_pfunc_decl(&codomain).unwrap();
            for dom in domain {
                builder.add_to_domain(&dom).unwrap();
            }
            let complete_with_name = |name: &Bound<'_, PyString>, builder: &mut PfuncBuilder| {
                builder
                    .complete_with_name(&name.to_cow()?)
                    .map_err(|f| PyValueError::new_err(f.to_string()))?;
                PyResult::Ok(())
            };
            if let Ok(value) = name.cast::<PyString>() {
                complete_with_name(value, &mut builder)?;
            } else if let Ok(iterator) = name.try_iter() {
                for (i, value) in iterator.enumerate() {
                    let value = value?;
                    if let Ok(value) = value.cast::<PyString>() {
                        complete_with_name(value, &mut builder)?;
                    } else {
                        return Err(PyTypeError::new_err(format!(
                            "pfunc name in position {} must be a string, found a {}",
                            i,
                            value.get_type().str()?,
                        )));
                    }
                }
            } else {
                return Err(PyTypeError::new_err(format!(
                    "Argument `name` must be a string or a tuple of strings, found a {}",
                    name.get_type().str()?
                )));
            }
            Ok(())
        })
    }

    /// Parses the given string to a type.
    ///
    /// # Raises
    ///
    /// - `ValueError` if the given string was not a type in the vocabulary.
    /// - `TypeError` if anything else but a string was given.
    fn parse_type(slf: &Bound<'_, Self>, value: &Bound<'_, PyString>) -> PyResult<Py<PyAny>> {
        slf.get()
            .0
            .get_py(slf.py())
            .parse_type(&value.to_cow()?)
            .map_err(|f| PyValueError::new_err(format!("{}", f)))
            .and_then(|f| convert_type(f, slf))
    }

    /// Parses the given string to a pfunc.
    ///
    /// # Raises
    ///
    /// - `ValueError` if the given string was not a pfunc in the vocabulary.
    /// - `TypeError` if anything else but a string was given.
    fn parse_pfunc(slf: &Bound<'_, Self>, value: &Bound<'_, PyString>) -> PyResult<Py<Pfunc>> {
        let this = slf.clone();
        slf.get()
            .0
            .get_py(slf.py())
            .parse_pfunc(&value.to_cow()?)
            .map_err(|f| PyValueError::new_err(format!("{}", f)))
            .and_then(|f| Pfunc::construct(f.name_rc(), this.unbind(), slf.py()))
    }

    /// Parses the given string to a symbol.
    ///
    /// # Raises
    ///
    /// - `ValueError` if the given string was not a symbol in the vocabulary.
    /// - `TypeError` if anything else but a string was given.
    fn parse_symbol(slf: Bound<'_, Self>, value: &Bound<'_, PyString>) -> PyResult<Py<PyAny>> {
        let this = slf.clone();
        slf.get()
            .0
            .get_py(slf.py())
            .parse_symbol(&value.to_cow()?)
            .map_err(|f| PyValueError::new_err(format!("{}", f)))
            .and_then(|f| convert_symbol(f, this))
    }

    fn __str__(&self, py: Python) -> String {
        format!("{}", self.0.get_py(py).as_ref())
    }

    /// Returns an iterator over all pfuncs in the vocabulary.
    fn iter_pfuncs(slf: Bound<'_, Self>) -> PfuncIter {
        // Safety:
        // InnerImIter guarantees a is never used after mutation occurs and may life for as long
        // as slf lives (which is just as long as InnerMutIter lives.
        let inner = unsafe {
            InnerImIter::construct(&slf, |f| {
                let a: Box<dyn Iterator<Item = PfuncRef> + Send + Sync> = Box::new(f.iter_pfuncs());
                core::mem::transmute::<
                    Box<dyn Iterator<Item = PfuncRef> + Send + Sync + '_>,
                    Box<dyn Iterator<Item = PfuncRef<'static>> + Send + Sync + 'static>,
                >(a)
            })
        };
        PfuncIter(inner)
    }

    /// Returns an iterator over all types in the vocabulary.
    fn iter_types(slf: Bound<'_, Self>) -> TypeIter {
        // Safety:
        // InnerImIter guarantees a is never used after mutation occurs and may life for as long
        // as slf lives (which is just as long as InnerMutIter lives.
        let inner = unsafe {
            InnerImIter::construct(&slf, |f| {
                let a: Box<dyn Iterator<Item = CustomTypeRef> + Send + Sync> =
                    Box::new(f.iter_types());
                core::mem::transmute::<
                    Box<dyn Iterator<Item = CustomTypeRef> + Send + Sync + '_>,
                    Box<dyn Iterator<Item = CustomTypeRef<'static>> + Send + Sync + 'static>,
                >(a)
            })
        };
        TypeIter(inner)
    }
}

#[pyclass(frozen)]
pub struct TypeIter(InnerImIter<CustomTypeRef<'static>, Vocabulary, Rc<vocabulary::Vocabulary>>);

#[pymethods]
impl TypeIter {
    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn vocab(slf: Bound<'_, Self>) -> Py<Vocabulary> {
        slf.get().0.holder().clone_ref(slf.py())
    }

    fn __next__(slf: Bound<'_, Self>) -> PyResult<Option<Py<PyAny>>> {
        let iter = slf.get().0.aquire_iter(slf.py());
        iter.next()
            .map_err(|_| PyRuntimeError::new_err("vocabulary changed during iteration"))?
            .and_then(|f| Some(convert_custom_type(f, &slf.get().0.holder().bind(slf.py()))))
            .transpose()
    }
}

#[pyclass(frozen)]
pub struct PfuncIter(InnerImIter<PfuncRef<'static>, Vocabulary, Rc<vocabulary::Vocabulary>>);

#[pymethods]
impl PfuncIter {
    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn vocab(slf: Bound<'_, Self>) -> Py<Vocabulary> {
        slf.get().0.holder().clone_ref(slf.py())
    }

    fn __next__(slf: Bound<'_, Self>) -> PyResult<Option<Py<Pfunc>>> {
        let iter = slf.get().0.aquire_iter(slf.py());
        iter.next()
            .map_err(|_| PyRuntimeError::new_err("vocabulary changed during iteration"))?
            .and_then(|f| {
                Some(Pfunc::construct(
                    f.name_rc(),
                    slf.get().0.holder().clone_ref(slf.py()),
                    slf.py(),
                ))
            })
            .transpose()
    }
}

#[pyclass(frozen)]
/// An representation of an FO(·) real
pub struct Real(pub(crate) vocabulary::Real);

impl Real {
    pub(crate) fn from_py_exact(value: Borrowed<PyAny>) -> PyResult<Self> {
        if let Ok(value) = value.cast::<Real>() {
            Ok(Real(value.get().0.clone()))
        } else if let Ok(value) = value.extract::<Int>() {
            Ok(Real(vocabulary::Real::from(value)))
        } else if let Ok(value) = value.extract::<f64>() {
            vocabulary::Real::try_from(value)
                .map_err(|f| PyValueError::new_err(format!("{}", f)))
                .map(Real)
        } else {
            Err(PyTypeError::new_err(format!(
                "expected a 'Real' or 'int' or 'float', found a '{}'",
                value.get_type().name()?.to_cow()?
            )))
        }
    }

    pub(crate) fn from_py_exact_op(value: Borrowed<PyAny>, operator: &str) -> PyResult<Self> {
        Real::from_py_exact(value.as_borrowed()).map_err(|_| {
            let value = match value.get_type().name() {
                Ok(value) => value,
                Err(err) => return err,
            };
            PyTypeError::new_err(format!(
                "unsupported operand type(s) for {}: 'Real' and '{}'",
                operator, value
            ))
        })
    }
}

#[pymethods]
impl Real {
    #[new]
    fn new(value: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(value) = value.extract::<Int>() {
            Ok(Real(vocabulary::Real::from(value)))
        } else if let Ok(value) = value.extract::<f64>() {
            Ok(Real(
                vocabulary::Real::try_from(value)
                    .map_err(|f| PyValueError::new_err(format!("{}", f)))?,
            ))
        } else if let Ok(value) = value.cast::<PyString>() {
            vocabulary::Real::from_str(&value.to_cow()?)
                .map_err(|f| PyValueError::new_err(format!("{}", f)))
                .map(Real)
        } else {
            Err(PyTypeError::new_err(format!(
                "Expected an int or a float or a string, found a {}",
                value.get_type().str()?
            )))
        }
    }

    fn __add__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        Ok(Real(
            self.0 + Real::from_py_exact_op(other.as_borrowed(), "-")?.0,
        ))
    }

    fn __sub__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        Ok(Real(
            self.0 - Real::from_py_exact_op(other.as_borrowed(), "-")?.0,
        ))
    }

    fn __mul__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        Ok(Real(
            self.0 * Real::from_py_exact_op(other.as_borrowed(), "/")?.0,
        ))
    }

    fn __truediv__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        Ok(Real(
            self.0
                .div(&Real::from_py_exact_op(other.as_borrowed(), "/")?.0)
                .map_err(|_| PyZeroDivisionError::new_err("division by zero"))?,
        ))
    }

    fn __mod__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        Ok(Real(
            self.0
                .rem(&Real::from_py_exact_op(other.as_borrowed(), "%")?.0)
                .map_err(|_| PyZeroDivisionError::new_err("division by zero"))?,
        ))
    }

    fn __str__(&self) -> String {
        format!("{}", self.0)
    }

    fn __float__(&self) -> f64 {
        self.0.into()
    }

    fn __repr__(&self) -> String {
        format!("Real(\"{}\")", self.0)
    }
}

pub fn submodule(py: Python) -> PyResult<Bound<'_, PyModule>> {
    let m = PyModule::new(py, "vocabulary")?;
    m.gil_used(false)?;
    m.add_class::<Vocabulary>()?;
    m.add_class::<TypeIter>()?;
    m.add_class::<PfuncIter>()?;
    m.add_class::<Symbol>()?;
    m.add_class::<CustomSymbol>()?;
    m.add_class::<Pfunc>()?;
    m.add_class::<BuiltinBool>()?;
    m.add_class::<BuiltinInt>()?;
    m.add_class::<BuiltinReal>()?;
    m.add("_bool", BuiltinBool::construct(py)?)?;
    m.add("_int", BuiltinInt::construct(py)?)?;
    m.add("_real", BuiltinReal::construct(py)?)?;
    m.add_class::<IntType>()?;
    m.add_class::<RealType>()?;
    m.add_class::<StrType>()?;
    m.add_class::<Real>()?;
    m.add_function(wrap_pyfunction!(_parse_builtin_type, &m)?)?;
    Ok(m)
}
