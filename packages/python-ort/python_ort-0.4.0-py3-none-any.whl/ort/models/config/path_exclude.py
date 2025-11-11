# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from pydantic import BaseModel, ConfigDict, Field

from ort.models.config.path_exclude_reason import PathExcludeReason


class PathExclude(BaseModel):
    """
    Defines paths which should be excluded. Each file or directory that is matched by the [glob][pattern] is marked as
    excluded. If a project definition file is matched by the [pattern], the whole project is excluded. For details about
    the glob syntax see the [FileMatcher] implementation.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    pattern: str = Field(
        description="A glob to match the path of the project definition file, relative to the root of the repository."
    )

    reason: PathExcludeReason = Field(
        description="The reason why the project is excluded, out of a predefined choice.",
    )

    comment: str = Field(
        default_factory=str,
        description="A comment to further explain why the [reason] is applicable here.",
    )
