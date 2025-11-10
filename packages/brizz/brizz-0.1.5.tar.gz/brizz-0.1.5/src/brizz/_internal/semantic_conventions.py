"""Semantic conventions for Brizz SDK."""

from opentelemetry.context import create_key

# Brizz namespace for attributes
BRIZZ = "brizz"

# Context key for association properties
PROPERTIES_CONTEXT_KEY = create_key("brizz.properties")

# Session ID key for context properties
SESSION_ID = "session.id"

# Brizz SDK attributes
BRIZZ_SDK_VERSION = "brizz.sdk.version"
BRIZZ_SDK_LANGUAGE = "brizz.sdk.language"

# SDK language value
SDK_LANGUAGE = "python"
