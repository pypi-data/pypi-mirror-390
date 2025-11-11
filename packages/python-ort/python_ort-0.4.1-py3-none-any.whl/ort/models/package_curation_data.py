# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT

from typing import Any

from pydantic import AnyUrl, BaseModel, ConfigDict, Field

from .hash import Hash
from .source_code_origin import SourceCodeOrigin
from .vcsinfo_curation_data import VcsInfoCurationData


class CurationArtifact(BaseModel):
    url: AnyUrl
    hash: Hash


class PackageCurationData(BaseModel):
    """
    Data model for package curation data.

    Attributes:
        comment (str | None): Optional comment about the curation.
        purl (str | None): The package URL (PURL) identifying the package.
        cpe (str | None): The Common Platform Enumeration (CPE) identifier.
        authors (list[str] | None): List of authors of the package.
        concluded_license (str | None): The license concluded for the package.
        description (str | None): Description of the package.
        homepage_url (str | None): URL of the package's homepage.
        binary_artifact (CurationArtifact | None): Information about the binary artifact.
        source_artifact (CurationArtifact | None): Information about the source artifact.
        vcs (VcsInfoCurationData | None): Version control system information.
        is_metadata_only (bool | None): Whether the curation is metadata only.
        is_modified (bool | None): Whether the package has been modified.
        declared_license_mapping (dict[str, Any]): Mapping of declared licenses.
        source_code_origins (list[SourceCodeOrigin] | None): List of source code origins.
        labels (dict[str, str]): Additional labels for the package.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    comment: str | None = None
    purl: str | None = None
    cpe: str | None = None
    authors: list[str] | None = None
    concluded_license: str | None = None
    description: str | None = None
    homepage_url: str | None = None
    binary_artifact: CurationArtifact | None = None
    source_artifact: CurationArtifact | None = None
    vcs: VcsInfoCurationData | None = None
    is_metadata_only: bool | None = None
    is_modified: bool | None = None
    declared_license_mapping: dict[str, Any] = Field(default_factory=dict)
    source_code_origins: list[SourceCodeOrigin] | None = None
    labels: dict[str, str] = Field(default_factory=dict)
