# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from pydantic import BaseModel, ConfigDict, Field

from ort.models.config.license_finding_curation import LicenseFindingCuration
from ort.models.config.path_exclude import PathExclude
from ort.models.config.vcsmatcher import VcsMatcher
from ort.models.identifier import Identifier
from ort.models.source_code_origin import SourceCodeOrigin


class PackageConfiguration(BaseModel):
    """
    A class used in the [OrtConfiguration] to configure [PathExclude]s and [LicenseFindingCuration]s for a specific
    [Package]'s [Identifier] (and [Provenance]).
    Note that [PathExclude]s and [LicenseFindingCuration]s for [Project]s are configured by a
    [RepositoryConfiguration]'s excludes and curations properties instead.

    Attributes:
        id (Identifier): The [Identifier] which must match with the identifier of the package in
            order for this package curation to apply. The [version][Identifier.version] can be
            either a plain version string matched for equality, or an Ivy-style version matchers.
            * The other components of the [identifier][id] are matched by equality.
        source_artifact_url (str | None): The source artifact this configuration applies to.
        vcs (VcsMatcher | None): The vcs and revision this configuration applies to.
        source_code_origin (SourceCodeOrigin | None): The source code origin this configuration
            applies to.
        path_excludes (list[PathExclude]): Path excludes.
        license_finding_curations (list[LicenseFindingCuration]): License finding curations.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    id: Identifier = Field(
        description="The [Identifier] which must match with the identifier of the package in order for this package"
        "curation to apply. The [version][Identifier.version] can be either a plain version string matched for"
        "equality, or an Ivy-style version matchers."
        "* The other components of the [identifier][id] are matched by equality.",
    )

    source_artifact_url: str | None = Field(
        default=None,
        description="The source artifact this configuration applies to.",
    )

    vcs: VcsMatcher | None = Field(
        default=None,
        description="The vcs and revision this configuration applies to.",
    )

    source_code_origin: SourceCodeOrigin | None = Field(
        default=None,
        description="The source code origin this configuration applies to.",
    )

    path_excludes: list[PathExclude] = Field(
        default_factory=list,
        description="Path excludes.",
    )

    license_finding_curations: list[LicenseFindingCuration] = Field(
        default_factory=list,
        description="License finding curations.",
    )
