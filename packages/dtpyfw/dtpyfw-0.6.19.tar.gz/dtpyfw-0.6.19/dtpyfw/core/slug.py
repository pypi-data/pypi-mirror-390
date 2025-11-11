"""Helpers for normalising strings into URL slugs."""

import re
import unicodedata

__all__ = ("create_slug",)


def create_slug(name: str) -> str | None:
    """Generate a URL-friendly slug from a string.

    This function converts a string into a slug by lowercasing it, replacing
    spaces with hyphens, removing special characters, and normalizing
    diacritics.

    Args:
        name: The string to convert into a slug.

    Returns:
        The generated slug as a string, or None if the input is empty.
    """

    if not name:
        return None

    # Convert to lowercase and replace spaces with hyphens
    slug = name.lower().replace(" ", "-")

    # Remove any characters that are not letters, numbers, hyphens, or underscores
    slug = re.sub(r"[^a-zA-Z0-9\-_]", "", slug)

    # Normalize the slug to remove any diacritic marks
    slug = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode("utf-8")

    # Remove any leading or trailing hyphens
    slug = slug.strip("-")

    return slug
