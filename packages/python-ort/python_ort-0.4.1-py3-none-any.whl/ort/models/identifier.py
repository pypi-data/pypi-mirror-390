# SPDX-FileCopyrightText: 2025 Helio Chissini de Castro <heliocastro@gmail.com>
# SPDX-License-Identifier: MIT


from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Identifier(BaseModel):
    """
    A unique identifier for a software component.

    Attributes:
        orttype (str): The type of component this identifier describes. When used in the context of a [Project],
            the type equals the one of the package manager that manages the project (e.g. 'Gradle'
            for a Gradle project). When used in the context of a [Package], the type is the name
            of the artifact ecosystem (e.g. 'Maven' for a file from a Maven repository).
        namespace (str): The namespace of the component, for example the group for 'Maven' or the scope for 'NPM'.
        name (str): The name of the component.
        version (str): The version of the component.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    orttype: str = Field(
        alias="type",
        description="The type of component this identifier describes. When used in the context of a [Project],"
        "the type equals the one of the package manager that manages the project (e.g. 'Gradle' "
        "for a Gradle project). When used in the context of a [Package], the type is the name"
        "of the artifact ecosystem (e.g. 'Maven' for a file from a Maven repository).",
    )

    namespace: str = Field(
        description="The namespace of the component, for examplethe group for 'Maven' or the scope for 'NPM'.",
    )

    name: str = Field(
        description="The name of the component.",
    )

    version: str = Field(
        description="The version of the component.",
    )

    @model_validator(mode="before")
    @classmethod
    def parse_string_or_dict(cls, value: Any):
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            parts = value.split(":")
            if len(parts) != 4:
                raise ValueError("Identifier string must be in the format 'type:namespace:name:version'")
            return {
                "type": parts[0],
                "namespace": parts[1],
                "name": parts[2],
                "version": parts[3],
            }
        raise TypeError("Identifier must be a dict or a string in the correct format")
