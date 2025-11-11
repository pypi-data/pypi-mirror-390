# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from pydantic import AnyUrl, BaseModel, ConfigDict, Field

from ort.models.vcstype import VcsType


class VcsMatcher(BaseModel):
    """
    A matcher which matches its properties against a [RepositoryProvenance].

    Attributes:
        orttype (VcsType): The [type] to match for equality against [VcsInfo.type].
        url (AnyUrl): The [url] to match for equality against [VcsInfo.url].
        revision (str | None): The revision to match for equality against [RepositoryProvenance.resolvedRevision],
        or null to match any revision.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    orttype: VcsType = Field(
        alias="type",
        description="The [type] to match for equality against [VcsInfo.type].",
    )

    url: AnyUrl = Field(
        description="The [url] to match for equality against [VcsInfo.url].",
    )

    revision: str | None = Field(
        default=None,
        description="The revision to match for equality against [RepositoryProvenance.resolvedRevision],"
        "or null to match anyrevision.",
    )
