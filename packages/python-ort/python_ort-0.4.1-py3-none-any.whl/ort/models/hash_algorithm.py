# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT

from typing import ClassVar

from pydantic import BaseModel, Field, model_validator


class HashAlgorithm(BaseModel):
    """
    A Python port of the Kotlin HashAlgorithm enum class.

    Each algorithm has one or more aliases, an empty hash value,
    and an 'is_verifiable' flag.
    """

    aliases: list[str] = Field(default_factory=list)
    empty_value: str = ""
    is_verifiable: bool = True

    # ---- known algorithms ----
    NONE: ClassVar["HashAlgorithm"]
    UNKNOWN: ClassVar["HashAlgorithm"]
    MD5: ClassVar["HashAlgorithm"]
    SHA1: ClassVar["HashAlgorithm"]
    SHA256: ClassVar["HashAlgorithm"]
    SHA384: ClassVar["HashAlgorithm"]
    SHA512: ClassVar["HashAlgorithm"]
    SHA1GIT: ClassVar["HashAlgorithm"]

    # ---- derived property ----
    @property
    def size(self) -> int:
        """The length of the empty hash string for this algorithm."""
        return len(self.empty_value)

    # ---- validation ----
    @model_validator(mode="before")
    @classmethod
    def _from_alias(cls, value):
        """Allow initialization from alias string."""
        if isinstance(value, str):
            algo = cls.from_string(value)
            return algo.model_dump()
        return value

    # ---- class methods ----
    @classmethod
    def from_string(cls, alias: str) -> "HashAlgorithm":
        """Find a HashAlgorithm by alias name (case-insensitive)."""
        alias_upper = alias.upper()
        for algo in cls._entries():
            if any(a.upper() == alias_upper for a in algo.aliases):
                return algo
        return cls.UNKNOWN

    @classmethod
    def create(cls, value: str) -> "HashAlgorithm":
        """
        Create a HashAlgorithm from a hash value string, based on its length.
        Returns NONE if value is blank, UNKNOWN otherwise.
        """
        if not value.strip():
            return cls.NONE
        for algo in cls._entries():
            if len(value) == algo.size:
                return algo
        return cls.UNKNOWN

    @classmethod
    def _entries(cls) -> list["HashAlgorithm"]:
        """Return the list of all defined algorithms."""
        return [
            cls.NONE,
            cls.UNKNOWN,
            cls.MD5,
            cls.SHA1,
            cls.SHA256,
            cls.SHA384,
            cls.SHA512,
            cls.SHA1GIT,
        ]

    def __str__(self) -> str:
        return self.aliases[0] if self.aliases else ""


HashAlgorithm.NONE = HashAlgorithm(aliases=[""], empty_value="", is_verifiable=False)
HashAlgorithm.UNKNOWN = HashAlgorithm(aliases=["UNKNOWN"], empty_value="", is_verifiable=False)
HashAlgorithm.MD5 = HashAlgorithm(
    aliases=["MD5"],
    empty_value="d41d8cd98f00b204e9800998ecf8427e",
)
HashAlgorithm.SHA1 = HashAlgorithm(
    aliases=["SHA-1", "SHA1"],
    empty_value="da39a3ee5e6b4b0d3255bfef95601890afd80709",
)
HashAlgorithm.SHA256 = HashAlgorithm(
    aliases=["SHA-256", "SHA256"],
    empty_value="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
)
HashAlgorithm.SHA384 = HashAlgorithm(
    aliases=["SHA-384", "SHA384"],
    empty_value=("38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6e1da274edebfe76f65fbd51ad2f14898b95b"),
)
HashAlgorithm.SHA512 = HashAlgorithm(
    aliases=["SHA-512", "SHA512"],
    empty_value=(
        "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce"
        "47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
    ),
)
HashAlgorithm.SHA1GIT = HashAlgorithm(
    aliases=["SHA-1-GIT", "SHA1-GIT", "SHA1GIT", "SWHID"],
    empty_value="e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
)
