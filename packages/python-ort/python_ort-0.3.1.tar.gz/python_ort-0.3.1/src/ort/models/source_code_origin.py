# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT

from enum import Enum


class SourceCodeOrigin(Enum):
    vcs = "VCS"
    artifact = "ARTIFACT"
