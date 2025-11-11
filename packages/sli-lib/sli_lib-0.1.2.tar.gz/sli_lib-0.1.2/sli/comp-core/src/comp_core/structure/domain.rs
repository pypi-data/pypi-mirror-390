use super::TypeInterps;
use crate::comp_core::vocabulary::{Domain, DomainSlice};
use sli_collections::{iterator::Iterator, rc::Rc};

pub struct DomainFull<D: AsRef<DomainSlice>, T: AsRef<TypeInterps>> {
    inner: D,
    type_interps: T,
}

impl<D: AsRef<DomainSlice>, T: AsRef<TypeInterps>> DomainFull<D, T> {
    pub fn domain_len(&self) -> usize {
        Domain::domain_len(self.inner.as_ref(), self.type_interps.as_ref())
    }

    pub fn domains_len<'a>(
        &'a self,
    ) -> impl Iterator<Item = usize> + ExactSizeIterator + DoubleEndedIterator + 'a {
        Domain::domains_len(self.inner.as_ref(), self.type_interps.as_ref())
    }
}

pub type DomainOwned = DomainFull<Box<DomainSlice>, Rc<TypeInterps>>;
