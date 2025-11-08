# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
#
# SPDX-License-Identifier: MIT


from enum import Enum


class LicenseFindingCurationReason(Enum):
    """
    A curation for a license finding. Use it to correct a license finding or to add a license that was not
    previously detected.

    Attributes:
        CODE: The findings occur in source code, for example the name of a variable.
        DATA_OF: The findings occur in a data, for example a JSON object defining all SPDX licenses.
        DOCUMENTATION_OF: The findings occur in documentation, for example in code comments or in the README.md.
        INCORRECT: The detected licenses are not correct. Use only if none of the other reasons apply.
        NOT_DETECTED: Add applicable license as the scanner did not detect it.
        REFERENCE: The findings reference a file or URL, e.g. SEE LICENSE IN LICENSE or https://jquery.org/license/.
    """

    CODE = "CODE"
    DATA_OF = "DATA_OF"
    DOCUMENTATION_OF = "DOCUMENTATION_OF"
    INCORRECT = "INCORRECT"
    NOT_DETECTED = "NOT_DETECTED"
    REFERENCE = "REFERENCE"
