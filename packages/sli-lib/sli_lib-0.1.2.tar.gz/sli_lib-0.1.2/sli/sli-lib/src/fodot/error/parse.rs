//! Data structure used to aggregate errors from parsing.

use super::SliError;
use crate::{
    ast::{self, LinesIter, Span},
    fodot::fmt::{FodotDisplay, FodotOptions, FormatOptions},
};
use itertools::Itertools;
use std::error::Error;
use std::fmt::Display;
use unicode_width::UnicodeWidthStr;

/// A span with some text.
#[allow(unused)]
#[derive(Debug, Clone)]
pub struct LabeledSpan {
    label: Option<Box<str>>,
    span: Span,
}

/// An error with a corresponding span.
#[derive(Debug, Clone)]
pub struct IDPError {
    error: SliError,
    span: Span,
    secondary_labels: Vec<LabeledSpan>,
    #[allow(unused)]
    #[cfg(all(debug_assertions, feature = "std"))]
    backtrace: backtrace::Backtrace,
}

impl IDPError {
    pub fn new(error: SliError, span: Span) -> Self {
        Self {
            error,
            span,
            secondary_labels: Default::default(),
            #[cfg(all(debug_assertions, feature = "std"))]
            backtrace: backtrace::Backtrace(std::backtrace::Backtrace::capture().into()),
        }
    }

    pub fn add_label(mut self, label: LabeledSpan) -> Self {
        self.secondary_labels.push(label);
        self
    }

    pub fn span(&self) -> &Span {
        &self.span
    }

    fn display_with_source(
        &self,
        f: &mut dyn core::fmt::Write,
        source: &dyn ast::Source,
        new_lines: &NewLineMap,
    ) -> core::fmt::Result {
        let begin_line = new_lines.til_prev_new_line(self.span.start);
        let end_line = new_lines.til_next_new_line(self.span.end);
        let begin_line_nr = begin_line.map(|f| new_lines.line_number(f)).unwrap_or(0) + 1;
        let is_multi_line = begin_line
            .map(|f| new_lines.til_next_new_line(f) != end_line)
            .unwrap_or(false);
        write!(f, "{}\n", self.error)?;
        let diag_span = Span {
            start: begin_line.unwrap_or(0),
            end: end_line.unwrap_or(source.len()),
        };

        if is_multi_line {
            let end_line_nr = end_line.map(|f| new_lines.line_number(f)).unwrap_or(0) + 1;
            let max_digit_count = end_line_nr.ilog10() + 1;
            for (line, line_nr) in LinesIter::new(source, &diag_span).zip(begin_line_nr..) {
                let this_digit_count = line_nr.ilog10() + 1;
                write!(f, "{line_nr} ")?;
                write!(
                    f,
                    "{:^<1$}",
                    "",
                    (max_digit_count - this_digit_count) as usize
                )?;
                write!(f, "| ")?;
                source.write_slice(&line, f)?;
                write!(f, "\n")?;
            }
        } else {
            let digit_count = begin_line_nr.ilog10() + 1;
            write!(f, "{begin_line_nr} ")?;
            const PREAMBLE: &str = "| ";
            write!(f, "{}", PREAMBLE)?;
            source.write_slice(&diag_span, f)?;
            let mut width_writer = WidthWriter::new(VoidWriter);
            _ = source.write_slice(
                &Span {
                    start: diag_span.start,
                    end: self.span.start,
                },
                &mut width_writer,
            );
            let chars_pre =
                width_writer.accum + digit_count as usize + 1 + UnicodeWidthStr::width(PREAMBLE);
            write!(f, "\n{: <1$}", "", chars_pre)?;
            let length = self.span.end - self.span.start;
            let mut width_writer = WidthWriter::new(VoidWriter);
            _ = source.write_slice(&self.span, &mut width_writer);
            let chars_in = width_writer.accum;
            if length == 0 {
                write!(f, "{:^<1$}", "", 1)?;
            } else {
                write!(f, "{:^<1$}", "", chars_in)?;
            }
        }
        Ok(())
    }
}

impl FodotOptions for IDPError {
    type Options<'a> = FormatOptions;
}

impl FodotDisplay for IDPError {
    fn fmt(
        fmt: crate::fodot::fmt::Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        write!(
            f,
            "from {} to {}: ",
            fmt.value.span.start, fmt.value.span.end
        )?;
        write!(f, "{}", fmt.with_format_opts(&fmt.value.error))
    }
}

impl Display for IDPError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display())
    }
}

impl Error for IDPError {}

/// A collection of [IDPError]s.
#[derive(Debug, Clone)]
pub struct Diagnostics {
    errors: Vec<IDPError>,
}

impl Default for Diagnostics {
    fn default() -> Self {
        Self::new()
    }
}

impl Diagnostics {
    pub fn new() -> Self {
        Self {
            errors: Default::default(),
        }
    }

    pub fn add_error(&mut self, error: IDPError) {
        self.errors.push(error)
    }

    pub fn errors(&self) -> &[IDPError] {
        &self.errors
    }

    pub fn with_source<'a>(&'a self, source: &'a dyn ast::Source) -> SourceDiagnostics<'a> {
        SourceDiagnostics { source, diag: self }
    }
}

impl Display for Diagnostics {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.errors().iter().format("\n"))
    }
}

/// A [Diagnostics] combined with a [ast::Source].
///
/// Used for pretty printing errors.
pub struct SourceDiagnostics<'a> {
    source: &'a dyn ast::Source,
    diag: &'a Diagnostics,
}

/// A mapping of source newlines.
struct NewLineMap {
    new_lines: Box<[usize]>,
    is_dos: bool,
}

impl NewLineMap {
    fn til_next_new_line(&self, pos: usize) -> Option<usize> {
        let res = self.new_lines.partition_point(|&f| f < pos);
        if res < self.new_lines.len() {
            Some(self.new_lines[res] - self.till_value())
        } else {
            None
        }
    }

    fn til_prev_new_line(&self, pos: usize) -> Option<usize> {
        let res = self.new_lines.partition_point(|&f| f < pos);
        if res < self.new_lines.len() {
            Some(self.new_lines[res.checked_sub(1)?] + 1)
        } else {
            None
        }
    }

    fn line_number(&self, pos: usize) -> usize {
        self.new_lines.partition_point(|&f| f < pos)
    }

    fn till_value(&self) -> usize {
        if self.is_dos { 1 } else { 0 }
    }
}

impl<'a> SourceDiagnostics<'a> {
    fn calculate_new_line_map(&self) -> NewLineMap {
        let Some(first) = self.source.next_char_pos(0, '\n') else {
            return NewLineMap {
                new_lines: [].into(),
                is_dos: false,
            };
        };
        let mut new_lines = vec![first];
        let is_dos = self.source.prev_char(first) == Some('\r');
        let Some(mut cur) = first.checked_add(1) else {
            return NewLineMap {
                new_lines: new_lines.into(),
                is_dos,
            };
        };
        while let Some(next) = self.source.next_char_pos(cur, '\n') {
            new_lines.push(next);
            if let Some(cur_new) = next.checked_add(1) {
                cur = cur_new;
            } else {
                return NewLineMap {
                    new_lines: new_lines.into(),
                    is_dos,
                };
            };
        }

        NewLineMap {
            new_lines: new_lines.into(),
            is_dos,
        }
    }
}

impl<'a> Display for SourceDiagnostics<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let mut errors = self.diag.errors.iter().peekable();
        let new_line_map = self.calculate_new_line_map();
        while let Some(error) = errors.next() {
            write!(f, "error: ")?;
            error.display_with_source(f, self.source, &new_line_map)?;
            if errors.peek().is_some() {
                write!(f, "\n")?;
            }
        }
        Ok(())
    }
}

/// A writer that keeps track of the width that has been written.
///
/// Uses [unicode_width] as width of Unicode characters.
pub struct WidthWriter<W: core::fmt::Write> {
    pub writer: W,
    pub accum: usize,
}

impl<W: core::fmt::Write> WidthWriter<W> {
    pub fn new(writer: W) -> Self {
        Self { writer, accum: 0 }
    }
}

impl<W: core::fmt::Write> core::fmt::Write for WidthWriter<W> {
    fn write_str(&mut self, s: &str) -> std::fmt::Result {
        self.accum += unicode_width::UnicodeWidthStr::width(s);
        self.writer.write_str(s)?;
        Ok(())
    }

    fn write_char(&mut self, c: char) -> std::fmt::Result {
        self.accum += unicode_width::UnicodeWidthChar::width(c).unwrap_or(0);
        self.writer.write_char(c)?;
        Ok(())
    }
}

/// A writer that discards anything that is being written to it.
///
/// Useful when used together with a [WidthWriter].
pub struct VoidWriter;

impl core::fmt::Write for VoidWriter {
    fn write_str(&mut self, _: &str) -> std::fmt::Result {
        Ok(())
    }

    fn write_char(&mut self, _: char) -> std::fmt::Result {
        Ok(())
    }

    fn write_fmt(&mut self, _: std::fmt::Arguments<'_>) -> std::fmt::Result {
        Ok(())
    }
}

#[cfg(all(debug_assertions, feature = "std"))]
mod backtrace {
    use std::fmt::Display;

    #[derive(Debug)]
    pub struct Backtrace(pub Option<std::backtrace::Backtrace>);

    impl Display for Backtrace {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            if let Some(backtrace) = &self.0 {
                write!(f, "{}", backtrace)?;
            }
            Ok(())
        }
    }

    impl Clone for Backtrace {
        fn clone(&self) -> Self {
            Self(None)
        }
    }
}
