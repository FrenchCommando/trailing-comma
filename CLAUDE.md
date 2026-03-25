# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`trailing-comma` is a minimal Python CLI tool that adds/removes trailing commas in Python source files. It replaces `add-trailing-comma` to fix one issue: a Windows stdin double-newline bug. It gives us an excuse to redesign the project and carve out features we don't want to support: 

- it's 2026, we use python 3.14
- the hard part is about modifying strings, we need to isolate this part
- we use `python` so we don't have an obsessive focus on performance
- i want to control the workflow/hooks

## Architecture

Token-based approach using `tokenize-rt` (the only runtime dependency). No AST walk — the tool walks the token stream directly, matching open/close braces and checking line numbers.

Core logic is a pure function `fix_trailing_commas(source: str) -> str` that:
1. Tokenizes with tokenize-rt
2. Walks tokens for `(` `[` `{`, finds matching close (tracks nesting)
3. Same line → removes trailing comma if present
4. Different lines → adds comma after last non-whitespace token
5. Fixes closing brace indentation (dedent to opening line indent for function defs)

Edge cases: empty braces (skip), generators (don't add comma — detect via `for` keyword in tokens), nested braces (each level independent).

## CLI interface

- `trailing-comma file1.py file2.py` — rewrite files in place
- `trailing-comma -` — read stdin, write stdout (uses `sys.stdout.buffer.write` to avoid Windows newline bug)
- Exit code 1 if any file was rewritten

One pain point which is clearly intentional in the initial design, is that there is not what to feed a string. We should fix that: the hard part is about converting a bad string to a clean string, all the work around files and bytes is an overhead that should be clearly carved out - this is one reason for the rewrite of the project.


## Build and install

```
pip install -e .
```

It should be deployed on PyPy as well.
package name is `trailing-comma` - not sure if it's taken yet.


## Testing

Unit tests cover `fix_trailing_commas` directly (no subprocess). Key test categories:
- All constructs: calls, defs, imports, lists, dicts, sets, tuples
- yapf cycle test (idempotence: yapf → tc → yapf → tc)
- Windows newline test (no `\r\r\n`)
- Edge cases: empty braces, generators, nested, single-element tuples

The initial repo uses `pytest`, can we move to `unittest`? Hopefully it's not using the `pytest` features too heavily.


## Scope boundaries

Constructs handled: function calls, function defs, imports, lists, dicts, sets, tuples.
Explicitly skipped: class bases, match/case patterns, PEP 695 type aliases, `with` statement commas.
