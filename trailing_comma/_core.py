"""Core logic for trailing-comma: add/remove trailing commas in Python source."""

import keyword
from typing import NamedTuple

from tokenize_rt import ESCAPED_NL
from tokenize_rt import NON_CODING_TOKENS
from tokenize_rt import Token
from tokenize_rt import UNIMPORTANT_WS
from tokenize_rt import src_to_tokens
from tokenize_rt import tokens_to_src

NEWLINES = frozenset((ESCAPED_NL, 'NEWLINE', 'NL'))
INDENT_TOKENS = frozenset(('INDENT', UNIMPORTANT_WS))
START_BRACES = frozenset(('(', '{', '['))
END_BRACES = frozenset((')', '}', ']'))


class _Fix(NamedTuple):
    braces: tuple[int, int]
    multi_arg: bool
    remove_comma: bool
    initial_indent: int
    has_for: bool
    is_empty: bool
    comma_count: int


def fix_trailing_commas(source: str) -> str:
    """Add or remove trailing commas in Python source code."""
    tokens = src_to_tokens(source)
    _fix_tokens(tokens)
    return tokens_to_src(tokens)


def _fix_tokens(tokens: list[Token]) -> None:
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if not token.src:
            index += 1
            continue
        if token.name == 'OP' and token.src in START_BRACES:
            fix_data = _analyze_braces(tokens, index)
            if fix_data is not None:
                add_comma, remove_comma = _comma_policy(tokens, index, fix_data)
                _apply_fix(
                    tokens, fix_data,
                    add_comma=add_comma, remove_comma=remove_comma,
                )
        index += 1


# --- brace analysis ---


def _analyze_braces(tokens: list[Token], first_brace: int) -> _Fix | None:
    """Find matching close brace and gather info about contents."""
    depth = 1
    multi_arg = False
    has_for = False
    comma_count = 0
    has_content = False

    for scan in range(first_brace + 1, len(tokens)):
        token = tokens[scan]
        if token.name == 'OP' and token.src in START_BRACES:
            depth += 1
        elif token.name == 'OP' and token.src in END_BRACES:
            depth -= 1

        if depth == 1:
            if token.src == ',':
                multi_arg = True
                comma_count += 1
            if token.name == 'NAME' and token.src == 'for':
                has_for = True

        if depth >= 1 and token.name not in NON_CODING_TOKENS:
            has_content = True

        if depth == 0:
            break
    else:
        raise AssertionError('Unmatched brace')

    last_brace = scan

    # single-line with trailing comma or whitespace before close brace
    if (
            tokens[first_brace].line == tokens[last_brace].line and (
                tokens[last_brace - 1].name == UNIMPORTANT_WS or
                tokens[last_brace - 1].src == ','
            )
    ):
        should_remove = True
    elif tokens[first_brace].line == tokens[last_brace].line:
        return None  # single line, nothing to do
    else:
        should_remove = False

    # determine indentation of the line containing the open brace
    walk = first_brace
    while walk >= 0 and tokens[walk].name not in NEWLINES:
        walk -= 1

    if walk >= 0 and tokens[walk + 1].name in INDENT_TOKENS:
        initial_indent = len(tokens[walk + 1].src)
    else:
        initial_indent = 0

    return _Fix(
        braces=(first_brace, last_brace),
        multi_arg=multi_arg,
        remove_comma=should_remove,
        initial_indent=initial_indent,
        has_for=has_for,
        is_empty=not has_content,
        comma_count=comma_count,
    )


# --- classification (replaces AST walk) ---


def _comma_policy(
        tokens: list[Token],
        first_brace: int,
        fix: _Fix,
) -> tuple[bool, bool]:
    """Decide (add_comma, remove_comma) for this brace construct."""
    if fix.is_empty:
        return False, False

    brace_char = tokens[first_brace].src

    # comprehension / generator — never touch
    if fix.has_for:
        return False, False

    # [ and {
    if brace_char in ('[', '{'):
        # subscript: name[...] or expr[...] — skip
        if brace_char == '[' and _preceded_by_expression(tokens, first_brace):
            return False, False
        return True, True

    # ( — need to classify
    paren_kind = _classify_paren(tokens, first_brace)
    if paren_kind == 'call':
        return True, True
    if paren_kind == 'skip':
        return False, False

    # not a call — check for tuple (has commas at depth 1)
    if fix.multi_arg:
        one_el_tuple = fix.comma_count == 1
        return True, not one_el_tuple

    # parenthesized expression — don't touch
    return False, False


def _preceded_by_expression(tokens: list[Token], brace_idx: int) -> bool:
    """Check if the token before a brace is part of an expression (name, ), ])."""
    walk = brace_idx - 1
    while walk >= 0 and tokens[walk].name in NON_CODING_TOKENS:
        walk -= 1
    if walk < 0:
        return False
    prev = tokens[walk]
    if prev.name == 'OP' and prev.src in (')', ']'):
        return True
    if prev.name == 'NAME':
        return not keyword.iskeyword(prev.src)
    return False


def _classify_paren(tokens: list[Token], first_brace: int) -> str:
    """Classify what ( belongs to. Returns 'call', 'skip', or 'other'."""
    walk = first_brace - 1
    while walk >= 0 and tokens[walk].name in NON_CODING_TOKENS:
        walk -= 1
    if walk < 0:
        return 'other'

    prev = tokens[walk]

    # import (
    if prev.name == 'NAME' and prev.src == 'import':
        return 'call'

    # )( or ]( — chained call
    if prev.name == 'OP' and prev.src in (')', ']'):
        return 'call'

    if prev.name == 'NAME':
        # hard keywords are never function names
        if keyword.iskeyword(prev.src):
            return 'other'

        # look back one more token: def name( or class name(
        back = walk - 1
        while back >= 0 and tokens[back].name in NON_CODING_TOKENS:
            back -= 1

        # class name( — skip class bases per scope boundaries
        if back >= 0 and tokens[back].src == 'class':
            return 'skip'

        # def name( / async def name( / regular call like foo(
        return 'call'

    return 'other'


# --- token manipulation ---


def _apply_fix(
        tokens: list[Token],
        fix_data: _Fix,
        *,
        add_comma: bool,
        remove_comma: bool,
) -> None:
    first_brace, last_brace = fix_data.braces

    # --- unhug: push content away from braces onto its own lines ---
    hug_open = tokens[first_brace + 1].name not in NON_CODING_TOKENS
    hug_close = tokens[last_brace - 1].name not in NON_CODING_TOKENS
    if (
            # single nested brace pair (e.g. return ([...]) )
            not fix_data.multi_arg
            and tokens[first_brace + 1].src in START_BRACES
            and tokens[last_brace - 1].src in END_BRACES
            or
            # single token between braces (triple-quoted string)
            first_brace + 2 == last_brace
            or
            (
                tokens[first_brace + 1].name == 'FSTRING_START'
                and tokens[last_brace - 1].name == 'FSTRING_END'
            )
            or
            (
                tokens[first_brace + 1].name == 'TSTRING_START'
                and tokens[last_brace - 1].name == 'TSTRING_END'
            )
            or
            # single-line — don't unhug
            fix_data.remove_comma
    ):
        hug_open = hug_close = False

    if hug_open:
        new_indent = fix_data.initial_indent + 4
        tokens[first_brace + 1:first_brace + 1] = [
            Token('NL', '\n'),
            Token(UNIMPORTANT_WS, ' ' * new_indent),
        ]
        last_brace += 2

        # re-indent contents to match
        min_indent = None
        indents = []
        insert_indents = []
        for scan in range(first_brace + 3, last_brace):
            if (
                    tokens[scan - 1].name == 'NL'
                    and tokens[scan].name != 'NL'
            ):
                if tokens[scan].name != UNIMPORTANT_WS:
                    min_indent = 0
                    insert_indents.append(scan)
                else:
                    indent_len = len(tokens[scan].src)
                    if min_indent is None or indent_len < min_indent:
                        min_indent = indent_len
                    indents.append(scan)

        if indents:
            assert min_indent is not None
            for scan in indents:
                old_len = len(tokens[scan].src)
                tokens[scan] = tokens[scan]._replace(
                    src=' ' * (old_len - min_indent + new_indent),
                )
        for scan in reversed(insert_indents):
            tokens.insert(scan, Token(UNIMPORTANT_WS, ' ' * new_indent))
            last_brace += 1

    if hug_close:
        tokens[last_brace:last_brace] = [
            Token('NL', '\n'),
            Token(UNIMPORTANT_WS, ' ' * fix_data.initial_indent),
        ]
        last_brace += 2

    # --- add trailing comma if needed ---
    walk = last_brace - 1
    while tokens[walk].name in NON_CODING_TOKENS:
        walk -= 1

    if add_comma and tokens[walk].src != ',' and walk + 1 != last_brace:
        tokens.insert(walk + 1, Token('OP', ','))
        last_brace += 1

    # --- fix closing brace indentation ---
    back_1 = tokens[last_brace - 1]
    back_2 = tokens[last_brace - 2]
    if (
            back_1.name == UNIMPORTANT_WS
            and back_2.name == 'NL'
            and len(back_1.src) != fix_data.initial_indent
    ):
        tokens[last_brace - 1] = back_1._replace(
            src=' ' * fix_data.initial_indent,
        )

    # --- remove trailing comma/whitespace on single-line constructs ---
    if fix_data.remove_comma:
        start = last_brace
        if tokens[start - 1].name == UNIMPORTANT_WS:
            start -= 1
        if remove_comma and tokens[start - 1].src == ',':
            start -= 1
        del tokens[start:last_brace]
