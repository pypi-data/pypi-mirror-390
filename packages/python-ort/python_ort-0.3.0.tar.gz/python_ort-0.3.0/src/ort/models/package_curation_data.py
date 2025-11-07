# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT

from typing import Any

from pydantic import AnyUrl, BaseModel, ConfigDict, Field

from .hash import Hash
from .source_code_origin import SourceCodeOrigin
from .vcsinfo import VcsInfo


class CurationArtifact(BaseModel):
    url: AnyUrl
    hash: Hash


class PackageCurationData(BaseModel):
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
    vcs: VcsInfo | None = None
    is_metadata_only: bool | None = None
    is_modified: bool | None = None
    declared_license_mapping: dict[str, Any] = Field(default_factory=dict)
    source_code_origins: list[SourceCodeOrigin] | None = None
    labels: dict[str, str] = Field(default_factory=dict)
