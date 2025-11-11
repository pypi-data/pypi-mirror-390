use super::{Vocabulary, convert_type};
use pyo3::{
    exceptions::{PyNotImplementedError, PyRuntimeError, PyTypeError, PyValueError},
    prelude::*,
    types::PyString,
};
use sli_collections::rc::Rc;
use sli_lib::fodot::vocabulary::{self, ConstructorRef, PfuncRc, PfuncRef, SymbolRef};

#[pyclass(frozen, subclass)]
/// An FO(·) symbol.
pub struct Symbol;

#[pymethods]
impl Symbol {
    fn name(&self) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }

    fn __str__(&self) -> PyResult<()> {
        Err(PyNotImplementedError::new_err(()))
    }
}

#[pyclass(frozen, extends=Symbol, subclass)]
/// A custom FO(·) symbol, this is always linked to a vocabulary.
///
/// A `CustomSymbol` can become invalid if an operation on the underlying vocabulary causes the
/// symbol to no longer exist in this vocabulary.
/// Any operation on a `CustomSymbol` in this state raises `RuntimeError`.
pub struct CustomSymbol {
    pub(crate) symbol: Rc<str>,
    pub(crate) vocab: Py<Vocabulary>,
}

impl CustomSymbol {
    /// Returns true if this symbol is still valid in the vocabulary, false otherwise.
    pub(crate) fn is_valid(&self, py: Python) -> bool {
        self.vocab
            .get()
            .0
            .get_py(py)
            .parse_symbol(&self.symbol)
            .is_ok()
    }

    pub(crate) fn is_valid_err(&self, py: Python) -> Result<(), PyErr> {
        if self.is_valid(py) {
            Ok(())
        } else {
            Err(PyRuntimeError::new_err(format!(
                "Custom '{}' symbol is no longer valid in vocabulary",
                &self.symbol
            )))
        }
    }
}

#[pymethods]
impl CustomSymbol {
    /// Returns the name of the symbol.
    pub fn name(&self, py: Python) -> PyResult<&str> {
        self.is_valid_err(py).map(|_| self.symbol.as_ref())
    }

    /// Vocabulary of the given symbol.
    pub fn vocab(slf: &Bound<'_, Self>) -> PyResult<Py<Vocabulary>> {
        slf.get()
            .is_valid_err(slf.py())
            .map(|_| slf.get().vocab.clone_ref(slf.py()))
    }

    pub fn __str__(&self, py: Python) -> PyResult<&str> {
        self.is_valid_err(py).map(|_| self.symbol.as_ref())
    }
}

#[pyclass(frozen, extends=CustomSymbol)]
pub struct Pfunc;

impl Pfunc {
    pub fn with_ref<R, F: FnOnce(PfuncRef) -> R>(slf: Borrowed<Self>, f: F) -> PyResult<R> {
        Ok(f(slf
            .as_super()
            .get()
            .vocab
            .get()
            .0
            .get_py(slf.py())
            .parse_pfunc(&slf.as_super().get().name(slf.py())?)
            .unwrap()))
    }

    pub fn as_rc(slf: Borrowed<Self>) -> PyResult<PfuncRc> {
        Ok(vocabulary::Vocabulary::parse_pfunc_rc(
            &slf.as_super().get().vocab.get().0.get_py(slf.py()),
            &slf.as_super().get().name(slf.py())?,
        )
        .unwrap())
    }
}

#[pymethods]
impl Pfunc {
    pub fn __str__(slf: &Bound<Self>) -> PyResult<String> {
        Self::with_ref(slf.as_borrowed(), |f| format!("{}", f))
    }

    pub fn __repr__(slf: &Bound<Self>) -> PyResult<String> {
        Ok(Self::with_ref(slf.as_borrowed(), |f| {
            Ok(format!(
                "<Pfunc({}, {})>",
                f,
                slf.as_super().get().vocab.bind(slf.py()).repr()?
            ))
        })
        .and_then(|f| f)?)
    }
}

impl Pfunc {
    pub fn construct(symbol: Rc<str>, vocab: Py<Vocabulary>, py: Python) -> PyResult<Py<Self>> {
        Py::new(
            py,
            PyClassInitializer::from(Symbol)
                .add_subclass(CustomSymbol { symbol, vocab })
                .add_subclass(Pfunc),
        )
    }

    pub(crate) fn from_ref(
        pfunc: PfuncRef,
        vocab: Py<Vocabulary>,
        py: Python,
    ) -> PyResult<Py<Self>> {
        Self::construct(pfunc.name_rc(), vocab, py)
    }
}

#[pyclass(frozen, extends=CustomSymbol)]
pub struct Constructor;

impl Constructor {
    pub fn construct(symbol: Rc<str>, vocab: Py<Vocabulary>, py: Python) -> PyResult<Py<Self>> {
        Py::new(
            py,
            PyClassInitializer::from(Symbol)
                .add_subclass(CustomSymbol { symbol, vocab })
                .add_subclass(Constructor),
        )
    }

    pub(crate) fn from_ref(
        constructor: ConstructorRef,
        vocab: Py<Vocabulary>,
        py: Python,
    ) -> PyResult<Py<Self>> {
        Self::construct(constructor.name_rc(), vocab, py)
    }
}

pub fn convert_symbol(value: SymbolRef, vocab: Bound<'_, Vocabulary>) -> PyResult<Py<PyAny>> {
    match value {
        vocabulary::Symbol::Type(type_ref) => convert_type(type_ref, &vocab),
        vocabulary::Symbol::Pfunc(pfunc) => {
            Pfunc::from_ref(pfunc, vocab.clone().unbind(), vocab.py()).map(|f| f.into())
        }
        vocabulary::Symbol::Constructor(constructor) => {
            Constructor::from_ref(constructor, vocab.clone().unbind(), vocab.py()).map(|f| f.into())
        }
    }
}

pub(crate) fn convert_pfunc_from_python_ref<'a>(
    pfunc: Borrowed<PyAny>,
    vocab: &'a vocabulary::Vocabulary,
) -> PyResult<PfuncRef<'a>> {
    if let Ok(name) = pfunc.cast::<PyString>() {
        vocabulary::Vocabulary::parse_pfunc(&vocab, &name.to_cow()?)
            .map_err(|f| PyValueError::new_err(format!("{}", f)))
    } else if let Ok(pfunc) = pfunc.cast::<Pfunc>() {
        if !pfunc
            .as_super()
            .get()
            .vocab
            .get()
            .0
            .get_py(pfunc.py())
            .exact_eq(vocab)
        {
            return Err(PyValueError::new_err(format!(
                "Found symbol {} from {}, expecting a symbol from <Vocabulary at {:p}>",
                pfunc.as_super().get().name(pfunc.py())?,
                &pfunc.as_super().get().vocab.bind(pfunc.py()).repr()?,
                vocab,
            )));
        }
        Ok(vocab
            .parse_pfunc(pfunc.as_super().get().name(pfunc.py())?)
            .unwrap())
    } else {
        Err(PyTypeError::new_err(format!(
            "expected a 'str' or a 'Pfunc', found a '{}'",
            pfunc.get_type().str()?
        )))
    }
}
