use super::{CustomSymbol, Symbol, Vocabulary};
use pyo3::{
    IntoPyObjectExt,
    exceptions::{PyTypeError, PyValueError},
    prelude::*,
    types::PyString,
};
use sli_lib::fodot::vocabulary::{
    self, CustomType, CustomTypeRc, CustomTypeRef, IntTypeRc, IntTypeRef, PrimitiveType,
    RealTypeRc, RealTypeRef, StrTypeRc, StrTypeRef, TypeRc, TypeRef, parse_primitive_type,
};
use std::{borrow::Cow, convert::Infallible};

pub enum _Type<'a> {
    String(Cow<'a, str>),
    Bool(BuiltinBool),
    Int(BuiltinInt),
    Real(BuiltinReal),
    IntType(&'a Bound<'a, IntType>),
    RealType(&'a Bound<'a, RealType>),
    StrType(&'a Bound<'a, StrType>),
}

impl<'a> _Type<'a> {
    pub fn from_any(value: &'a Bound<'a, PyAny>, what: &str) -> PyResult<Self> {
        if let Ok(str) = value.downcast::<PyString>() {
            Ok(Self::String(str.to_cow()?))
        } else if let Ok(bool) = value.downcast::<BuiltinBool>() {
            Ok(Self::Bool(bool.get().clone()))
        } else if let Ok(int) = value.downcast::<BuiltinInt>() {
            Ok(Self::Int(int.get().clone()))
        } else if let Ok(real) = value.downcast::<BuiltinReal>() {
            Ok(Self::Real(real.get().clone()))
        } else if let Ok(int_type) = value.downcast::<IntType>() {
            Ok(Self::IntType(int_type))
        } else if let Ok(real_type) = value.downcast::<RealType>() {
            Ok(Self::RealType(real_type))
        } else if let Ok(str_type) = value.downcast::<StrType>() {
            Ok(Self::StrType(str_type))
        } else {
            Err(PyTypeError::new_err(format!(
                "{what} must be a BaseType, a string, not {}",
                value.get_type().str()?
            )))
        }
    }
}

pub fn convert_custom_type(
    value: CustomTypeRef,
    vocab: &Bound<'_, Vocabulary>,
) -> PyResult<Py<PyAny>> {
    match value {
        CustomType::Int(int_type) => {
            Ok(IntType::from_ref(int_type, vocab)?.into_py_any(vocab.py())?)
        }
        CustomType::Real(real_type) => {
            Ok(RealType::from_ref(real_type, vocab)?.into_py_any(vocab.py())?)
        }
        CustomType::Str(str_type) => {
            Ok(StrType::from_ref(str_type, vocab)?.into_py_any(vocab.py())?)
        }
    }
}

pub fn convert_type(value: TypeRef, vocab: &Bound<'_, Vocabulary>) -> PyResult<Py<PyAny>> {
    match value {
        vocabulary::Type::Bool => Ok(py_bool(vocab.py()).into()),
        vocabulary::Type::Int => Ok(py_int(vocab.py()).into()),
        vocabulary::Type::Real => Ok(py_real(vocab.py()).into()),
        vocabulary::Type::IntType(int_type) => {
            Ok(IntType::from_ref(int_type, vocab)?.into_py_any(vocab.py())?)
        }
        vocabulary::Type::RealType(real_type) => {
            Ok(RealType::from_ref(real_type, vocab)?.into_py_any(vocab.py())?)
        }
        vocabulary::Type::StrType(str_type) => {
            Ok(StrType::from_ref(str_type, vocab)?.into_py_any(vocab.py())?)
        }
    }
}

#[pyclass(frozen, extends=Symbol)]
/// The builtin boolean type.
///
/// This is a singleton object.
#[derive(Clone, Copy)]
pub struct BuiltinBool;

impl BuiltinBool {
    pub(crate) fn construct(py: Python) -> PyResult<Py<Self>> {
        Py::new(py, (BuiltinBool, Symbol))
    }
}

#[pymethods]
impl BuiltinBool {
    #[new]
    fn new() -> Py<Self> {
        Python::attach(|f| py_bool(f).unbind())
    }

    fn __str__(&self) -> String {
        format!("{}", TypeRc::Bool)
    }

    fn name(&self) -> &str {
        sli_lib::fodot::fmt::BOOL_ASCII
    }

    fn __repr__(&self) -> &str {
        "<BuiltinBool>"
    }
}

#[pyclass(frozen, extends=Symbol)]
/// The builtin integer type.
///
/// This is a singleton object.
#[derive(Clone, Copy)]
pub struct BuiltinInt;

impl BuiltinInt {
    pub(crate) fn construct(py: Python) -> PyResult<Py<Self>> {
        Py::new(py, (BuiltinInt, Symbol))
    }
}

#[pymethods]
impl BuiltinInt {
    #[new]
    fn new() -> Py<Self> {
        Python::attach(|f| py_int(f).unbind())
    }

    fn __str__(&self) -> String {
        format!("{}", TypeRc::Int)
    }

    fn name(&self) -> &str {
        sli_lib::fodot::fmt::INT_ASCII
    }

    fn __repr__(&self) -> &str {
        "<BuiltinInt>"
    }
}

#[pyclass(frozen, extends=Symbol)]
/// The builtin real type.
///
/// This is a singleton object.
#[derive(Clone, Copy)]
pub struct BuiltinReal;

impl BuiltinReal {
    pub(crate) fn construct(py: Python) -> PyResult<Py<Self>> {
        Py::new(py, (BuiltinReal, Symbol))
    }
}

#[pymethods]
impl BuiltinReal {
    #[new]
    fn new() -> Py<Self> {
        Python::attach(|f| py_real(f).unbind())
    }

    fn __str__(&self) -> String {
        format!("{}", TypeRc::Real)
    }

    fn name(&self) -> &str {
        sli_lib::fodot::fmt::REAL_ASCII
    }

    fn __repr__(&self) -> &str {
        "<BuiltinReal>"
    }
}

#[pyclass(frozen, extends=CustomSymbol)]
/// A custom integer type.
pub struct IntType;

impl IntType {
    pub fn from_ref<'a>(
        value: IntTypeRef,
        vocab: &Bound<'a, Vocabulary>,
    ) -> PyResult<Bound<'a, Self>> {
        Ok(Bound::new(
            vocab.py(),
            PyClassInitializer::from(Symbol)
                .add_subclass(CustomSymbol {
                    symbol: value.name_rc(),
                    vocab: vocab.clone().unbind(),
                })
                .add_subclass(IntType),
        )?)
    }

    pub fn vocab<'a>(slf: Borrowed<'a, '_, Self>) -> Py<Vocabulary> {
        slf.as_super().get().vocab.clone_ref(slf.py())
    }

    pub fn with_ref<R, F: FnOnce(IntTypeRef) -> R>(slf: Borrowed<Self>, f: F) -> PyResult<R> {
        match slf
            .as_super()
            .get()
            .vocab
            .get()
            .0
            .get_py(slf.py())
            .parse_type(&slf.as_super().get().name(slf.py())?)
            .unwrap()
        {
            vocabulary::Type::IntType(value) => Ok(f(value)),
            _ => unreachable!(),
        }
    }

    pub fn as_rc(slf: Borrowed<Self>) -> PyResult<IntTypeRc> {
        match vocabulary::Vocabulary::parse_type_rc(
            &slf.as_super().get().vocab.get().0.get_py(slf.py()),
            &slf.as_super().get().name(slf.py())?,
        )
        .unwrap()
        {
            vocabulary::Type::IntType(value) => Ok(value),
            _ => unreachable!(),
        }
    }
}

#[pymethods]
impl IntType {
    pub fn __repr__(slf: Bound<Self>) -> PyResult<String> {
        Ok(format!(
            "<IntType({}, {})>",
            slf.as_super().get().name(slf.py())?,
            slf.as_super().get().vocab.bind(slf.py()).repr()?
        ))
    }
}

#[pyclass(frozen, extends=CustomSymbol)]
/// A custom real type.
pub struct RealType;

impl RealType {
    pub fn from_ref<'a>(
        value: RealTypeRef,
        vocab: &Bound<'a, Vocabulary>,
    ) -> PyResult<Bound<'a, Self>> {
        Ok(Bound::new(
            vocab.py(),
            PyClassInitializer::from(Symbol)
                .add_subclass(CustomSymbol {
                    symbol: value.name_rc(),
                    vocab: vocab.clone().unbind(),
                })
                .add_subclass(RealType),
        )?)
    }

    pub fn with_ref<R, F: FnOnce(RealTypeRef) -> R>(slf: Borrowed<Self>, f: F) -> PyResult<R> {
        match slf
            .as_super()
            .get()
            .vocab
            .get()
            .0
            .get_py(slf.py())
            .parse_type(&slf.as_super().get().name(slf.py())?)
            .unwrap()
        {
            vocabulary::Type::RealType(value) => Ok(f(value)),
            _ => unreachable!(),
        }
    }

    pub fn as_rc(slf: Borrowed<Self>) -> PyResult<RealTypeRc> {
        match vocabulary::Vocabulary::parse_type_rc(
            &slf.as_super().get().vocab.get().0.get_py(slf.py()),
            &slf.as_super().get().name(slf.py())?,
        )
        .unwrap()
        {
            vocabulary::Type::RealType(value) => Ok(value),
            _ => unreachable!(),
        }
    }
}

#[pymethods]
impl RealType {
    pub fn __repr__(slf: Bound<Self>) -> PyResult<String> {
        Ok(format!(
            "<RealType({}, {})>",
            slf.as_super().get().name(slf.py())?,
            slf.as_super().get().vocab.bind(slf.py()).repr()?
        ))
    }
}

#[pyclass(frozen, extends=CustomSymbol)]
/// A custom type.
pub struct StrType;

impl StrType {
    pub fn from_ref<'a>(
        value: StrTypeRef,
        vocab: &Bound<'a, Vocabulary>,
    ) -> PyResult<Bound<'a, Self>> {
        Ok(Bound::new(
            vocab.py(),
            PyClassInitializer::from(Symbol)
                .add_subclass(CustomSymbol {
                    symbol: value.name_rc(),
                    vocab: vocab.clone().unbind(),
                })
                .add_subclass(StrType),
        )?)
    }

    pub fn with_ref<R, F: FnOnce(StrTypeRef) -> R>(slf: Borrowed<Self>, f: F) -> PyResult<R> {
        match slf
            .as_super()
            .get()
            .vocab
            .get()
            .0
            .get_py(slf.py())
            .parse_type(&slf.as_super().get().name(slf.py())?)
            .unwrap()
        {
            vocabulary::Type::StrType(value) => Ok(f(value)),
            _ => unreachable!(),
        }
    }

    pub fn as_rc(slf: Borrowed<Self>) -> PyResult<StrTypeRc> {
        match vocabulary::Vocabulary::parse_type_rc(
            &slf.as_super().get().vocab.get().0.get_py(slf.py()),
            &slf.as_super().get().name(slf.py())?,
        )
        .unwrap()
        {
            vocabulary::Type::StrType(value) => Ok(value),
            _ => unreachable!(),
        }
    }
}

#[pymethods]
impl StrType {
    pub fn __repr__(slf: Bound<Self>) -> PyResult<String> {
        Ok(format!(
            "<StrType({}, {})>",
            slf.as_super().get().name(slf.py())?,
            slf.as_super().get().vocab.bind(slf.py()).repr()?
        ))
    }
}

#[pyfunction]
pub fn _parse_builtin_type<'a>(value: &Bound<'a, PyString>) -> PyResult<Bound<'a, PyAny>> {
    parse_primitive_type(&value.cast::<PyString>()?.to_cow()?)
        .map(|f| match f {
            PrimitiveType::Bool => py_bool(value.py()).into_any(),
            PrimitiveType::Int => py_int(value.py()).into_any(),
            PrimitiveType::Real => py_real(value.py()).into_any(),
        })
        .map_err(|f| PyValueError::new_err(format!("{}", f)))
}

pub(crate) fn py_bool<'a>(python: Python<'a>) -> Bound<'a, BuiltinBool> {
    python
        .import("sli_lib._fodot.vocabulary")
        .unwrap()
        .getattr("_bool")
        .unwrap()
        .cast_into_exact()
        .unwrap()
}

pub(crate) fn py_int<'a>(python: Python<'a>) -> Bound<'a, BuiltinInt> {
    python
        .import("sli_lib._fodot.vocabulary")
        .unwrap()
        .getattr("_int")
        .unwrap()
        .cast_into_exact()
        .unwrap()
}

pub(crate) fn py_real<'a>(python: Python<'a>) -> Bound<'a, BuiltinReal> {
    python
        .import("sli_lib._fodot.vocabulary")
        .unwrap()
        .getattr("_real")
        .unwrap()
        .cast_into_exact()
        .unwrap()
}

pub(crate) fn convert_or_parse_builtin_type<'a>(
    value: Borrowed<'a, 'a, PyAny>,
) -> PyResult<PrimitiveType> {
    if let Ok(str) = value.downcast::<PyString>() {
        parse_primitive_type(&str.to_cow()?).map_err(|f| PyValueError::new_err(f.to_string()))
    } else {
        convert_builtin_type_from_python(value)
            .map_err(|f| {
                if f.is_instance_of::<PyTypeError>(value.py()) {
                    let value = match value.get_type().str() {
                        Ok(value) => value,
                        Err(value) => return value,
                    };
                    PyTypeError::new_err(format!(
                        "Expected a value of type `BuiltinTypes` or its member values or a string, found a {}",
                        value
                    ))
                } else {
                    f
                }
            })
    }
}

pub(crate) fn convert_builtin_type_from_python<'a>(
    value: Borrowed<'a, 'a, PyAny>,
) -> PyResult<PrimitiveType> {
    let py_builtin = value
        .py()
        .import("sli_lib.fodot.vocabulary")
        .unwrap()
        .getattr("BuiltinTypes")
        .unwrap();
    let member_value_holder;
    let member_value = if value.is_instance(&py_builtin)? {
        member_value_holder = value.getattr("value").unwrap();
        member_value_holder.as_borrowed()
    } else {
        value
    };
    if member_value.eq(py_bool(member_value.py()))? {
        Ok(PrimitiveType::Bool)
    } else if member_value.eq(py_int(member_value.py()))? {
        Ok(PrimitiveType::Int)
    } else if member_value.eq(py_real(member_value.py()))? {
        Ok(PrimitiveType::Real)
    } else {
        Err(PyTypeError::new_err(format!(
            "Expected a value of type `BuiltinTypes` or its member values, found a {}",
            value.get_type().str()?
        )))
    }
}

/// Convert or parse to from python.
///
/// # Errors:
///
/// - `ValueError` if a string was given but this string is not a type in the given vocabulary,
///     if a symbol type was given with the wrong vocabulary, or if an invalid symbol was given.
/// - `TypeError` if an unexpected type was given.
pub(crate) fn convert_or_parse_type_from_python<'a>(
    value: Borrowed<'a, 'a, PyAny>,
    vocabulary: Borrowed<'a, 'a, Vocabulary>,
) -> PyResult<TypeRc> {
    if let Ok(value) = value.cast::<PyString>() {
        Ok(vocabulary::Vocabulary::parse_type_rc(
            &vocabulary.get().0.get_py(value.py()),
            &value.to_cow()?,
        )
        .map_err(|err| PyValueError::new_err(err.to_string()))?)
    } else {
        convert_type_from_python(value, vocabulary)
            .map_err(|f| {
                if f.is_instance_of::<PyTypeError>(value.py()) {
                    let value = match value.get_type().str() {
                        Ok(value) => value,
                        Err(value) => return value,
                    };
                    PyTypeError::new_err(format!(
                        "Expected a value of type `BuiltinTypes` or its member values or a user defined type or a string, found a {}",
                        value
                    ))
                } else {
                    f
                }
            })
    }
}

pub(crate) fn convert_or_parse_custom_type_from_python<'a>(
    value: Borrowed<'a, 'a, PyAny>,
    vocabulary: Borrowed<'a, 'a, Vocabulary>,
) -> PyResult<CustomTypeRc> {
    use vocabulary::Type as T;
    match convert_or_parse_type_from_python(value, vocabulary)? {
        value @ (T::Bool | T::Int | T::Real) => Err(PyValueError::new_err(format!(
            "expected a custom type found: {}",
            value
        ))),
        T::IntType(value) => Ok(value.into()),
        T::RealType(value) => Ok(value.into()),
        T::StrType(value) => Ok(value.into()),
    }
}

pub(crate) fn vocab_mismatch(
    name: &str,
    first: &Py<Vocabulary>,
    second: Borrowed<Vocabulary>,
) -> PyErr {
    let _vocab_mismatch = |name: &str, first: &Py<Vocabulary>, second: Borrowed<Vocabulary>| {
        Err::<Infallible, PyErr>(PyValueError::new_err(Python::attach(|py| {
            PyResult::Ok(format!(
                "Found symbol {} from {}, expecting a symbol from {}",
                name,
                first.bind(py).repr()?,
                second.repr()?,
            ))
        })?))
    };
    _vocab_mismatch(name, first, second).unwrap_err()
}

/// Convert or parse to from python.
///
/// # Errors:
///
/// - `ValueError` if a symbol type was given with the wrong vocabulary, or a invalid symbol was
/// given.
/// - `TypeError` if an unexpected type was given.
pub(crate) fn convert_type_from_python<'a>(
    value: Borrowed<'a, 'a, PyAny>,
    vocabulary: Borrowed<'a, 'a, Vocabulary>,
) -> PyResult<TypeRc> {
    if let Ok(value) = convert_builtin_type_from_python(value) {
        Ok(value.into())
    } else {
        if let Ok(value) = value.cast::<IntType>() {
            if !value
                .as_super()
                .get()
                .vocab
                .get()
                .0
                .get_py(value.py())
                .exact_eq(vocabulary.get().0.get_py(value.py()).as_ref())
            {
                Err(vocab_mismatch(
                    value.as_super().get().name(value.py())?,
                    &value.as_super().get().vocab,
                    vocabulary,
                ))
            } else {
                Ok(IntType::as_rc(value.as_borrowed())?.into())
            }
        } else if let Ok(value) = value.cast::<RealType>() {
            if !value
                .as_super()
                .get()
                .vocab
                .get()
                .0
                .get_py(value.py())
                .exact_eq(vocabulary.get().0.get_py(value.py()).as_ref())
            {
                Err(vocab_mismatch(
                    value.as_super().get().name(value.py())?,
                    &value.as_super().get().vocab,
                    vocabulary,
                ))
            } else {
                Ok(RealType::as_rc(value.as_borrowed())?.into())
            }
        } else if let Ok(value) = value.cast::<StrType>() {
            if !value
                .as_super()
                .get()
                .vocab
                .get()
                .0
                .get_py(value.py())
                .exact_eq(vocabulary.get().0.get_py(value.py()).as_ref())
            {
                Err(vocab_mismatch(
                    value.as_super().get().name(value.py())?,
                    &value.as_super().get().vocab,
                    vocabulary,
                ))
            } else {
                Ok(StrType::as_rc(value.as_borrowed())?.into())
            }
        } else {
            Err(PyTypeError::new_err(format!(
                "Expected a value of type `BuiltinTypes` or its member values or a user defined type, found a {}",
                value.get_type().str()?
            )))
        }
    }
}
