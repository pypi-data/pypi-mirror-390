"""
Parse Elasticsearch query string syntax to extract field filters.

Based on Lucene query syntax specification from:
https://lucene.apache.org/core/2_9_4/queryparsersyntax.html
https://github.com/pyparsing/pyparsing/blob/master/examples/lucene_grammar.py
"""

import pyparsing as pp

# Enable packrat parsing for performance
pp.ParserElement.enable_packrat()


def parse_field_filters(
    query_text: str,
) -> tuple[str, dict[str, list[str]], dict[str, list[str]]]:
    """
    Parse field filters from an Elasticsearch query string using Lucene grammar.

    Supports full Lucene/Elasticsearch query syntax including:
    - Field filters: field:value, field:"quoted value"
    - Positive/Negative filters: +field:value, -field:value
    - Range queries: field:[min TO max], field:{min TO max}
    - Fuzzy search: field:value~0.8
    - Proximity search: field:"phrase"~10
    - Wildcards: field:val*, field:te?t
    - Regular expressions: field:/regex/
    - Boosting: field:value^2, field:"phrase"^2.5
    - Comparison operators: field:>10, field:>=10, field:<100, field:<=100
    - Wildcard field names: book.*:value
    - Escaped field names: first\\ name:value
    - Escaped characters: field:"value with \\" quote"
    - Boolean operators: AND, OR, NOT
    - Elasticsearch extensions: _exists_:field, _missing_:field

    Args:
        query_text: The query string to parse

    Returns:
        A tuple of (remaining_text, filters, excludes) where:
        - remaining_text: Query text with field filters removed
        - filters: Dict mapping field names to lists of values
        - excludes: Dict mapping field names to lists of excluded values

    Examples:
        >>> parse_field_filters('name:"Jane Doe" countries:USA')
        ('', {'name': ['Jane Doe'], 'countries': ['USA']}, {})

        >>> parse_field_filters('foo bar schema:Person')
        ('foo bar', {'schema': ['Person']}, {})

        >>> parse_field_filters('test -schema:Page')
        ('test', {}, {'schema': ['Page']})

        >>> parse_field_filters('date:[2020 TO 2022]')
        ('', {'date': ['[ 2020 TO 2022 ]']}, {})

        >>> parse_field_filters('name:john~0.8')
        ('', {'name': ['john~0.8']}, {})

        >>> parse_field_filters('title:"jakarta apache"~10')
        ('', {'title': ['"jakarta apache"~10']}, {})

        >>> parse_field_filters('title:quick^2')
        ('', {'title': ['quick^2']}, {})

        >>> parse_field_filters('age:>10')
        ('', {'age': ['>10']}, {})
    """
    if not query_text or not query_text.strip():
        return "", {}, {}

    filters: dict[str, list[str]] = {}
    excludes: dict[str, list[str]] = {}
    remaining_parts: list[str] = []

    # Define grammar elements
    COLON = pp.Literal(":")
    MINUS = pp.Literal("-")
    PLUS = pp.Literal("+")
    CARAT = pp.Literal("^")

    # Field name: alphanumeric, underscore, dot, hyphen, wildcard, or escaped spaces
    # Based on Lucene spec and Elasticsearch extensions
    # Support: book.author, field_name, book.*, first\ name
    field_name_part = pp.Regex(r'(?:[a-zA-Z0-9_.\-*]|\\ )+')
    field_name = field_name_part("field")

    # Boost modifier: ^[number]
    # Can follow any value type
    boost_modifier = CARAT + pp.Regex(r'[0-9.]+')

    # Range queries: field:[min TO max] or field:{min TO max}
    TILDE = pp.Literal("~")
    LBRACK = pp.Literal("[")
    RBRACK = pp.Literal("]")
    LBRACE = pp.Literal("{")
    RBRACE = pp.Literal("}")
    TO = pp.CaselessKeyword("TO")

    # Range term: anything except TO keyword and brackets
    range_term = pp.Regex(r'[^\s\[\]{}"]+')

    # Inclusive range [min TO max]
    incl_range = LBRACK + range_term + TO + range_term + RBRACK
    # Exclusive range {min TO max}
    excl_range = LBRACE + range_term + TO + range_term + RBRACE

    # Range value with optional boost
    # Custom parsing to format: "[ min TO max ]" or "[ min TO max ]^2"
    def format_range(tokens):
        # tokens[0] is the combined string from Combine, e.g., "[ 2020 TO 2022 ] ^ 2"
        # We need to remove space before ^
        if len(tokens) == 1:
            result = str(tokens[0])
            # Remove spaces around ^
            import re
            result = re.sub(r'\s+\^\s*', '^', result)
            return result
        return str(tokens[0])

    range_value = pp.Combine(
        (incl_range | excl_range) + pp.Optional(boost_modifier),
        adjacent=False,
        join_string=" "
    )("value")
    range_value.set_parse_action(format_range)

    # Quoted string with escape support
    quoted_string_base = pp.QuotedString('"', esc_char="\\")

    # Proximity search: "phrase"~10^2 - must preserve quotes and modifiers
    # Match the entire structure including quotes, proximity, and boost
    quoted_with_proximity = pp.Combine(
        pp.Literal('"')
        + pp.Regex(r'(?:[^"\\]|\\.)*')  # Content with escape support
        + pp.Literal('"')
        + TILDE  # Require tilde
        + pp.Optional(pp.Regex(r'[0-9.]+'))
        + pp.Optional(boost_modifier),  # Optional boost after proximity
        adjacent=True,
        join_string=""
    )

    # Regular quoted string with optional boost - quotes are removed
    quoted_with_boost = pp.Combine(
        quoted_string_base + boost_modifier,
        adjacent=True,
        join_string=""
    )
    quoted_without_boost = quoted_string_base

    # Try proximity version first (most specific), then boost, then plain
    quoted_value = (
        quoted_with_proximity | quoted_with_boost | quoted_without_boost
    )("value")

    # Regular expression value: /regex/
    # Content between forward slashes
    SLASH = pp.Literal("/")
    regex_content = pp.Regex(r'[^/]+')  # Everything between slashes
    regex_value = pp.Combine(
        SLASH + regex_content + SLASH + pp.Optional(boost_modifier),
        adjacent=True,
        join_string=""
    )("value")

    # Unquoted value with optional fuzzy and boost modifiers
    # For fuzzy search: word~0.8^2, word~0.8, word^2
    fuzzy_modifier = TILDE + pp.Optional(pp.Regex(r'[0-9.]+'))
    unquoted_word = pp.Regex(r'[^\s:()[\]{}"\-+~/]+')

    # Try all combinations: fuzzy+boost, fuzzy only, boost only, plain
    unquoted_with_fuzzy_boost = pp.Combine(
        unquoted_word + fuzzy_modifier + boost_modifier,
        adjacent=True,
        join_string=""
    )
    unquoted_with_fuzzy = pp.Combine(
        unquoted_word + fuzzy_modifier,
        adjacent=True,
        join_string=""
    )
    unquoted_with_boost = pp.Combine(
        unquoted_word + boost_modifier,
        adjacent=True,
        join_string=""
    )
    unquoted_plain = unquoted_word

    unquoted_value = (
        unquoted_with_fuzzy_boost
        | unquoted_with_fuzzy
        | unquoted_with_boost
        | unquoted_plain
    )("value")

    # Value can be range, quoted, regex, or unquoted (order matters)
    value = range_value | quoted_value | regex_value | unquoted_value

    # Optional positive/negative modifiers
    # + means required (we treat as normal filter)
    # - means excluded (negation)
    modifier = pp.Optional(MINUS | PLUS)("modifier")

    # Field filter pattern: [+/-]field:value
    field_filter = pp.Group(modifier + field_name + COLON + value)

    # Scan for all field filter matches in the query
    last_end = 0
    for tokens, start, end in field_filter.scan_string(query_text):
        # Add any text before this match to remaining parts
        if start > last_end:
            text_before = query_text[last_end:start].strip()
            if text_before:
                # Filter out standalone operators
                words = text_before.split()
                for word in words:
                    if word.upper() not in ("AND", "OR", "NOT"):
                        remaining_parts.append(word)

        # Extract the matched filter
        match = tokens[0]  # type: ignore[index]
        mod = str(match.get("modifier", ""))  # type: ignore[union-attr]
        is_negated = mod == "-"
        field = str(match["field"])  # type: ignore[index]
        val = str(match["value"])  # type: ignore[index]

        # Clean up escaped spaces in field names
        field = field.replace("\\ ", " ")

        # Add to appropriate dict
        target = excludes if is_negated else filters
        if field not in target:
            target[field] = []
        target[field].append(val)

        last_end = end

    # Add any remaining text after the last match
    if last_end < len(query_text):
        text_after = query_text[last_end:].strip()
        if text_after:
            words = text_after.split()
            for word in words:
                if word.upper() not in ("AND", "OR", "NOT"):
                    remaining_parts.append(word)

    remaining_text = " ".join(remaining_parts)
    return remaining_text, filters, excludes
