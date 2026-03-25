# trailing-comma — minimal replacement for add-trailing-comma

## Why replace add-trailing-comma?

### Bug: Windows stdin double newlines

In `_main.py:fix_file`, stdin is read as binary (line 58: `sys.stdin.buffer.read()`),
decoded without newline translation (line 64: `.decode()`), then printed via text-mode
stdout (line 73: `print(contents_text, end='')`).

On Windows, subprocess `text=True` sends `\r\n` to stdin. The tool preserves `\r` as
content, then `print()` adds its own `\r\n`, producing `\r\r\n` per line. Python reads
this back and the stray `\r` appears as a blank line.

File mode works fine (reads/writes binary, never hits text-mode stdout).

### Problem: yapf cycle on annotated function defs

yapf and add-trailing-comma fight on annotated defs and never converge:

```python
# add-trailing-comma produces dedented style:
def load_daily_sigma(
    root: str, date_from: dt.date, date_to: dt.date,
) -> dict[dt.date, float]:
    pass

# yapf reformats to continuation-indent:
def load_daily_sigma(root: str, date_from: dt.date, date_to: dt.date,
                     ) -> dict[dt.date, float]:
    pass

# add-trailing-comma puts it back — infinite cycle
```

### Unnecessary complexity

Constructs we don't need: match/case patterns, PEP 695 type aliases, with statement
commas, class base commas, tuple edge cases (_fix_tuple_py38), plugin discovery via
pkgutil.walk_packages, fstring state tracking, `from __future__` imports everywhere.

### Dependency: tokenize-rt

tokenize-rt (round-trip tokenizer) is a good dependency — handles token manipulation
cleanly. Worth keeping. Only runtime dependency.


## What we actually need

Two operations on braced constructs (parens, brackets, braces):
1. **Add trailing comma** when closing brace is on a different line than last element
2. **Remove trailing comma** when everything fits on one line (the `,)` case)

### Constructs to handle

| Construct | Priority |
|-----------|----------|
| Function calls: `foo(a=1, b=2,)` | Must have |
| Function defs: `def foo(a: int,) -> None:` | Must have |
| Imports: `from x import (a, b,)` | Must have |
| Lists, dicts, sets | Must have |
| Tuples: `(1, 2, 3,)` | Nice to have |
| Class bases, match/case, PEP 695, with | Skip |

### Behavior examples

**Add comma — multi-line call (yapf output has no trailing comma):**
```python
plot_vol(
    expiry_arr=fit["DTE"], vov_arr=fit["MedianVoV"],
    amplitude=fit["Amplitude"], r_squared=fit["RSquared"]   # <- add comma here
)
```

**Remove comma — single-line (yapf quirk keeps comma on collapse):**
```python
# before:  result = foo(a=1, b=2, c=3,)
# after:   result = foo(a=1, b=2, c=3)
```

**Dedent closing brace — the cycle fix:**
```python
# before (yapf continuation-indent):
def load(root: str, date_from: dt.date,
         ) -> dict[dt.date, float]:
# after (dedented to base indent):
def load(
    root: str, date_from: dt.date,
) -> dict[dt.date, float]:
```

**Nested — each level independent:**
```python
result = outer(
    inner(a, b, c),
    inner(d, e, f),  # <- added
)
```


## Architecture decisions

**Keep tokenize-rt.** Token-based approach is correct. No reason to reinvent.

**Drop the AST walk.** Current code walks the AST to find Call/FunctionDef/Import nodes,
then maps offsets to token-level fixers. Simpler: walk the token stream directly. When
you see `(` `[` `{`, find matching close. Check line numbers. Add/remove comma. The only
AST case is generators (`sum(x for x in ...)`) — detect via `for` keyword in tokens.

**Fix the Windows bug.** Use `sys.stdout.buffer.write(result.encode())` not `print()`.

**CLI interface.** Same as add-trailing-comma:
- `trailing-comma file1.py file2.py` — rewrite in place
- `trailing-comma -` — read stdin, write stdout
- Exit code 1 if any file was rewritten


## Implementation plan

### Step 1: Core logic (single file, pure function)

`fix_trailing_commas(source: str) -> str`:
1. Tokenize with tokenize-rt
2. Walk tokens for `(` `[` `{`, find matching close (track nesting)
3. Same line → remove trailing comma + whitespace if present
4. Different lines → add comma after last non-whitespace token
5. Fix closing brace indentation (dedent to opening line indent)

Edge cases: empty braces (skip), generators (don't add comma), string
concatenation in parens (not a tuple), nested braces (each level independent).

### Open questions

**Cycle fix needs context.** The dedent behavior (moving `)` to base indent) only applies
to function defs, not arbitrary calls. A pure token walk sees `(` but doesn't know if it
belongs to a `def` or a call. Options: (a) light AST pass for this case only, (b) look
backwards from `(` for `def`/`async def` keyword tokens, (c) always dedent (may be fine
since yapf already controls call indentation).

**Unhug behavior.** add-trailing-comma also splits `foo(a=1,\n    b=2)` into
`foo(\n    a=1,\n    b=2,\n)` (content on same line as open brace gets pushed down).
Verify whether yapf already handles this — if so, we can skip it.

### Step 2: CLI wrapper

Minimal `__main__.py`:
- Stdin: `sys.stdin.buffer.read()` → process → `sys.stdout.buffer.write()` (no Windows bug)
- Files: read binary, write binary (same as current)
- Exit code 1 if any file changed

### Step 3: Test suite

- Unit tests for `fix_trailing_commas` directly (no subprocess)
- yapf cycle test (verify idempotence: yapf → tc → yapf → tc)
- Windows newline test (no `\r\r\n`)
- All constructs: calls, defs, imports, lists, dicts, sets, tuples
- Edge cases: empty braces, generators, nested, single-element tuples

### Step 4: Integration with theta-options

- `pip install -e C:/Users/Martial/trailing-comma`
- Update `lint/test_yapf_style.py` to use new package
- Update `.claude/skills/check/SKILL.md` command
- Update `.claude/settings.local.json` permission
- Remove `add-trailing-comma` from `requirements.txt`

### Dependencies

- `tokenize-rt` — keep (MIT, essential for round-trip token editing)
- `ast` — stdlib, only if needed for generator detection
- Nothing else

## License

MIT. Keep original copyright (derived from add-trailing-comma):
```
Copyright (c) 2017 Anthony Sottile
Copyright (c) 2026 Martial Ren
```
