//! This module contains datastructures for representing comp core expressions.
//! The ideas here are good, but everything should be a bit more understandable.
//! i.e. this module should be rewritten in the near future.
use super::VariableValue;
use crate::{
    comp_core::{
        IndexRange, IndexRepr,
        constraints::{BoundVarId, ExtraIndex, NodeIndex, ToConstraint, ToNodeArgs},
        create_index,
        node::{Node, NodeEnum, Variables},
        structure::{
            DomainEnumBuilder, DomainEnumSingleVar, TypeElement, TypeEnumIter, TypeInterps,
            partial::{immutable, mutable, owned},
            traits::partial::SetInterps,
        },
        vocabulary::{
            DomainEnum, DomainIndex, DomainSlice, PfuncIndex, SymbolFull, Type, TypeEnum,
            Vocabulary,
        },
    },
    interp_structures::{InterpContext, LayoutSatSet, LayoutVec},
    node::ExprType,
    structure::{
        PartialStructure,
        backend::{self, indexes::PredIndex},
    },
};
use sli_collections::{hash_map::IdHashMap, rc::Rc};
use std::{
    fmt::Debug,
    ops::{ControlFlow, Range},
    slice::Iter,
};
use typed_index_collections::TiVec;

pub type Nodes = TiVec<NodeIndex, Node>;
pub type Extra = TiVec<ExtraIndex, IndexRepr>;
pub type PfuncMap = IdHashMap<NodeIndex, PfuncIndex>;
pub type AuxMap = IdHashMap<NodeIndex, AuxIndex>;
pub type TypeMap = IdHashMap<BoundVarId, Type>;

create_index!(AuxIndex, "Index for auxiliary symbols.");

impl AuxIndex {
    pub(crate) fn to_pfunc_index(self) -> PfuncIndex {
        PfuncIndex(self.into())
    }

    #[allow(unused)]
    pub(crate) fn from_func_index(value: PfuncIndex) -> AuxIndex {
        AuxIndex(value.into())
    }
}

/// Container for comp core expressions.
///
/// ## Internal
///
/// These fields might seems haphazardly chosen, and that is because they have been.
/// The main reason for using this instead of keeping a vector of some mutation of
/// [NodeEnums](NodeEnum) is because a [NodeEnum] is heavily padded which can cause large amounts of
/// memory to be lost when storing large amounts of it.
#[derive(Debug, Clone)]
pub struct Expressions {
    /// A vector of [Nodes](Node).
    nodes: Nodes,
    /// Any extra information a node in the AST needs will be inserted here.
    /// This information is type erased so requires unsafe to extract back.
    extra: Extra,
    /// A map for any node that requires knowledge of a [PfuncIndex].
    pfunc_map: PfuncMap,
    /// A map for any node that requires knowledge of an [AuxIndex].
    aux_map: AuxMap,
    /// Maps types to variables.
    type_map: TypeMap,
    bound_var_amount: usize,
    quant_elements: IdHashMap<NodeIndex, IDomainPredicate>,
    aux_symbols: AuxSymbols,
}

impl Expressions {
    pub fn new(type_interps: Rc<TypeInterps>) -> Self {
        Self {
            nodes: Nodes::new(),
            extra: Extra::new(),
            pfunc_map: Default::default(),
            aux_map: Default::default(),
            type_map: Default::default(),
            bound_var_amount: 0,
            quant_elements: Default::default(),
            aux_symbols: AuxSymbols::new(type_interps),
        }
    }

    pub fn clear(&mut self) {
        self.nodes.clear();
        self.extra.clear();
        self.pfunc_map.clear();
        self.aux_map.clear();
        self.type_map.clear();
        self.quant_elements.clear();
        self.aux_symbols.clear();
    }

    pub fn iter_funcs_map<'a>(&'a self) -> impl Iterator<Item = (NodeIndex, PfuncIndex)> + 'a {
        self.pfunc_map.iter().map(|d| (*d.0, *d.1))
    }

    pub fn get_type_map(&self) -> &TypeMap {
        &self.type_map
    }

    pub fn get_type_map_mut(&mut self) -> &mut TypeMap {
        &mut self.type_map
    }

    pub fn as_type_element(&self, index: NodeIndex) -> Option<TypeElement> {
        match self.to_expression(index).first_node_enum() {
            NodeEnum::Element(el) => el.try_into().ok(),
            _ => None,
        }
    }

    pub fn as_bool(&self, index: NodeIndex) -> Option<bool> {
        match self.as_type_element(index)? {
            TypeElement::Bool(b) => Some(b),
            _ => None,
        }
    }

    #[inline(always)]
    pub fn in_quant_domain(&self, var: NodeIndex, el: DomainEnum) -> bool {
        match self.quant_elements_get(var) {
            None => true,
            Some(bv) => bv.contains(el),
        }
    }

    pub fn new_bound_var(&mut self) -> BoundVarId {
        let new = self.bound_var_amount;
        self.bound_var_amount += 1;
        new.into()
    }

    pub(in crate::comp_core) fn set_bound_var_start(&mut self, start: BoundVarId) {
        self.bound_var_amount = start.into();
    }

    pub(in crate::comp_core) fn cur_bound_var(&self) -> BoundVarId {
        self.bound_var_amount.into()
    }

    pub(in crate::comp_core) fn push_node<T>(&mut self, mut node: T) -> NodeIndex
    where
        T: ToConstraint,
    {
        let sub_id = node.sub_node().map(|f| self.push_node(f));
        let children = node.children();
        self.extra.reserve(children.len());
        let mut children_ids = children
            .into_vec()
            .into_iter()
            .map(|child| IndexRepr::from(self.push_node(child)))
            .collect();
        let extra_index = self.extra.len();
        self.extra.append(&mut children_ids);
        let extra_children = node.extra_children();
        self.extra.extend(extra_children.iter().copied());
        let index = self.nodes.len().into();
        if let Some(pfunc_index) = node.to_pfunc_map() {
            self.pfunc_map.insert(index, pfunc_index);
        }
        if let Some(aux_index) = node.to_aux_map() {
            self.aux_map.insert(index, aux_index);
        }
        for (var, type_e) in node.to_type_map() {
            self.type_map.insert(*var, *type_e);
        }
        if let Some(quant_el) = node.quant_elements() {
            self.quant_elements_insert(index, quant_el);
        }

        let to_node_args = ToNodeArgs {
            extra_len: extra_index,
            sub: sub_id,
        };
        self.nodes.push(node.to_node(to_node_args));
        index
    }

    pub fn quant_elements(&self, index: NodeIndex) -> &IDomainPredicate {
        &self.quant_elements[&index]
    }

    pub fn quant_elements_get(&self, index: NodeIndex) -> Option<&IDomainPredicate> {
        self.quant_elements.get(&index)
    }

    pub fn quant_elements_insert(
        &mut self,
        index: NodeIndex,
        dom_pred: IDomainPredicate,
    ) -> Option<IDomainPredicate> {
        self.quant_elements.insert(index, dom_pred)
    }

    pub fn quant_elements_remove(&mut self, index: NodeIndex) -> Option<IDomainPredicate> {
        self.quant_elements.remove(&index)
    }

    pub fn to_expression(&self, start: NodeIndex) -> ExpressionRef {
        ExpressionRef::new(self, start)
    }

    pub fn new_at(&self, start: NodeIndex) -> ExpressionRef {
        self.to_expression(start)
    }

    pub fn nodes(&self, index: NodeIndex) -> &Node {
        &self.nodes[index]
    }

    pub fn extra(&self, index: ExtraIndex) -> IndexRepr {
        self.extra[index]
    }

    pub fn extra_slice<'a>(&'a self, range: Range<ExtraIndex>) -> &'a [IndexRepr] {
        self.extra[range].as_ref()
    }

    pub fn pfunc_map(&self, index: NodeIndex) -> PfuncIndex {
        self.pfunc_map[&index]
    }

    pub fn aux_map(&self, index: NodeIndex) -> AuxIndex {
        self.aux_map[&index]
    }

    pub fn type_map(&self, bound_var: BoundVarId) -> Type {
        self.type_map[&bound_var]
    }

    pub fn iter_variables<'a, M, V: VariableValue>(
        &self,
        variables: &Variables<'a>,
        type_interps: &TypeInterps,
        var_values: &mut V,
        mut each: M,
    ) where
        M: FnMut(&mut V),
    {
        self.iter_variables_with_end(variables, type_interps, var_values, |f| {
            each(f);
            ControlFlow::Continue(())
        })
    }

    /// Iterates over variables.
    /// The return value of `for_each` decides if we should continue iterating.
    pub fn iter_variables_with_end<T: VariableValue, M>(
        &self,
        variables: &Variables,
        type_interps: &TypeInterps,
        var_values: &mut T,
        mut for_each: M,
    ) where
        M: FnMut(&mut T) -> ControlFlow<()>,
    {
        if let Some(i_dom_pred) = variables.get_i_dom_pred() {
            // Caution! Here be dragons.
            // This branch is written with the idea of predicates being sparse

            // order of type_enum
            let order: Box<[_]> = i_dom_pred
                .layout()
                .iter()
                .map(|f| variables.iter_vars().position(|j| *j == f))
                .collect();
            // values of variables in layout before iter
            let pre_values: Box<[_]> = i_dom_pred
                .layout()
                .iter()
                .map(|f| var_values.get_type_enum(f))
                .collect();
            // happy path if no prevalues
            let nope = pre_values.iter().all(|&f| f == None);
            // variables missing from the layout
            let missing_from_layout: Vec<_> = variables
                .iter_vars()
                .filter_map(|f| {
                    if !i_dom_pred.layout().contains_var(*f) {
                        Some((*f, self.type_map(*f).len(type_interps)))
                    } else {
                        None
                    }
                })
                .collect();
            // Buffer of type enums
            let mut buf: Box<[_]> = (0..i_dom_pred.layout().len())
                .map(|_| TypeEnum::from(0))
                .collect();
            // iters for missing variables in layout
            let mut iters_missing: Box<[_]> = missing_from_layout
                .iter()
                .map(|f| IndexRange::<TypeEnum>::new(0..f.1))
                .collect();
            let mut cur = 0;
            let mut do_things = |var_values: &mut T| {
                let afd =
                    DomTypeEnumIter::new(i_dom_pred.iter_new(), &i_dom_pred.domain, type_interps);
                'big_loop: for type_enums in afd {
                    for (pos, type_enum) in type_enums.enumerate() {
                        if !nope {
                            if let Some(val) = pre_values[pos] {
                                if val != type_enum {
                                    // Irrelevant type_enums, skip
                                    continue 'big_loop;
                                }
                            }
                        }
                        buf[pos] = type_enum;
                    }
                    for (i, val) in buf.iter().enumerate() {
                        if let Some(ord) = order[i] {
                            var_values.set_type_enum(variables.slice_vars()[ord], *val);
                        }
                    }
                    if let ControlFlow::Break(()) = for_each(var_values) {
                        return;
                    }
                }
            };
            loop {
                if let Some(possible_val) = iters_missing.get_mut(cur).map(|f| f.next()) {
                    if let Some(val) = possible_val {
                        var_values.set_type_enum(missing_from_layout[cur].0, val);
                        if cur != iters_missing.len() - 1 {
                            cur += 1;
                            // next iter until there is not next iter
                            continue;
                        }
                        do_things(var_values);
                    } else {
                        if cur == 0 {
                            break;
                        }
                        iters_missing[cur] =
                            IndexRange::<TypeEnum>::new(0..missing_from_layout[cur].1);
                        cur -= 1;
                    }
                } else {
                    do_things(var_values);
                    break;
                }
            }
        } else {
            let len = LayoutVec::domain_len_of_iter(
                variables.iter_vars().copied(),
                &InterpContext::new(self.get_type_map(), type_interps),
            );
            for dom_enum in IndexRange::<DomainEnum>::new(0..len) {
                let type_enum_iter = type_interps.type_enum_iter(
                    variables.iter_vars().map(|f| &self.get_type_map()[f]),
                    dom_enum,
                );
                for (pos, type_enums) in type_enum_iter.enumerate() {
                    var_values.set_type_enum(variables.slice_vars()[pos], type_enums);
                }
                if let ControlFlow::Break(()) = for_each(var_values) {
                    return;
                }
            }
        }
        for var in variables.iter_vars() {
            var_values.remove_var(*var);
        }
    }

    pub fn add_aux(&mut self, new_symb: AuxSignature) -> AuxIndex {
        self.aux_symbols.add_aux(new_symb)
    }

    pub fn new_aux_from(&mut self, index: PfuncIndex) -> AuxSymbolBuilder {
        self.aux_symbols.new_aux_from(index)
    }

    pub fn vocab(&self) -> &Vocabulary {
        self.aux_symbols.structure.type_interps().vocab()
    }

    pub(crate) fn add_aux_decl(&mut self, new_symb: AuxDecl) -> AuxIndex {
        self.aux_symbols.add_aux_decl(new_symb)
    }

    pub fn aux_pfuncs(&self, index: AuxIndex) -> AuxSymbol {
        self.aux_symbols.aux_funcs(index)
    }

    pub fn aux_decl(&self, index: AuxIndex) -> AuxDecl {
        self.aux_symbols.aux_decl(index)
    }

    pub fn set_aux(&mut self, value: owned::SymbolInterp) {
        self.aux_symbols.structure.set(value);
    }

    pub fn set_aux_with_index(&mut self, value: owned::SymbolInterp, index: AuxIndex) {
        self.aux_symbols
            .structure
            .set_with_index(value, IndexRepr::from(index).into());
    }

    /// Escape hatch for setting a predicate
    pub fn set_aux_pred(&mut self, index: AuxIndex, value: backend::partial_interp::owned::Pred) {
        // TODO: fix this
        self.aux_symbols
            .structure
            .store
            .set_pred(PredIndex(usize::from(index).into()), value);
    }

    pub fn get_mut<'a>(&'a mut self, index: AuxIndex) -> mutable::SymbolInterp<'a> {
        self.aux_symbols.get_mut(index)
    }

    pub fn get<'a>(&'a self, index: AuxIndex) -> immutable::SymbolInterp<'a> {
        self.aux_symbols.get(index)
    }

    pub fn rc_type_interps(&self) -> &Rc<TypeInterps> {
        &self.aux_symbols.structure.rc_type_interps()
    }

    pub fn type_interps(&self) -> &TypeInterps {
        &self.aux_symbols.structure.rc_type_interps()
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuxDecl {
    pub codomain: Type,
    pub domain: DomainIndex,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuxSignature {
    pub codomain: Type,
    pub domain: Box<DomainSlice>,
}

#[derive(Debug, Clone)]
pub struct AuxSymbol<'a> {
    pub index: AuxIndex,
    pub codomain: Type,
    pub domain: &'a DomainSlice,
    pub type_interps: &'a TypeInterps,
}

#[derive(Debug, Clone)]
pub struct AuxSymbols {
    aux_symbols: TiVec<AuxIndex, AuxDecl>,
    structure: PartialStructure,
}

impl AuxSymbols {
    fn fake_symbol<'a>(
        index: AuxIndex,
        type_interps: &'a TypeInterps,
        aux_symbols: &'a TiVec<AuxIndex, AuxDecl>,
    ) -> SymbolFull<'a> {
        let aux_symb = &aux_symbols[index];
        let domain = type_interps.vocab().get_domain(aux_symb.domain);
        SymbolFull {
            index: index.to_pfunc_index(),
            domain,
            codomain: aux_symb.codomain.with_interps(type_interps),
            type_interps,
            vocabulary: type_interps.vocab(),
        }
    }

    pub fn new(type_interps: Rc<TypeInterps>) -> Self {
        Self {
            aux_symbols: TiVec::new(),
            structure: PartialStructure::new(type_interps),
        }
    }

    pub fn clear(&mut self) {
        self.aux_symbols.clear();
        self.structure = PartialStructure::new(self.structure.rc_type_interps().clone());
    }

    pub fn add_aux(&mut self, new_symb: AuxSignature) -> AuxIndex {
        let decl = AuxDecl {
            codomain: new_symb.codomain,
            domain: self
                .structure
                .type_interps()
                .vocab()
                .add_domain(new_symb.domain),
        };
        let index = self.aux_symbols.len();
        self.aux_symbols.push(decl);
        index.into()
    }

    pub(crate) fn add_aux_decl(&mut self, new_symb: AuxDecl) -> AuxIndex {
        let decl = AuxDecl {
            codomain: new_symb.codomain,
            domain: new_symb.domain,
        };
        let index = self.aux_symbols.len();
        self.aux_symbols.push(decl);
        index.into()
    }

    pub fn new_aux_from(&mut self, index: PfuncIndex) -> AuxSymbolBuilder {
        let pfunc_decl = self.structure.type_interps().vocab().get_pfunc_decl(index);
        AuxSymbolBuilder {
            cur_decl: AuxDecl {
                codomain: pfunc_decl.codomain,
                domain: pfunc_decl.domain,
            },
            aux_symbols: self,
        }
    }

    pub fn aux_funcs(&self, index: AuxIndex) -> AuxSymbol {
        let decl = &self.aux_symbols[index];
        AuxSymbol {
            index,
            domain: self
                .structure
                .type_interps()
                .vocab()
                .get_domain(decl.domain),
            codomain: decl.codomain,
            type_interps: self.structure.type_interps(),
        }
    }

    pub fn aux_decl(&self, index: AuxIndex) -> AuxDecl {
        self.aux_symbols[index].clone()
    }

    pub fn get_mut<'a>(&'a mut self, index: AuxIndex) -> mutable::SymbolInterp<'a> {
        let (store, type_interps) = self.structure.split();
        PartialStructure::get_mut_store(
            store,
            index.to_pfunc_index(),
            Self::fake_symbol(index, type_interps, &self.aux_symbols),
        )
    }

    pub fn get<'a>(&'a self, index: AuxIndex) -> immutable::SymbolInterp<'a> {
        self.structure.get_store(
            index.to_pfunc_index(),
            Self::fake_symbol(index, self.structure.type_interps(), &self.aux_symbols),
        )
    }
}

pub struct AuxSymbolBuilder<'a> {
    aux_symbols: &'a mut AuxSymbols,
    cur_decl: AuxDecl,
}

impl<'a> AuxSymbolBuilder<'a> {
    pub fn with_domain<T: Into<Box<DomainSlice>>>(self, domain: T) -> Self {
        let new_index = self
            .aux_symbols
            .structure
            .type_interps()
            .vocab()
            .add_domain(domain);
        Self {
            cur_decl: AuxDecl {
                domain: new_index,
                ..self.cur_decl
            },
            ..self
        }
    }

    pub fn domain(&self) -> &DomainSlice {
        self.aux_symbols
            .structure
            .type_interps()
            .vocab()
            .get_domain(self.cur_decl.domain)
    }

    pub fn with_codomain(self, codomain: Type) -> Self {
        Self {
            cur_decl: AuxDecl {
                codomain,
                ..self.cur_decl
            },
            ..self
        }
    }

    pub fn finish(self) -> AuxIndex {
        self.aux_symbols.add_aux_decl(self.cur_decl)
    }
}

impl<'a> AsRef<Expressions> for Expressions {
    fn as_ref(&self) -> &Expressions {
        self
    }
}

impl<'a> AsMut<Expressions> for Expressions {
    fn as_mut(&mut self) -> &mut Expressions {
        self
    }
}

#[derive(Clone, Copy)]
pub struct ExpressionRef<'a> {
    pub expressions: &'a Expressions,
    pub start: NodeIndex,
}

impl<'a> Debug for ExpressionRef<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{:?}",
            ExpressionTree::<2> {
                exp_ref: self.clone(),
                depth: 0,
            }
        )
    }
}

#[derive(Clone, Copy)]
pub struct ExpressionTree<'a, const INC: usize> {
    pub exp_ref: ExpressionRef<'a>,
    pub depth: usize,
}

impl<'a, const INC: usize> ExpressionTree<'a, INC> {
    fn new_at(&self, start: NodeIndex) -> Self {
        Self {
            exp_ref: self.exp_ref.new_at(start),
            depth: self.depth + INC,
        }
    }

    fn new_at_extra_inc(&self, start: NodeIndex, inc_amount: usize) -> Self {
        Self {
            exp_ref: self.exp_ref.new_at(start),
            depth: self.depth + INC * inc_amount,
        }
    }

    fn write_ws_one(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:width$}", " ", width = INC)?;
        Ok(())
    }

    fn write_ws(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:width$}", " ", width = self.depth)?;
        Ok(())
    }
}

impl<'a, const INC: usize> Debug for ExpressionTree<'a, INC> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let node_enum = self.exp_ref.first_node_enum();
        write!(f, "({}: ", self.exp_ref.start.0)?;
        match node_enum {
            NodeEnum::BinOps(bin_op) => {
                write!(f, "{:?}\n", bin_op.bin_op)?;
                self.write_ws(f)?;
                self.write_ws_one(f)?;
                write!(f, "{:?}\n", self.new_at(bin_op.lhs))?;
                self.write_ws(f)?;
                self.write_ws_one(f)?;
                write!(f, "{:?}\n", self.new_at(bin_op.rhs))?;
                self.write_ws(f)?;
            }
            NodeEnum::NumNeg(n) => {
                write!(f, "numerical_neg {:?}", self.new_at(n.child))?;
            }
            NodeEnum::Neg(n) => {
                write!(f, "neg {:?}", self.new_at(n.child))?;
            }
            NodeEnum::IsInt(n) => {
                write!(f, "is_int {:?}", self.new_at(n.child))?;
            }
            NodeEnum::Agg(agg) => {
                write!(f, "{:?}\n", agg.aggregate_type)?;
                self.write_ws(f)?;
                write!(f, "{:?}\n", agg.variables)?;
                self.write_ws(f)?;
                write!(f, "{:?}\n", self.new_at(agg.formula))?;
                self.write_ws(f)?;
            }
            NodeEnum::Quant(quant) => {
                write!(f, "{:?}\n", quant.quant_type)?;
                self.write_ws_one(f)?;
                self.write_ws(f)?;
                write!(f, "Vars: {:?}\n", quant.variables)?;
                self.write_ws_one(f)?;
                self.write_ws(f)?;
                write!(f, "{:?}\n", self.new_at(quant.formula))?;
                self.write_ws(f)?;
            }
            NodeEnum::Element(el) => {
                write!(f, "{:?}", el)?;
            }
            NodeEnum::AppliedSymb(applied_symb) => {
                write!(f, "AppliedSymb: {:?}", applied_symb.index)?;
                let mut children = applied_symb.child_iter().peekable();
                while let Some(child) = children.next() {
                    write!(f, "\n")?;
                    let end = children.peek().is_none();
                    self.write_ws(f)?;
                    self.write_ws_one(f)?;
                    write!(f, "{:?}", child)?;
                    if end {
                        write!(f, "\n")?;
                        self.write_ws(f)?;
                    }
                }
            }
            NodeEnum::AppliedAuxSymb(applied_symb) => {
                write!(f, "AppliedAuxSymb: {:?}", applied_symb.index)?;
                let mut children = applied_symb.child_iter().peekable();
                while let Some(child) = children.next() {
                    write!(f, "\n")?;
                    let end = children.peek().is_none();
                    self.write_ws(f)?;
                    self.write_ws_one(f)?;
                    write!(f, "{:?}", child)?;
                    if end {
                        write!(f, "\n")?;
                        self.write_ws(f)?;
                    }
                }
            }
            NodeEnum::Ite(ite) => {
                write!(f, "Ite:\n")?;
                self.write_ws(f)?;
                write!(f, "If: {:?}\n", self.new_at(ite.cond))?;
                self.write_ws(f)?;
                write!(f, "Then: {:?}\n", self.new_at(ite.then_term))?;
                self.write_ws(f)?;
                write!(f, "Else: {:?}\n", self.new_at(ite.else_term))?;
                self.write_ws(f)?;
            }
            NodeEnum::Def(def) => {
                write!(f, "Def:\n")?;
                for rule in def.iter_indexes() {
                    self.write_ws(f)?;
                    self.write_ws_one(f)?;
                    write!(f, "{:?}\n", self.new_at(rule))?;
                }
                self.write_ws(f)?;
            }
            NodeEnum::Rule(rule) => {
                write!(f, "Rule:\n")?;
                self.write_ws(f)?;
                self.write_ws_one(f)?;
                write!(f, "Head:\n")?;
                self.write_ws(f)?;
                self.write_ws_one(f)?;
                self.write_ws_one(f)?;
                write!(f, "Vars: {:?}\n", rule.head.variables)?;
                self.write_ws(f)?;
                self.write_ws_one(f)?;
                self.write_ws_one(f)?;
                write!(f, "definiendum: {:?}\n", rule.head.definiendum)?;
                self.write_ws(f)?;
                self.write_ws_one(f)?;
                write!(f, "Body:\n")?;
                self.write_ws(f)?;
                self.write_ws_one(f)?;
                self.write_ws_one(f)?;
                write!(f, "{:?}\n", self.new_at_extra_inc(rule.body, 2))?;
                self.write_ws(f)?;
            }
        }
        write!(f, ")")
    }
}

impl<'a> ExpressionRef<'a> {
    pub fn new<T: AsRef<Expressions>>(expressions: &'a T, start: NodeIndex) -> Self {
        Self {
            expressions: expressions.as_ref(),
            start,
        }
    }
}

impl<'a> From<(NodeIndex, &'a Expressions)> for ExpressionRef<'a> {
    fn from(value: (NodeIndex, &'a Expressions)) -> Self {
        Self {
            start: value.0,
            expressions: value.1,
        }
    }
}

impl<'a> ExpressionRef<'a> {
    pub fn first_node(&self) -> Node {
        self.expressions.nodes(self.start).clone()
    }

    pub fn new_at(&self, index: NodeIndex) -> Self {
        Self {
            expressions: self.expressions,
            start: index,
        }
    }

    pub fn start(&self) -> NodeIndex {
        self.start
    }

    pub fn expressions(&self) -> &'a Expressions {
        self.expressions
    }

    pub fn first_node_enum(&self) -> NodeEnum {
        let ex = self.expressions();
        NodeEnum::from(self.start(), ex)
    }

    pub fn try_first_node_enum(&self) -> Result<NodeEnum, ExprType> {
        let ex = self.expressions();
        NodeEnum::try_from((self.start(), ex))
    }

    pub fn try_into_bool(&self) -> Option<bool> {
        let ex = self.expressions();
        ex.nodes(self.start()).try_into_bool()
    }

    pub fn try_into_type_element(&self) -> Option<TypeElement> {
        match self.first_node_enum() {
            NodeEnum::Element(el) => el.try_into().ok(),
            _ => None,
        }
    }

    pub fn eval_first(&self) -> bool {
        self.expressions.nodes(self.start()).expr.eval_first()
    }

    pub fn get_type_map(&self) -> &TypeMap {
        self.expressions.get_type_map()
    }

    /// Walks entire tree.
    pub fn for_each<F>(&self, func: &mut F)
    where
        F: FnMut(&NodeEnum),
    {
        let node_enum = self.first_node_enum();
        func(&node_enum);
        match node_enum {
            NodeEnum::BinOps(bin_op) => {
                self.new_at(bin_op.lhs).for_each(func);
                self.new_at(bin_op.rhs).for_each(func);
            }
            NodeEnum::NumNeg(n) => self.new_at(n.child).for_each(func),
            NodeEnum::Neg(n) => self.new_at(n.child).for_each(func),
            NodeEnum::IsInt(n) => self.new_at(n.child).for_each(func),
            NodeEnum::Agg(agg) => self.new_at(agg.formula).for_each(func),
            NodeEnum::Quant(quant) => self.new_at(quant.formula).for_each(func),
            NodeEnum::Element(_) => {}
            NodeEnum::AppliedSymb(_) => {}
            NodeEnum::AppliedAuxSymb(_) => {}
            NodeEnum::Ite(ite) => {
                self.new_at(ite.cond).for_each(func);
                self.new_at(ite.then_term).for_each(func);
                self.new_at(ite.else_term).for_each(func);
            }
            NodeEnum::Def(def) => def
                .iter_indexes()
                .for_each(|f| self.new_at(f).for_each(func)),
            NodeEnum::Rule(rule) => self.new_at(rule.body).for_each(func),
        }
    }

    /// Walks entire tree with a pre and post function.
    pub fn bi_for_each<F, D>(&self, pre_func: &mut F, post_func: &mut D)
    where
        F: FnMut(&NodeEnum),
        D: FnMut(&NodeEnum),
    {
        let node_enum = self.first_node_enum();
        pre_func(&node_enum);
        match &node_enum {
            NodeEnum::BinOps(bin_op) => {
                self.new_at(bin_op.lhs).bi_for_each(pre_func, post_func);
                self.new_at(bin_op.rhs).bi_for_each(pre_func, post_func);
            }
            NodeEnum::NumNeg(n) => self.new_at(n.child).bi_for_each(pre_func, post_func),
            NodeEnum::Neg(n) => self.new_at(n.child).bi_for_each(pre_func, post_func),
            NodeEnum::IsInt(n) => self.new_at(n.child).bi_for_each(pre_func, post_func),
            NodeEnum::Agg(agg) => self.new_at(agg.formula).bi_for_each(pre_func, post_func),
            NodeEnum::Quant(quant) => self.new_at(quant.formula).bi_for_each(pre_func, post_func),
            NodeEnum::Element(_) => {}
            NodeEnum::AppliedSymb(_) => {}
            NodeEnum::AppliedAuxSymb(_) => {}
            NodeEnum::Ite(ite) => {
                self.new_at(ite.cond).bi_for_each(pre_func, post_func);
                self.new_at(ite.then_term).bi_for_each(pre_func, post_func);
                self.new_at(ite.else_term).bi_for_each(pre_func, post_func);
            }
            NodeEnum::Def(def) => def
                .iter_indexes()
                .for_each(|f| self.new_at(f).bi_for_each(pre_func, post_func)),
            NodeEnum::Rule(rule) => self.new_at(rule.body).bi_for_each(pre_func, post_func),
        }
        post_func(&node_enum);
    }

    /// Walks tree until func returns true once. If func never returns true false is returned
    pub fn any<F>(&self, mut func: F) -> bool
    where
        F: FnMut(&NodeEnum) -> bool + Copy,
    {
        let node_enum = self.first_node_enum();
        if func(&node_enum) {
            return true;
        }
        match node_enum {
            NodeEnum::BinOps(bin_op) => {
                if !self.new_at(bin_op.lhs).any(func) {
                    self.new_at(bin_op.rhs).any(func)
                } else {
                    true
                }
            }
            NodeEnum::NumNeg(n) => self.new_at(n.child).any(func),
            NodeEnum::Neg(n) => self.new_at(n.child).any(func),
            NodeEnum::IsInt(n) => self.new_at(n.child).any(func),
            NodeEnum::Agg(agg) => self.new_at(agg.formula).any(func),
            NodeEnum::Quant(quant) => self.new_at(quant.formula).any(func),
            NodeEnum::Element(_) => false,
            NodeEnum::AppliedSymb(_) => false,
            NodeEnum::AppliedAuxSymb(_) => false,
            NodeEnum::Ite(ite) => {
                if self.new_at(ite.cond).any(func) {
                    true
                } else if self.new_at(ite.then_term).any(func) {
                    true
                } else if self.new_at(ite.else_term).any(func) {
                    true
                } else {
                    false
                }
            }
            NodeEnum::Def(def) => def.iter_indexes().any(|f| self.new_at(f).any(func)),
            NodeEnum::Rule(rule) => self.new_at(rule.body).any(func),
        }
    }
}

#[derive(Debug, Clone)]
pub struct IDomainPredicate {
    pub(crate) bit_vec: LayoutSatSet,
    domain: Box<DomainSlice>,
}

impl IDomainPredicate {
    pub fn contains(&self, el: DomainEnum) -> bool {
        self.bit_vec.contains(el)
    }

    pub fn get_domain(&self) -> &Box<DomainSlice> {
        &self.domain
    }

    pub fn iter<'a, T: VariableValue>(
        &'a self,
        structure: &'a TypeInterps,
        quant: BoundVarId,
        var_values: &T,
    ) -> DomainIter<'a> {
        // TODO don't do this instead use future iter
        let mut domain_enum_builder = DomainEnumBuilder::from_struct(&self.domain, structure);
        for a in self.bit_vec.layout().iter() {
            if a != quant {
                domain_enum_builder
                    .add_enum_arg(var_values.get(a))
                    .expect("Internal error: blablabla");
            } else {
                domain_enum_builder
                    .add_var(a)
                    .expect("Internal error: bleep bloop");
            }
        }
        let domain_enum = domain_enum_builder
            .iter_single_var_indexes()
            .expect("Internal error: bliblibloo");
        DomainIter::DomPred {
            domain_enum,
            dom_pred: self,
        }
    }

    pub fn cardinality(&self) -> usize {
        self.bit_vec.cardinality()
    }

    pub fn iter_new<'a>(&'a self) -> impl Iterator<Item = DomainEnum> + 'a {
        self.bit_vec.iter()
    }

    pub fn translate_layout(&mut self, var_translation: &IdHashMap<BoundVarId, BoundVarId>) {
        self.bit_vec.mut_layout().translate_layout(var_translation)
    }

    pub fn layout(&self) -> &LayoutVec {
        self.bit_vec.layout()
    }

    pub fn from_satset(value: LayoutSatSet, type_map: &TypeMap) -> Self {
        IDomainPredicate {
            domain: value.layout().get_domain(type_map).into(),
            bit_vec: value,
        }
    }
}

impl AsRef<LayoutSatSet> for IDomainPredicate {
    fn as_ref(&self) -> &LayoutSatSet {
        &self.bit_vec
    }
}

#[derive(Debug)]
pub enum DomainIter<'a> {
    DomPred {
        dom_pred: &'a IDomainPredicate,
        domain_enum: DomainEnumSingleVar<'a>,
    },
    Domain(IndexRange<TypeEnum>),
}

impl<'a> Iterator for DomainIter<'a> {
    type Item = TypeEnum;
    fn next(&mut self) -> Option<Self::Item> {
        match self {
            DomainIter::DomPred {
                dom_pred,
                domain_enum,
            } => {
                let mut cur = domain_enum.next();
                while let Some(dom_e) = cur {
                    if dom_pred.contains(usize::from(dom_e).into()) {
                        let type_e = domain_enum
                            .get_type_interps()
                            .type_enum_iter(domain_enum.get_domain().iter(), dom_e)
                            .nth(domain_enum.var_at())
                            .expect("Internal error: disagreeing domain length");
                        return Some(type_e);
                    }
                    cur = domain_enum.next();
                }
                return None;
            }
            DomainIter::Domain(r) => r.next(),
        }
    }
}

pub struct DomTypeEnumIter<'a, T> {
    type_interps: &'a TypeInterps,
    iter: T,
    iter_domain: &'a DomainSlice,
}

impl<'a, T> DomTypeEnumIter<'a, T>
where
    T: Iterator<Item = DomainEnum> + 'a,
{
    pub fn new(iter: T, iter_domain: &'a DomainSlice, type_interps: &'a TypeInterps) -> Self {
        Self {
            iter,
            type_interps,
            iter_domain,
        }
    }
}

impl<'a, T> Iterator for DomTypeEnumIter<'a, T>
where
    T: Iterator<Item = DomainEnum> + 'a,
{
    type Item = TypeEnumIter<'a, Iter<'a, Type>>;

    fn next(&mut self) -> Option<Self::Item> {
        let domain_enum = self.iter.next()?;
        self.type_interps
            .type_enum_iter(self.iter_domain.iter(), domain_enum)
            .into()
    }
}

pub struct DomNestedIter<'a> {
    type_enum_iter: TypeEnumIter<'a, Iter<'a, Type>>,
}

impl<'a> Iterator for DomNestedIter<'a> {
    type Item = TypeEnum;

    fn next(&mut self) -> Option<Self::Item> {
        self.type_enum_iter.next()
    }
}
