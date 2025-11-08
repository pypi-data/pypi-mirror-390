# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT

from pydantic import AnyUrl, BaseModel, Field

from .vcstype import VcsType


class VcsInfoCurationData(BaseModel):
    """
    Bundles general Version Control System information.

    Attributes:
        type(VcsType): The type of the VCS, for example Git, GitRepo, Mercurial, etc.
        url(AnyUrl): The URL to the VCS repository.
        revision(str): The VCS-specific revision (tag, branch, SHA1) that the version of the package maps to.
        path(str): The path inside the VCS to take into account.
            If the VCS supports checking out only a subdirectory, only this path is checked out.
    """

    type: VcsType | None = Field(
        default=None,
        description="The type of the VCS, for example Git, GitRepo, Mercurial, etc.",
    )
    url: AnyUrl | None = Field(
        default=None,
        description="The URL to the VCS repository.",
    )
    revision: str | None = Field(
        default=None,
        description="The VCS-specific revision (tag, branch, SHA1) that the version of the package maps to.",
    )
    path: str | None = Field(
        default=None,
        description="The path inside the VCS to take into account."
        "If the VCS supports checking out only a subdirectory, only this path is checked out.",
    )
