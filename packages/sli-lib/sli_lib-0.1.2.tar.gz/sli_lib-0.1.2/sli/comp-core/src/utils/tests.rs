// TODO use proper functions instead of this garbage
// TODO create proper functions instead of this garbage
// wait what?
// Intended to be used in testing macros
#![allow(unused)]

macro_rules! vocab_add_types {
    (
        {},
        $vocab:expr,
        $unstruct:expr $(,)?
    ) => {
        {
            ()
        }
    };
    (
        {
            $($rest:tt)*
        },
        $vocab:expr,
        $unstruct:expr $(,)?
    ) => {
        vocab_add_types!(munch {$($rest)*}, $vocab, $unstruct)
    };
    (
        munch {},
        $vocab:expr,
        $unstruct:expr $(,)?
    ) => {()};
    (
        munch
        {
            type $type_name:literal $(:= { $($type_e:expr),+ $(,)? })? isa { $base:expr }
            $($tail:tt)*
        },
        $vocab:expr,
        $unstruct:expr $(,)?
    ) => {
        {
            #[allow(warnings)]
            'end_outer: {
                vocab_add_types!(
                    type $type_name $(:= { $($type_e),+ })? isa { $base }, $vocab, $unstruct);
                vocab_add_types!(munch {$($tail)*}, $vocab, $unstruct);
            }
        }
    };
    (
        type $type_name:literal $(:= { $($type_e:expr),+ $(,)? })? isa { $base:expr },
        $vocab:expr,
        $unstruct:expr $(,
            $to_vocab:expr
        )?
    ) => {
        {
            #[allow(warnings)]
            'end: {
                use crate::comp_core::{
                    structure::{TypeInterp, UnfinishedStructure},
                    vocabulary::{BaseType, TypeDecl, Vocabulary},
                };
                use indexmap::IndexSet;
                use paste::paste;
                let vocab: &mut Vocabulary = $vocab;
                let unfinished_struct: &mut UnfinishedStructure = $unstruct;
                paste! {
                    let [<type_name $type_name>] = vocab.add_type_decl(TypeDecl {
                        super_type: $base,
                    });
                    $(
                        crate::utils::tests::structure_add_type_interp!(
                            $type_name := { $($type_e),* }. &*vocab, unfinished_struct);
                    )?
                    let interp = unfinished_struct.get_interp([<type_name $type_name>]);
                }
            }
        }
    };
}

macro_rules! vocab_add_domain {
    (, $vocab:expr $(,)?) => {
        {
            #[allow(warnings)]
            'end: {
                use crate::comp_core::vocabulary::{Type, DeclIndex};
                let vocab: &mut Vocabulary = $vocab;
                let mut domain: [Type; 0] = [];
                vocab.add_domain(domain)
            }
        }
    };
    ($first_domain:literal $(* $rest:literal)* , $vocab:expr $(,)?) => {
        {
            #[allow(warnings)]
            'end: {
                use crate::comp_core::vocabulary::{Type, TypeIndex, DeclIndex, BaseType};
                let vocab: &mut Vocabulary = $vocab;
                let mut domain = [
                    {
                        let type_id = TypeIndex::from($first_domain);
                        match vocab.types[type_id].super_type {
                            BaseType::Str => Type::Str(type_id),
                            BaseType::Int => Type::IntType(type_id),
                            BaseType::Real => Type::RealType(type_id),
                        }
                    },
                    $(
                        {
                            let type_id = TypeIndex::from($rest);
                            match vocab.types[type_id].super_type {
                                BaseType::Str => Type::Str(type_id),
                                BaseType::Int => Type::IntType(type_id),
                                BaseType::Real => Type::RealType(type_id),
                            }
                        },
                    )*
                ];
                vocab.add_domain(domain)
            }
        }
    };
}

macro_rules! structure_add_type_interp {
    (
        {
        },
        $vocab:expr,
        $structure:expr $(,)?
    ) => {
        {
            ()
        }
    };
    (
        {
            $($interps:tt)*
        },
        $vocab:expr,
        $structure:expr $(,)?
    ) => {
        structure_add_type_interp!(
            munch {
                $($interps)*
            },
            $vocab, $structure)
    };
    (
        munch
        {
        },
        $vocab:expr,
        $structure:expr $(,)?
    ) => {};
    (
        munch
        {
            $type_name:literal := { $($type_e:expr),* }.
            $($tail:tt)*
        },
        $vocab:expr,
        $structure:expr $(,)?
    ) => {
        {
            #[allow(warnings)]
            'end: {
                structure_add_type_interp!(
                    $type_name := { $($type_e),* }.
                    $vocab, $structure);
                structure_add_type_interp!(
                    munch
                    {
                        $($tail::t)*
                    },
                    $vocab, $structure);
            }
        }
    };
    (
        $type_name:literal := { $($type_e:expr),* }.
        $vocab:expr,
        $un_structure:expr $(,)?
    ) => {
        {
        #[allow(warnings)]
        'end:
            {
                use crate::comp_core::structure::{
                    IntInterp, StrInterp, TypeInterp, UnfinishedStructure, RealInterp,
                };
                use crate::comp_core::vocabulary::{BaseType, DeclIndex, Type, TypeIndex, Vocabulary};
                use crate::comp_core::Real;
                use indexmap::IndexSet;
                let vocab: &Vocabulary = $vocab.into();
                let un_structure: &mut UnfinishedStructure = $un_structure.into();
                let type_index = TypeIndex::from($type_name);
                let base_type = vocab.types[type_index].super_type;
                let interp = match base_type {
                    BaseType::Int => {
                        TypeInterp::Int(match IntInterp::try_from_iterator(
                                [
                                $(
                                    match stringify!($type_e).parse() {
                                        Ok(i) => i,
                                        Err(e) => panic!(),
                                    },
                                    )+
                                ]) { Ok(i) => i.into(), Err(e) => panic!() })
                    }
                    BaseType::Real => {
                        TypeInterp::Real(match vec![
                                    $(
                                        stringify!($type_e).parse::<Real>(),
                                    )+
                                ].into_iter()
                                .collect::<Result<RealInterp, _>>() {
                                    Ok(i) => i.into(),
                                    Err(e) => panic!()
                                })
                    }
                    BaseType::Str => {
                        TypeInterp::Custom(StrInterp::new(
                                [
                                $(
                                    stringify!($type_e),
                                    )+
                                ].len()).into())
                    }
                };
                un_structure.add_type_interp(type_index, interp);
            }
        }
    };
}

macro_rules! vocab_add_pfunc_decl {
    (
        $type_name:literal: $($first_domain:literal $(* $rest:literal)*)? -> $codomain:expr,
        $vocab:expr $(,)?
    ) => {
        {
            #[allow(warnings)]
            'end: {
                use crate::comp_core::vocabulary::{PfuncDecl, Type};
                use crate::utils::tests::vocab_add_domain;
                let vocab: &mut Vocabulary = $vocab.into();
                let codomain = $codomain;
                let domain = vocab_add_domain!{
                    $($first_domain $(* $rest)*)?, vocab
                };
                vocab.add_pfunc_decl(
                    PfuncDecl {
                        codomain,
                        domain,
                    }
                )
            }
        }
    };
}

pub(crate) use structure_add_type_interp;
pub(crate) use vocab_add_domain;
pub(crate) use vocab_add_pfunc_decl;
pub(crate) use vocab_add_types;

#[cfg(test)]
mod tests {
    use std::error::Error;

    use crate::comp_core::{
        structure::{PartialStructure, UnfinishedStructure},
        vocabulary::{
            BaseType, DeclIndex, Domain, DomainSlice, Symbol, Type, TypeIndex, Vocabulary,
        },
    };

    #[test]
    fn add_type() {
        let mut vocab = Vocabulary::new();
        let mut un_struct = UnfinishedStructure::new();
        vocab_add_types!(
            type 0 := { a, b, c } isa { BaseType::Str }, &mut vocab, &mut un_struct
        );

        assert_eq!(vocab.types.len(), 1);
        assert_eq!(vocab.types[TypeIndex::from(0)].super_type, BaseType::Str);

        un_struct.has_type_interpretation(0.into());

        let structure = PartialStructure::new(un_struct.finish(vocab.into()).unwrap().into());
        let interp = &structure.type_interps()[TypeIndex::from(0)];
        let expected_len = 3;
        assert_eq!(interp.len(), expected_len);
    }

    #[test]
    fn add_types() {
        let mut vocab = Vocabulary::new();
        let mut un_struct = UnfinishedStructure::new();
        vocab_add_types!(
            {
                type 0 := { a, b, c } isa { BaseType::Str }
                type 1 := { d, e, f, } isa { BaseType::Str }
            },
            &mut vocab, &mut un_struct
        );

        vocab_add_types!({}, &mut vocab, &mut un_struct);

        assert_eq!(vocab.types.len(), 2);
        let type_a = TypeIndex::from(0);
        let type_b = TypeIndex::from(1);
        assert_eq!(vocab.types[type_a].super_type, BaseType::Str);
        assert_eq!(vocab.types[type_b].super_type, BaseType::Str);
        un_struct.has_type_interpretation(type_a);
        un_struct.has_type_interpretation(type_b);
        let structure = PartialStructure::new(un_struct.finish(vocab.into()).unwrap().into());
        let interp_check = [(type_a, 3), (type_b, 3)];
        for (type_id, expected_len) in interp_check {
            let interp = &structure.type_interps()[type_id];
            assert_eq!(interp.len(), expected_len)
        }
    }

    #[test]
    fn add_domain() {
        let mut vocab = Vocabulary::new();
        let mut un_struct = UnfinishedStructure::new();
        vocab_add_types!(
            type 0 isa { BaseType::Str }, &mut vocab, &mut un_struct
        );
        let type_id = TypeIndex::from(0);
        let dom_id1 = vocab_add_domain!(0 * 0, &mut vocab);
        let dom_id2 = vocab_add_domain!(0, &mut vocab);
        assert_eq!(
            vocab.get_domain(dom_id1),
            &Domain([Type::Str(type_id), Type::Str(type_id)])
        );
        assert_eq!(vocab.get_domain(dom_id2), &Domain([Type::Str(type_id)]));
    }

    #[test]
    fn add_structure_types() {
        let mut vocab = Vocabulary::new();
        let mut un_struct = UnfinishedStructure::new();
        vocab_add_types!(
            type 0 isa { BaseType::Str }, &mut vocab, &mut un_struct
        );
        assert!(!un_struct.has_type_interpretation(0.into()));

        structure_add_type_interp!(
            {
                0 := { a, b, c}.
            },
            &vocab,
            &mut un_struct,
        );

        structure_add_type_interp!({}, &vocab, &mut un_struct,);

        assert!(un_struct.has_type_interpretation(0.into()));

        let structure = PartialStructure::new(un_struct.finish(vocab.into()).unwrap().into());
        let interp = &structure.type_interps()[TypeIndex::from(0)];
        let expected_len = 3;
        assert_eq!(interp.len(), expected_len);
    }

    #[test]
    fn add_func_decl() {
        let mut vocab = Vocabulary::new();
        let mut un_struct = UnfinishedStructure::new();
        vocab_add_types! {
            type 0 isa { BaseType::Str}, &mut vocab, &mut un_struct
        };
        let type_id = Type::Str(TypeIndex::from(0));
        let id = vocab_add_pfunc_decl! {
            0: 0 * 0 -> Type::Int,  &mut vocab
        };

        let const_id = vocab_add_pfunc_decl! {
            1: -> Type::Int,  &mut vocab
        };

        let symbol_1 = vocab.pfuncs(id);
        let symbol_2 = vocab.pfuncs(const_id);
        let domain = Domain([type_id, type_id]);
        assert!(matches! {
            symbol_1,
            Symbol {
                domain,
                codomain: Type::Int,
                index: id,
                ..
            }
        });
        assert!(matches! {
            symbol_2,
            Symbol {
                domain: Domain([]),
                codomain: Type::Int,
                index: const_id,
                ..
            }
        });
    }
}
