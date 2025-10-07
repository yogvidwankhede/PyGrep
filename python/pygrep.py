#!/usr/bin/env python3
"""
Custom Regular Expression Engine
--------------------------------
This module implements a lightweight regex engine supporting a restricted but
useful subset of common features:
    - Literal characters and the wildcard '.'
    - Character classes with ranges (e.g., [a-z], [^0-9])
    - Escape sequences: \d (digit), \w (alphanumeric or underscore)
    - Grouping with parentheses ( ... ) and alternation (cat|dog)
    - Quantifiers: ?, +, *
    - Backreferences: \1, \2, ...
    - Anchors: ^ (start of string), $ (end of string)

Design Principles:
    • Pedagogical clarity over optimization.
    • Recursive generator-based backtracking matcher.
    • Explicit handling of capture groups and quantifiers.

This code is written for academic demonstration and research-oriented projects.
"""

import os
import sys


# ======================================================================
#  Regex Engine
# ======================================================================

class MiniRegex:
    """
    A handcrafted regex engine based on recursive backtracking.

    Attributes:
        pattern (str): Raw regex pattern provided by the user.
        captures (list[str]): Captured substrings from groups.
        num_groups (int): Total number of capturing groups detected.
    """

    def __init__(self, pattern: str):
        self.pattern = pattern
        self.captures = []
        self.num_groups = self._count_groups(pattern)

    # ------------------------------------------------------------------
    #  Utility: Counting capture groups
    # ------------------------------------------------------------------
    def _count_groups(self, pat: str) -> int:
        """
        Count number of capturing groups, ignoring escaped parentheses.
        """
        count, i = 0, 0
        while i < len(pat):
            if pat[i] == "\\":
                i += 2
            elif pat[i] == "(":
                count += 1
                i += 1
            else:
                i += 1
        return count

    # ------------------------------------------------------------------
    #  Character classification utilities
    # ------------------------------------------------------------------
    @staticmethod
    def is_digit(c: str) -> bool:
        return c.isdigit()

    @staticmethod
    def is_alpha(c: str) -> bool:
        return c.isalpha()

    @staticmethod
    def is_underscore(c: str) -> bool:
        return c == "_"

    # ------------------------------------------------------------------
    #  Character class matcher
    # ------------------------------------------------------------------
    def _match_class(self, c: str, class_expr: str, negated: bool = False) -> bool:
        """
        Evaluate whether character `c` belongs to a class expression.
        Supports ranges like 'a-z'.
        """
        matched, i = False, 0
        while i < len(class_expr):
            if i + 2 < len(class_expr) and class_expr[i + 1] == "-":
                if class_expr[i] <= c <= class_expr[i + 2]:
                    matched = True
                    break
                i += 3
            else:
                if class_expr[i] == c:
                    matched = True
                    break
                i += 1
        return not matched if negated else matched

    # ------------------------------------------------------------------
    #  Pattern parsing utilities
    # ------------------------------------------------------------------
    def _parse_atom(self, pat: str):
        """
        Parse the next atomic element (literal, escape, class, wildcard).
        Returns: (atom_type, atom_value, length_consumed, negated_flag)
        """
        p, neg = 0, False
        if pat[p] == "\\":
            p += 1
            esc = pat[p]
            if esc.isdigit():
                return "backref", int(esc), p + 1, neg
            elif esc in "dw":
                return "escape", esc, p + 1, neg
            return "literal", esc, p + 1, neg

        if pat[p] == "[":
            p += 1
            if p < len(pat) and pat[p] == "^":
                neg = True
                p += 1
            start = p
            while p < len(pat) and pat[p] != "]":
                p += 1
            if p >= len(pat):
                raise ValueError("Unterminated character class")
            return "class", pat[start:p], p + 1, neg

        if pat[p] == ".":
            return "wildcard", ".", 1, neg

        return "literal", pat[p], 1, neg

    def _find_matching_paren(self, pat: str, start_idx: int) -> int:
        """
        Find the matching ')' for the '(' at start_idx, accounting for nesting.
        """
        depth = 1
        for i in range(start_idx + 1, len(pat)):
            if pat[i] == "(":
                depth += 1
            elif pat[i] == ")":
                depth -= 1
                if depth == 0:
                    return i
        raise ValueError("Missing closing parenthesis in pattern.")

    def _split_alternatives(self, content: str) -> list[str]:
        """
        Split a group's content by top-level '|', ignoring nested groups.
        """
        parts, depth, last = [], 0, 0
        for i, ch in enumerate(content):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "|" and depth == 0:
                parts.append(content[last:i])
                last = i + 1
        parts.append(content[last:])
        return parts

    def _parse_expression(self, pat: str):
        """
        Parse one logical expression: either a group or a single atom.
        """
        if pat.startswith("("):
            end_idx = self._find_matching_paren(pat, 0)
            inner = pat[1:end_idx]
            return "group", self._split_alternatives(inner), end_idx + 1, False
        return self._parse_atom(pat)

    # ------------------------------------------------------------------
    #  Atom matcher factory
    # ------------------------------------------------------------------
    def _matcher_for(self, atom_type: str, atom_val, neg: bool):
        if atom_type == "escape":
            if atom_val == "d":
                return self.is_digit
            if atom_val == "w":
                return lambda c: (self.is_alpha(c) or
                                  self.is_digit(c) or
                                  self.is_underscore(c))
        if atom_type == "literal":
            return lambda c: c == atom_val
        if atom_type == "class":
            return lambda c: self._match_class(c, atom_val, neg)
        if atom_type == "wildcard":
            return lambda c: True
        return None

    # ------------------------------------------------------------------
    #  Recursive matching generator
    # ------------------------------------------------------------------
    def _match_inner(self, text: str, pat: str, group_idx: int):
        """
        Core recursive matcher. Yields (length_consumed, new_group_index).
        """
        if not pat:
            yield 0, group_idx
            return

        expr_type, expr_val, consumed, neg = self._parse_expression(pat)
        quant = pat[consumed] if consumed < len(
            pat) and pat[consumed] in "+?*" else None
        remainder = pat[consumed + (1 if quant else 0):]

        # Handle groups
        if expr_type == "group":
            this_group = group_idx + 1
            alts = expr_val

            def match_group_once(inp, gidx):
                for alt in alts:
                    saved = list(self.captures)
                    for alt_len, next_idx in self._match_inner(inp, alt, gidx):
                        self.captures[this_group - 1] = inp[:alt_len]
                        yield alt_len, next_idx
                    self.captures = saved

            if quant is None:
                for mlen, idx in match_group_once(text, this_group):
                    for rlen, r_idx in self._match_inner(text[mlen:], remainder, idx):
                        yield mlen + rlen, r_idx
                return

            if quant == "?":
                for mlen, idx in match_group_once(text, this_group):
                    for rlen, r_idx in self._match_inner(text[mlen:], remainder, idx):
                        yield mlen + rlen, r_idx
                for rlen, r_idx in self._match_inner(text, remainder, group_idx):
                    yield rlen, r_idx
                return

            if quant == "+":
                def plus_recurse(inp, gidx):
                    for one_len, one_idx in match_group_once(inp, gidx):
                        saved_caps = list(self.captures)
                        for more_len, more_idx in plus_recurse(inp[one_len:], gidx):
                            yield one_len + more_len, more_idx
                        self.captures = saved_caps
                        yield one_len, one_idx

                for total_len, idx in plus_recurse(text, this_group):
                    for rlen, r_idx in self._match_inner(text[total_len:], remainder, idx):
                        yield total_len + rlen, r_idx
                return

        # Handle backreference
        if expr_type == "backref":
            ref = expr_val
            if ref <= len(self.captures) and self.captures[ref - 1] is not None:
                cap = self.captures[ref - 1]
                if text.startswith(cap):
                    for rlen, r_idx in self._match_inner(text[len(cap):], remainder, group_idx):
                        yield len(cap) + rlen, r_idx
            return

        # Handle single atom
        matcher = self._matcher_for(expr_type, expr_val, neg)

        if quant is None:
            if text and matcher(text[0]):
                for rlen, r_idx in self._match_inner(text[1:], remainder, group_idx):
                    yield 1 + rlen, r_idx
            return

        if quant == "+":
            if not text or not matcher(text[0]):
                return
            reps = 1
            while reps < len(text) and matcher(text[reps]):
                reps += 1
            for used in range(reps, 0, -1):
                for rlen, r_idx in self._match_inner(text[used:], remainder, group_idx):
                    yield used + rlen, r_idx
            return

        if quant == "?":
            if text and matcher(text[0]):
                for rlen, r_idx in self._match_inner(text[1:], remainder, group_idx):
                    yield 1 + rlen, r_idx
            for rlen, r_idx in self._match_inner(text, remainder, group_idx):
                yield rlen, r_idx
            return

        if quant == "*":
            reps = 0
            while reps < len(text) and matcher(text[reps]):
                reps += 1
            for used in range(reps, -1, -1):
                for rlen, r_idx in self._match_inner(text[used:], remainder, group_idx):
                    yield used + rlen, r_idx
            return

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def _strip_anchors(self, pat: str):
        start = pat.startswith("^")
        end = pat.endswith("$")
        core = pat[int(start):-int(end) or None]
        return start, end, core

    def matches(self, text: str) -> bool:
        """
        Public entry point: returns True if pattern matches text.
        """
        anchored_start, anchored_end, core = self._strip_anchors(self.pattern)
        self.captures = [None] * self.num_groups

        if anchored_start:
            gen = self._match_inner(text, core, 0)
            if anchored_end:
                return any(length == len(text) for length, _ in gen)
            return next(gen, None) is not None

        for i in range(len(text) + 1):
            gen = self._match_inner(text[i:], core, 0)
            if anchored_end:
                if any(i + length == len(text) for length, _ in gen):
                    return True
            else:
                if next(gen, None) is not None:
                    return True
        return False


# ======================================================================
#  Command-Line Interface
# ======================================================================

class CLI:
    """
    Handles input/output and command-line argument parsing.
    """

    def __init__(self):
        self.pattern = None
        self.files = None

    def _parse_args(self):
        recursive = False
        if len(sys.argv) >= 5 and sys.argv[1] == "-r" and sys.argv[2] == "-E":
            return sys.argv[3], sys.argv[4], True
        if len(sys.argv) < 3 or sys.argv[1] != "-E":
            print("Usage: ./prog [-r] -E <pattern> [files...]")
            sys.exit(1)
        return sys.argv[2], sys.argv[3:] if len(sys.argv) > 3 else None, False

    def _read_stdin(self):
        text = sys.stdin.read()
        return text[:-1] if text.endswith("\n") else text

    def _find_files_recursive(self, path: str, base: str, acc: list):
        try:
            for entry in os.listdir(path):
                full = os.path.join(path, entry)
                if os.path.isfile(full):
                    acc.append(os.path.relpath(full, base))
                elif os.path.isdir(full):
                    self._find_files_recursive(full, base, acc)
        except PermissionError:
            pass

    def run(self):
        parsed = self._parse_args()
        self.pattern = parsed[0]
        engine = MiniRegex(self.pattern)

        # Recursive directory search
        if len(parsed) == 3 and parsed[2]:
            target_dir = parsed[1]
            if not os.path.isdir(target_dir):
                print(f"Error: {target_dir} is not a directory")
                sys.exit(1)

            abs_target = os.path.abspath(target_dir)
            base = os.path.dirname(abs_target) or "."
            paths = []
            self._find_files_recursive(abs_target, base, paths)

            matched_any = False
            for rel in paths:
                full = os.path.join(base, rel)
                try:
                    with open(full, "r") as f:
                        for line in f:
                            stripped = line.rstrip("\n")
                            if engine.matches(stripped):
                                sys.stdout.write(f"{rel}:{stripped}\n")
                                matched_any = True
                except (IOError, PermissionError):
                    continue
            sys.exit(0 if matched_any else 1)

        # Multiple file mode
        if isinstance(parsed[1], list) and parsed[1] is not None:
            matched_any = False
            self.files = parsed[1]
            for fname in self.files:
                with open(fname, "r") as f:
                    for line in f:
                        stripped = line.rstrip("\n")
                        if engine.matches(stripped):
                            if len(self.files) == 1:
                                sys.stdout.write(line)
                            else:
                                sys.stdout.write(f"{fname}:{line}")
                            matched_any = True
            sys.exit(0 if matched_any else 1)

        # Stdin single-line mode
        text = self._read_stdin()
        result = engine.matches(text)
        if result:
            sys.stdout.write("\nPattern matched :)\n")
            sys.exit(0)
        else:
            sys.stdout.write("\nPattern does not match :(\n")
            sys.exit(1)


# ======================================================================
#  Entry Point
# ======================================================================

if __name__ == "__main__":
    CLI().run()
