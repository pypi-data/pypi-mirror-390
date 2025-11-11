use super::{ElementNode, ExprType, FromExpressionUnchecked, NodeEnum};
use crate::IndexRepr;
use crate::comp_core::constraints::{BoundVarId, NodeIndex, ToConstraint, ToNodeArgs};
use crate::comp_core::expression::{AuxIndex, AuxSymbol, Expressions, VariableValue};
use crate::comp_core::node::Node;
use crate::comp_core::structure::{DomainEnumBuilder, TypeElement};
use crate::comp_core::structure::{PartialStructure, TypeInterps};
use crate::comp_core::vocabulary::{DomainEnum, DomainSlice, PfuncIndex, Symbol};
use std::mem::transmute;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Kind {
    None,
    /// Used in satset simplification
    Splitted,
}

impl Default for Kind {
    fn default() -> Self {
        Kind::None
    }
}

impl Kind {
    fn from_expr_type(expr_type: ExprType) -> Self {
        match expr_type {
            ExprType::SplittedAppliedSymb | ExprType::SplittedAppliedAuxSymb => Kind::Splitted,
            _ => Kind::None,
        }
    }

    pub fn is_splitted(&self) -> bool {
        matches!(self, Self::Splitted)
    }
}

/// A generic node for applied symbols.
/// Index identifies which symbol is being applied.
/// A comp core symbol may only be applied with [ElementNodes](ElementNode), i.e. an applied symbol
/// may not be nested.
#[derive(Debug, Clone)]
pub struct IndexAppliedSymbNode<'a, I: Copy> {
    pub index: I,
    kind: Kind,
    children: &'a [NodeIndex],
    expr: &'a Expressions,
}

impl<'b, I: Copy> IndexAppliedSymbNode<'b, I> {
    pub fn child_iter<'a>(&'a self) -> AppliedSymbChildrenIter<'a> {
        AppliedSymbChildrenIter {
            children: self.children.iter(),
            expr: self.expr,
        }
    }

    pub fn get_kind(&self) -> Kind {
        self.kind
    }

    pub fn contains_var<'a>(&'a self, var: BoundVarId) -> bool {
        self.child_iter()
            .any(|arg| matches!(arg, ElementNode::Quant(el) if el.bound_var_id == var))
    }

    fn build_domain_enum<V: VariableValue>(
        &self,
        domain: &DomainSlice,
        type_interps: &TypeInterps,
        var_values: &V,
    ) -> DomainEnum {
        let mut as_builder = DomainEnumBuilder::new(domain, type_interps);
        for args in self.child_iter() {
            match args {
                ElementNode::Quant(q) => {
                    let type_enum = var_values.get(q.bound_var_id);
                    as_builder.add_enum_arg(type_enum).unwrap();
                }
                el => {
                    let type_el: TypeElement = el.try_into().unwrap();
                    as_builder.add_type_el_arg(type_el).unwrap();
                }
            }
        }
        as_builder.get_index().unwrap()
    }

    pub fn at_index(&self, index: usize) -> Option<ElementNode> {
        return self.children.get(index).map(|f| {
            match self.expr.to_expression(*f).first_node_enum() {
                NodeEnum::Element(e) => e,
                _ => unreachable!(),
            }
        });
    }

    pub fn arg_amount(&self) -> usize {
        self.children.len()
    }

    pub fn to_builder(self) -> IndexAppliedSymbBuilder<I> {
        self.into()
    }
}

impl<'a, I: Copy> From<IndexAppliedSymbNode<'a, I>> for IndexAppliedSymbBuilder<I> {
    fn from(value: IndexAppliedSymbNode<'a, I>) -> Self {
        Self {
            kind: value.kind,
            index: value.index,
            children: value.child_iter().collect(),
        }
    }
}

#[derive(Clone)]
pub struct AppliedSymbChildrenIter<'a> {
    children: core::slice::Iter<'a, NodeIndex>,
    expr: &'a Expressions,
}

impl<'a> Iterator for AppliedSymbChildrenIter<'a> {
    type Item = ElementNode;

    fn next(&mut self) -> Option<Self::Item> {
        self.children
            .next()
            .map(|f| match self.expr.to_expression(*f).first_node_enum() {
                NodeEnum::Element(e) => e,
                _ => unreachable!(),
            })
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        self.children.size_hint()
    }
}

impl ExactSizeIterator for AppliedSymbChildrenIter<'_> {}

pub type AppliedSymbNode<'a> = IndexAppliedSymbNode<'a, PfuncIndex>;

impl<'a> FromExpressionUnchecked<'a> for AppliedSymbNode<'a> {
    fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
        let expression = value.1.as_ref();
        let index = value.0;
        let node = expression.nodes(value.0);
        debug_assert!(matches!(
            node.expr,
            ExprType::AppliedSymb | ExprType::SplittedAppliedSymb
        ));
        let child_start = node.data[0];
        let child_end = child_start + node.data[1];
        let children =
            unsafe { transmute(expression.extra_slice(child_start.into()..child_end.into())) };
        let pfunc_index = expression.pfunc_map(index);
        Self {
            kind: Kind::from_expr_type(node.expr),
            index: pfunc_index,
            children,
            expr: expression,
        }
    }
}

impl<'b> AppliedSymbNode<'b> {
    pub fn get_domain_enum<V: VariableValue>(
        &self,
        structure: &PartialStructure,
        var_values: &V,
    ) -> DomainEnum {
        let domain = structure.vocab().pfuncs(self.index).domain;
        self.build_domain_enum(domain, structure.as_ref(), var_values)
    }

    pub fn symbol(&self) -> Symbol {
        self.expr.vocab().pfuncs(self.index)
    }

    pub fn get_value<V: VariableValue>(
        &self,
        structure: &PartialStructure,
        var_values: &V,
    ) -> Option<TypeElement> {
        let domain_enum = self.get_domain_enum(structure, var_values);
        structure.get(self.index).get_i(domain_enum)
    }
}

/// A builder for applied symbols.
/// Index identifies which symbol is being applied.
/// A comp core symbol may only be applied with [ElementNodes](ElementNode), i.e. an applied symbol
/// may not be nested.
#[derive(Debug, Clone)]
pub struct IndexAppliedSymbBuilder<I: Copy> {
    pub kind: Kind,
    index: I,
    children: Vec<ElementNode>,
}

impl<I: Copy> IndexAppliedSymbBuilder<I> {
    pub fn new(index: I) -> Self {
        Self {
            kind: Kind::None,
            index,
            children: Vec::new(),
        }
    }

    pub fn apply(index: I, args: Vec<ElementNode>) -> Self {
        Self {
            kind: Kind::None,
            index,
            children: args,
        }
    }

    pub fn take_args(self) -> Vec<ElementNode> {
        self.children
    }

    pub fn set_args(&mut self, args: Vec<ElementNode>) {
        self.children = args;
    }

    pub fn add_arg(&mut self, arg: ElementNode) {
        self.children.push(arg)
    }

    pub fn index(&self) -> I {
        self.index
    }

    pub fn set_index(&mut self, new: I) {
        self.index = new;
    }

    pub fn iter_children(&self) -> impl Iterator<Item = ElementNode> + '_ {
        self.children.iter().cloned()
    }

    pub fn map_children<F: FnMut(ElementNode) -> ElementNode>(mut self, mut map: F) -> Self {
        self.children.iter_mut().for_each(|f| {
            let new = map(f.clone());
            *f = new;
        });
        self
    }
}

pub type AppliedSymbBuilder = IndexAppliedSymbBuilder<PfuncIndex>;

impl ToConstraint for AppliedSymbBuilder {
    fn to_pfunc_map(&self) -> Option<PfuncIndex> {
        Some(self.index)
    }

    fn children(&self) -> Box<[super::StandaloneNode]> {
        self.children.iter().map(|f| f.clone().into()).collect()
    }

    fn to_node(self, ToNodeArgs { extra_len, .. }: ToNodeArgs) -> Node {
        Node {
            expr: match self.kind {
                Kind::None => ExprType::AppliedSymb,
                Kind::Splitted => ExprType::SplittedAppliedSymb,
            },
            data: [
                extra_len.try_into().unwrap(),
                self.children.len().try_into().unwrap(),
            ],
        }
    }
}

pub type AppliedAuxSymbBuilder = IndexAppliedSymbBuilder<AuxIndex>;

impl ToConstraint for AppliedAuxSymbBuilder {
    fn children(&self) -> Box<[super::StandaloneNode]> {
        self.children.iter().map(|f| f.clone().into()).collect()
    }

    fn to_aux_map(&self) -> Option<AuxIndex> {
        Some(self.index)
    }

    fn to_node(self, ToNodeArgs { extra_len, .. }: ToNodeArgs) -> Node {
        Node {
            expr: match self.kind {
                Kind::None => ExprType::AppliedAuxSymb,
                Kind::Splitted => ExprType::SplittedAppliedAuxSymb,
            },
            data: [
                extra_len.try_into().unwrap(),
                self.children.len().try_into().unwrap(),
            ],
        }
    }
}

pub type AppliedAuxSymbNode<'a> = IndexAppliedSymbNode<'a, AuxIndex>;

impl<'a> FromExpressionUnchecked<'a> for AppliedAuxSymbNode<'a> {
    fn from_node<T: AsRef<Expressions>>(value: (NodeIndex, &'a T)) -> Self {
        let expression = value.1.as_ref();
        let index = value.0;
        let node = expression.nodes(value.0);
        debug_assert!(matches!(
            node.expr,
            ExprType::AppliedAuxSymb | ExprType::SplittedAppliedAuxSymb
        ));
        let child_start = node.data[0];
        let child_end = child_start + node.data[1];
        let children = unsafe {
            transmute::<&[IndexRepr], &[NodeIndex]>(
                expression.extra_slice(child_start.into()..child_end.into()),
            )
        };
        let aux_index = expression.aux_map(index);
        Self {
            kind: Kind::from_expr_type(node.expr),
            index: aux_index,
            children,
            expr: expression,
        }
    }
}

impl<'b> AppliedAuxSymbNode<'b> {
    pub fn symbol(&self) -> AuxSymbol {
        self.expr.aux_pfuncs(self.index)
    }

    pub fn get_domain_enum<V: VariableValue>(
        &self,
        expr: &Expressions,
        var_values: &V,
    ) -> DomainEnum {
        let aux_symb = expr.aux_pfuncs(self.index);
        self.build_domain_enum(aux_symb.domain, aux_symb.type_interps, var_values)
    }

    pub fn get_value<V: VariableValue>(
        &self,
        expr: &Expressions,
        var_values: &V,
    ) -> Option<TypeElement> {
        let domain_enum = self.get_domain_enum(expr, var_values);
        expr.get(self.index).get_i(domain_enum)
    }
}
