use itertools::Either;
use std::{cmp::Ordering, iter::Peekable};

/// Performs a natural join of two iterators, implemented in the form of an iterator.
/// When matches are found, a tuple with the left and right element are returned.
///
/// Main idea of the sort merge join algorithm is that after sorting both 'tables'
/// the values we need to join always appear in sequences of equality, which
/// potentially requires less work than the alternatives.
/// For more info see [wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
///
/// Note: The input iterators must be sorted beforehand, or the correctness cannot be guaranteed!
pub struct SortMergeJoin<L, R, K>
where
    L: Iterator + Clone,
    R: Iterator,
    K: Fn(&L::Item, &R::Item) -> Ordering,
    L::Item: Clone,
    R::Item: Clone,
{
    left: Peekable<L>,
    left_equsequence: Peekable<L>,
    right: Peekable<R>,
    in_run: Option<Either<(), ()>>,
    ord_key: K,
}

// from future rust core::iter::traits::is_sorted_by
#[cfg(debug_assertions)]
fn is_sorted_by<I: Iterator + Sized, F>(mut iter: I, compare: F) -> bool
where
    F: FnMut(&I::Item, &I::Item) -> bool,
{
    #[inline]
    fn check<'a, T>(
        last: &'a mut T,
        mut compare: impl FnMut(&T, &T) -> bool + 'a,
    ) -> impl FnMut(T) -> bool + 'a {
        move |curr| {
            if !compare(&last, &curr) {
                return false;
            }
            *last = curr;
            true
        }
    }

    let mut last = match iter.next() {
        Some(e) => e,
        None => return true,
    };

    iter.all(check(&mut last, compare))
}

impl<L, R, K> SortMergeJoin<L, R, K>
where
    L: Iterator + Clone,
    R: Iterator + Clone,
    K: Fn(&L::Item, &R::Item) -> Ordering,
    L::Item: Clone,
    R::Item: Clone,
{
    /// Iterators `left`, and `right` must be sorted!
    /// `ord_left` and `ord_right` check in debug builds if the iterator is in fact sorted.
    /// Providing unsorted iterators just results in unexpected behaviour (not undefined but still
    /// something we want to avoid).
    pub fn new<KL, KR>(
        left: L,
        right: R,
        ord_key: K,
        #[allow(unused_variables)] ord_left: KL,
        #[allow(unused_variables)] ord_right: KR,
    ) -> Self
    where
        KL: Fn(&L::Item, &L::Item) -> Ordering,
        KR: Fn(&R::Item, &R::Item) -> Ordering,
    {
        // TODO: add release build in ci
        #[cfg(debug_assertions)]
        {
            debug_assert!(is_sorted_by(left.clone(), |left, right| {
                ord_left(left, right).is_le()
            }));
            debug_assert!(is_sorted_by(right.clone(), |left, right| {
                ord_right(left, right).is_le()
            }));
        }
        Self {
            left: left.clone().peekable(),
            left_equsequence: left.peekable(),
            right: right.peekable(),
            in_run: None,
            ord_key,
        }
    }
}

impl<L, R, K> Iterator for SortMergeJoin<L, R, K>
where
    L: Iterator + Clone,
    R: Iterator,
    K: Fn(&L::Item, &R::Item) -> Ordering,
    L::Item: Clone,
    R::Item: Clone,
{
    type Item = (L::Item, R::Item);

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            if let Some(in_run) = &mut self.in_run {
                // We are in a run!!!
                'equsequence: loop {
                    match in_run {
                        Either::Left(()) => {
                            // Walk through all left values in run
                            // Only proceed left if we find a match
                            let left = if let Some(left) = self.left_equsequence.peek() {
                                left.clone()
                            } else {
                                *in_run = Either::Right(());
                                continue 'equsequence;
                            };
                            let right = self.right.peek()?.clone();
                            if (self.ord_key)(&left, &right).is_eq() {
                                // proceed left
                                _ = self.left_equsequence.next();
                                return Some((left, right));
                            } else {
                                // No more left values in run continue in right branch
                                *in_run = Either::Right(());
                                continue 'equsequence;
                            }
                        }
                        Either::Right(()) => {
                            // right has been peeked, remove peek so we can continue right
                            // by one in next peek
                            _ = self.right.next();
                            let (left, right) = (
                                // Compare with beginning of run
                                self.left.peek()?.clone(),
                                self.right.peek()?.clone(), // right continues here
                            );
                            if (self.ord_key)(&left, &right).is_eq() {
                                // We have continued right and are still in a run!
                                // Now we must walk left again from beginning of this run
                                // with new right
                                // restore left at beginning of run
                                self.left_equsequence = self.left.clone();
                                // left_runner was peeked, undo the peek;
                                _ = self.left_equsequence.next();
                                *in_run = Either::Left(());
                                return Some((left, right));
                            } else {
                                // right has left end of a run
                                self.in_run = None;
                                // continue looking for a run at the end of left.
                                self.left = self.left_equsequence.clone();
                                break 'equsequence;
                            }
                        }
                    }
                }
            }
            // Continue till we find a run
            let (left, right) = (self.left.peek()?.clone(), self.right.peek()?.clone());
            match (self.ord_key)(&left, &right) {
                Ordering::Equal => {
                    // Run found!!
                    self.in_run = Some(Either::Left(()));
                    // Save left iterator
                    self.left_equsequence = self.left.clone();
                    // Was peeked remove peek
                    _ = self.left_equsequence.next();
                    return Some((left, right.clone()));
                }
                Ordering::Less => {
                    // left is less then right, continue left
                    _ = self.left.next();
                }
                Ordering::Greater => {
                    // left is greater than right, continue right
                    _ = self.right.next();
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::SortMergeJoin;
    use duplicate::duplicate_item;

    #[duplicate_item(
        [
            test_name [sort_merge_join1]
            left_v [
                ("Harry", 3415, "Finance"),
                ("George", 3401, "Finance"),
                ("Mary", 1257, "Human Resources"),
                ("Jhon", 1257, "Production"),
                ("Sally", 2241, "Sales"),
                ("Harriet", 2202, "Sales"),
            ]
            right_v [
                ("Finance", "George"),
                ("Production", "Charles"), 
                ("Sales", "Harriet"),
            ]
            key [
            |left: &(&str, i32, &str), right: &(&str, &str)|
                left.2.cmp(right.0)
            ]
            key_swapped [
            |left: &(&str, &str), right: &(&str, i32, &str)|
                left.0.cmp(right.2)
            ]
            key_left [
            |left_1: &(&str, i32, &str), left_2: &(&str, i32, &str)|
                left_1.2.cmp(left_2.2)
            ]
            key_right [
            |right_1: &(&str, &str), right_2: &(&str, &str)|
                right_1.0.cmp(right_2.0)
            ]
            // Left side of join
            exp_left [
                ("Harry", 3415, "Finance"),
                ("George", 3401, "Finance"),
                ("Jhon", 1257, "Production"),
                ("Sally", 2241, "Sales"),
                ("Harriet", 2202, "Sales"),
            ]
            // Right side of join
            exp_right [
                ("Finance", "George"),
                ("Finance", "George"),
                ("Production", "Charles"),
                ("Sales", "Harriet"),
                ("Sales", "Harriet"),
            ]
        ]
        [
            test_name [sort_merge_join2]
            left_v [
                // employ, numb, works at, dep numb
                ("Harry", 3415, "Finance", "1"),
                ("George", 3401, "Finance", "2"),
                ("Mary", 1257, "Human Resources", "1"),
                ("Jhon", 1257, "Production", "1"),
                ("Sally", 2241, "Sales", "1"),
                ("Harriet", 2202, "Sales", "2"),
            ]
            right_v [
                // dep, numb, dep manager
                ("Finance", "1", "George"),
                ("Finance", "2", "Harry Potter"),
                ("Production", "1", "Charles"), 
                ("Sales", "2", "Harriet"),
            ]
            key [
            |left: &(&str, i32, &str, &str), right: &(&str, &str, &str)|
                (left.2, left.3).cmp(&(right.0, right.1))
            ]
            key_swapped [
            |right: &(&str, &str, &str), left: &(&str, i32, &str, &str)|
                (right.0, right.1).cmp(&(left.2, left.3))
            ]
            key_left [
            |left_1: &(&str, i32, &str, &str), left_2: &(&str, i32, &str, &str)|
                left_1.2.cmp(left_2.2)
            ]
            key_right [
            |right_1: &(&str, &str, &str), right_2: &(&str, &str, &str)|
                right_1.0.cmp(right_2.0)
            ]
            // Left side of join
            exp_left [
                ("Harry", 3415, "Finance", "1"),
                ("George", 3401, "Finance", "2"),
                ("Jhon", 1257, "Production", "1"),
                ("Harriet", 2202, "Sales", "2"),
            ]
            // Right side of join
            exp_right [
                ("Finance", "1", "George"),
                ("Finance", "2", "Harry Potter"),
                ("Production", "1", "Charles"),
                ("Sales", "2", "Harriet"),
            ]
        ]
    )]
    #[test]
    fn test_name() {
        let a = vec![left_v].into_iter();
        let a = a.into_iter();
        let b = vec![right_v].into_iter();
        let merge_join = SortMergeJoin::new(a, b, key, key_left, key_right);

        let left_exp = vec![exp_left];

        let right_exp = vec![exp_right];

        let expected = Vec::from_iter(left_exp.into_iter().zip(right_exp.into_iter()));
        let result = Vec::from_iter(merge_join);

        println!("result:\n{:?} =\n expected:\n{:?}", result, expected);
        assert_eq!(expected, result);

        let a = vec![left_v].into_iter();
        let a = a.into_iter();
        let b = vec![right_v].into_iter();
        // we must use swap here since ordering is by convention:
        // left {operator} right
        let merge_join = SortMergeJoin::new(b, a, key_swapped, key_right, key_left);

        let left_exp = vec![exp_left];

        let right_exp = vec![exp_right];

        let expected = Vec::from_iter(right_exp.into_iter().zip(left_exp.into_iter()));
        let result = Vec::from_iter(merge_join);

        println!("result:\n{:?} =\n expected:\n{:?}", result, expected);
        assert_eq!(expected, result);
    }

    #[cfg(debug_assertions)]
    #[should_panic]
    #[test]
    fn sort_merge_join_non_sorted() {
        let mut a = vec![
            ("Harry", 3415, "Finance"),
            ("George", 3401, "Finance"),
            ("Mary", 1257, "Human Resources"),
            ("Jhon", 1257, "Production"),
            ("Sally", 2241, "Sales"),
            ("Harriet", 2202, "Sales"),
        ];
        // Sorting needs to be by key otherwise merge join cannot operate correctly
        a.sort();
        let a = a.into_iter();
        let mut b = vec![
            ("Finance", "George"),
            ("Production", "Charles"),
            ("Sales", "Harriet"),
        ];
        b.sort();
        let b = b.into_iter();
        let merge_join = SortMergeJoin::new(
            a,
            b,
            |left: &(&str, i32, &str), right: &(&str, &str)| left.2.cmp(right.0),
            |left1: &(&str, i32, &str), left2: &(&str, i32, &str)| left1.2.cmp(left2.2),
            |right1: &(&str, &str), right2: &(&str, &str)| right1.1.cmp(right2.0),
        );
        merge_join.for_each(|_| {})
    }
}
