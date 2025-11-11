# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ort.models.config.license_finding_curation_reason import LicenseFindingCurationReason


class LicenseFindingCuration(BaseModel):
    """
    A curation for a license finding. Use it to correct a license finding or to add a license
    that was not previously detected.

    Attributes:
        path (str): A glob to match the file path of a license finding.
        start_lines (list[int] | None): A matcher for the start line of a license finding, matches if the start line
            matches any of [startLines] or if [startLines] is empty.
        line_count (int | None): A matcher for the line count of a license finding
            matches if the line count equals [lineCount] or if [lineCount] is None
        detected_license (str | None): The concluded license as SPDX expression or None
            for no license, see https://spdx.dev/spdx-specification-21-web-version#h.jxpfx0ykyb60.
        concluded_license (str): The concluded license as SPDX expression or None for no license,
            see https://spdx.dev/spdx-specification-21-web-version#h.jxpfx0ykyb60.
        reason (LicenseFindingCurationReason): The reason why the curation was made, out of a predefined choice.
        comment (str | None): A comment explaining this [LicenseFindingCuration].
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    path: str = Field(
        description="A glob to match the file path of a license finding.",
    )
    start_lines: list[int] | None = Field(
        default=None,
        description="A matcher for the start line of a license finding, matches if the start line matches any of"
        "[startLines] or if [startLines] is empty.",
    )
    line_count: int | None = Field(
        default=None,
        description="A matcher for the line count of a license finding"
        "matches if the line count equals [lineCount] or if [lineCount] is None",
    )

    detected_license: str | None = Field(
        default=None,
        description="The concluded license as SPDX expression or None"
        "for no license, see https://spdx.dev/spdx-specification-21-web-version#h.jxpfx0ykyb60.",
    )
    concluded_license: str = Field(
        description="The concluded license as SPDX expression or None for no license,"
        " see https://spdx.dev/spdx-specification-21-web-version#h.jxpfx0ykyb60.",
    )
    reason: LicenseFindingCurationReason = Field(
        description="The reason why the curation was made, out of a predefined choice.",
    )
    comment: str | None = Field(
        default=None,
        description="A comment explaining this [LicenseFindingCuration].",
    )

    @field_validator("start_lines", mode="before")
    @classmethod
    def parse_start_lines(cls, value: Any) -> list[int] | None:
        if value is None or value == "":
            return None
        if isinstance(value, str):
            # CSV style split
            return [int(x.strip()) for x in value.split(",") if x.strip()]
        if isinstance(value, list):
            return [int(x) for x in value]
        if isinstance(value, int):
            return [value]
        raise ValueError("start_lines must be a comma-separated string or a list of integers")
