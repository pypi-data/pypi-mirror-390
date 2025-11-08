# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
#
# SPDX-License-Identifier: MIT


from enum import Enum


class HashAlgorithm(Enum):
    """
    An enum of supported hash algorithms. Each algorithm has one or more [aliases] associated to it,
    where the first alias is the definite name.

    Attributes:
        NONE: No hash algorithm.
        UNKNOWN: An unknown hash algorithm.
        MD5: The Message-Digest 5 hash algorithm, see [MD5](http://en.wikipedia.org/wiki/MD5).
        SHA1: The Secure Hash Algorithm 1, see [SHA-1](https://en.wikipedia.org/wiki/SHA-1).
        SHA256: The Secure Hash Algorithm 2 with 256 bits, see [SHA-256](https://en.wikipedia.org/wiki/SHA-256).
        SHA384: The Secure Hash Algorithm 2 with 384 bits, see [SHA-384](https://en.wikipedia.org/wiki/SHA-384).
        SHA512: The Secure Hash Algorithm 2 with 512 bits, see [SHA-512](https://en.wikipedia.org/wiki/SHA-512).
        SHA1GIT: The Secure Hash Algorithm 1, but calculated on a Git "blob" object, see
            - https://git-scm.com/book/en/v2/Git-Internals-Git-Objects#_object_storage
            - https://docs.softwareheritage.org/devel/swh-model/persistent-identifiers.html#git-compatibility
    """

    NONE = "NONE"
    UNKNOWN = "UNKNOWN"
    MD5 = "MD5"
    SHA1 = "SHA1"
    SHA256 = "SHA256"
    SHA384 = "SHA384"
    SHA512 = "SHA512"
    SHA1GIT = (
        ["SHA-1-GIT", "SHA1-GIT", "SHA1GIT", "SWHID"],
        "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    )
