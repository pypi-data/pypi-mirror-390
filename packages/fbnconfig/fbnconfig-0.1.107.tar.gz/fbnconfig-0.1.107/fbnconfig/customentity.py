from __future__ import annotations

import copy
from enum import StrEnum
from typing import Annotated, Any, Dict, List

import httpx
from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer, model_validator

from . import property  # type: noqa
from .resource_abc import CamelAlias, Ref, Resource, register_resource

_ = property  # force property import to be used becuase it was exposed before


class CollectionType(StrEnum):
    SINGLE = "Single"
    ARRAY = "Array"


class LifeTime(StrEnum):
    PERPETUAL = "Perpetual"
    TIMEVARIANT = "TimeVariant"


class FieldType(StrEnum):
    STRING = "String"
    BOOLEAN = "Boolean"
    DATE_TIME = "DateTime"
    DECIMAL = "Decimal"


class FieldDefinition(CamelAlias, BaseModel):
    name: str
    lifetime: LifeTime
    type: FieldType
    collection_type: CollectionType = CollectionType.SINGLE
    required: bool
    description: str = ""


# These are optional in the API create and will be given default values. When read is called
# they will not be returned if they have the default value
DEFAULT_FIELD = {"collectionType": "Single", "description": ""}


@register_resource()
class EntityTypeResource(CamelAlias, BaseModel, Resource):
    id: str = Field(exclude=True)
    entity_type_name: str
    display_name: str
    description: str
    field_schema: List[FieldDefinition]

    @model_validator(mode="before")
    @classmethod
    def des_model(cls, data: Any, info) -> Dict[str, Any]:
        if not isinstance(data, dict):
            return data
        if info.context and info.context.get("id"):
            return data | {"id": info.context.get("id")}
        return data

    def read(self, client, old_state) -> Dict[str, Any]:
        entity_type = old_state.entitytype
        return client.request("get", f"/api/api/customentities/entitytypes/{entity_type}").json()

    def create(self, client: httpx.Client):
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        res = client.request("POST", "/api/api/customentities/entitytypes", json=desired).json()
        return {"entitytype": res["entityType"]}

    def update(self, client: httpx.Client, old_state):
        remote = self.read(client, old_state)
        # enrich remote fields with the default values if not present
        remote["fieldSchema"] = [rem | DEFAULT_FIELD for rem in remote["fieldSchema"]]
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        effective = remote | copy.deepcopy(desired)
        for i in range(0, len(self.field_schema)):
            if i < len(remote["fieldSchema"]):
                eff_field = remote["fieldSchema"][i] | desired["fieldSchema"][i]
                effective["fieldSchema"][i] = eff_field
        if effective == remote:
            return None
        res = client.request(
            "PUT", f"/api/api/customentities/entitytypes/{old_state.entitytype}", json=desired
        ).json()
        return {"entitytype": res["entityType"]}

    @staticmethod
    def delete(client, old_state):
        raise RuntimeError("Cannot delete a custom entity definition")

    def deps(self):
        return []


class EntityTypeRef(CamelAlias, BaseModel, Ref):
    id: str = Field(exclude=True)
    entity_type_name: str

    def attach(self, client):
        entity_type = self.entity_type_name
        try:
            client.get(f"/api/api/customentities/entitytypes/{entity_type}").json()
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 404:
                raise RuntimeError(f"Custom Entity Defintion {entity_type} does not exist")
            else:
                raise ex


def ser_entitytype_key(value, info):
    if info.context and info.context.get("style", "api") == "dump":
        return {"$ref": value.id}
    return "~" + value.entity_type_name


def des_entitytype_key(value, info):
    if not isinstance(value, dict):
        return value
    if info.context and info.context.get("$refs"):
        ref = info.context["$refs"][value["$ref"]]
        return ref
    return value


EntityTypeKey = Annotated[
    EntityTypeResource | EntityTypeRef,
    BeforeValidator(des_entitytype_key), PlainSerializer(ser_entitytype_key)
]
