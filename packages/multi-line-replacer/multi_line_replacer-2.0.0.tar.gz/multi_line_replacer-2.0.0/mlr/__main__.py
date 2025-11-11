#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.text import Style, Text

from mlr.core import extract_code_blocks_from_md_text, replace_text
from mlr.exceptions import CodeBlocksMismatched, TargetCodeBlockEmpty
from mlr.path import ExpandedPath, read_text, write_text


class CLIArgs(argparse.Namespace):
    """
    A subclass of argparse.Namespace that exposes type information for all CLI
    arguments supported by the program
    """

    input_paths: list[ExpandedPath]
    rule_paths: list[ExpandedPath]
    dry_run: bool
    quiet: bool


def get_cli_args() -> CLIArgs:
    """Define and parse CLI arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_paths",
        metavar="INPUT_FILE",
        nargs="+",
        type=ExpandedPath,
        help="One or more paths to files to apply replacements to.",
    )
    parser.add_argument(
        "-r",
        "--rules",
        metavar="RULE_FILE",
        dest="rule_paths",
        nargs="+",
        required=True,
        type=ExpandedPath,
        help="One or more paths to replacement rule Markdown files. Each file should contain pairs of triple-backtick (```) fenced code blocks, where the first fenced block is the text to be replaced and the second fenced block is the replacement text.",  # noqa: E501
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform all replacements in memory without writing changes to "
        "disk. Useful for testing which files would be changed.",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppresses all output except for errors.",
    )
    return parser.parse_args(namespace=CLIArgs())


def extract_code_blocks_from_md_path(md_path: Path) -> list[str]:
    """Extract fenced code blocks from a Markdown file at the given path"""
    md_text = md_path.read_text()
    try:
        return extract_code_blocks_from_md_text(md_text)
    except TargetCodeBlockEmpty:
        print(
            f"{Path(sys.argv[0]).name}: "
            f"{md_path}: "
            f"target text code block cannot be empty"
        )
        sys.exit(1)
    except CodeBlocksMismatched:
        print(
            f"{Path(sys.argv[0]).name}: "
            f"{md_path}: "
            f"replacement file must have an even number of fenced code blocks"
        )
        sys.exit(1)


def print_file_statuses(results: list[tuple[ExpandedPath, bool]]) -> None:
    """Print each processed file path along with whether it changed.

    Output format (no color):
        /abs/path/to/file.yml
        /abs/path/to/other.yml (unchanged)

    Colors (when rich + TTY available):
        changed   -> default
        unchanged -> dim
    """
    # If rich is available and stdout is a terminal, use color; otherwise
    # fall back to plain print
    console = Console()
    for path_obj, changed in results:
        status_text = "changed" if changed else "unchanged"
        if console.is_terminal:
            # Build styled text
            color = Style(color=None) if changed else "dim"
            txt = Text(str(path_obj), style=color)
            if not changed:
                txt.append(f" ({status_text})", style=color)
            console.print(txt)
        elif changed:
            print(f"{path_obj}")
        else:
            print(f"{path_obj} ({status_text})")


def print_dry_run_message() -> None:
    """
    Print a dry run notice to the console to inform the user that modifications
    will not be written to disk.
    """
    console = Console()
    console.print(
        "[yellow]Note: Dry run enabled; no files will be modified on disk.[/yellow]"
    )


line_endings = ("\r\n", "\n", "\r")


def get_line_ending_from_text(text: str) -> str:
    """
    Choose a single EOL to preserve by inspecting the raw text.
    Prefer CRLF if present, else LF, else CR.
    Fallback to LF if no newline is found.
    """
    for line_ending in line_endings:
        if line_ending in text:
            return line_ending
    return "\n"


def main() -> None:
    """The entry point for the `multi-line-replacer` / `mlr` CLI program"""
    args = get_cli_args()
    results: list[tuple[ExpandedPath, bool]] = []
    for input_path in args.input_paths:
        # Read once without translation to detect original line endings
        orig_line_ending = get_line_ending_from_text(read_text(input_path, newline=""))
        # Read again with universal newlines for normalized processing
        orig_input_text = read_text(input_path)
        input_text = orig_input_text
        # Apply each replacement rule to each input file
        for rule_path in args.rule_paths:
            code_blocks = extract_code_blocks_from_md_path(rule_path)
            # Enumerate fenced code blocks in pairs to get each pair of
            # target/replacement rules
            for target_text, replacement_text in zip(
                code_blocks[0::2], code_blocks[1::2]
            ):
                input_text = replace_text(input_text, target_text, replacement_text)
        file_changed = orig_input_text != input_text
        if file_changed and not args.dry_run:
            write_text(input_path, input_text, newline=orig_line_ending)
        results.append((input_path, file_changed))
    if not args.quiet:
        if args.dry_run:
            print_dry_run_message()
        print_file_statuses(results)


if __name__ == "__main__":
    main()
