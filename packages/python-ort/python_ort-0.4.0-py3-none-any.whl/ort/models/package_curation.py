# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from pydantic import BaseModel, ConfigDict

from .package_curation_data import PackageCurationData


class PackageCuration(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    id: str
    curations: PackageCurationData
