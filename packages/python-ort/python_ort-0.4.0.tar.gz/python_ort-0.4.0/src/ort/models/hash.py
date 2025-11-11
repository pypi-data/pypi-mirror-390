# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT

from pydantic import BaseModel, Field

from ort.models.hash_algorithm import HashAlgorithm


class Hash(BaseModel):
    """
    A class that bundles a hash algorithm with its hash value.

    Attributes:
        value (str): The value calculated using the hash algorithm.
        algorithm (HashAlgorithm): The algorithm used to calculate the hash value.
    """

    value: str = Field(description="The value calculated using the hash algorithm.")
    algorithm: HashAlgorithm = Field(description="The algorithm used to calculate the hash value.")
