use super::{structure::Structure, vocabulary::Vocabulary};
use crate::interior_mut::InnerMut;
use pyo3::{exceptions::PyValueError, prelude::*, types::PyString};
use sli_collections::rc::Rc;
use sli_lib::fodot::theory;

#[pyclass(frozen)]
/// A set of FO(·) assertions.
pub struct Assertions(InnerMut<Rc<theory::Assertions>>);

impl Assertions {
    pub(crate) fn construct(assertions: Rc<theory::Assertions>) -> Self {
        Self(InnerMut::new(assertions))
    }
}

#[pymethods]
impl Assertions {
    #[new]
    fn new(vocabulary: &Bound<'_, Vocabulary>) -> Self {
        let vocab = vocabulary.get().0.get_py(vocabulary.py()).clone();
        Self::construct(theory::Assertions::new(vocab).into())
    }

    /// Returns the vocabulary of the assertions.
    fn vocab(slf: &Bound<'_, Self>) -> Vocabulary {
        Vocabulary::construct(slf.get().0.get_py(slf.py()).vocab_rc().clone())
    }

    /// Adds the given string form FO(·) assertions to this object.
    fn parse(slf: Bound<'_, Self>, decls: Bound<'_, PyString>) -> PyResult<Py<Self>> {
        let source = decls.to_cow()?;
        let source_str: &str = &source;
        Rc::make_mut(&mut slf.get().0.get_mut_py(slf.py()))
            .parse(source_str)
            .map_err(|f| PyValueError::new_err(format!("{}", f.with_source(&source_str))))?;
        Ok(slf.unbind())
    }

    fn __str__(&self, py: Python) -> String {
        format!("{}", self.0.get_py(py).as_ref())
    }
}

#[pyclass(frozen)]
/// An FO(·) theory.
pub struct Theory(pub(crate) theory::Theory);

impl Theory {
    pub(crate) fn construct(theory: theory::Theory) -> Self {
        Self(theory)
    }
}

impl AsRef<theory::Theory> for Theory {
    fn as_ref(&self) -> &theory::Theory {
        &self.0
    }
}

#[pymethods]
impl Theory {
    #[new]
    fn new(assertions: Bound<'_, Assertions>, structure: Bound<'_, Structure>) -> PyResult<Self> {
        let structure = structure
            .get()
            .0
            .get_py(assertions.py())
            .clone()
            .try_into_partial()
            .map_err(|f| f.type_interps().missing_type_error())
            .map_err(|f| PyValueError::new_err(format!("{}", f)))?;
        Ok(Self::construct(
            theory::Theory::new(
                assertions.get().0.get_py(assertions.py()).clone(),
                structure,
            )
            .map_err(|f| PyValueError::new_err(format!("{}", f)))?,
        ))
    }

    /// Creates a `Theory` from an FO(·) specification containing one vocabulary block, one theory
    /// block and one structure block.
    #[staticmethod]
    fn from_specification(value: &str) -> PyResult<Self> {
        theory::Theory::from_specification(value)
            .map(|inner| Theory::construct(inner))
            .map_err(|f| pyo3::exceptions::PyValueError::new_err(format!("{}", f)))
    }

    /// Returns the vocabulary of the theory.
    fn vocab(slf: Bound<'_, Self>) -> Vocabulary {
        Vocabulary(InnerMut::new(slf.get().0.vocab_rc().clone()))
    }

    /// Returns the assertions of the theory.
    fn assertions(&self) -> Assertions {
        Assertions::construct(self.0.assertions_rc().clone())
    }

    /// Returns the structure of the theory.
    fn structure(slf: Bound<'_, Self>) -> Structure {
        Structure::construct(slf.get().0.structure().clone().into_incomplete())
    }

    fn __str__(&self) -> String {
        format!("{}", &self.0)
    }
}

pub fn submodule(py: Python) -> PyResult<Bound<'_, PyModule>> {
    let m = PyModule::new(py, "theory")?;
    m.gil_used(false)?;
    m.add_class::<Assertions>()?;
    m.add_class::<Theory>()?;
    Ok(m)
}
