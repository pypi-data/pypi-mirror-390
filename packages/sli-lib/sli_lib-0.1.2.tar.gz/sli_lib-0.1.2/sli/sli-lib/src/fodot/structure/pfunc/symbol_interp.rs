macro_rules! create_big_enum {
    (
        // $partial_owned:ident,
        $partial_im:ident,
        $partial_mut:ident,
        // $partial_nullary_owned:ident,
        $partial_nullary_immutable:ident,
        $partial_nullary_mutable:ident,
        // $partial_func_owned:ident,
        $partial_func_immutable:ident,
        $partial_func_mutable:ident,
        // $complete_owned:ident,
        $complete_im:ident,
        $complete_mut:ident,
        // $complete_nullary_owned:ident,
        $complete_nullary_immutable:ident,
        $complete_nullary_mutable:ident,
        // $complete_func_owned:ident,
        $complete_func_immutable:ident,
        $complete_func_mutable:ident,
        $(
            $e_interp:ident: [
                {
                    $(nullary: $nullary_tag:literal,)?
                    $(func: $func_tag:literal,)?
                },
                // $part_owned_interp_ty:ty,
                $part_im_interp_ty:ty,
                $part_mut_interp_ty:ty,
                // $complete_owned_interp_ty:ty,
                $complete_im_interp_ty:ty,
                $complete_mut_interp_ty:ty,
                $unwrap_func:ident,
            ]
        ),* $(,)?
    ) => {
        create_big_enum! {
            create_iterator:
            /// An iterator for symbol interpetations.
            SymbolIter,
            $(
                $e_interp: (true),
            )*
        }
        create_big_enum! {
            create_iterator:
            FuncIter,
            $($(
                $e_interp: ($func_tag),
            )?)*
        }
        // // Not needed currently
        // create_big_enum! {
        //     create_iterator:
        //     NullaryIter,
        //     $($(
        //         $e_interp: ($nullary_tag),
        //     )?)*
        // }

        // // Partial owned
        // create_big_enum! {
        //     create:
        //     #[derive(Clone, Debug)]
        //     $partial_owned,
        //     partial_symbol_owned,
        //     $(
        //         $e_interp: (true, $part_owned_interp_ty),
        //     )*
        // }
        // create_big_enum! {
        //     partial_symbol_im_impls:
        //     partial_symbol_owned::$partial_owned<'a>,
        //     complete_symbol_immutable::$complete_im,
        //     complete_symbol_owned::$complete_owned,
        //     partial_nullary_owned::$partial_nullary_owned,
        //     partial_func_owned::$partial_func_owned,
        //     partial_symbol_owned::$partial_owned,
        //     SymbolIter,
        //     $($(
        //         $e_interp: ($nullary_tag, $part_owned_interp_ty, partial_nullary_owned::$partial_nullary_owned, Left),
        //     )?)*
        //     $($(
        //         $e_interp: ($func_tag, $part_owned_interp_ty, partial_func_owned::$partial_func_owned, Right),
        //     )?)*
        // }
        // create_big_enum! {
        //     partial_mut_impls:
        //     partial_symbol_owned::$partial_owned<'a>,
        //     $(
        //         $e_interp: (true, $part_owned_interp_ty),
        //     )*
        // }
        //
        // // partial nullary owned
        // create_big_enum! {
        //     create:
        //     #[derive(Clone, Debug)]
        //     $partial_nullary_owned,
        //     partial_nullary_owned,
        //     $($(
        //         $e_interp: ($nullary_tag, $part_owned_interp_ty),
        //     )?)*
        // }
        // create_big_enum! {
        //     partial_nullary_im_impls:
        //     partial_nullary_owned::$partial_nullary_owned<'a>,
        //     complete_nullary_immutable::$complete_nullary_immutable,
        //     complete_nullary_owned::$complete_nullary_owned,
        //     $($(
        //         $e_interp: ($nullary_tag, $part_owned_interp_ty),
        //     )?)*
        // }
        // create_big_enum! {
        //     partial_nullary_mut_impls:
        //     partial_nullary_owned::$partial_nullary_owned<'a>,
        //     $($(
        //         $e_interp: ($nullary_tag, $part_owned_interp_ty),
        //     )?)*
        // }
        //
        // // partial func owned
        // create_big_enum! {
        //     create:
        //     #[derive(Clone, Debug)]
        //     $partial_func_owned,
        //     partial_func_owned,
        //     $($(
        //         $e_interp: ($func_tag, $part_owned_interp_ty),
        //     )?)*
        // }
        // create_big_enum! {
        //     partial_im_impls:
        //     partial_func_owned::$partial_func_owned<'a>,
        //     complete_func_immutable::$complete_func_immutable,
        //     complete_func_owned::$complete_func_owned,
        //     partial_func_owned::$partial_func_owned,
        //     FuncIter,
        //     $($(
        //         $e_interp: ($func_tag, $part_owned_interp_ty),
        //     )?)*
        // }
        // create_big_enum! {
        //     partial_mut_impls:
        //     partial_func_owned::$partial_func_owned<'a>,
        //     $($(
        //         $e_interp: ($func_tag, $part_owned_interp_ty),
        //     )?)*
        // }

        // Partial immutable
        create_big_enum! {
            create:
            /// A partial immutable symbol interpretation.
            ///
            /// See also: [partial::mutable::SymbolInterp],
            /// [complete::immutable::SymbolInterp] and
            /// [complete::mutable::SymbolInterp].
            #[derive(Clone, Debug)]
            $partial_im,
            partial_symbol_immutable,
            $(
                $e_interp: (true, $part_im_interp_ty),
            )*
        }
        create_big_enum! {
            partial_symbol_im_impls:
            partial_symbol_immutable::$partial_im<'a>,
            complete_symbol_immutable::$complete_im,
            complete_symbol_immutable::$complete_im,
            partial_nullary_immutable::$partial_nullary_immutable,
            partial_func_immutable::$partial_func_immutable,
            SymbolIter,
            $($(
                $e_interp: (
                    $nullary_tag, $part_im_interp_ty, partial_nullary_immutable::$partial_nullary_immutable, Left
                ),
            )?)*
            $($(
                $e_interp: ($func_tag, $part_im_interp_ty, partial_func_immutable::$partial_func_immutable, Right),
            )?)*
        }

        // partial nullary immutable
        create_big_enum! {
            create:
            /// A partial immutable nullary interpretation.
            ///
            /// See also: [partial::mutable::NullaryInterp],
            /// [complete::immutable::NullaryInterp] and
            /// [complete::mutable::NullaryInterp].
            #[derive(Clone, Debug)]
            $partial_nullary_immutable,
            partial_nullary_immutable,
            $($(
                $e_interp: ($nullary_tag, $part_im_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_nullary_im_impls:
            partial_nullary_immutable::$partial_nullary_immutable<'a>,
            complete_nullary_immutable::$complete_nullary_immutable,
            complete_nullary_immutable::$complete_nullary_immutable,
            $($(
                $e_interp: ($nullary_tag, $part_im_interp_ty),
            )?)*
        }

        // partial func immutable
        create_big_enum! {
            create:
            /// A partial immutable function interpretation.
            ///
            /// See also: [partial::mutable::FuncInterp],
            /// [complete::immutable::FuncInterp] and
            /// [complete::mutable::FuncInterp].
            #[derive(Clone, Debug)]
            $partial_func_immutable,
            partial_func_immutable,
            $($(
                $e_interp: ($func_tag, $part_im_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_im_impls:
            partial_func_immutable::$partial_func_immutable<'a>,
            complete_func_immutable::$complete_func_immutable,
            complete_func_immutable::$complete_func_immutable,
            FuncIter,
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty),
            )?)*
        }

        // Partial mutable
        create_big_enum! {
            create:
            /// A partial mutable symbol interpretation.
            ///
            /// See also: [partial::immutable::SymbolInterp],
            /// [complete::immutable::SymbolInterp] and
            /// [complete::mutable::SymbolInterp].
            #[derive(Debug)]
            $partial_mut,
            partial_symbol_mutable,
            $(
                $e_interp: (true, $part_mut_interp_ty),
            )*
        }
        create_big_enum! {
            partial_symbol_im_impls:
            partial_symbol_mutable::$partial_mut<'a>,
            complete_symbol_immutable::$complete_im,
            complete_symbol_mutable::$complete_mut,
            partial_nullary_mutable::$partial_nullary_mutable,
            partial_func_mutable::$partial_func_mutable,
            SymbolIter,
            $($(
                $e_interp: (
                    $nullary_tag, $part_mut_interp_ty, partial_nullary_mutable::$partial_nullary_mutable, Left
                ),
            )?)*
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty, partial_func_mutable::$partial_func_mutable, Right),
            )?)*
        }
        create_big_enum! {
            partial_mut_impls:
            partial_symbol_mutable::$partial_mut<'a>,
            $(
                $e_interp: (true, $part_mut_interp_ty),
            )*
        }

        // partial nullary mutable
        create_big_enum! {
            create:
            /// A partial mutable nullary interpretation.
            ///
            /// See also: [partial::immutable::NullaryInterp],
            /// [complete::immutable::NullaryInterp] and
            /// [complete::mutable::NullaryInterp].
            #[derive(Debug)]
            $partial_nullary_mutable,
            partial_nullary_mutable,
            $($(
                $e_interp: ($nullary_tag, $part_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_nullary_im_impls:
            partial_nullary_mutable::$partial_nullary_mutable<'a>,
            complete_nullary_immutable::$complete_nullary_immutable,
            complete_nullary_mutable::$complete_nullary_mutable,
            $($(
                $e_interp: ($nullary_tag, $part_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_nullary_mut_impls:
            partial_nullary_mutable::$partial_nullary_mutable<'a>,
            $($(
                $e_interp: ($nullary_tag, $part_mut_interp_ty),
            )?)*
        }

        // partial func mutable
        create_big_enum! {
            create:
            /// A partial mutable function interpretation.
            ///
            /// See also: [partial::immutable::FuncInterp],
            /// [complete::immutable::FuncInterp] and
            /// [complete::mutable::FuncInterp].
            #[derive(Debug)]
            $partial_func_mutable,
            partial_func_mutable,
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_im_impls:
            partial_func_mutable::$partial_func_mutable<'a>,
            complete_func_immutable::$complete_func_immutable,
            complete_func_mutable::$complete_func_mutable,
            FuncIter,
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            partial_mut_impls:
            partial_func_mutable::$partial_func_mutable<'a>,
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty),
            )?)*
        }

        // // // Complete owned
        // // create_big_enum! {
        // //     create:
        // //     #[derive(Clone, Debug)]
        // //     $complete_owned,
        // //     complete_symbol_owned,
        // //     $(
        // //         $e_interp: (true, $complete_owned_interp_ty),
        // //     )*
        // // }
        // // create_big_enum! {
        // //     complete_symbol_im_impls:
        // //     complete_symbol_owned::$complete_owned<'a>,
        // //     complete_nullary_owned::$partial_nullary_owned,
        // //     complete_func_owned::$partial_func_owned,
        // //     SymbolIter,
        // //     $($(
        // //         $e_interp: (
        // //             $nullary_tag, $part_owned_interp_ty, complete_nullary_owned::$complete_nullary_owned, Left
        // //         ),
        // //     )?)*
        // //     $($(
        // //         $e_interp: ($func_tag, $part_owned_interp_ty, complete_func_owned::$complete_func_owned, Right),
        // //     )?)*
        // // }
        // // create_big_enum! {
        // //     complete_mut_impls:
        // //     complete_symbol_owned::$complete_owned<'a>,
        // //     $(
        // //         $e_interp: (true, $complete_owned_interp_ty),
        // //     )*
        // // }
        // //
        // // // complete nullary owned
        // // create_big_enum! {
        // //     create:
        // //     #[derive(Clone, Debug)]
        // //     $complete_nullary_owned,
        // //     complete_nullary_owned,
        // //     $($(
        // //         $e_interp: ($nullary_tag, $complete_owned_interp_ty),
        // //     )?)*
        // // }
        // // create_big_enum! {
        // //     complete_nullary_im_impls:
        // //     complete_nullary_owned::$complete_nullary_owned<'a>,
        // //     $($(
        // //         $e_interp: ($nullary_tag, $complete_owned_interp_ty),
        // //     )?)*
        // // }
        // // create_big_enum! {
        // //     complete_nullary_mut_impls:
        // //     complete_nullary_owned::$complete_nullary_owned<'a>,
        // //     $($(
        // //         $e_interp: ($nullary_tag, $complete_owned_interp_ty),
        // //     )?)*
        // // }
        // //
        // // // complete func owned
        // // create_big_enum! {
        // //     create:
        // //     #[derive(Clone, Debug)]
        // //     $complete_func_owned,
        // //     complete_func_owned,
        // //     $($(
        // //         $e_interp: ($func_tag, $complete_owned_interp_ty),
        // //     )?)*
        // // }
        // // create_big_enum! {
        // //     complete_im_impls:
        // //     complete_func_owned::$complete_func_owned<'a>,
        // //     FuncIter,
        // //     $($(
        // //         $e_interp: ($func_tag, $complete_owned_interp_ty),
        // //     )?)*
        // // }
        // // create_big_enum! {
        // //     complete_mut_impls:
        // //     complete_func_owned::$complete_func_owned<'a>,
        // //     $($(
        // //         $e_interp: ($func_tag, $complete_owned_interp_ty),
        // //     )?)*
        // // }

        // Complete immutable
        create_big_enum! {
            create:
            /// A complete immutable symbol interpretation.
            ///
            /// See also: [complete::mutable::SymbolInterp],
            /// [partial::immutable::SymbolInterp] and
            /// [partial::mutable::SymbolInterp].
            #[derive(Clone, Debug)]
            $complete_im,
            complete_symbol_immutable,
            $(
                $e_interp: (true, $complete_im_interp_ty),
            )*
        }
        create_big_enum! {
            complete_symbol_im_impls:
            complete_symbol_immutable::$complete_im<'a>,
            complete_nullary_immutable::$partial_nullary_immutable,
            complete_func_immutable::$partial_func_immutable,
            SymbolIter,
            $($(
                $e_interp: (
                    $nullary_tag, $part_im_interp_ty, complete_nullary_immutable::$complete_nullary_immutable, Left
                ),
            )?)*
            $($(
                $e_interp: ($func_tag, $part_im_interp_ty, complete_func_immutable::$complete_func_immutable, Right),
            )?)*
        }

        // complete nullary immutable
        create_big_enum! {
            create:
            /// A complete immutable nullary interpretation.
            ///
            /// See also: [complete::mutable::NullaryInterp],
            /// [partial::immutable::NullaryInterp] and
            /// [partial::mutable::NullaryInterp].
            #[derive(Clone, Debug)]
            $complete_nullary_immutable,
            complete_nullary_immutable,
            $($(
                $e_interp: ($nullary_tag, $complete_im_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_nullary_im_impls:
            complete_nullary_immutable::$complete_nullary_immutable<'a>,
            $($(
                $e_interp: ($nullary_tag, $complete_im_interp_ty),
            )?)*
        }

        // complete func immutable
        create_big_enum! {
            create:
            /// A complete immutable function interpretation.
            ///
            /// See also: [complete::mutable::FuncInterp],
            /// [partial::immutable::FuncInterp] and
            /// [partial::mutable::FuncInterp].
            #[derive(Clone, Debug)]
            $complete_func_immutable,
            complete_func_immutable,
            $($(
                $e_interp: ($func_tag, $complete_im_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_im_impls:
            complete_func_immutable::$complete_func_immutable<'a>,
            FuncIter,
            $($(
                $e_interp: ($func_tag, $complete_im_interp_ty),
            )?)*
        }

        // Complete mutable
        create_big_enum! {
            create:
            /// A complete mutable symbol interpretation.
            ///
            /// See also: [complete::immutable::SymbolInterp],
            /// [partial::immutable::SymbolInterp] and
            /// [partial::mutable::SymbolInterp].
            #[derive(Debug)]
            $complete_mut,
            complete_symbol_mutable,
            $(
                $e_interp: (true, $complete_mut_interp_ty),
            )*
        }
        create_big_enum! {
            complete_symbol_im_impls:
            complete_symbol_mutable::$complete_mut<'a>,
            complete_nullary_mutable::$partial_nullary_mutable,
            complete_func_mutable::$partial_func_mutable,
            SymbolIter,
            $($(
                $e_interp: (
                    $nullary_tag, $part_mut_interp_ty, complete_nullary_mutable::$complete_nullary_mutable, Left
                ),
            )?)*
            $($(
                $e_interp: ($func_tag, $part_mut_interp_ty, complete_func_mutable::$complete_func_mutable, Right),
            )?)*
        }
        create_big_enum! {
            complete_mut_impls:
            complete_symbol_mutable::$complete_mut<'a>,
            $(
                $e_interp: (true, $complete_mut_interp_ty),
            )*
        }

        // complete nullary mutable
        create_big_enum! {
            create:
            /// A complete mutable nullary interpretation.
            ///
            /// See also: [complete::immutable::NullaryInterp],
            /// [partial::immutable::NullaryInterp] and
            /// [partial::mutable::NullaryInterp].
            #[derive(Debug)]
            $complete_nullary_mutable,
            complete_nullary_mutable,
            $($(
                $e_interp: ($nullary_tag, $complete_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_nullary_im_impls:
            complete_nullary_mutable::$complete_nullary_mutable<'a>,
            $($(
                $e_interp: ($nullary_tag, $complete_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_nullary_mut_impls:
            complete_nullary_mutable::$complete_nullary_mutable<'a>,
            $($(
                $e_interp: ($nullary_tag, $complete_mut_interp_ty),
            )?)*
        }

        // complete func mutable
        create_big_enum! {
            create:
            /// A complete mutable function interpretation.
            ///
            /// See also: [complete::immutable::FuncInterp],
            /// [partial::immutable::FuncInterp] and
            /// [partial::mutable::FuncInterp].
            #[derive(Debug)]
            $complete_func_mutable,
            complete_func_mutable,
            $($(
                $e_interp: ($func_tag, $complete_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_im_impls:
            complete_func_mutable::$complete_func_mutable<'a>,
            FuncIter,
            $($(
                $e_interp: ($func_tag, $complete_mut_interp_ty),
            )?)*
        }
        create_big_enum! {
            complete_mut_impls:
            complete_func_mutable::$complete_func_mutable<'a>,
            $($(
                $e_interp: ($func_tag, $complete_mut_interp_ty),
            )?)*
        }
    };
    (
        create:
        $(#[$($derives:tt)*])*
        $name:ident,
        $name_mod:ident,
        $($variants:ident: ($($tag:literal)?, $var_ty:ty)),* $(,)?
    ) => {
        mod $name_mod {
            use super::*;
            $(#[$($derives)*])*
            pub enum $name<'a> {
                $(
                    $variants($var_ty),
                )*
            }

            $(
                impl<'a> From<$var_ty> for $name<'a> {
                    fn from(value: $var_ty) -> $name<'a> {
                        $name::$variants(value)
                    }
                }
            )*
            crate::fodot::structure::pfunc::common_impls! {
                ($name<'a>,
                'a,
                (TypeElement, TypeElement<'a>)),
                {},
                $(($variants )),*
            }
            create_big_enum! {
                common:
                $name,
                $(
                    $variants: (true, $var_ty),
                )*
            }
        }
    };
    (
        common:
        $name:ident,
        $($variants:ident: ($($tag:literal)?, $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $name<'a> {
            /// Codomain of the symbol as [TypeFull](crate::fodot::structure::TypeFull).
            pub fn codomain_full(&self) -> crate::fodot::structure::TypeFull<'a> {
                match self {
                    $(
                        Self::$variants(interp) => interp.symb_codomain_full(),
                    )*
                }
            }
        }
    };
    (
        create_iterator:
        $(#[$attr:meta])*
        $name:ident,
        $($variants:ident: ($($tag:literal)?)),* $(,)?
    ) => {
        $(#[$attr])*
        pub enum $name<
            $(
                $variants,
            )*
        > {
            $(
                $variants($variants),
            )*
        }

        impl<
            I,
            $(
                $variants: Iterator<Item = I>,
            )*
        > Iterator for $name<
            $(
                $variants,
            )*
        > {
            type Item = I;

            fn next(&mut self) -> Option<Self::Item> {
                match self {
                    $(
                        Self::$variants(value) => value.next(),
                    )*
                }
            }
        }
    };
    (
        partial_symbol_im_impls:
        $symbol_ty:ty,
        $as_prefix:ident :: $as_complete_ty:ident,
        $into_prefix:ident :: $into_complete_ty:ident,
        $nullary_prefix:ident :: $nullary:ident,
        $func_prefix:ident :: $func:ident,
        $iterator_name:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty, $cor_prefix:ident::$cor_split:ident, $either_var:ident)),* $(,)?
    ) => {
        create_big_enum! {
            partial_im_impls:
            $symbol_ty,
            $as_prefix::$as_complete_ty,
            $into_prefix::$into_complete_ty,
            $iterator_name,
            $(
                $variants: ($($tag,)? $var_ty),
            )*
        }
        impl<'a> $symbol_ty {
            /// Splits the interpretation into either the nullary variant or the function variant.
            pub fn split(self) -> itertools::Either<$nullary_prefix::$nullary<'a>, $func_prefix::$func<'a>> {
                match self {
                    $(
                        Self::$variants(interp) => itertools::Either::$either_var($cor_prefix::$cor_split::$variants(interp)),
                    )*
                }
            }
        }
    };
    (
        partial_im_impls:
        $symbol_ty:ty,
        $as_prefix:ident :: $as_complete_ty:ident,
        $into_prefix:ident :: $into_complete_ty:ident,
        $iterator_name:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        create_big_enum! {
            try_into_impls:
            $symbol_ty,
            $as_prefix::$as_complete_ty,
            $into_prefix::$into_complete_ty,
            $(
                $variants: ($($tag,)? $var_ty),
            )*
        }
        impl<'a> $symbol_ty {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(&self, args: ArgsRef) -> Result<Option<TypeElement<'a>>, ArgMismatchError> {
                match self {
                    $(
                        Self::$variants(interp) => interp.symbol_get(args).map(|opt| opt.map(|f| f.into())),
                    )*
                }
            }

            /// Returns true if at least one argument has a value.
            pub fn any_known(&self) -> bool {
                match self {
                    $(
                        Self::$variants(interp) => interp.any_known(),
                    )*
                }
            }

            /// The amount of arguments of this symbol that have an interpretation.
            pub fn amount_known(&self) -> usize {
                match self {
                    $(
                        Self::$variants(interp) => interp.amount_known(),
                    )*
                }
            }

            /// The amount of arguments of this symbol that don't have an interpretation.
            pub fn amount_unknown(&self) -> usize {
                match self {
                    $(
                        Self::$variants(interp) => interp.amount_unknown(),
                    )*
                }
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl SIterator<Item = (ArgsRef<'a>, TypeElement<'a>)> + 'b {
                match self {
                    $(
                        Self::$variants(interp) =>
                            $iterator_name::$variants(interp.iter().map(|(arg, f)| (arg, f.into()))),
                    )*
                }
            }

            /// Returns an owned iterator over all arguments and their corresponding interpretation.
            pub fn into_iter(self) -> impl SIterator<Item = (ArgsRef<'a>, TypeElement<'a>)> {
                match self {
                    $(
                        Self::$variants(interp) =>
                            $iterator_name::$variants(interp.into_iter().map(|(arg, f)| (arg, f.into()))),
                    )*
                }
            }
        }
    };
    (
        partial_nullary_im_impls:
        $symbol_ty:ty,
        $as_prefix:ident :: $as_complete_ty:ident,
        $into_prefix:ident :: $into_complete_ty:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        create_big_enum! {
            try_into_impls:
            $symbol_ty,
            $as_prefix::$as_complete_ty,
            $into_prefix::$into_complete_ty,
            $(
                $variants: ($($tag,)? $var_ty),
            )*
        }
        impl<'a> $symbol_ty {
            /// Get the interpretation of the symbol.
            pub fn get(&self) -> Option<TypeElement> {
                match self {
                    $(
                        Self::$variants(value) => value.get().map(|f| f.into()),
                    )*
                }
            }
        }
    };
    (
        try_into_impls:
        $symbol_ty:ty,
        $as_prefix:ident :: $as_complete_ty:ident,
        $into_prefix:ident :: $into_complete_ty:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            /// Try converting this interpretation into its complete immutable counterpart.
            ///
            /// This function returns [Err] if the interpretation is not complete.
            pub fn try_as_complete<'b>(&'b self) -> Result<$as_prefix::$as_complete_ty<'b>, ()> {
                match self {
                    $(
                        Self::$variants(value) => Ok(
                            $as_prefix::$as_complete_ty::$variants(value.try_as_complete()?)
                        ),
                    )*
                }
            }

            /// Returns true if the interpretation is complete.
            pub fn is_complete(&self) -> bool {
                self.try_as_complete().is_ok()
            }

            /// Try converting this interpretation into its complete counterpart.
            ///
            /// This function returns the original interpretation in [Err] if the interpretation is
            /// not complete.
            pub fn try_into_complete(self) -> Result<$into_prefix::$into_complete_ty<'a>, Self> {
                match self {
                    $(
                        Self::$variants(value) => Ok(
                            $into_prefix::$into_complete_ty::$variants(
                                value.try_into_complete()
                                .map_err(|f| Self::$variants(f))?
                            )
                        ),
                    )*
                }
            }
        }
    };
    (
        partial_mut_impls:
        $symbol_ty:ty,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            /// Sets the interpretation for the given argument with the given value.
            pub fn set(
                &mut self,
                args: ArgsRef,
                value: Option<TypeElement>
            ) -> Result<(), ExtendedPfuncError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            Ok(interp.symbol_set(
                                args,
                                value.map(|f| interp.symbol_codomain_from_type_element(f))
                                    .transpose()?
                            )?)
                        },
                    )*
                }
            }

            /// Sets the interpretation of the given arguments if it is currently unknown.
            ///
            /// Returns true if the value was actually set, i.e. the previous interpretation was
            /// unknown.
            pub fn set_if_unknown(
                &mut self,
                args: ArgsRef,
                value: TypeElement
            ) -> Result<bool, ExtendedPfuncError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            interp.symbol_set_if_unknown(
                                args,
                                interp.symbol_codomain_from_type_element(value)?
                            )
                        },
                    )*
                }
            }

            /// Sets all unknown values to the given value.
            pub fn set_all_unknown_to_value(
                &mut self,
                value: TypeElement
            ) -> Result<(), NullaryError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            interp.symbol_set_all_unknown_to_value(
                                interp.symbol_codomain_from_type_element(value)?
                            )?;
                            Ok(())
                        },
                    )*
                }
            }
        }
    };
    (
        partial_nullary_mut_impls:
        $symbol_ty:ty,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            /// Sets the interpretation to the given value.
            pub fn set(&mut self, value: Option<TypeElement>) -> Result<(), NullaryError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            Ok(interp.nullary_set(
                                value.map(|f| interp.symbol_codomain_from_type_element(f))
                                    .transpose()?
                            )?)
                        },
                    )*
                }
            }

            /// Sets the interpretation if it is currently unknown.
            ///
            /// Returns true if the value was actually set, i.e. the previous interpretation was
            /// unknown.
            pub fn set_if_unknown(&mut self, value: TypeElement) -> Result<bool, NullaryError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            Ok(interp.nullary_set_if_unknown(
                                interp.symbol_codomain_from_type_element(value)?
                            )?)
                        },
                    )*
                }
            }
        }
    };
    (
        complete_symbol_im_impls:
        $symbol_ty:ty,
        $nullary_prefix:ident :: $nullary:ident,
        $func_prefix:ident :: $func:ident,
        $iterator_name:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty, $cor_prefix:ident::$cor_split:ident, $either_var:ident)),* $(,)?
    ) => {
        create_big_enum! {
            complete_im_impls:
            $symbol_ty,
            $iterator_name,
            $(
                $variants: ($($tag,)? $var_ty),
            )*
        }
        impl<'a> $symbol_ty {
            /// Splits the interpretation into either the nullary variant or the function variant.
            pub fn split(self) -> itertools::Either<$nullary_prefix::$nullary<'a>, $func_prefix::$func<'a>> {
                match self {
                    $(
                        Self::$variants(interp) =>
                            itertools::Either::$either_var($cor_prefix::$cor_split::$variants(interp)),
                    )*
                }
            }
        }
    };
    (
        complete_im_impls:
        $symbol_ty:ty,
        $iterator_name:ident,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            /// Get the interpretation of the symbol with the given arguments.
            pub fn get(
                &self,
                args: ArgsRef,
            ) -> Result<TypeElement<'a>, ArgMismatchError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            Ok(interp.symbol_get(args)?.into())
                        },
                    )*
                }
            }

            /// Returns an iterator over all arguments and their corresponding interpretation.
            pub fn iter<'b>(&'b self) -> impl SIterator<Item = (ArgsRef<'a>, TypeElement<'a>)> + 'b {
                match self {
                    $(
                        Self::$variants(value) => {
                            $iterator_name::$variants(value.iter().map(|(arg, value)| (arg, value.into())))
                        }
                    )*
                }
            }

            /// Returns an owned iterator over all arguments and their corresponding
            /// interpretation.
            pub fn into_iter(self) -> impl SIterator<Item = (ArgsRef<'a>, TypeElement<'a>)> {
                match self {
                    $(
                        Self::$variants(value) => {
                            $iterator_name::$variants(value.into_iter().map(|(arg, value)| (arg, value.into())))
                        }
                    )*
                }
            }
        }
    };
    (
        complete_nullary_im_impls:
        $symbol_ty:ty,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            /// Get the interpretation of the symbol.
            pub fn get(&self) -> TypeElement {
                match self {
                    $(
                        Self::$variants(value) => {
                            value.get().into()
                        },
                    )*
                }
            }
        }
    };
    (
        complete_mut_impls:
        $symbol_ty:ty,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            /// Sets the interpretation for the given argument with the given value.
            pub fn set(
                &mut self,
                args: ArgsRef,
                value: TypeElement,
            ) -> Result<(), ExtendedPfuncError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            interp.symbol_set(
                                args,
                                interp.symbol_codomain_from_type_element(value)?
                            )?;
                            Ok(())
                        },
                    )*
                }
            }
        }
    };
    (
        complete_nullary_mut_impls:
        $symbol_ty:ty,
        $($variants:ident: ($($tag:literal,)? $var_ty:ty)),* $(,)?
    ) => {
        impl<'a> $symbol_ty {
            /// Sets the interpretation to the given value.
            pub fn set(
                &mut self,
                value: TypeElement,
            ) -> Result<(), NullaryError> {
                match self {
                    $(
                        Self::$variants(interp) => {
                            interp.nullary_set(
                                interp.symbol_codomain_from_type_element(value)?
                            )?;
                            Ok(())
                        },
                    )*
                }
            }
        }
    };
}

pub(crate) use create_big_enum;

use super::{complete, partial};
use crate::fodot::{
    error::{ArgMismatchError, ExtendedPfuncError, NullaryError},
    structure::{ArgsRef, TypeElement},
};
use sli_collections::iterator::Iterator as SIterator;

create_big_enum! {
    SymbolInterp,
    SymbolInterp,
    NullaryInterp,
    NullaryInterp,
    FuncInterp,
    FuncInterp,
    SymbolInterp,
    SymbolInterp,
    NullaryInterp,
    NullaryInterp,
    FuncInterp,
    FuncInterp,
    Prop: [
        {
            nullary: true,
        },
        partial::immutable::PropInterp<'a>,
        partial::mutable::PropInterp<'a>,
        complete::immutable::PropInterp<'a>,
        complete::mutable::PropInterp<'a>,
        unwrap_prop,
    ],
    IntConst: [
        {
            nullary: true,
        },
        partial::immutable::IntConstSymbolInterp<'a>,
        partial::mutable::IntConstSymbolInterp<'a>,
        complete::immutable::IntConstSymbolInterp<'a>,
        complete::mutable::IntConstSymbolInterp<'a>,
        unwrap_int_const,
    ],
    RealConst: [
        {
            nullary: true,
        },
        partial::immutable::RealConstSymbolInterp<'a>,
        partial::mutable::RealConstSymbolInterp<'a>,
        complete::immutable::RealConstSymbolInterp<'a>,
        complete::mutable::RealConstSymbolInterp<'a>,
        unwrap_real_const,
    ],
    StrConst: [
        {
            nullary: true,
        },
        partial::immutable::StrConstInterp<'a>,
        partial::mutable::StrConstInterp<'a>,
        complete::immutable::StrConstInterp<'a>,
        complete::mutable::StrConstInterp<'a>,
        unwrap_str_const,
    ],
    Pred: [
        {
            func: true,
        },
        partial::immutable::PredInterp<'a>,
        partial::mutable::PredInterp<'a>,
        complete::immutable::PredInterp<'a>,
        complete::mutable::PredInterp<'a>,
        unwrap_pred,
    ],
    IntFunc: [
        {
            func: true,
        },
        partial::immutable::IntFuncSymbolInterp<'a>,
        partial::mutable::IntFuncSymbolInterp<'a>,
        complete::immutable::IntFuncSymbolInterp<'a>,
        complete::mutable::IntFuncSymbolInterp<'a>,
        unwrap_int_func,
    ],
    RealFunc: [
        {
            func: true,
        },
        partial::immutable::RealFuncSymbolInterp<'a>,
        partial::mutable::RealFuncSymbolInterp<'a>,
        complete::immutable::RealFuncSymbolInterp<'a>,
        complete::mutable::RealFuncSymbolInterp<'a>,
        unwrap_real_func,
    ],
    StrFunc: [
        {
            func: true,
        },
        partial::immutable::StrFuncInterp<'a>,
        partial::mutable::StrFuncInterp<'a>,
        complete::immutable::StrFuncInterp<'a>,
        complete::mutable::StrFuncInterp<'a>,
        unwrap_str_func,
    ],
}

pub mod symbols {
    use super::*;
    pub mod partial {
        use super::*;
        pub mod immutable {
            use super::*;
            pub use partial_func_immutable::*;
            pub use partial_nullary_immutable::*;
            pub use partial_symbol_immutable::*;
        }

        pub mod mutable {
            use super::*;
            pub use partial_func_mutable::*;
            pub use partial_nullary_mutable::*;
            pub use partial_symbol_mutable::*;
        }
    }

    pub mod complete {
        use super::*;
        pub mod immutable {
            use super::*;
            pub use complete_func_immutable::*;
            pub use complete_nullary_immutable::*;
            pub use complete_symbol_immutable::*;
        }

        pub mod mutable {
            use super::*;
            pub use complete_func_mutable::*;
            pub use complete_nullary_mutable::*;
            pub use complete_symbol_mutable::*;
        }
    }
}
