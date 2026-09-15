# SPDX-License-Identifier: AGPL-3.0-or-later
"""Command parser for the console."""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ParsedCommand:
    """Parsed command structure."""
    command: str = ""
    args: List[str] = field(default_factory=list)
    flags: dict = field(default_factory=dict)
    raw: str = ""


class CommandParser:
    """Parses command input into structured format."""

    def parse(self, input_str: str) -> ParsedCommand:
        """Parse a command string."""
        result = ParsedCommand(raw=input_str.strip())
        
        if not result.raw:
            return result

        # Tokenize
        tokens = self._tokenize(result.raw)
        if not tokens:
            return result

        result.command = tokens[0].lower()
        remaining = tokens[1:]

        # Parse flags and arguments
        i = 0
        while i < len(remaining):
            token = remaining[i]
            if token.startswith("--"):
                # Long flag
                if "=" in token:
                    key, value = token[2:].split("=", 1)
                    result.flags[key] = value
                else:
                    result.flags[token[2:]] = True
            elif token.startswith("-") and len(token) > 1:
                # Short flag
                result.flags[token[1:]] = True
            else:
                result.args.append(token)
            i += 1

        return result

    def _tokenize(self, input_str: str) -> List[str]:
        """Tokenize input string, handling quoted strings."""
        tokens = []
        current = ""
        in_quote = False
        quote_char = None

        for char in input_str:
            if in_quote:
                if char == quote_char:
                    in_quote = False
                else:
                    current += char
            else:
                if char in ('"', "'"):
                    in_quote = True
                    quote_char = char
                elif char == ' ':
                    if current:
                        tokens.append(current)
                        current = ""
                else:
                    current += char

        if current:
            tokens.append(current)

        return tokens
