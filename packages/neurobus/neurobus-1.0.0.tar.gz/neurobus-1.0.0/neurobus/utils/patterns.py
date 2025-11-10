"""Pattern matching utilities for topic patterns."""

import re
from fnmatch import fnmatch


def wildcard_match(pattern: str, topic: str) -> bool:
    """
    Match topic against wildcard pattern.

    Supports:
    - * : matches any characters within a segment
    - # : matches zero or more segments
    - . : segment separator

    Examples:
        - "user.*" matches "user.login", "user.logout"
        - "user.#" matches "user.login", "user.profile.update"
        - "*.error" matches "system.error", "network.error"

    Args:
        pattern: Pattern string with wildcards
        topic: Topic string to match

    Returns:
        True if topic matches pattern
    """
    # Convert pattern to regex
    regex_pattern = _wildcard_to_regex(pattern)
    return bool(re.match(regex_pattern, topic))


def _wildcard_to_regex(pattern: str) -> str:
    """
    Convert wildcard pattern to regex.

    Args:
        pattern: Wildcard pattern

    Returns:
        Regex pattern
    """
    # Escape special regex characters except * and #
    escaped = re.escape(pattern)

    # Replace escaped wildcards with regex equivalents
    # \* (single segment wildcard) -> [^.]+
    # \# (multi segment wildcard) -> .*
    regex = escaped.replace(r"\*", r"[^.]+")
    regex = regex.replace(r"\#", r".*")

    # Anchor to start and end
    return f"^{regex}$"


def glob_match(pattern: str, topic: str) -> bool:
    """
    Match topic using shell-style glob patterns.

    Args:
        pattern: Glob pattern
        topic: Topic string

    Returns:
        True if matches
    """
    return fnmatch(topic, pattern)


def extract_variables(pattern: str, topic: str) -> dict[str, str] | None:
    """
    Extract variables from topic based on pattern.

    Pattern can include named captures: {variable_name}

    Example:
        pattern = "user.{user_id}.{action}"
        topic = "user.123.login"
        result = {"user_id": "123", "action": "login"}

    Args:
        pattern: Pattern with variable placeholders
        topic: Topic to extract from

    Returns:
        Dictionary of variable names to values, or None if no match
    """
    # Convert pattern to regex with named groups
    regex_pattern = pattern
    variables = re.findall(r"\{(\w+)\}", pattern)

    for var in variables:
        regex_pattern = regex_pattern.replace(f"{{{var}}}", f"(?P<{var}>[^.]+)")

    # Replace remaining wildcards
    regex_pattern = regex_pattern.replace("*", r"[^.]+")
    regex_pattern = regex_pattern.replace("#", r".*")

    regex_pattern = f"^{regex_pattern}$"

    match = re.match(regex_pattern, topic)
    if match:
        return match.groupdict()
    return None


def is_wildcard_pattern(pattern: str) -> bool:
    """
    Check if pattern contains wildcards.

    Args:
        pattern: Pattern to check

    Returns:
        True if pattern contains * or #
    """
    return "*" in pattern or "#" in pattern


def is_variable_pattern(pattern: str) -> bool:
    """
    Check if pattern contains variable placeholders.

    Args:
        pattern: Pattern to check

    Returns:
        True if pattern contains {variable} placeholders
    """
    return bool(re.search(r"\{\w+\}", pattern))


def normalize_pattern(pattern: str) -> str:
    """
    Normalize pattern for consistent matching.

    - Removes redundant separators
    - Converts to lowercase (if case-insensitive)
    - Removes leading/trailing separators

    Args:
        pattern: Pattern to normalize

    Returns:
        Normalized pattern
    """
    # Remove leading/trailing dots
    pattern = pattern.strip(".")

    # Replace multiple dots with single dot
    pattern = re.sub(r"\.+", ".", pattern)

    return pattern


def pattern_similarity(pattern1: str, pattern2: str) -> float:
    """
    Compute similarity between two patterns.

    Used for ranking subscriptions.

    Args:
        pattern1: First pattern
        pattern2: Second pattern

    Returns:
        Similarity score (0.0-1.0)
    """
    # Simple Levenshtein-based similarity
    # More sophisticated implementations could use embedding similarity

    # Exact match
    if pattern1 == pattern2:
        return 1.0

    # Compute edit distance
    distance = _levenshtein_distance(pattern1, pattern2)
    max_len = max(len(pattern1), len(pattern2))

    if max_len == 0:
        return 1.0

    return 1.0 - (distance / max_len)


def _levenshtein_distance(s1: str, s2: str) -> int:
    """
    Compute Levenshtein distance between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Edit distance
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
