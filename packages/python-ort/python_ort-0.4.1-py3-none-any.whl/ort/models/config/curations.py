# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from pydantic import BaseModel, ConfigDict, Field

from ort.models.config.license_finding_curation import LicenseFindingCuration
from ort.models.package_curation import PackageCuration


class Curations(BaseModel):
    """
    Curations for artifacts in a repository.

    Attributes:
        packages(list[PackageCuration]): Curations for third-party packages.
        license_findings(list[LicenseFindingCuration]): Curations for license findings.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    packages: list[PackageCuration] = Field(
        default_factory=list,
        description="Curations for third-party packages.",
    )
    license_findings: list[LicenseFindingCuration] = Field(
        default_factory=list,
        description="Curations for license findings.",
    )
