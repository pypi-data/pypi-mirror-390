use std::ops::DerefMut;

use crate::{
    fodot::{
        structure::{GlobModel, Model, Structure},
        theory::Theory,
    },
    interior_mut::{InnerMut, InnerMutIter},
};
use pyo3::{exceptions::PyRuntimeError, prelude::*};
use sli_lib::{
    fodot::structure,
    solver::{self, SatResult, Solver, SolverIter},
};

#[pyclass(frozen)]
/// A solver using Z3.
pub struct Z3Solver {
    inner: InnerMut<solver::Z3Solver<'static>>,
    // inner references this Theory object on python heap,
    // make sure this is dropped last
    // TODO: make this Theory object immutable (i.e. copy on write).
    pytheory: Py<Theory>,
}

impl AsRef<InnerMut<solver::Z3Solver<'static>>> for Z3Solver {
    fn as_ref(&self) -> &InnerMut<solver::Z3Solver<'static>> {
        &self.inner
    }
}

#[pymethods]
impl Z3Solver {
    #[new]
    fn new(theory: Bound<'_, Theory>) -> Self {
        let theory_ptr: *const _ = &theory.get().0;
        Self {
            // Safety:
            // This is safe since theory is guaranteed to not be deallocated whilst inner still
            // lives and also not mutated.
            inner: InnerMut::new(solver::Z3Solver::initialize(unsafe {
                theory_ptr.as_ref().unwrap()
            })),
            pytheory: theory.unbind(),
        }
    }

    /// Returns the theory bound to this solver.
    fn theory(slf: Bound<'_, Self>) -> Py<Theory> {
        slf.borrow().pytheory.clone_ref(slf.py())
    }

    /// Checks satisfiability of the given theory.
    fn check<'a>(&self, py: Python<'a>) -> Bound<'a, PyAny> {
        match py.detach(|| InnerMut::get_mut(&self.inner).check()) {
            SatResult::Sat => sat_result(py),
            SatResult::Unsat => unsat_result(py),
            SatResult::Unknown => unknown_result(py),
        }
    }

    /// Returns the current model of the solver.
    fn get_model(&self, py: Python) -> Option<GlobModel> {
        py.detach(|| {
            let mut guard = InnerMut::get_mut(&self.inner);
            guard.check();
            guard.get_model()
        })
        .map(|f| GlobModel::construct(f))
    }

    /// Does backbone propagation on the current state of the solver.
    fn propagate(&self, py: Python) -> Option<Structure> {
        py.detach(|| InnerMut::get_mut(&self.inner).propagate())
            .map(|f| Structure::construct(f.into()))
    }

    /// Skips infinite values by default.
    fn iter_glob_models(slf: Bound<'_, Self>) -> Z3GlobModelIterator {
        Z3GlobModelIterator(
            // Safety:
            // the returned iterator only references of the first argument.
            unsafe {
                InnerMutIter::construct(&slf, |value| {
                    // Safety: InnererMutIter ensure we are the only ones that can mutably
                    // acces slf, for as long as the iterator isn't invalidated.
                    // And it lives for as long as this iterator lives.
                    core::mem::transmute::<
                        solver::ModelIterator<'_, '_, solver::Z3Solver<'_>>,
                        solver::ModelIterator<'static, 'static, solver::Z3Solver<'static>>,
                    >(value.iter_models())
                })
            },
        )
    }

    /// Skips infinite values by default.
    fn iter_models(slf: Bound<'_, Self>) -> Z3ModelIterator {
        Z3ModelIterator(
            // Safety:
            // the returned iterator only references of the first argument.
            unsafe {
                InnerMutIter::construct(&slf, |value| {
                    // Safety: InnererMutIter ensure we are the only ones that can mutably
                    // acces slf, for as long as the iterator isn't invalidated.
                    // And it lives for as long as this iterator lives.
                    core::mem::transmute::<
                        solver::CompleteModelIterator<'_, '_, solver::Z3Solver<'_>>,
                        solver::CompleteModelIterator<'static, 'static, solver::Z3Solver<'static>>,
                    >(value.iter_models().complete())
                })
            },
        )
    }
}

#[pyclass(frozen)]
/// An iterator over glob models.
///
/// This iterator modifies the solver state at each iteration!
/// This iterator gets invalidated if any other state operation happens on the original solver.
pub struct Z3GlobModelIterator(
    InnerMutIter<
        structure::GlobModel,
        Z3Solver,
        solver::Z3Solver<'static>,
        solver::ModelIterator<'static, 'static, solver::Z3Solver<'static>>,
    >,
);

#[pymethods]
impl Z3GlobModelIterator {
    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn __next__(slf: Bound<'_, Self>) -> PyResult<Option<GlobModel>> {
        slf.get()
            .0
            .aquire_iter(slf.py())
            .next_detached()
            .map(|f| f.map(|model| GlobModel::construct(model)))
            .map_err(|_| PyRuntimeError::new_err("underlying Z3Solver changed during iteration"))
    }
}

#[pyclass(frozen)]
/// An iterator over models.
///
/// This iterator modifies the solver state at each iteration!
/// This iterator gets invalidated if any other state operation happens on the original solver.
///
/// This is roughly equivalent to the following example, but still providing the ability to turn on
/// or off the skipping of infinite values, and all from Rust.
///
/// ```python
/// from sli_lib.fodot.structure import Model
/// from sli_lib.solver import Z3GlobModelIterator
/// from itertools import chain
/// from typing import Iterator
///
/// def iter_models(iter: Z3GlobModelIterator) -> Iterator[Model]:
///     return chain.chain_from_iterable(map(lambda x: x.iter_models(), iter))
/// ```
pub struct Z3ModelIterator(
    InnerMutIter<
        structure::Model,
        Z3Solver,
        solver::Z3Solver<'static>,
        solver::CompleteModelIterator<'static, 'static, solver::Z3Solver<'static>>,
    >,
);

#[pymethods]
impl Z3ModelIterator {
    fn __iter__(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf
    }

    fn __next__(slf: Bound<'_, Self>) -> PyResult<Option<Model>> {
        slf.get()
            .0
            .aquire_iter(slf.py())
            .next_detached()
            .map(|f| f.map(|model| Model::construct(model)))
            .map_err(|_| PyRuntimeError::new_err("underlying Z3Solver changed during iteration"))
    }

    /// Enables the skipping of values that would result in infinitely many expansions.
    ///
    /// This method modifies the iterator **inplace**, it just returns the current object to allow
    /// chaining.
    fn enable_skip_infinite(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf.get()
            .0
            .aquire_iter(slf.py())
            .inner_mut()
            .deref_mut()
            .as_mut()
            .map(|f| f.mut_enable_skip_infinite());
        slf
    }

    /// Disables the skipping of values that would result in infinitely many expansions.
    ///
    /// This method modifies the iterator **inplace**, it just returns the current object to allow
    /// chaining.
    fn disable_skip_infinite(slf: Bound<'_, Self>) -> Bound<'_, Self> {
        slf.get()
            .0
            .aquire_iter(slf.py())
            .inner_mut()
            .deref_mut()
            .as_mut()
            .map(|f| f.mut_disable_skip_infinite());
        slf
    }

    /// Enables or disables skipping of infinite values based on the given boolean value.
    ///
    /// This method modifies the iterator **inplace**, it just returns the current object to allow
    /// chaining.
    fn skip_infinite(slf: Bound<'_, Self>, skip: bool) -> Bound<'_, Self> {
        slf.get()
            .0
            .aquire_iter(slf.py())
            .inner_mut()
            .deref_mut()
            .as_mut()
            .map(|f| f.mut_skip_infinite(skip));
        slf
    }
}

pub fn sat_result(py: Python) -> Bound<PyAny> {
    py.import("sli_lib.solver")
        .unwrap()
        .getattr("SatResult")
        .unwrap()
        .getattr("SAT")
        .unwrap()
}

pub fn unsat_result(py: Python) -> Bound<PyAny> {
    py.import("sli_lib.solver")
        .unwrap()
        .getattr("SatResult")
        .unwrap()
        .getattr("UNSAT")
        .unwrap()
}

pub fn unknown_result(py: Python) -> Bound<PyAny> {
    py.import("sli_lib.solver")
        .unwrap()
        .getattr("SatResult")
        .unwrap()
        .getattr("UNKNOWN")
        .unwrap()
}

pub fn submodule(py: Python) -> PyResult<Bound<'_, PyModule>> {
    let m = PyModule::new(py, "_solver")?;
    m.gil_used(false)?;
    m.add_class::<Z3Solver>()?;
    m.add_class::<Z3GlobModelIterator>()?;
    m.add_class::<Z3ModelIterator>()?;
    Ok(m)
}
