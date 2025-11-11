# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from pydantic import BaseModel, ConfigDict, Field

from ort.models.config.package_manager_configuration import PackageManagerConfiguration


class RepositoryAnalyzerConfiguration(BaseModel):
    """
    Enable the analysis of projects that use version ranges to declare their dependencies. If set to true,
    dependencies of exactly the same project might change with another scan done at a later time if any of the
    (transitive) dependencies are declared using version ranges and a new version of such a dependency was
    published in the meantime. If set to false, analysis of projects that use version ranges will fail. Defaults to
    false.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    allow_dynamic_versions: bool | None = Field(
        default=None,
        description="Enable the analysis of projects that use version ranges to declare their dependencies."
        "If set to true, dependencies of exactly the same project might change with another scan done at a later time"
        "if any of the (transitive) dependencies are declared using version ranges and a new version of such a"
        "dependency was published in the meantime. If set to false, analysis of projects that use version ranges will"
        "fail. Defaults to false.",
    )
    enabled_package_managers: list[str] | None = Field(
        default=None,
        description="A list of the case-insensitive names of package managers that are enabled."
        "Disabling a package manager in [disabledPackageManagers] overrides enabling it here.",
    )
    disabled_package_managers: list[str] | None = Field(
        default=None,
        description="A list of the case-insensitive names of package managers that are disabled."
        "Disabling a package manager in this list overrides [enabledPackageManagers].",
    )
    package_managers: dict[str, PackageManagerConfiguration] | None = Field(
        default=None,
        description="Get a [PackageManagerConfiguration] from [packageManagers]. The difference to accessing the map"
        "directly is that [packageManager] can be case-insensitive.",
    )
    skip_excluded: bool | None = Field(
        default=None,
        description="A flag to control whether excluded scopes and paths should be skipped during the analysis.",
    )
