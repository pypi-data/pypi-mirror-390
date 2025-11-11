# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT

from pydantic import BaseModel, Field, model_validator

# Define known VCS types as constants
GIT = ["Git", "GitHub", "GitLab"]
GIT_REPO = ["GitRepo", "git-repo", "repo"]
MERCURIAL = ["Mercurial", "hg"]
SUBVERSION = ["Subversion", "svn"]

KNOWN_TYPES = GIT + GIT_REPO + MERCURIAL + SUBVERSION


class VcsType(BaseModel):
    """
    A class for Version Control System types. Each type has one or more [aliases] associated to it,
    where the first alias is the definite name. This class is not implemented as an enum as
    constructing from an unknown type should be supported while maintaining that type as the primary
    alias for the string representation.

    Attributes:
        name(str): Primary name and aliases
    """

    name: str = Field(default_factory=str)

    @model_validator(mode="before")
    @classmethod
    def _forName(cls, value):
        # Allow direct string input (e.g., "Git" or "gitlab")
        if isinstance(value, str):
            if any(item.lower() == value.lower() for item in KNOWN_TYPES):
                return {"name": value}
            else:
                # Not a known type → default to empty string
                return {"name": ""}
        # Allow dict input or existing model
        elif isinstance(value, dict):
            name = value.get("name", "")
            if any(item.lower() == name.lower() for item in KNOWN_TYPES):
                return value
            else:
                return {"name": ""}
        return {"name": ""}
