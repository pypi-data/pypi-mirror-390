# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from pydantic import BaseModel, ConfigDict, Field


class PackageManagerConfiguration(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    must_run_after: list[str] | None = Field(
        default=None,
        description="The configuration model for a package manager. This class is (de-)serialized in the following"
        "places:"
        "- Deserialized from config.yml as part of [OrtConfiguration] (via Hoplite)."
        "- Deserialized from .ort.yml as part of [RepositoryAnalyzerConfiguration] (via Jackson)"
        "- (De-)Serialized as part of [org.ossreviewtoolkit.model.OrtResult] (via Jackson).",
    )

    options: dict[str, str] | None = Field(
        default=None,
        description="Custom configuration options for the package manager. See the documentation of the respective"
        "class for available options.",
    )
