use crate::{
    fodot::vocabulary::{Pfunc, Real, Vocabulary},
    interior_mut::{InnerImIter, InnerMut, InnerMutReadGuard},
};
use pyo3::{
    PyTypeInfo,
    exceptions::{PyRuntimeError, PyValueError},
    prelude::*,
    sync::MutexExt,
    types::{PyBool, PyInt, PyNone, PyString, PyTuple, PyType},
};
use sli_collections::rc::Rc;
use sli_lib::fodot::{
    structure::{
        self, ArgsBuilder, ArgsRef, DomainFullRef, PartialTypeInterps, TypeElement, TypeInterp,
    },
    vocabulary::{self, CustomTypeRef},
};
use std::{ops::Deref, ptr::NonNull, sync::Mutex};

mod type_interps;
pub use type_interps::*;

use super::vocabulary::{convert_or_parse_custom_type_from_python, convert_pfunc_from_python_ref};

#[pyclass(frozen)]
/// An FO(·) structure.
///
/// Represents a state of affairs for a vocabulary.
pub struct Structure(pub(crate) InnerMut<structure::IncompleteStructure>);

impl Structure {
    pub(crate) fn construct(structure: structure::IncompleteStructure) -> Self {
        Self(InnerMut::new(structure))
    }
}

impl AsRef<InnerMut<structure::IncompleteStructure>> for Structure {
    fn as_ref(&self) -> &InnerMut<structure::IncompleteStructure> {
        &self.0
    }
}

#[pymethods]
impl Structure {
    #[new]
    fn new(vocabulary: Bound<'_, Vocabulary>) -> Self {
        let type_interps = vocabulary::Vocabulary::get_type_interps(Rc::clone(
            &vocabulary.get().0.get_py(vocabulary.py()),
        ));
        let incomplete_structure = structure::IncompleteStructure::new(type_interps);
        Structure(InnerMut::new(incomplete_structure))
    }

    fn __getitem__(slf: Bound<'_, Self>, pfunc: &Bound<'_, PyAny>) -> PyResult<PfuncInterp> {
        let name = {
            let vocab = slf.get().0.get_py(slf.py());
            let decl = convert_pfunc_from_python_ref(pfunc.as_borrowed(), vocab.vocab())?;
            decl.name_rc().clone()
        };
        Ok(PfuncInterp {
            name,
            structure: slf.unbind(),
        })
    }

    /// Returns the type interpretation of the given type, if any.
    fn get_type_interp(
        slf: Bound<'_, Self>,
        custom_type: &Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let vocab = Py::new(slf.py(), slf.get().vocab())?;
        let custom_type = convert_or_parse_custom_type_from_python(
            custom_type.as_borrowed(),
            vocab.bind(slf.py()).as_borrowed(),
        )?;
        get_interp(
            custom_type.as_ref(),
            slf.get().0.get_py(slf.py()).type_interps(),
            slf.py(),
        )
    }

    /// Set the type interpretation of the given type.
    fn set_type_interp(
        slf: Bound<'_, Self>,
        custom_type: &Bound<'_, PyAny>,
        type_interp: Bound<'_, PyAny>,
    ) -> PyResult<()> {
        let vocab = Py::new(slf.py(), slf.get().vocab())?;
        let custom_type = convert_or_parse_custom_type_from_python(
            custom_type.as_borrowed(),
            vocab.bind(slf.py()).as_borrowed(),
        )?;
        let interp = py_type_interp_to_interp(type_interp.as_borrowed())?;
        slf.get()
            .0
            .get_mut_py(slf.py())
            .set_interp(custom_type.as_ref(), interp)
            .map_err(|f| PyValueError::new_err(format!("{}", f)))
            .map(|_| ())
    }

    /// Parses structure declarations and adds them to this structure.
    ///
    /// This method does not override previous interpretations.
    /// If the resulting structure would not be a model of its vocabulary an exception is raised.
    fn parse<'a>(
        slf: &'a Bound<'a, Self>,
        source: &Bound<'_, PyString>,
    ) -> PyResult<&'a Bound<'a, Self>> {
        let mut this = slf.get().0.get_mut_py(slf.py());
        let source_cow = source.to_cow()?;
        let source_str = source_cow.deref();
        this.parse(source_str)
            .map(|_| ())
            .map_err(|f| PyValueError::new_err(format!("{}", f.with_source(&source_str))))?;
        Ok(slf)
    }

    /// Returns a boolean value signifying if the domain of the structure is complete.
    /// i.e. all types have been given an interpretation.
    fn completed_domain(&self, py: Python) -> bool {
        self.0.get_py(py).type_interps().is_complete()
    }

    /// Returns a boolean value signifying if every symbol has an interpretation, and all those
    /// interpretations are complete.
    fn is_complete(&self, py: Python) -> bool {
        self.0.get_py(py).is_complete()
    }

    /// Returns an iterator over all complete stuctures that are an expansion of this structure.
    ///
    /// # Raises
    ///
    /// - `ValueError` if this structure's domain is not completely known.
    fn iter_complete(&self, py: Python) -> PyResult<CompleteStructureIter> {
        let clone = self.0.get_py(py).clone();
        clone
            .try_into_partial()
            .map(|f| CompleteStructureIter {
                inner: Mutex::new(f.into_iter_complete()),
            })
            .map_err(|f| {
                PyValueError::new_err(format!("{}", f.type_interps().missing_type_error()))
            })
    }

    /// Returns the domain of the structure.
    fn vocab(&self) -> Vocabulary {
        Python::attach(|py| Vocabulary(InnerMut::new(self.0.get_py(py).vocab_rc().clone())))
    }

    fn __str__(&self) -> String {
        Python::attach(|py| format!("{}", self.0.get_py(py).deref()))
    }
}

#[pyclass(frozen)]
/// An iterator over all expansions of a structure.
pub struct CompleteStructureIter {
    inner: Mutex<structure::IntoIterCompleteStructure>,
}

#[pymethods]
impl CompleteStructureIter {
    /// Enables the skipping of values that would result in infinitely many expansions.
    ///
    /// This method modifies the iterator **inplace**, it just returns the current object to allow
    /// chaining.
    fn enable_skip_infinite(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf.get()
            .inner
            .lock_py_attached(slf.py())
            .unwrap()
            .mut_skip_infinite(true);
        slf
    }

    /// Disables the skipping of values that would result in infinitely many expansions.
    ///
    /// This method modifies the iterator **inplace**, it just returns the current object to allow
    /// chaining.
    fn disable_skip_infinite(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf.get()
            .inner
            .lock_py_attached(slf.py())
            .unwrap()
            .mut_skip_infinite(false);
        slf
    }

    /// Enables or disables skipping of infinite values based on the given boolean value.
    ///
    /// This method modifies the iterator **inplace**, it just returns the current object to allow
    /// chaining.
    fn skip_infinite(slf: Bound<'_, Self>, skip: bool) -> Bound<'_, Self> {
        slf.get()
            .inner
            .lock_py_attached(slf.py())
            .unwrap()
            .mut_skip_infinite(skip);
        slf
    }

    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn __next__(slf: Bound<'_, Self>) -> Option<Structure> {
        slf.get()
            .inner
            .lock_py_attached(slf.py())
            .unwrap()
            .next()
            .map(|f| Structure(InnerMut::new(f.into_partial().into_incomplete())))
    }
}

#[pyclass(frozen, generic)]
/// A pfunc interpretation.
pub struct PfuncInterp {
    name: Rc<str>,
    structure: Py<Structure>,
}

impl PfuncInterp {
    fn with_symbol_with_structure<
        'a,
        R,
        F: FnOnce(structure::partial::immutable::SymbolInterp<'a>) -> R,
    >(
        &self,
        structure: &'a structure::IncompleteStructure,
        f: F,
    ) -> PyResult<R> {
        let decl = structure.vocab_rc().parse_pfunc(&self.name).unwrap();
        Ok(f(structure
            .get(decl)
            .map_err(|f| PyRuntimeError::new_err(format!("{}", f)))?))
    }

    fn with_symbol_with_guard<
        'a,
        R,
        F: FnOnce(structure::partial::immutable::SymbolInterp<'a>) -> R,
    >(
        &self,
        structure: &'a InnerMutReadGuard<structure::IncompleteStructure>,
        f: F,
    ) -> PyResult<R> {
        self.with_symbol_with_structure(&structure, f)
    }

    fn with_symbol_py<R, F: FnOnce(structure::partial::immutable::SymbolInterp) -> R>(
        &self,
        py: Python,
        f: F,
    ) -> PyResult<R> {
        let structure = self.structure.get().0.get_py(py);
        self.with_symbol_with_guard(&structure, f)
    }

    fn with_mut_symbol_py<R, F: FnOnce(structure::partial::mutable::SymbolInterp) -> R>(
        &self,
        py: Python,
        f: F,
    ) -> PyResult<R> {
        let mut structure = self.structure.get().0.get_mut_py(py);
        let vocab = structure.vocab_rc().clone();
        let decl = vocab.parse_pfunc(&self.name).unwrap();
        Ok(f(structure
            .get_mut(decl)
            .map_err(|f| PyRuntimeError::new_err(format!("{}", f)))?))
    }

    fn opt_set_setup<
        R,
        F: FnOnce(ArgsRef, Option<TypeElement>, structure::partial::mutable::SymbolInterp) -> R,
    >(
        &self,
        args: &Bound<PyTuple>,
        value: &Bound<PyAny>,
        f: F,
    ) -> PyResult<R> {
        let mut structure = self.structure.get().0.get_mut_py(args.py());
        let vocab = structure.vocab_rc().clone();
        let decl = vocab.parse_pfunc(&self.name).unwrap();
        let interp = structure
            .get_mut(decl)
            .map_err(|f| PyRuntimeError::new_err(format!("{}", f)))?;
        let sli_args = py_tuple_to_args(&args, interp.domain_full())?;
        let value = if !value.is_none() {
            Some(pyobject_to_type_element(
                value.as_borrowed(),
                interp.codomain_full(),
            )?)
        } else {
            None
        };
        Ok(f(sli_args, value, interp))
    }

    fn set_setup<
        R,
        F: FnOnce(ArgsRef, TypeElement, structure::partial::mutable::SymbolInterp) -> R,
    >(
        &self,
        args: &Bound<PyTuple>,
        value: &Bound<PyAny>,
        f: F,
    ) -> PyResult<R> {
        let mut structure = self.structure.get().0.get_mut_py(args.py());
        let vocab = structure.vocab_rc().clone();
        let decl = vocab.parse_pfunc(&self.name).unwrap();
        let interp = structure
            .get_mut(decl)
            .map_err(|f| PyRuntimeError::new_err(format!("{}", f)))?;
        let sli_args = py_tuple_to_args(&args, interp.domain_full())?;
        let value = pyobject_to_type_element(value.as_borrowed(), interp.codomain_full())?;
        Ok(f(sli_args, value, interp))
    }

    fn get_py_codomain(&self, py: Python) -> PyResult<Py<PyType>> {
        use structure::TypeFull;
        self.with_symbol_py(py, |f| match f.codomain_full() {
            TypeFull::Bool => PyBool::type_object(py).unbind(),
            TypeFull::Int | TypeFull::IntType(_) => PyInt::type_object(py).unbind(),
            TypeFull::Real | TypeFull::RealType(_) => Real::type_object(py).unbind(),
            TypeFull::Str(_) => PyString::type_object(py).unbind(),
        })
    }
}

pub struct PyTupleToArgs<'a> {
    cur: usize,
    tuple: Borrowed<'a, 'a, PyTuple>,
    #[allow(unused)]
    domain_full: DomainFullRef<'a>,
}

impl<'a> PyTupleToArgs<'a> {
    pub fn new(tuple: Borrowed<'a, 'a, PyTuple>, domain_full: DomainFullRef<'a>) -> Self {
        Self {
            cur: 0,
            tuple,
            domain_full,
        }
    }
}

impl<'a> Iterator for PyTupleToArgs<'a> {
    type Item = PyResult<structure::TypeElement<'a>>;

    fn next(&mut self) -> Option<Self::Item> {
        let ret = if let Ok(value) = self.tuple.get_borrowed_item(self.cur) {
            if self.cur < self.domain_full.arity() {
                Some(pyobject_to_type_element(
                    value,
                    self.domain_full.get_ref(self.cur),
                ))
            } else {
                None
            }
        } else {
            None
        };
        self.cur += 1;
        ret
    }
}

pub fn py_tuple_to_args<'a>(
    args: &Bound<PyTuple>,
    domain_full: DomainFullRef<'a>,
) -> PyResult<ArgsRef<'a>> {
    let mut arg_builder = ArgsBuilder::new(domain_full.clone());
    let py_args = PyTupleToArgs::new(args.as_borrowed(), domain_full);
    for arg in py_args {
        arg_builder
            .add_argument(arg?)
            .map_err(|f| PyValueError::new_err(format!("{}", f)))?;
    }
    arg_builder
        .get_args()
        .map_err(|f| PyValueError::new_err(format!("{}", f)))
}

#[pymethods]
impl PfuncInterp {
    /// Get the interpretation's value for the given arguments.
    ///
    /// This class has a `__call__` function making it callable.
    /// Making it possible to emulate the application of a symbol.
    #[pyo3(signature = (*args))]
    fn get(&self, args: &Bound<'_, PyTuple>) -> PyResult<Py<PyAny>> {
        self.with_symbol_py(args.py(), |f| {
            let sli_args = py_tuple_to_args(args, f.domain_full())?;
            let result = f.get(sli_args).unwrap();
            opt_type_element_to_pyobject(args.py(), result)
        })
        .and_then(|f| f)
    }

    #[pyo3(signature = (*args))]
    fn __call__(&self, args: &Bound<'_, PyTuple>) -> PyResult<Py<PyAny>> {
        self.get(args)
    }

    /// Set the interpretation's value for the given arguments and the given value.
    fn set(
        slf: Bound<'_, Self>,
        args: Bound<'_, PyTuple>,
        value: Bound<'_, PyAny>,
    ) -> PyResult<()> {
        slf.get()
            .opt_set_setup(&args, &value, |args, value, mut f| {
                f.set(args, value)
                    .map_err(|f| PyValueError::new_err(format!("{}", f)))
            })
            .and_then(|f| f)
    }

    /// Set the interpretation's value for the given arguments and the given value if the current
    /// value is unknown.
    fn set_if_unknown(
        slf: Bound<'_, Self>,
        args: Bound<'_, PyTuple>,
        value: Bound<'_, PyAny>,
    ) -> PyResult<bool> {
        slf.get()
            .set_setup(&args, &value, |args, value, mut f| {
                f.set_if_unknown(args, value)
                    .map_err(|f| PyValueError::new_err(format!("{}", f)))
            })
            .and_then(|f| f)
    }

    /// Set all unknown values in the interpretation to the given value.
    fn set_all_unknown_to_value(slf: Bound<'_, Self>, value: Bound<'_, PyAny>) -> PyResult<()> {
        slf.get()
            .with_mut_symbol_py(slf.py(), |mut f| {
                let value = pyobject_to_type_element(value.as_borrowed(), f.codomain_full())?;
                f.set_all_unknown_to_value(value)
                    .map_err(|f| PyValueError::new_err(format!("{}", f)))
            })
            .and_then(|f| f)
    }

    /// Returns true if the interpretation is not empty.
    fn any_known(slf: &Bound<'_, Self>) -> PyResult<bool> {
        slf.get().with_symbol_py(slf.py(), |f| f.any_known())
    }

    /// Returns the amount of known values in the interpretation.
    fn amount_known(slf: &Bound<'_, Self>) -> PyResult<usize> {
        slf.get().with_symbol_py(slf.py(), |f| f.amount_known())
    }

    /// Returns the amount of arguments that have not been given an interpretation.
    fn amount_unknown(slf: &Bound<'_, Self>) -> PyResult<usize> {
        slf.get().with_symbol_py(slf.py(), |f| f.amount_unknown())
    }

    /// Returns the `Pfunc` of the interpretation.
    fn decl(slf: &Bound<'_, Self>) -> PyResult<Py<Pfunc>> {
        slf.get()
            .with_symbol_py(slf.py(), |f| {
                Python::attach(|py| {
                    let vocab = Py::new(py, slf.get().structure.get().vocab())?;
                    Pfunc::from_ref(f.decl(), vocab, py)
                })
            })
            .and_then(|f| f)
    }

    /// Returns the vocabulary of the pfunc.
    fn vocab(&self) -> Vocabulary {
        self.structure.get().vocab()
    }

    /// Returns the structure of the interpretation.
    fn structure(slf: Bound<'_, Self>) -> Py<Structure> {
        slf.get().structure.clone_ref(slf.py())
    }

    /// Returns the name of the pfunc.
    fn name(&self) -> &str {
        &self.name
    }

    /// Returns true if all the tuples in the domain have been given an interpretation.
    fn is_complete(slf: &Bound<'_, Self>) -> PyResult<bool> {
        slf.get().with_symbol_py(slf.py(), |f| f.is_complete())
    }

    fn __str__(slf: &Bound<'_, Self>) -> PyResult<String> {
        slf.get().with_symbol_py(slf.py(), |f| format!("{}", f))
    }

    fn _py_codomain(slf: Bound<'_, Self>) -> PyResult<Py<PyType>> {
        slf.get().get_py_codomain(slf.py())
    }

    fn __iter__(slf: Bound<'_, Self>) -> PyResult<PfuncInterpIter> {
        let inner = unsafe {
            InnerImIter::try_construct(
                slf.get().structure.clone_ref(slf.py()).bind(slf.py()),
                |f| {
                    let iter = slf
                        .get()
                        .with_symbol_with_structure(&*f, |f| Box::new(f.into_iter()))?;
                    // Safety:
                    // InnerMutIter guarantees a is never used after mutation occurs and may life for as long
                    // as slf.structure lives (which is just as long as InnerMutIter lives).
                    PyResult::Ok(core::mem::transmute::<
                        Box<dyn Iterator<Item = (ArgsRef, TypeElement)> + Send + Sync + '_>,
                        Box<
                            dyn Iterator<Item = (ArgsRef<'static>, TypeElement<'static>)>
                                + Send
                                + Sync
                                + 'static,
                        >,
                    >(iter))
                },
            )
        }?;
        Ok(PfuncInterpIter(inner, slf.get().name.clone()))
    }
}

#[pyclass(frozen, generic)]
pub struct PfuncInterpIter(
    InnerImIter<
        (ArgsRef<'static>, TypeElement<'static>),
        Structure,
        structure::IncompleteStructure,
    >,
    Rc<str>,
);

#[pymethods]
impl PfuncInterpIter {
    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn __next__(slf: Bound<'_, Self>) -> PyResult<Option<Py<PyTuple>>> {
        let iter = slf.get().0.aquire_iter(slf.py());
        iter.next()
            .map_err(|_| PyRuntimeError::new_err("underlying Structure changed during iteration"))?
            .map(|f| {
                let args = args_to_py_tuple(slf.py(), f.0)?;
                let value = type_element_to_pyobject(slf.py(), f.1)?;
                PyTuple::new(slf.py(), [args.into_any().unbind(), value]).map(|f| f.unbind())
            })
            .transpose()
    }

    fn _py_codomain(slf: Bound<'_, Self>) -> PyResult<Py<PyType>> {
        PfuncInterp {
            name: slf.get().1.clone(),
            structure: slf.get().0.holder().clone_ref(slf.py()),
        }
        .get_py_codomain(slf.py())
    }
}

#[pyclass(frozen)]
/// Represents a model of a theory.
pub struct Model(pub(crate) structure::Model);

impl Model {
    pub(crate) fn construct(model: structure::Model) -> Self {
        Self(model)
    }
}

#[pymethods]
impl Model {
    fn __str__(&self) -> String {
        format!("{}", self.0)
    }

    /// Returns the vocabulary of model.
    fn vocab(&self) -> Vocabulary {
        Vocabulary(InnerMut::new(self.0.as_ref().vocab_rc().clone()))
    }

    fn __getitem__(slf: Bound<'_, Self>, pfunc: Bound<'_, PyAny>) -> PyResult<ModelPfuncInterp> {
        let name = {
            let vocab = &slf.get().0;
            let decl = convert_pfunc_from_python_ref(pfunc.as_borrowed(), vocab.as_ref().vocab())?;
            decl.name_rc().clone()
        };
        Ok(ModelPfuncInterp {
            name,
            model: slf.unbind(),
        })
    }

    /// Returns the model as a structure.
    fn into_structure(&self) -> Structure {
        Structure(InnerMut::new(
            self.0.clone().into_partial().into_incomplete(),
        ))
    }
}

#[pyclass(frozen, generic)]
pub struct ModelPfuncInterp {
    name: Rc<str>,
    model: Py<Model>,
}

impl ModelPfuncInterp {
    fn with_symbol_with_model<
        'a,
        R,
        F: FnOnce(structure::complete::immutable::SymbolInterp<'a>) -> R,
    >(
        &self,
        structure: &'a structure::Model,
        f: F,
    ) -> R {
        let decl = structure.as_ref().vocab().parse_pfunc(&self.name).unwrap();
        f(structure.as_ref().get(decl))
    }

    fn with_symbol<R, F: FnOnce(structure::complete::immutable::SymbolInterp) -> R>(
        &self,
        f: F,
    ) -> R {
        let structure = &self.model.get().0;
        self.with_symbol_with_model(structure, f)
    }

    fn get_py_codomain(&self, py: Python) -> Py<PyType> {
        use structure::TypeFull;
        self.with_symbol(|f| match f.codomain_full() {
            TypeFull::Bool => PyBool::type_object(py).unbind(),
            TypeFull::Int | TypeFull::IntType(_) => PyInt::type_object(py).unbind(),
            TypeFull::Real | TypeFull::RealType(_) => Real::type_object(py).unbind(),
            TypeFull::Str(_) => PyString::type_object(py).unbind(),
        })
    }
}

#[pymethods]
impl ModelPfuncInterp {
    /// Get the interpretation's value for the given arguments.
    ///
    /// This class has a `__call__` function making it callable.
    /// Making it possible to emulate the application of a symbol.
    #[pyo3(signature = (*args))]
    fn get(&self, args: &Bound<'_, PyTuple>) -> PyResult<Py<PyAny>> {
        self.with_symbol(|f| {
            let sli_args = py_tuple_to_args(args, f.domain_full())?;
            let result = f.get(sli_args).unwrap();
            type_element_to_pyobject(args.py(), result)
        })
    }

    #[pyo3(signature = (*args))]
    fn __call__(&self, args: &Bound<'_, PyTuple>) -> PyResult<Py<PyAny>> {
        self.get(args)
    }

    /// Returns the `Pfunc` of the interpretation.
    fn decl(&self) -> PyResult<Py<Pfunc>> {
        self.with_symbol(|f| {
            Python::attach(|py| {
                let vocab = Py::new(py, self.model.get().vocab())?;
                Pfunc::from_ref(f.decl(), vocab, py)
            })
        })
    }

    /// Returns the vocabulary of the pfunc.
    fn vocab(&self) -> Vocabulary {
        self.model.get().vocab()
    }

    /// Returns the model of the interpretation.
    fn model(slf: Bound<'_, Self>) -> Py<Model> {
        slf.get().model.clone_ref(slf.py())
    }

    /// Returns the name of the pfunc.
    fn name(&self) -> &str {
        &self.name
    }

    fn __str__(&self) -> String {
        self.with_symbol(|f| format!("{}", f))
    }

    fn _py_codomain(slf: Bound<'_, Self>) -> Py<PyType> {
        slf.get().get_py_codomain(slf.py())
    }

    fn __iter__(slf: Bound<'_, Self>) -> ModelPfuncInterpIter {
        let value = slf.borrow();
        let guard = &value.model.get().0;
        let a = slf.get().with_symbol_with_model(guard, |f| {
            let a: Box<dyn Iterator<Item = (ArgsRef, TypeElement)> + Send + Sync> =
                Box::new(f.into_iter());
            // Safety:
            // InnerMutIter guarantees a is never used after mutation occurs and may life for as long
            // as slf lives (which is just as long as InnerMutIter lives).
            unsafe {
                core::mem::transmute::<
                    Box<dyn Iterator<Item = (ArgsRef, TypeElement)> + Send + Sync + '_>,
                    Box<
                        dyn Iterator<Item = (ArgsRef<'static>, TypeElement<'static>)>
                            + Send
                            + Sync
                            + 'static,
                    >,
                >(a)
            }
        });
        unsafe {
            ModelPfuncInterpIter::new_extended(
                slf.get().name.clone(),
                a,
                slf.get().model.clone_ref(slf.py()),
            )
        }
    }
}

#[pyclass(frozen, generic)]
pub struct ModelPfuncInterpIter {
    name: Rc<str>,
    inner: Mutex<
        NonNull<
            dyn Iterator<Item = (ArgsRef<'static>, TypeElement<'static>)> + Sync + Send + 'static,
        >,
    >,
    // Field required so we don't drop Model when iterating.
    #[allow(unused)]
    model: Py<Model>,
}

impl ModelPfuncInterpIter {
    unsafe fn new_extended<'a>(
        name: Rc<str>,
        inner: Box<
            dyn Iterator<Item = (ArgsRef<'static>, TypeElement<'static>)> + Sync + Send + 'a,
        >,
        model: Py<Model>,
    ) -> Self {
        Self {
            name,
            inner: Mutex::new(
                NonNull::new(Box::into_raw(inner)
                    as *mut (
                        dyn Iterator<Item = (ArgsRef<'static>, TypeElement<'static>)>
                            + Sync
                            + Send
                            + 'static
                    ))
                .unwrap(),
            ),
            model,
        }
    }
}

// Safety:
// This is safe since all fields are Sync and Send, and GlobModel is immutable.
unsafe impl Sync for ModelPfuncInterpIter {}
// Safety:
// This is safe since all fields are Sync and Send, and GlobModel is immutable.
unsafe impl Send for ModelPfuncInterpIter {}

#[pymethods]
impl ModelPfuncInterpIter {
    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn __next__(slf: Bound<'_, Self>) -> PyResult<Option<Py<PyTuple>>> {
        unsafe { slf.get().inner.lock_py_attached(slf.py()).unwrap().as_mut() }
            .next()
            .map(|f| {
                let args = args_to_py_tuple(slf.py(), f.0)?;
                let value = type_element_to_pyobject(slf.py(), f.1)?;
                PyTuple::new(slf.py(), [args.into_any().unbind(), value]).map(|f| f.unbind())
            })
            .transpose()
    }

    fn _py_codomain(slf: Bound<'_, Self>) -> Py<PyType> {
        ModelPfuncInterp {
            name: slf.get().name.clone(),
            model: slf.get().model.clone_ref(slf.py()),
        }
        .get_py_codomain(slf.py())
    }
}

impl Drop for ModelPfuncInterpIter {
    fn drop(&mut self) {
        // Even if we poisoned the lock we allocation is still ok and should be cleaned up,
        // See https://doc.rust-lang.org/nomicon/poisoning.html
        let ptr = self
            .inner
            .get_mut()
            .unwrap_or_else(|e| e.into_inner())
            .as_ptr();
        // Safety:
        // The pointer was created from a into_raw call
        drop(unsafe { Box::from_raw(ptr) })
    }
}

#[pyclass(frozen)]
/// Represents a set of models of a theory as a partial structure.
pub struct GlobModel(pub(crate) structure::GlobModel);

impl GlobModel {
    pub(crate) fn construct(model: structure::GlobModel) -> Self {
        Self(model)
    }
}

#[pymethods]
impl GlobModel {
    fn __str__(&self) -> String {
        format!("{}", self.0)
    }

    /// Returns the vocabulary of this glob model.
    fn vocab(&self) -> Vocabulary {
        Vocabulary(InnerMut::new(self.0.as_ref().vocab_rc().clone()))
    }

    fn __getitem__(
        slf: Bound<'_, Self>,
        pfunc: Bound<'_, PyAny>,
    ) -> PyResult<GlobModelPfuncInterp> {
        let name = {
            let vocab = &slf.get().0;
            let decl = convert_pfunc_from_python_ref(pfunc.as_borrowed(), vocab.as_ref().vocab())?;
            decl.name_rc().clone()
        };
        Ok(GlobModelPfuncInterp {
            name,
            structure: slf.unbind(),
        })
    }

    /// Returns an iterator over all complete structure as models that are an expansion of this
    /// partial structure.
    fn iter_models(slf: Bound<'_, Self>) -> CompleteModelIter {
        CompleteModelIter {
            inner: Mutex::new(slf.get().0.clone().into_iter_models()),
        }
    }

    /// Returns this as a structure.
    fn into_structure(&self) -> Structure {
        Structure(InnerMut::new(
            structure::PartialStructure::from(self.0.clone()).into_incomplete(),
        ))
    }
}

#[pyclass(frozen)]
pub struct CompleteModelIter {
    inner: Mutex<structure::IntoIterCompleteModel>,
}

#[pymethods]
impl CompleteModelIter {
    fn enable_skip_infinite(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf.get()
            .inner
            .lock_py_attached(slf.py())
            .unwrap()
            .mut_skip_infinite(true);
        slf
    }

    fn disable_skip_infinite(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf.get()
            .inner
            .lock_py_attached(slf.py())
            .unwrap()
            .mut_skip_infinite(false);
        slf
    }

    fn skip_infinite(slf: Bound<'_, Self>, skip: bool) -> Bound<'_, Self> {
        slf.get()
            .inner
            .lock_py_attached(slf.py())
            .unwrap()
            .mut_skip_infinite(skip);
        slf
    }

    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn __next__(slf: Bound<'_, Self>) -> Option<Model> {
        slf.get()
            .inner
            .lock_py_attached(slf.py())
            .unwrap()
            .next()
            .map(|f| Model(f))
    }
}

#[pyclass(frozen, generic)]
pub struct GlobModelPfuncInterp {
    name: Rc<str>,
    structure: Py<GlobModel>,
}

impl GlobModelPfuncInterp {
    fn with_symbol_with_guard<
        'a,
        R,
        F: FnOnce(structure::partial::immutable::SymbolInterp<'a>) -> R,
    >(
        &self,
        structure: &'a structure::GlobModel,
        f: F,
    ) -> R {
        let decl = structure
            .as_ref()
            .vocab_rc()
            .parse_pfunc(&self.name)
            .unwrap();
        f(structure.as_ref().get(decl))
    }

    fn with_symbol<R, F: FnOnce(structure::partial::immutable::SymbolInterp) -> R>(
        &self,
        f: F,
    ) -> R {
        let structure = &self.structure.get().0;
        self.with_symbol_with_guard(structure, f)
    }

    fn get_py_codomain(&self, py: Python) -> Py<PyType> {
        use structure::TypeFull;
        self.with_symbol(|f| match f.codomain_full() {
            TypeFull::Bool => PyBool::type_object(py).unbind(),
            TypeFull::Int | TypeFull::IntType(_) => PyInt::type_object(py).unbind(),
            TypeFull::Real | TypeFull::RealType(_) => Real::type_object(py).unbind(),
            TypeFull::Str(_) => PyString::type_object(py).unbind(),
        })
    }
}

#[pymethods]
impl GlobModelPfuncInterp {
    /// Get the interpretation's value for the given arguments.
    ///
    /// This class has a `__call__` function making it callable.
    /// Making it possible to emulate the application of a symbol.
    #[pyo3(signature = (*args))]
    fn get(&self, args: &Bound<'_, PyTuple>) -> PyResult<Py<PyAny>> {
        self.with_symbol(|f| {
            let sli_args = py_tuple_to_args(args, f.domain_full())?;
            let result = f.get(sli_args).unwrap();
            opt_type_element_to_pyobject(args.py(), result)
        })
    }

    #[pyo3(signature = (*args))]
    fn __call__(&self, args: &Bound<'_, PyTuple>) -> PyResult<Py<PyAny>> {
        self.get(args)
    }

    /// Returns true if the interpretation is not empty.
    fn any_known(&self) -> bool {
        self.with_symbol(|f| f.any_known())
    }

    /// Returns the amount of known values in the interpretation.
    fn amount_known(&self) -> usize {
        self.with_symbol(|f| f.amount_known())
    }

    /// Returns the amount of that have not been given an interpretation, compared to the pfuncs
    /// domain.
    fn amount_unknown(&self) -> usize {
        self.with_symbol(|f| f.amount_unknown())
    }

    /// Returns the `Pfunc` of the interpretation.
    fn decl(&self) -> PyResult<Py<Pfunc>> {
        self.with_symbol(|f| {
            Python::attach(|py| {
                let vocab = Py::new(py, self.structure.get().vocab())?;
                Pfunc::from_ref(f.decl(), vocab, py)
            })
        })
    }

    /// Returns the vocabulary of the pfunc.
    fn vocab(&self) -> Vocabulary {
        self.structure.get().vocab()
    }

    /// Returns the glob model of the interpretation.
    fn glob_model(slf: Bound<'_, Self>) -> Py<GlobModel> {
        slf.get().structure.clone_ref(slf.py())
    }

    /// Returns the name of the pfunc.
    fn name(&self) -> &str {
        &self.name
    }

    /// Returns true if all the tuples in the domain have been given an interpretation.
    fn is_complete(&self) -> bool {
        self.with_symbol(|f| f.is_complete())
    }

    fn __str__(&self) -> String {
        self.with_symbol(|f| format!("{}", f))
    }

    fn _py_codomain(slf: Bound<'_, Self>) -> Py<PyType> {
        slf.get().get_py_codomain(slf.py())
    }

    fn __iter__(slf: Bound<'_, Self>) -> GlobModelPfuncInterpIter {
        let value = slf.borrow();
        let guard = &value.structure.get().0;
        let a = slf.get().with_symbol_with_guard(guard, |f| {
            let a: Box<dyn Iterator<Item = (ArgsRef, TypeElement)> + Send + Sync> =
                Box::new(f.into_iter());
            // Safety:
            // InnerMutIter guarantees a is never used after mutation occurs and may life for as long
            // as slf lives (which is just as long as InnerMutIter lives).
            unsafe {
                core::mem::transmute::<
                    Box<dyn Iterator<Item = (ArgsRef, TypeElement)> + Send + Sync + '_>,
                    Box<
                        dyn Iterator<Item = (ArgsRef<'static>, TypeElement<'static>)>
                            + Send
                            + Sync
                            + 'static,
                    >,
                >(a)
            }
        });
        unsafe {
            GlobModelPfuncInterpIter::new_extended(
                slf.get().name.clone(),
                a,
                slf.get().structure.clone_ref(slf.py()),
            )
        }
    }
}

#[pyclass(frozen, generic)]
pub struct GlobModelPfuncInterpIter {
    name: Rc<str>,
    inner: Mutex<
        NonNull<
            dyn Iterator<Item = (ArgsRef<'static>, TypeElement<'static>)> + Sync + Send + 'static,
        >,
    >,
    // Field required so we don't drop GlobModel when iterating.
    #[allow(unused)]
    glob_model: Py<GlobModel>,
}

impl GlobModelPfuncInterpIter {
    unsafe fn new_extended<'a>(
        name: Rc<str>,
        inner: Box<
            dyn Iterator<Item = (ArgsRef<'static>, TypeElement<'static>)> + Sync + Send + 'a,
        >,
        glob_model: Py<GlobModel>,
    ) -> Self {
        Self {
            name,
            inner: Mutex::new(
                NonNull::new(Box::into_raw(inner)
                    as *mut (
                        dyn Iterator<Item = (ArgsRef<'static>, TypeElement<'static>)>
                            + Sync
                            + Send
                            + 'static
                    ))
                .unwrap(),
            ),
            glob_model,
        }
    }
}

// Safety:
// This is safe since all fields are Sync and Send, and GlobModel is immutable.
unsafe impl Sync for GlobModelPfuncInterpIter {}
// Safety:
// This is safe since all fields are Sync and Send, and GlobModel is immutable.
unsafe impl Send for GlobModelPfuncInterpIter {}

#[pymethods]
impl GlobModelPfuncInterpIter {
    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn __next__(slf: Bound<'_, Self>) -> PyResult<Option<Py<PyTuple>>> {
        unsafe { slf.get().inner.lock_py_attached(slf.py()).unwrap().as_mut() }
            .next()
            .map(|f| {
                let args = args_to_py_tuple(slf.py(), f.0)?;
                let value = type_element_to_pyobject(slf.py(), f.1)?;
                PyTuple::new(slf.py(), [args.into_any().unbind(), value]).map(|f| f.unbind())
            })
            .transpose()
    }

    fn _py_codomain(slf: Bound<'_, Self>) -> Py<PyType> {
        GlobModelPfuncInterp {
            name: slf.get().name.clone(),
            structure: slf.get().glob_model.clone_ref(slf.py()),
        }
        .get_py_codomain(slf.py())
    }
}

impl Drop for GlobModelPfuncInterpIter {
    fn drop(&mut self) {
        // Even if we poisoned the lock we allocation is still ok and should be cleaned up
        // See https://doc.rust-lang.org/nomicon/poisoning.html
        let ptr = self
            .inner
            .get_mut()
            .unwrap_or_else(|e| e.into_inner())
            .as_ptr();
        // Safety:
        // The pointer was created from a into_raw call
        drop(unsafe { Box::from_raw(ptr) })
    }
}

pub(crate) fn get_interp(
    custom_type: CustomTypeRef,
    type_interps: &PartialTypeInterps,
    py: Python,
) -> PyResult<Py<PyAny>> {
    type_interps
        .get_interp_cloned(custom_type)
        .map_err(|f| PyValueError::new_err(format!("{}", f)))
        .and_then(|f| {
            Ok(match f {
                None => PyNone::get(py).as_any().clone().unbind(),
                Some(TypeInterp::Int(value)) => {
                    Py::new(py, IntInterp::construct(value))?.into_any()
                }
                Some(TypeInterp::Real(value)) => {
                    Py::new(py, RealInterp::construct(value))?.into_any()
                }
                Some(TypeInterp::Str(value)) => {
                    Py::new(py, StrInterp::construct(value))?.into_any()
                }
            })
        })
}

pub fn submodule(py: Python) -> PyResult<Bound<'_, PyModule>> {
    let m = PyModule::new(py, "structure")?;
    m.gil_used(false)?;
    m.add_class::<Structure>()?;
    m.add_class::<PfuncInterp>()?;
    m.add_class::<PfuncInterpIter>()?;
    m.add_class::<CompleteStructureIter>()?;
    m.add_class::<GlobModel>()?;
    m.add_class::<GlobModelPfuncInterp>()?;
    m.add_class::<GlobModelPfuncInterpIter>()?;
    m.add_class::<CompleteModelIter>()?;
    m.add_class::<Model>()?;
    m.add_class::<ModelPfuncInterp>()?;
    m.add_class::<ModelPfuncInterpIter>()?;
    m.add_class::<IntInterp>()?;
    m.add_class::<IntInterpIter>()?;
    m.add_class::<RealInterp>()?;
    m.add_class::<RealInterpIter>()?;
    m.add_class::<StrInterp>()?;
    m.add_class::<StrInterpIter>()?;
    Ok(m)
}
