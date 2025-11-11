use super::Transformer;
use crate::comp_core::{constraints::NodeIndex, expression::ExpressionRef};

pub struct CopyTransform;

impl<'a> Transformer<'a> for CopyTransform {
    fn transform_expression(
        &mut self,
        from_expr: ExpressionRef<'a>,
        expr_transformer: &mut super::tranform_assistor::ExpressionTransformer,
    ) -> NodeIndex {
        expr_transformer.rec_copy(from_expr)
    }
}
