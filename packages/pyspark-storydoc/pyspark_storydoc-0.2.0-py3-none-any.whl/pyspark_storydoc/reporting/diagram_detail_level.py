#!/usr/bin/env python3
"""
Detail Level Constants for Business Flow Diagrams.

This module provides enum-like constants for specifying the level of detail
in business flow diagrams, avoiding typos and providing type safety.
"""

from enum import Enum


class DiagramDetailLevel(str, Enum):
    """
    Detail levels for business flow diagrams.

    Attributes:
        MINIMAL: Shows only business concepts (one node per concept)
        IMPACTING: Shows operations that impact record counts or tracked columns
        COMPLETE: Shows all operations including non-impacting transformations
    """
    MINIMAL = "minimal"
    IMPACTING = "impacting"
    COMPLETE = "complete"

    def __str__(self):
        """Return the string value for easy use."""
        return self.value


# Export constants for convenience
MINIMAL = DiagramDetailLevel.MINIMAL
IMPACTING = DiagramDetailLevel.IMPACTING
COMPLETE = DiagramDetailLevel.COMPLETE
