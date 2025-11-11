use super::{
    AuxDecl, AuxIndex, AuxSignature, AuxSymbol, AuxSymbolBuilder, ExpressionRef, IDomainPredicate,
    TypeMap, expressions::Expressions,
};
use crate::{
    comp_core::{
        IndexRepr,
        constraints::{BoundVarId, ExtraIndex, NodeIndex, ToConstraint},
        node::{Node, NodeEnum},
        structure::{
            TypeElement, TypeInterps,
            partial::{immutable, mutable, owned},
        },
        vocabulary::{PfuncIndex, Type},
    },
    structure::backend,
};
use sli_collections::cell::Cell;
use sli_collections::{hash_map::IdHashMap, rc::Rc};
use std::ops::Range;

pub type OriginMap = IdHashMap<NodeIndex, NodeIndex>;

/// A version of [Expressions] that keeps track of its origins.
/// TODO: keeping track of its origins is broken.
#[derive(Debug, Clone)]
pub struct TransformedExpressions {
    expressions: Expressions,
    origin_map: OriginMap,
}

impl<'a> Into<&'a Expressions> for &'a TransformedExpressions {
    fn into(self) -> &'a Expressions {
        &self.expressions
    }
}

impl<'a> Into<&'a mut Expressions> for &'a mut TransformedExpressions {
    fn into(self) -> &'a mut Expressions {
        &mut self.expressions
    }
}

impl AsRef<TransformedExpressions> for TransformedExpressions {
    fn as_ref(&self) -> &TransformedExpressions {
        &self
    }
}

impl AsRef<Expressions> for TransformedExpressions {
    fn as_ref(&self) -> &Expressions {
        &self.expressions
    }
}

impl AsMut<TransformedExpressions> for TransformedExpressions {
    fn as_mut(&mut self) -> &mut TransformedExpressions {
        self
    }
}

impl TransformedExpressions {
    pub fn new(type_interps: Rc<TypeInterps>) -> Self {
        Self {
            expressions: Expressions::new(type_interps),
            origin_map: OriginMap::default(),
        }
    }

    pub fn clear(&mut self) {
        self.expressions.clear();
        self.origin_map.clear();
    }

    pub fn get_type_map(&self) -> &TypeMap {
        self.expressions.get_type_map()
    }

    pub fn get_type_map_mut(&mut self) -> &mut TypeMap {
        self.expressions.get_type_map_mut()
    }

    pub fn to_expression(&self, start: NodeIndex) -> TransformedExpressionRef {
        TransformedExpressionRef::new(self, start)
    }

    pub fn to_mut_expression(&mut self, start: NodeIndex) -> TransformedExpressionMutRef {
        TransformedExpressionMutRef::new(self, start)
    }

    pub fn as_type_element(&self, index: NodeIndex) -> Option<TypeElement> {
        self.expressions.as_type_element(index)
    }

    pub fn quant_elements_insert(
        &mut self,
        index: NodeIndex,
        dom_pred: IDomainPredicate,
    ) -> Option<IDomainPredicate> {
        self.expressions.quant_elements_insert(index, dom_pred)
    }

    pub fn as_bool(&self, index: NodeIndex) -> Option<bool> {
        self.expressions.as_bool(index)
    }

    pub fn new_bound_var(&mut self) -> BoundVarId {
        self.expressions.new_bound_var()
    }

    pub fn set_bound_var_start(&mut self, start: BoundVarId) {
        self.expressions.set_bound_var_start(start)
    }

    pub fn cur_bound_var(&self) -> BoundVarId {
        self.expressions.cur_bound_var().into()
    }

    pub fn get_origin(&self, index: NodeIndex) -> NodeIndex {
        self.origin_map[&index]
    }

    pub fn push_node<T>(&mut self, node: T, original_index: NodeIndex) -> NodeIndex
    where
        T: ToConstraint,
    {
        let index = self.expressions.push_node(node);
        self.origin_map.insert(index, original_index);
        index
    }

    pub(super) fn replace<T>(&mut self, node: T, id: NodeIndex) -> NodeIndex
    where
        T: ToConstraint,
    {
        let index = self.expressions.push_node(node);
        let origin = self.origin_map[&id];
        self.origin_map.insert(index, origin);
        index
    }

    pub fn nodes(&self, index: NodeIndex) -> &Node {
        self.expressions.nodes(index)
    }

    pub fn extra(&self, index: ExtraIndex) -> IndexRepr {
        self.expressions.extra(index)
    }

    pub fn func_map(&self, index: NodeIndex) -> PfuncIndex {
        self.expressions.pfunc_map(index)
    }

    pub fn type_map(&self, bound_var: BoundVarId) -> Type {
        self.expressions.type_map(bound_var)
    }

    pub fn extra_slice<'a>(&'a self, range: Range<ExtraIndex>) -> &'a [IndexRepr] {
        self.expressions.extra_slice(range)
    }

    pub fn get_origin_map(&self) -> &OriginMap {
        &self.origin_map
    }

    pub fn add_aux(&mut self, new_symb: AuxSignature) -> AuxIndex {
        self.expressions.add_aux(new_symb)
    }

    pub(crate) fn add_aux_decl(&mut self, new_symb: AuxDecl) -> AuxIndex {
        self.expressions.add_aux_decl(new_symb)
    }

    pub fn aux_funcs(&self, index: AuxIndex) -> AuxSymbol {
        self.expressions.aux_pfuncs(index)
    }

    pub fn aux_decl(&self, index: AuxIndex) -> AuxDecl {
        self.expressions.aux_decl(index)
    }

    pub fn new_aux_from(&mut self, index: PfuncIndex) -> AuxSymbolBuilder {
        self.expressions.new_aux_from(index)
    }

    pub fn set_aux(&mut self, value: owned::SymbolInterp) {
        self.expressions.set_aux(value)
    }

    pub fn set_aux_with_index(&mut self, value: owned::SymbolInterp, index: AuxIndex) {
        self.expressions.set_aux_with_index(value, index)
    }

    /// Escape hatch for setting a predicate
    pub fn set_aux_pred(&mut self, index: AuxIndex, value: backend::partial_interp::owned::Pred) {
        self.expressions.set_aux_pred(index, value);
    }

    pub fn get_mut<'a>(&'a mut self, index: AuxIndex) -> mutable::SymbolInterp<'a> {
        self.expressions.get_mut(index)
    }

    pub fn get<'a>(&'a self, index: AuxIndex) -> immutable::SymbolInterp<'a> {
        self.expressions.get(index)
    }

    pub fn rc_type_interps(&self) -> &Rc<TypeInterps> {
        self.expressions.rc_type_interps()
    }
}

pub struct TransformedExpressionRef<'a> {
    pub expressions: &'a TransformedExpressions,
    pub start: NodeIndex,
}

impl<'a> From<TransformedExpressionRef<'a>> for ExpressionRef<'a> {
    fn from(value: TransformedExpressionRef<'a>) -> Self {
        ExpressionRef::new(value.expressions, value.start)
    }
}

impl<'a> TransformedExpressionRef<'a> {
    pub fn new<T: Into<&'a TransformedExpressions>>(expressions: T, start: NodeIndex) -> Self {
        Self {
            expressions: expressions.into(),
            start,
        }
    }

    pub fn get_origin(&self) -> NodeIndex {
        self.expressions.origin_map[&self.start]
    }

    pub fn new_at(self, index: NodeIndex) -> Self {
        Self {
            expressions: self.expressions,
            start: index,
        }
    }

    pub fn start(&self) -> NodeIndex {
        self.start
    }

    pub fn expressions(&self) -> &TransformedExpressions {
        self.expressions.into()
    }

    pub fn first_node_enum(&self) -> NodeEnum {
        let ex = self.expressions();
        NodeEnum::from(self.start(), ex)
    }

    pub fn try_into_bool(&self) -> Option<bool> {
        let ex = self.expressions();
        ex.nodes(self.start()).try_into_bool()
    }
}

pub struct TransformedExpressionMutRef<'a> {
    pub expressions: Cell<&'a mut TransformedExpressions>,
    pub start: Cell<NodeIndex>,
}

impl<'a> TransformedExpressionMutRef<'a> {
    pub fn new<T>(expressions: &'a mut T, start: NodeIndex) -> Self
    where
        T: AsMut<TransformedExpressions>,
    {
        Self {
            expressions: Cell::new(expressions.as_mut()),
            start: Cell::new(start),
        }
    }

    pub fn get_origin(&self) -> NodeIndex {
        self.expressions().get_origin(self.start())
    }

    pub fn start_at(&self, index: NodeIndex) -> &Self {
        self.start.set(index);
        self
    }

    pub fn im_at(&self, index: NodeIndex) -> TransformedExpressionRef {
        TransformedExpressionRef::new(self.expressions(), index)
    }

    pub fn im_at_self(&self) -> TransformedExpressionRef {
        TransformedExpressionRef::new(self.expressions(), self.start())
    }

    pub fn get_type_map(&self) -> &TypeMap {
        self.expressions().get_type_map()
    }

    pub fn start(&self) -> NodeIndex {
        unsafe { *self.start.as_ptr() }
    }

    pub fn expressions(&self) -> &TransformedExpressions {
        unsafe { &*self.expressions.as_ptr() }
    }

    pub fn replace<T>(&mut self, id: NodeIndex, node: T) -> NodeIndex
    where
        T: ToConstraint,
    {
        let index = self.expressions.get_mut().replace(node, id);
        if self.start() == id {
            self.start.set(index);
        }
        index
    }

    pub fn replace_self<T>(&mut self, node: T)
    where
        T: ToConstraint,
    {
        self.replace(self.start(), node);
    }

    pub fn add_to_expression<T>(&mut self, node: T) -> NodeIndex
    where
        T: ToConstraint,
    {
        let origin = self.get_origin();
        self.expressions.get_mut().push_node(node, origin)
    }

    pub fn add_as_self<T>(&mut self, node: T) -> NodeIndex
    where
        T: ToConstraint,
    {
        let origin = self.get_origin();
        self.expressions.get_mut().push_node(node, origin)
    }

    pub fn mut_expression(&mut self) -> &mut TransformedExpressions {
        self.expressions.get_mut()
    }

    pub fn take_mut_expression(self) -> &'a mut TransformedExpressions {
        self.expressions.into_inner()
    }

    pub fn first_node_enum(&self) -> NodeEnum {
        NodeEnum::from(self.start(), self.expressions())
    }

    pub fn try_into_bool(&self) -> Option<bool> {
        let ex = self.expressions();
        ex.nodes(self.start()).try_into_bool()
    }
}

impl<'a> From<TransformedExpressionMutRef<'a>> for ExpressionRef<'a> {
    fn from(value: TransformedExpressionMutRef<'a>) -> Self {
        ExpressionRef::new(value.expressions.into_inner(), value.start.into_inner())
    }
}
