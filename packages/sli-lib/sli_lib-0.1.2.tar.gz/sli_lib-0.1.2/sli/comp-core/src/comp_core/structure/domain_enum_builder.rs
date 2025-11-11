use crate::comp_core::{
    constraints::BoundVarId,
    vocabulary::{DomainEnum, DomainIndex, DomainSlice, PfuncIndex, Type, TypeEnum},
};
use std::error::Error;

use super::{TypeElement, TypeFull, TypeInterps};

pub fn domain_enum_of_element_iter<I: IntoIterator<Item = TypeElement>>(
    args: I,
    domain: &DomainSlice,
    types: &TypeInterps,
) -> Result<DomainEnum, DomainEnumErrors> {
    let mut fnc_enum_builder = DomainEnumBuilder::new(domain, types);
    for arg in args {
        fnc_enum_builder.add_type_el_arg(arg)?;
    }
    Ok(fnc_enum_builder.get_index()?)
}

pub fn domain_enum_of_element_args(
    args: &[TypeElement],
    domain: &DomainSlice,
    types: &TypeInterps,
) -> Result<DomainEnum, DomainEnumErrors> {
    let mut fnc_enum_builder = DomainEnumBuilder::new(domain, types);
    for arg in args {
        fnc_enum_builder.add_type_el_arg(*arg)?;
    }
    Ok(fnc_enum_builder.get_index()?)
}

#[derive(Debug, Clone)]
pub struct BoundVarArg {
    var: BoundVarId,
    index: usize,
}

/// Generic implemention for creating [DomainEnum]s.
/// See [DomainEnumBuilder].
#[derive(Debug, Clone)]
pub struct DomainEnumIterGeneric<'a, T, S>
where
    T: AsRef<[BoundVarArg]> + AsMut<[BoundVarArg]>,
    S: AsRef<[usize]> + AsMut<[usize]>,
{
    type_interps: &'a TypeInterps,
    domain: &'a DomainSlice,
    end: bool,
    partial_index: usize,
    vars: T,
    var_val: S,
}

impl<'a, T, S> DomainEnumIterGeneric<'a, T, S>
where
    T: AsRef<[BoundVarArg]> + AsMut<[BoundVarArg]>,
    S: AsRef<[usize]> + AsMut<[usize]>,
{
    pub fn get_type_interps(&self) -> &TypeInterps {
        self.type_interps
    }

    pub fn get_domain(&self) -> &DomainSlice {
        self.domain
    }
}

pub type DomainEnumIter<'a> = DomainEnumIterGeneric<'a, Box<[BoundVarArg]>, Box<[usize]>>;

pub type DomainEnumSingleVar<'a> = DomainEnumIterGeneric<'a, [BoundVarArg; 1], [usize; 1]>;

impl<'a> DomainEnumSingleVar<'a> {
    pub fn new<T: AsRef<TypeInterps>>(
        type_interps: &'a T,
        domain: &'a DomainSlice,
        partial_index: usize,
        arg: BoundVarArg,
    ) -> Self {
        let mut new_arg = arg.clone();
        new_arg.var = 0.into();
        Self {
            // structure,
            type_interps: type_interps.as_ref(),
            domain,
            partial_index,
            end: false,
            vars: [new_arg],
            var_val: [0],
        }
    }

    pub fn var_at(&self) -> usize {
        self.vars[0].index
    }
}

impl<'a> DomainEnumIter<'a> {
    pub fn new<T: AsRef<TypeInterps>>(
        type_interps: &'a T,
        domain: &'a DomainSlice,
        partial_index: usize,
        args_slice: &[BoundVarArg],
    ) -> Self {
        let mut vars: Box<[_]> = args_slice.into();
        // sort by var to map vars from 0 to len
        vars.sort_by_key(|f| usize::from(f.var));
        let mut cur = 0;
        let mut last_seen = None;
        for var in vars.iter_mut() {
            if let Some(last_val) = last_seen {
                if usize::from(var.var) > last_val {
                    last_seen = Some(var.var.into());
                    cur += 1;
                    var.var = cur.into();
                } else if usize::from(var.var) == last_val {
                    var.var = cur.into();
                } else {
                    // vars sorted by key
                    unreachable!()
                }
            } else {
                last_seen = Some(var.var.into());
                var.var = cur.into();
            }
        }
        // sort by index
        vars.sort_by_key(|f| f.index);
        let mut vars_count: Box<[_]> = args_slice.iter().map(|f| f.var).collect();
        vars_count.sort();
        let var_amount = if vars_count.is_empty() {
            0
        } else {
            1 + vars_count.windows(2).filter(|win| win[0] != win[1]).count()
        };
        let var_val: Box<[_]> = vec![0; var_amount].into_boxed_slice();
        Self {
            type_interps: type_interps.as_ref(),
            domain,
            partial_index,
            end: false,
            vars,
            var_val,
        }
    }
}

impl<'a, T, S> Iterator for DomainEnumIterGeneric<'a, T, S>
where
    T: AsRef<[BoundVarArg]> + AsMut<[BoundVarArg]>,
    S: AsRef<[usize]> + AsMut<[usize]>,
{
    type Item = DomainEnum;

    fn next(&mut self) -> Option<Self::Item> {
        if self.end {
            return None;
        }
        if self.vars.as_ref().len() == 0 {
            self.end = true;
            return Some(self.partial_index.into());
        }
        let mut index = self.partial_index;
        let mut increase = 1;
        let args_end = self.vars.as_ref().len();
        let mut cur_arg = 0;
        for (i, len) in self.domain.domains_len(self.type_interps).enumerate() {
            let arg = &self.vars.as_ref()[cur_arg];
            if arg.index == i {
                index += self.var_val.as_ref()[usize::from(arg.var)] * increase;
                cur_arg += 1;
                if cur_arg == args_end {
                    break;
                }
            }
            increase *= len;
        }
        let var_end = self.var_val.as_ref().len();
        let mut cur_var = 0;

        for (i, len) in self.domain.domains_len(self.type_interps).enumerate() {
            let arg = &self.vars.as_ref()[cur_var];
            if arg.index == i {
                self.var_val.as_mut()[usize::from(arg.var)] += 1;
                cur_var += 1;
                if self.var_val.as_ref()[usize::from(arg.var)] < len {
                    break;
                } else {
                    if cur_var >= var_end {
                        self.end = true;
                        break;
                    } else {
                        self.var_val.as_mut()[usize::from(arg.var)] = 0;
                    }
                }
            }
        }
        return Some(index.into());
    }
}

/// When creating [DomainEnum]s the left most argument is least significant, right most is
/// most significant. Adding arguments starts at least significant argument first towards
/// most significant argument next.
/// Concretely this means lower [DomainEnum]s represent the first values of the domain's
/// interpretation.
///
/// e.g. `type A := { a, b }.`
///
/// | A * A  |[DomainEnum]|
/// |--------|------------|
/// | (a, a) |      0     |
/// | (b, a) |      1     |
/// | (a, b) |      2     |
/// | (b, b) |      3     |
pub struct DomainEnumBuilder<'a> {
    type_interps: &'a TypeInterps,
    domain: &'a DomainSlice,
    index: usize,
    cur_dom: usize,
    cur_length: usize,
    vars: Vec<BoundVarArg>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DomainEnumErrors {
    TooManyArgs,
    TooFewArgs,
    ContainsVariables,
    WrongType,
}

impl std::fmt::Display for DomainEnumErrors {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:#?}", self)
    }
}

impl Error for DomainEnumErrors {}

impl<'a> DomainEnumBuilder<'a> {
    pub fn new(domain: &'a DomainSlice, type_interps: &'a TypeInterps) -> Self {
        let mut s = Self {
            type_interps,
            domain,
            index: 0,
            cur_dom: 0,
            cur_length: 0,
            vars: Vec::new(),
        };
        s.reset();
        s
    }

    pub fn from_struct<T>(domain: &'a DomainSlice, structure: &'a T) -> Self
    where
        T: AsRef<TypeInterps>,
    {
        Self::new(domain, structure.as_ref())
    }

    pub fn from_pfunc_id<T>(pfunc_id: PfuncIndex, structure: &'a T) -> Self
    where
        T: AsRef<TypeInterps>,
    {
        let domain = structure.as_ref().vocab().pfuncs(pfunc_id).domain;
        Self::new(domain, structure.as_ref())
    }

    pub fn from_domain_id<T>(domain_index: DomainIndex, structure: &'a T) -> Self
    where
        T: AsRef<TypeInterps>,
    {
        let domain = structure.as_ref().vocab().get_domain(domain_index);
        Self::new(domain, structure.as_ref())
    }

    pub fn add_type_el_arg(&mut self, type_element: TypeElement) -> Result<(), DomainEnumErrors> {
        if self.cur_dom >= self.domain.len() {
            return Err(DomainEnumErrors::TooManyArgs);
        }
        match type_element {
            TypeElement::Bool(b) => match b {
                false => self.add_enum_arg(0.into()),
                true => self.add_enum_arg(1.into()),
            },
            TypeElement::Int(i) => {
                let arg_type = self.domain[self.cur_dom].with_interps(self.type_interps);
                match arg_type {
                    TypeFull::Int => unimplemented!(),
                    TypeFull::IntType((_, interp)) => {
                        if let Some(type_enum) = interp.get_index_of(&i) {
                            self.add_enum_arg(type_enum.into())
                        } else {
                            Err(DomainEnumErrors::WrongType)
                        }
                    }
                    _ => Err(DomainEnumErrors::WrongType),
                }
            }
            TypeElement::Real(r) => {
                let arg_type = self.domain[self.cur_dom].with_interps(self.type_interps);
                match arg_type {
                    TypeFull::Real => unimplemented!(),
                    TypeFull::RealType((_, interp)) => {
                        if let Some(type_enum) = interp.get_index_of(&r) {
                            self.add_enum_arg(type_enum.into())
                        } else {
                            Err(DomainEnumErrors::WrongType)
                        }
                    }
                    _ => Err(DomainEnumErrors::WrongType),
                }
            }
            TypeElement::Custom(t_el) => {
                if self
                    .cur_type()
                    .type_index()
                    .map(|f| f != t_el.0)
                    .unwrap_or(false)
                {
                    return Err(DomainEnumErrors::WrongType);
                }
                self.add_enum_arg(t_el.1)
            }
        }
    }

    pub fn cur_type(&self) -> &Type {
        &self.domain[self.cur_arg_index()]
    }

    pub fn add_var(&mut self, var: BoundVarId) -> Result<(), DomainEnumErrors> {
        if self.cur_dom >= self.domain.len() {
            return Err(DomainEnumErrors::TooManyArgs);
        }
        self.vars.push(BoundVarArg {
            index: self.cur_dom,
            var,
        });
        self.next_arg();
        Ok(())
    }

    pub fn get_index(&self) -> Result<DomainEnum, DomainEnumErrors> {
        if self.cur_dom < self.domain.len() {
            return Err(DomainEnumErrors::TooFewArgs);
        }
        if self.vars.len() != 0 {
            return Err(DomainEnumErrors::ContainsVariables);
        }
        return Ok(self.index.into());
    }

    pub fn iter_indexes(&mut self) -> DomainEnumIter<'a> {
        DomainEnumIter::new(self.type_interps, self.domain, self.index, &self.vars)
    }

    pub fn iter_single_var_indexes(&mut self) -> Option<DomainEnumSingleVar<'a>> {
        if self.vars.len() != 1 {
            None
        } else {
            Some(DomainEnumSingleVar::new(
                self.type_interps,
                self.domain,
                self.index,
                self.vars[0].clone(),
            ))
        }
    }

    pub fn add_enum_arg(&mut self, type_enum: TypeEnum) -> Result<(), DomainEnumErrors> {
        if self.cur_dom >= self.domain.len() {
            return Err(DomainEnumErrors::TooManyArgs);
        }
        self.index += usize::from(type_enum) * self.cur_length;
        self.next_arg();
        Ok(())
    }

    pub fn cur_arg_index(&self) -> usize {
        self.cur_dom
    }

    fn next_arg(&mut self) {
        let len = self.domain[self.cur_dom].len(self.type_interps);
        // increase cur length since next arguments are more significant
        self.cur_length *= len;
        self.cur_dom += 1;
    }

    pub fn reset(&mut self) {
        // we start our cur length at max since the first argument is the least significant arg
        // let cur_length = self.domain.domain_len(self.type_interps);
        self.cur_length = 1;
        self.cur_dom = 0;
        self.index = 0;
        self.vars.drain(..);
    }
}

#[allow(unused)]
#[cfg(test)]
mod tests {
    #![allow(non_snake_case)]
    use super::{DomainEnumBuilder, DomainEnumErrors, TypeElement};
    use crate::comp_core::{
        constraints::BoundVarId,
        structure::{LexTypeEnumIter, PartialStructure, TypeElementIndex, UnfinishedStructure},
        vocabulary::{DomainEnum, Vocabulary},
    };
    use crate::utils::tests::{vocab_add_domain, vocab_add_types};
    use std::error::Error;

    macro_rules! domain_enum_builder_test {
        (
            $($name:ident: {
                    types: {
                        $($types:tt)*
                    },
                    domain: {$($domain:tt)*} ,
                    expected: $expected:tt $(,)?
                }
            ,)+
        ) => {
            $(
                #[allow(warnings)]
                #[test]
                fn $name() -> Result<(), Box<dyn Error>> {
                    use crate::comp_core::structure::{TypeElement, TypeElementIndex};
                    use TypeElement::Bool as Bool;
                    use TypeElement::Int as Int;
                    use TypeElement::Real as Real;
                    use TypeElement::Custom as Custom;
                    use TypeElementIndex as TI;
                    let mut vocab = Vocabulary::new();
                    let mut u_structure = UnfinishedStructure::new();
                    vocab_add_types!({$($types)*}, &mut vocab, &mut u_structure);
                    let dom_id = vocab_add_domain!($($domain)*, &mut vocab);
                    let structure = PartialStructure::new(u_structure.finish(vocab.into())?.into());

                    domain_enum_builder_test!(
                        test $expected, dom_id, structure
                    )
                }
            )+
        };
        (test
         {
            $(
                ( [$($args:expr),* $(,)?], [$($expected:expr),+])
            ),+ $(,)?,
         },
         $dom:ident, $struct:ident) => {
            {
            let mut builder = DomainEnumBuilder::from_domain_id($dom, &$struct);
            let expected = vec![$(($($args,)*),)*];
            let args_expected = [
                $(
                    (
                        [
                        $(
                            PfuncArg::from($args),
                         )*
                        ],
                        [$($expected,)+],
                    ),
                )+
            ];
            for ((args, expected), str_args) in args_expected.into_iter().zip(expected) {
                // test Errors
                for arg in args.iter() {
                    assert_eq!(DomainEnumErrors::TooFewArgs,
                               builder.get_index().unwrap_err());
                    match arg {
                        PfuncArg::Element(s) => builder.add_type_el_arg(s.clone())?,
                        PfuncArg::Var(s) => builder.add_var(*s)?,
                    }
                }

                println!("args: {:?}", &str_args);
                if expected.len() == 1 {
                    // test full index when only one when expected
                    assert_eq!(DomainEnum::from(expected[0]), builder.get_index()?);
                } else {
                    // test full index when only multiple indexes expected
                    assert_eq!(
                        DomainEnumErrors::ContainsVariables, builder.get_index().unwrap_err());
                }
                let mut it = builder.iter_indexes();
                for expec in expected {
                    assert_eq!(Some(DomainEnum::from(expec)), it.next());
                }
                assert_eq!(None, it.next());

                if args.iter().filter(|f| matches!(f, PfuncArg::Var(_))).count() != 1 {
                    assert!(builder.iter_single_var_indexes().is_none());
                } else {
                    let mut it = builder.iter_single_var_indexes().unwrap();
                    for expec in expected {
                        assert_eq!(Some(DomainEnum::from(expec)), it.next());
                    }
                    assert_eq!(None, it.next());
                }
                builder.reset();
            }
            Ok(())
            }
        };
        (test {$(( [$($args:expr),* $(,)?], $expected:expr)),+ $(,)?,},
         $dom:ident, $struct:ident) => {
            domain_enum_builder_test!(
                test {$(( [$($args,)*], [$expected]),)+, }, $dom, $struct
                )
        };
    }

    enum PfuncArg {
        Element(TypeElement),
        Var(BoundVarId),
    }

    impl From<TypeElement> for PfuncArg {
        fn from(value: TypeElement) -> Self {
            Self::Element(value)
        }
    }

    impl From<TypeElementIndex> for PfuncArg {
        fn from(value: TypeElementIndex) -> Self {
            Self::Element(value.into())
        }
    }

    impl From<BoundVarId> for PfuncArg {
        fn from(value: BoundVarId) -> Self {
            Self::Var(value)
        }
    }

    impl From<usize> for PfuncArg {
        fn from(value: usize) -> Self {
            Self::Var(BoundVarId::from(value))
        }
    }

    // numbers in args represent variables

    domain_enum_builder_test! {
        test_domain_enum_basic_1: {
            types: {
                type 0 := { a, b, } isa { BaseType::Str }
            },
            domain: {
                0
            },
            expected: {
                ([TI::from((0, 0))], 0),
                ([TI::from((0, 1))], 1),
            }
        },
        test_domain_enum_basic_2: {
            types: {
                type 0 := { a, b, } isa { BaseType::Str }
            },
            domain: {
                0 * 0 * 0
            },
            expected: {
                ([TI::from((0, 0)), TI::from((0, 0)), TI::from((0, 0))], 0),
                ([TI::from((0, 1)), TI::from((0, 0)), TI::from((0, 0))], 1),
                ([TI::from((0, 0)), TI::from((0, 1)), TI::from((0, 0))], 2),
                ([TI::from((0, 1)), TI::from((0, 1)), TI::from((0, 0))], 3),
                ([TI::from((0, 0)), TI::from((0, 0)), TI::from((0, 1))], 4),
                ([TI::from((0, 1)), TI::from((0, 0)), TI::from((0, 1))], 5),
                ([TI::from((0, 0)), TI::from((0, 1)), TI::from((0, 1))], 6),
                ([TI::from((0, 1)), TI::from((0, 1)), TI::from((0, 1))], 7),
            }
        },
        test_domain_enum_basic_3: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { 1, 2 } isa { BaseType::Int }
            },
            domain: {
                0 * 1
            },
            expected: {
                ([TI::from((0, 0)), TI::from((1, 0))], 0),
                ([TI::from((0, 1)), TI::from((1, 0))], 1),
                ([TI::from((0, 0)), TI::from((1, 1))], 2),
                ([TI::from((0, 1)), TI::from((1, 1))], 3),
            }
        },
        test_domain_enum_basic_4: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { a1, a2 } isa { BaseType::Str }
            },
            domain: {
                0 * 1
            },
            expected: {
                ([TI::from((0, 0)), TI::from((1, 0))], 0),
                ([TI::from((0, 1)), TI::from((1, 0))], 1),
                ([TI::from((0, 0)), TI::from((1, 1))], 2),
                ([TI::from((0, 1)), TI::from((1, 1))], 3),
            }
        },
        test_domain_enum_basic_5: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { x, y, z } isa { BaseType::Str }
            },
            domain: {
                0 * 1
            },
            expected: {
                ([TI::from((0, 0)), TI::from((1, 0))], 0),
                ([TI::from((0, 1)), TI::from((1, 0))], 1),
                ([TI::from((0, 0)), TI::from((1, 1))], 2),
                ([TI::from((0, 1)), TI::from((1, 1))], 3),
                ([TI::from((0, 0)), TI::from((1, 2))], 4),
                ([TI::from((0, 1)), TI::from((1, 2))], 5),
            }
        },
        test_domain_enum_basic_6: {
            types: {},
            domain: {

            },
            expected: {
                ([], 0),
            }
        },
        test_domain_enum_vars_1: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            domain: {
                0 * 0
            },
            expected: {
                ([TI::from((0, 0)), 0], [0, 2]),
                ([TI::from((0, 1)), 10], [1, 3]),
            }
        },
        test_domain_enum_vars_2: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            domain: {
                0 * 0
            },
            expected: {
                ([0, TI::from((0, 0))], [0, 1]),
                ([3, TI::from((0, 1))], [2, 3]),
            }
        },
        test_domain_enum_vars_3: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            domain: {
                0 * 0
            },
            expected: {
                ([1, 0], [0, 1, 2, 3]),
                ([0, 1], [0, 1, 2, 3]),
                ([2, 234], [0, 1, 2, 3]),
            }
        },
        test_domain_enum_vars_4: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { c, d, e } isa { BaseType::Str }
            },
            domain: {
                0 * 1
            },
            expected: {
                ([1, 0], [0, 1, 2, 3, 4, 5]),
            }
        },
        test_domain_enum_vars_5: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            domain: {
                0 * 0
            },
            expected: {
                ([0, 0], [0, 3]),
                ([3, 3], [0, 3]),
            }
        },
    }

    macro_rules! type_element_iter_test {
        (
            $($name:ident: {
                    types: {
                        $($types:tt)*
                    },
                    domain: {$($domain:tt)*} ,
                    expected: $expected:tt $(,)?
                }
            ,)+
        ) => {
            $(
                #[allow(warnings)]
                #[test]
                fn $name() -> Result<(), Box<dyn Error>> {
                    let mut vocab = Vocabulary::new();
                    let mut u_structure = UnfinishedStructure::new();
                    vocab_add_types!({$($types)*}, &mut vocab, &mut u_structure);
                    let dom_id = vocab_add_domain!($($domain)*, &mut vocab);
                    let structure = PartialStructure::new(u_structure.finish(vocab.into())?.into());

                    type_element_iter_test!(
                        test $expected, dom_id, structure
                    )
                }
            )+
        };
        (
            test
            {$(
                (
                    $dom_enum:literal,
                    [$($type_el:expr),*]
                )
              ),+ $(,)?
            },
         $dom:ident, $struct:ident
        ) => {
            {
                let structure = $struct;
                let dom = structure.vocab().get_domain($dom);
                let arg_expected = [
                    $(
                        (
                            DomainEnum::from($dom_enum),
                            [
                                $($type_el,)*
                            ]
                        ),
                    )+
                ];
                for (arg, expected) in arg_expected {
                    let mut it = structure.type_interps().type_element_iter(
                        dom,
                        arg);
                    for expec in expected {
                        assert_eq!(Some(expec), it.next());
                    }
                    assert_eq!(None, it.next());
                }
                Ok(())
            }
        };
    }

    macro_rules! lex_type_enum_iter_test {
        (
            $($name:ident: {
                    types: {
                        $($types:tt)*
                    },
                    domain: {$($domain:tt)*} ,
                    expected: $expected:tt $(,)?
                }
            ,)+
        ) => {
            $(
                #[allow(warnings)]
                #[test]
                fn $name() -> Result<(), Box<dyn Error>> {
                    let mut vocab = Vocabulary::new();
                    let mut u_structure = UnfinishedStructure::new();
                    vocab_add_types!({$($types)*}, &mut vocab, &mut u_structure);
                    let dom_id = vocab_add_domain!($($domain)*, &mut vocab);
                    let structure = PartialStructure::new(u_structure.finish(vocab.into())?.into());

                    lex_type_enum_iter_test!(
                        test $expected, dom_id, structure
                    )
                }
            )+
        };
        (
            test
            {$(
                (
                    $dom_enum:literal,
                    [$($type_el:expr),*]
                )
              ),+ $(,)?
            },
         $dom:ident, $struct:ident
        ) => {
            {
                let structure = $struct;
                let dom = structure.vocab().get_domain($dom);
                let arg_expected = [
                    $(
                        (
                            DomainEnum::from($dom_enum),
                            [
                                $($type_el.into(),)*
                            ]
                        ),
                    )+
                ];
                for (arg, expected) in arg_expected {
                    let mut it = LexTypeEnumIter::new(
                        structure.type_interps(),
                        dom,
                        arg
                    );
                    println!("{:?}:", arg);
                    for expec in expected {
                        let value = it.next();
                        println!("    {:?} {:?}", Some(expec), value);
                        assert_eq!(Some(expec), value);
                    }
                    assert_eq!(None, it.next());
                }
                Ok(())
            }
        };
    }

    use TypeElement::Custom;

    type_element_iter_test! {
        test_type_element_iter_1: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            domain: {
                0
            },
            expected: {
                (0, [TypeElement::Custom((0, 0).into())]),
                (1, [TypeElement::Custom((0, 1).into())]),
            },
        },
        test_type_element_iter_2: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            domain: {
                0 * 0
            },
            expected: {
                (0, [Custom((0, 0).into()), Custom((0, 0).into())]),
                (1, [Custom((0, 1).into()), Custom((0, 0).into())]),
                (2, [Custom((0, 0).into()), Custom((0, 1).into())]),
                (3, [Custom((0, 1).into()), Custom((0, 1).into())]),
            },
        },
        test_type_element_iter_3: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { c, d } isa { BaseType::Str }
            },
            domain: {
                0 * 1
            },
            expected: {
                (0, [Custom((0, 0).into()), Custom((1, 0).into())]),
                (1, [Custom((0, 1).into()), Custom((1, 0).into())]),
                (2, [Custom((0, 0).into()), Custom((1, 1).into())]),
                (3, [Custom((0, 1).into()), Custom((1, 1).into())]),
            },
        },
        test_type_element_iter_4: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { c, d, e } isa { BaseType::Str }
            },
            domain: {
                0 * 1
            },
            expected: {
                (0, [Custom((0, 0).into()), Custom((1, 0).into())]),
                (1, [Custom((0, 1).into()), Custom((1, 0).into())]),
                (2, [Custom((0, 0).into()), Custom((1, 1).into())]),
                (3, [Custom((0, 1).into()), Custom((1, 1).into())]),
                (4, [Custom((0, 0).into()), Custom((1, 2).into())]),
                (5, [Custom((0, 1).into()), Custom((1, 2).into())]),
            },
        },
        test_type_element_iter_5: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { 0, 1, 2 } isa { BaseType::Int }
            },
            domain: {
                0 * 1
            },
            expected: {
                (0, [Custom((0, 0).into()), 0.into()]),
                (1, [Custom((0, 1).into()), 0.into()]),
                (2, [Custom((0, 0).into()), 1.into()]),
                (3, [Custom((0, 1).into()), 1.into()]),
                (4, [Custom((0, 0).into()), 2.into()]),
                (5, [Custom((0, 1).into()), 2.into()]),
            },
        },
        test_type_element_iter_6: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { -1, 1, 2 } isa { BaseType::Int }
            },
            domain: {
                0 * 1
            },
            expected: {
                (0, [Custom((0, 0).into()), (-1).into()]),
                (1, [Custom((0, 1).into()), (-1).into()]),
                (2, [Custom((0, 0).into()), 1.into()]),
                (3, [Custom((0, 1).into()), 1.into()]),
                (4, [Custom((0, 0).into()), 2.into()]),
                (5, [Custom((0, 1).into()), 2.into()]),
            },
        },
    }
    lex_type_enum_iter_test! {
        test_lex_type_enum_iter_1: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            domain: {
                0
            },
            expected: {
                (0, [0]),
                (1, [1]),
            },
        },
        test_lex_type_enum_iter_2: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
            },
            domain: {
                0 * 0
            },
            expected: {
                (0, [0, 0]),
                (1, [0, 1]),
                (2, [1, 0]),
                (3, [1, 1]),
            },
        },
        test_lex_type_enum_iter_3: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { c, d } isa { BaseType::Str }
            },
            domain: {
                0 * 1
            },
            expected: {
                (0, [0, 0]),
                (1, [0, 1]),
                (2, [1, 0]),
                (3, [1, 1]),
            },
        },
        test_lex_type_enum_iter_4: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { c, d, e } isa { BaseType::Str }
            },
            domain: {
                0 * 1
            },
            expected: {
                (0, [0, 0]),
                (1, [0, 1]),
                (2, [1, 0]),
                (3, [1, 1]),
                (4, [2, 0]),
                (5, [2, 1]),
            },
        },
        test_lex_type_enum_iter_5: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { 0, 1, 2 } isa { BaseType::Int }
            },
            domain: {
                0 * 1
            },
            expected: {
                (0, [0, 0]),
                (1, [0, 1]),
                (2, [1, 0]),
                (3, [1, 1]),
                (4, [2, 0]),
                (5, [2, 1]),
            },
        },
        test_lex_type_enum_iter_6: {
            types: {
                type 0 := { a, b } isa { BaseType::Str }
                type 1 := { -1, 1, 2 } isa { BaseType::Int }
            },
            domain: {
                0 * 1
            },
            expected: {
                (0, [0, 0]),
                (1, [0, 1]),
                (2, [1, 0]),
                (3, [1, 1]),
                (4, [2, 0]),
                (5, [2, 1]),
            },
        },
    }
}
