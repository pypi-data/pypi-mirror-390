# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT

from enum import Enum, auto


class PathExcludeReason(Enum):
    """
    Possible reasons for excluding a path.
    Attributes
        BUILD_TOOL_OF
            The path only contains tools used for building source code which are not included in
            distributed build artifacts.

        DATA_FILE_OF
            The path only contains data files such as fonts or images which are not included in
            distributed build artifacts.

        DOCUMENTATION_OF
            The path only contains documentation which is not included in distributed build artifacts.

        EXAMPLE_OF
            The path only contains source code examples which are not included in distributed build
            artifacts.

        OPTIONAL_COMPONENT_OF
            The path only contains optional components for the code that is built which are not included
            in distributed build artifacts.

        OTHER
            Any other reason which cannot be represented by any other element of PathExcludeReason.

        PROVIDED_BY
            The path only contains packages or sources for packages that have to be provided by the user
            of distributed build artifacts.

        TEST_OF
            The path only contains files used for testing source code which are not included in
            distributed build artifacts.

        TEST_TOOL_OF
            The path only contains tools used for testing source code which are not included in
            distributed build artifacts.
    """

    # The path only contains tools used for building source code which are not included in distributed build artifacts.
    BUILD_TOOL_OF = auto()

    # The path only contains data files such as fonts or images which are not included in distributed build artifacts.
    DATA_FILE_OF = auto()

    # The path only contains documentation which is not included in distributed build artifacts.
    DOCUMENTATION_OF = auto()

    # The path only contains source code examples which are not included in distributed build artifacts.
    EXAMPLE_OF = auto()

    # The path only contains optional components for the code that is built which are not included
    # in distributed build artifacts.
    OPTIONAL_COMPONENT_OF = auto()

    # Any other reason which cannot be represented by any other element of PathExcludeReason.
    OTHER = auto()

    # The path only contains packages or sources for packages that have to be provided by the user
    # of distributed build artifacts.
    PROVIDED_BY = auto()

    # The path only contains files used for testing source code which are not included in distributed build artifacts.
    TEST_OF = auto()

    # The path only contains tools used for testing source code which are not included in distributed build artifacts.
    TEST_TOOL_OF = auto()
