# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT

from pydantic import BaseModel, Field, model_validator


class VcsType(BaseModel):
    """
    A class for Version Control System types. Each type has one or more [aliases] associated to it,
    where the first alias is the definite name. This class is not implemented as an enum as
    constructing from an unknown type should be supported while maintaining that type as the primary
    alias for the string representation.

    Attributes:
        aliases(list[str]): Primary name and aliases
    """

    aliases: list[str] = Field(default_factory=list, description="Primary name and aliases")

    @model_validator(mode="after")
    def ensure_non_empty(self):
        """Ensure the aliases list is never empty."""
        if not self.aliases:
            self.aliases = [""]
        return self

    def __str__(self):
        return self.aliases[0] if self.aliases else ""

    @classmethod
    def for_name(cls, name: str) -> "VcsType":
        """Lookup known type by name, or create a new instance."""
        for t in KNOWN_TYPES:
            if any(alias.lower() == name.lower() for alias in t.aliases):
                return t
        return cls(aliases=[name])


# Define known VCS types as constants
GIT = VcsType(aliases=["Git", "GitHub", "GitLab"])
GIT_REPO = VcsType(aliases=["GitRepo", "git-repo", "repo"])
MERCURIAL = VcsType(aliases=["Mercurial", "hg"])
SUBVERSION = VcsType(aliases=["Subversion", "svn"])
UNKNOWN = VcsType(aliases=[""])

KNOWN_TYPES = [GIT, GIT_REPO, MERCURIAL, SUBVERSION]
