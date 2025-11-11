from __future__ import annotations

import datetime as dt
import json
from enum import StrEnum
from hashlib import sha256
from typing import Annotated, Any, Dict, List, Optional, Self, Sequence, Union

import httpx
from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer, model_validator

from fbnconfig.property import LifeTime, PropertyKey
from fbnconfig.transaction_type import MetricValue

from .resource_abc import CamelAlias, Ref, Resource, register_resource


def des_isodate(value: str | dt.datetime) -> dt.datetime:
    """Deserialize ISO 8601 date string to datetime object."""
    if isinstance(value, dt.datetime):
        return value.astimezone(tz=dt.timezone.utc)
    return dt.datetime.fromisoformat(value)


def ser_isodate(value: dt.datetime) -> str:
    """Serialize datetime object to ISO 8601 string."""
    return value.isoformat()


IsoDateTime = Annotated[
    dt.datetime | dt.date,
    BeforeValidator(des_isodate), PlainSerializer(ser_isodate)
]


class PropertyValue(CamelAlias, BaseModel):
    property_key: PropertyKey = Field(serialization_alias="propertyKey")
    label_value: Optional[str] = Field(default=None, serialization_alias="labelValue")
    metric_value: Optional[MetricValue] = Field(default=None, serialization_alias="metricValue")
    label_set_value: Optional[List[str]] = Field(default=None, serialization_alias="labelSetValue")
    effective_from: IsoDateTime | None = None
    effective_until: IsoDateTime | None = None

    @model_validator(mode="before")
    @classmethod
    def des_model(cls, data, info):
        if not isinstance(data, dict):
            return data
        style = info.context.get("style", "api") if info.context else "api"
        if style == "api" and data.get("value", None):
            return data | data["value"]
        return data

    @model_validator(mode="after")
    def validate_one_value_exists(self) -> Self:
        fields = ["label_value", "metric_value", "label_set_value"]
        s = [field for field in fields if getattr(self, field) is not None]
        if len(s) > 1:
            raise KeyError(f"Cannot set {' and '.join(s)}, only one of {' or '.join(fields)} can be set")

        return self


class SupportedDomain(StrEnum):
    Instrument = "Instrument"
    Person = "Person"
    LegalEntity = "LegalEntity"
    CustomEntity = "CustomEntity"


def serialize_properties_as_dict(values: List[PropertyValue], info):
    style = info.context.get("style", "api") if info.context else "api"
    if style == "dump":
        return values
    property_dict = {}
    for prop in values:
        value = {}
        if prop.label_value:
            value["labelValue"] = prop.label_value
        elif prop.metric_value:
            value["metricValue"] = prop.metric_value
        elif prop.label_set_value:
            value["labelSetValue"] = prop.label_set_value
        key = f"{prop.property_key.domain.value}/{prop.property_key.scope}/{prop.property_key.code}"
        property_dict[key] = {"key": key, "value": value}

        if prop.effective_from is not None:
            property_dict[key]["effectiveFrom"] = prop.effective_from

        if prop.effective_until is not None:
            property_dict[key]["effectiveUntil"] = prop.effective_until

    return property_dict


def des_properties_dict(data, info) -> Sequence[PropertyValue] | Dict | None:
    if not isinstance(data, dict) or data is None:
        return data
    style = info.context.get("style", "api") if info.context else "api"
    if style == "api" and isinstance(data, dict):
        data = [value | {"propertyKey": value["key"]} for value in data.values()]
    return data


PropertyValueDict = Annotated[
    Sequence[PropertyValue],
    BeforeValidator(des_properties_dict), PlainSerializer(serialize_properties_as_dict)
]


@register_resource()
class IdentifierDefinitionRef(BaseModel, Ref):
    """
    Reference to an identifier definition resource.

    Example
    ----------
    >>> from fbnconfig import identifier_definition
    >>> ref = identifier_definition.IdentifierDefinitionRef(
    >>>  id="identifier-def-ref",
    >>>  domain="Instrument",
    >>>  identifier_scope="id_scope",
    >>>  identifier_type="id_type")
    """

    id: str = Field(exclude=True)
    domain: SupportedDomain
    identifier_scope: str
    identifier_type: str

    def attach(self, client):
        """Attach to an existing identifier definition resource."""
        scope = self.identifier_scope
        id_type = self.identifier_type
        try:
            client.get(f"/api/api/identifierdefinitions/{self.domain}/{scope}/{id_type}")
        except httpx.HTTPStatusError as ex:
            error_message = f"Identifier Definition {self.domain}/{scope}/{id_type} does not exist"
            if ex.response.status_code == 404:
                raise RuntimeError(error_message)
            else:
                raise ex


@register_resource()
class IdentifierDefinitionResource(CamelAlias, BaseModel, Resource):
    """identifier definition resource"""

    id: str = Field(exclude=True)
    domain: SupportedDomain
    identifier_scope: str
    identifier_type: str
    life_time: LifeTime
    hierarchy_usage: str | None = None
    hierarchy_level: str | None = None
    display_name: str | None = None
    description: str | None = None
    properties: PropertyValueDict | None = None

    @model_validator(mode="before")
    @classmethod
    def des_model(cls, data, info) -> Dict[str, Any]:
        if not isinstance(data, dict):
            return data
        # Handle id from context (for dump/undump)
        if info.context and info.context.get("id"):
            data = data | {"id": info.context.get("id")}

        return data

    def __get_content_hash__(self) -> str:
        dump = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        return sha256(json.dumps(dump, sort_keys=True).encode()).hexdigest()

    def read(self, client: httpx.Client, old_state) -> Dict[str, Any]:
        domain = old_state.domain
        scope = old_state.identifier_scope
        id_type = old_state.identifier_type
        response = client.get(f"/api/api/identifierdefinitions/{domain}/{scope}/{id_type}")

        result = response.json()
        # Remove unnecessary fields
        result.pop("href", None)

        return result

    def create(self, client: httpx.Client) -> Dict[str, Any]:
        body = self.model_dump(mode="json", exclude_none=True, by_alias=True)

        response = client.post("/api/api/identifierdefinitions", json=body)
        result = response.json()

        # Remove unnecessary fields
        result.pop("href", None)

        source_version = self.__get_content_hash__()
        remote_version = result["version"]["asAtVersionNumber"]

        return {
            "domain": self.domain,
            "identifier_scope": self.identifier_scope,
            "identifier_type": self.identifier_type,
            "source_version": source_version,
            "remote_version": remote_version
        }

    def update(self, client: httpx.Client, old_state) -> Union[None, Dict[str, Any]]:
        current_identity_tuple = (self.domain, self.identifier_scope, self.identifier_type)
        old_state_tuple = (old_state.domain, old_state.identifier_scope, old_state.identifier_type)

        if current_identity_tuple != old_state_tuple:
            self.delete(client, old_state)
            return self.create(client)

        source_hash = self.__get_content_hash__()
        remote = self.read(client, old_state)
        remote_hash = remote["version"]["asAtVersionNumber"]

        if remote_hash == old_state.remote_version and source_hash == old_state.source_version:
            return None

        #  Exclude fields not needed in put call
        body = self.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
            exclude={"domain", "identifier_scope", "identifier_type"}
        )

        scope = self.identifier_scope
        id_type = self.identifier_type

        response = client.put(
            f"/api/api/identifierdefinitions/{self.domain}/{scope}/{id_type}",
            json=body)
        result = response.json()

        # Remove unnecessary fields
        result.pop("href", None)

        return {
            "domain": self.domain,
            "identifier_scope": self.identifier_scope,
            "identifier_type": self.identifier_type,
            "source_version": source_hash,
            "remote_version": result["version"]["asAtVersionNumber"]
        }

    @staticmethod
    def delete(client: httpx.Client, old_state) -> None:

        domain = old_state.domain
        scope = old_state.identifier_scope
        id_type = old_state.identifier_type
        client.delete(f"/api/api/identifierdefinitions/{domain}/{scope}/{id_type}")

    def deps(self):
        deps = []
        if self.properties is None:
            return deps

        for perp_prop in self.properties:
            deps.append(perp_prop.property_key)

        return deps
