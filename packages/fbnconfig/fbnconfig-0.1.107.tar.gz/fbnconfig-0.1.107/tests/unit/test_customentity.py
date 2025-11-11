import json
from types import SimpleNamespace

import httpx
import pytest

from fbnconfig import customentity

TEST_BASE = "https://foo.lusid.com"


def response_hook(response: httpx.Response):
    response.read()
    response.raise_for_status()


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeEntityTypeResource:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    def test_create(self, respx_mock):
        respx_mock.post("/api/api/customentities/entitytypes").mock(
            return_value=httpx.Response(200, json={"entityType": "~typename"})
        )
        # given a desired definition with one field
        sut = customentity.EntityTypeResource(
            id="xyz",
            entity_type_name="animal",
            display_name="Animal",
            description="Not mineral or vegetable",
            field_schema=[
                customentity.FieldDefinition(
                    name="legs",
                    lifetime=customentity.LifeTime.PERPETUAL,
                    type=customentity.FieldType.DECIMAL,
                    required=False,
                )
            ],
        )
        # when we create it
        state = sut.create(self.client)
        # then the state the typename returned by the create call
        assert state == {"entitytype": "~typename"}
        # and a create request was sent without the startValue
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/api/api/customentities/entitytypes"
        assert json.loads(request.content) == {
            "entityTypeName": "animal",
            "displayName": "Animal",
            "description": "Not mineral or vegetable",
            "fieldSchema": [
                {
                    "name": "legs",
                    "lifetime": "Perpetual",
                    "type": "Decimal",
                    "description": "",
                    "collectionType": "Single",
                    "required": False,
                }
            ],
        }

    def test_update_with_no_changes(self, respx_mock):
        # given an existing CE where the field has a description
        respx_mock.get("/api/api/customentities/entitytypes/~whatevah").mock(
            return_value=httpx.Response(
                200,
                json={
                    "entityTypeName": "animal",
                    "displayName": "Animal",
                    "description": "Not mineral or vegetable",
                    "fieldSchema": [
                        {
                            "name": "legs",
                            "lifetime": "Perpetual",
                            "type": "Decimal",
                            "description": "",
                            "collectionType": "Single",
                            "required": False,
                        }
                    ],
                },
            )
        )
        # and a desired which is the same but the field description is none
        sut = customentity.EntityTypeResource(
            id="xyz",
            entity_type_name="animal",
            display_name="Animal",
            description="Not mineral or vegetable",
            field_schema=[
                customentity.FieldDefinition(
                    name="legs",
                    lifetime=customentity.LifeTime.PERPETUAL,
                    type=customentity.FieldType.DECIMAL,
                    required=False,
                )
            ],
        )
        old_state = SimpleNamespace(entitytype="~whatevah")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state is None
        assert state is None
        # and a read was made but no PUT

    def test_update_with_collection_single(self, respx_mock):
        # given an existing CE with a collection type of single
        # note, api will not return single here even if the user has
        # set it
        respx_mock.get("/api/api/customentities/entitytypes/~whatevah").mock(
            return_value=httpx.Response(
                200,
                json={
                    "entityTypeName": "animal",
                    "displayName": "Animal",
                    "description": "Not mineral or vegetable",
                    "fieldSchema": [
                        {
                            "name": "arms",
                            "lifetime": "Perpetual",
                            "type": "Decimal",
                            "required": False,
                            # no collectionType member from GET
                        }
                    ],
                },
            )
        )
        # and a desired where the user has explicitly asked for single
        sut = customentity.EntityTypeResource(
            id="xyz",
            entity_type_name="animal",
            display_name="Animal",
            description="Not mineral or vegetable",
            field_schema=[
                customentity.FieldDefinition(
                    name="arms",
                    lifetime=customentity.LifeTime.PERPETUAL,
                    type=customentity.FieldType.DECIMAL,
                    collection_type=customentity.CollectionType.SINGLE,
                    required=False,
                )
            ],
        )
        old_state = SimpleNamespace(entitytype="~whatevah")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state None because there is no change
        assert state is None

    def test_update_with_changed_field(self, respx_mock):
        # given an existing CE with an arms field
        respx_mock.get("/api/api/customentities/entitytypes/~whatevah").mock(
            return_value=httpx.Response(
                200,
                json={
                    "entityTypeName": "animal",
                    "displayName": "Animal",
                    "description": "Not mineral or vegetable",
                    "fieldSchema": [
                        {
                            "name": "arms",
                            "lifetime": "Perpetual",
                            "type": "Decimal",
                            "description": "a default descriptoin",
                        }
                    ],
                },
            )
        )
        respx_mock.put("/api/api/customentities/entitytypes/~whatevah").mock(
            return_value=httpx.Response(200, json={"entityType": "~whatevah"})
        )
        # and a desired with a legs field
        sut = customentity.EntityTypeResource(
            id="xyz",
            entity_type_name="animal",
            display_name="Animal",
            description="Not mineral or vegetable",
            field_schema=[
                customentity.FieldDefinition(
                    name="legs",
                    lifetime=customentity.LifeTime.PERPETUAL,
                    type=customentity.FieldType.DECIMAL,
                    required=False,
                )
            ],
        )
        old_state = SimpleNamespace(entitytype="~whatevah")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state is the same
        assert state == {"entitytype": "~whatevah"}
        # and a put request was sent with legs
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/api/api/customentities/entitytypes/~whatevah"
        assert json.loads(request.content) == {
            "entityTypeName": "animal",
            "displayName": "Animal",
            "description": "Not mineral or vegetable",
            "fieldSchema": [
                {
                    "name": "legs",
                    "lifetime": "Perpetual",
                    "type": "Decimal",
                    "required": False,
                    "description": "",
                    "collectionType": "Single",
                }
            ],
        }

    def test_update_with_removed_field(self, respx_mock):
        # given an existing CE with arms and legs
        respx_mock.get("/api/api/customentities/entitytypes/~whatevah").mock(
            return_value=httpx.Response(
                200,
                json={
                    "entityTypeName": "animal",
                    "displayName": "Animal",
                    "description": "Not mineral or vegetable",
                    "fieldSchema": [
                        {
                            "name": "legs",
                            "lifetime": "Perpetual",
                            "type": "Decimal",
                            "description": "a default descriptoin",
                        },
                        {
                            "name": "arms",
                            "lifetime": "Perpetual",
                            "type": "Decimal",
                            "description": "a default descriptoin",
                        },
                    ],
                },
            )
        )
        respx_mock.put("/api/api/customentities/entitytypes/~whatevah").mock(
            return_value=httpx.Response(200, json={"entityType": "~whatevah"})
        )
        # and a desired with a legs field
        sut = customentity.EntityTypeResource(
            id="xyz",
            entity_type_name="animal",
            display_name="Animal",
            description="Not mineral or vegetable",
            field_schema=[
                customentity.FieldDefinition(
                    name="legs",
                    lifetime=customentity.LifeTime.PERPETUAL,
                    type=customentity.FieldType.DECIMAL,
                    required=False,
                )
            ],
        )
        old_state = SimpleNamespace(entitytype="~whatevah")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state is the same
        assert state == {"entitytype": "~whatevah"}
        # and a put request was sent with legs
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/api/api/customentities/entitytypes/~whatevah"
        assert json.loads(request.content) == {
            "entityTypeName": "animal",
            "displayName": "Animal",
            "description": "Not mineral or vegetable",
            "fieldSchema": [
                {
                    "name": "legs",
                    "lifetime": "Perpetual",
                    "type": "Decimal",
                    "required": False,
                    "description": "",
                    "collectionType": "Single",
                }
            ],
        }

    def test_update_with_additional_field(self, respx_mock):
        # given an existing CE with an arms field
        respx_mock.get("/api/api/customentities/entitytypes/~whatevah").mock(
            return_value=httpx.Response(
                200,
                json={
                    "entityTypeName": "animal",
                    "displayName": "Animal",
                    "description": "Not mineral or vegetable",
                    "fieldSchema": [
                        {
                            "name": "arms",
                            "lifetime": "Perpetual",
                            "type": "Decimal",
                            "description": "a default descriptoin",
                        }
                    ],
                },
            )
        )
        respx_mock.put("/api/api/customentities/entitytypes/~whatevah").mock(
            return_value=httpx.Response(200, json={"entityType": "~whatevah"})
        )
        # and a desired with an arms and a legs field
        sut = customentity.EntityTypeResource(
            id="xyz",
            entity_type_name="animal",
            display_name="Animal",
            description="Not mineral or vegetable",
            field_schema=[
                customentity.FieldDefinition(
                    name="legs",
                    lifetime=customentity.LifeTime.PERPETUAL,
                    type=customentity.FieldType.DECIMAL,
                    required=False,
                ),
                customentity.FieldDefinition(
                    name="arms",
                    lifetime=customentity.LifeTime.PERPETUAL,
                    type=customentity.FieldType.DECIMAL,
                    required=False,
                ),
            ],
        )
        old_state = SimpleNamespace(entitytype="~whatevah")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state is the same
        assert state == {"entitytype": "~whatevah"}
        # and a put request was sent with the new fields
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/api/api/customentities/entitytypes/~whatevah"
        assert json.loads(request.content) == {
            "entityTypeName": "animal",
            "displayName": "Animal",
            "description": "Not mineral or vegetable",
            "fieldSchema": [
                {
                    "name": "legs",
                    "lifetime": "Perpetual",
                    "type": "Decimal",
                    "required": False,
                    "description": "",
                    "collectionType": "Single",
                },
                {
                    "name": "arms",
                    "lifetime": "Perpetual",
                    "type": "Decimal",
                    "required": False,
                    "description": "",
                    "collectionType": "Single",
                },
            ],
        }

    def test_delete_throws(self):
        # given a resource that exists in the remnte
        old_state = SimpleNamespace(entitytype="~whatever")
        # when we delete it throws brcause uou cant delete a CE
        with pytest.raises(RuntimeError):
            customentity.EntityTypeResource.delete(self.client, old_state)

    def test_deps(self):
        sut = customentity.EntityTypeResource(
            id="xyz",
            entity_type_name="animal",
            display_name="Animal",
            description="Not mineral or vegetable",
            field_schema=[],
        )
        # it's deps are empty
        assert sut.deps() == []

    def test_dump(self):
        # given an entity type resource
        sut = customentity.EntityTypeResource(
            id="et1",
            entity_type_name="TestEntity",
            display_name="Test Entity Type",
            description="A test entity type",
            field_schema=[
                customentity.FieldDefinition(
                    name="field1",
                    lifetime=customentity.LifeTime.PERPETUAL,
                    type=customentity.FieldType.STRING,
                    collection_type=customentity.CollectionType.SINGLE,
                    required=True,
                    description="First field"
                ),
                customentity.FieldDefinition(
                    name="field2",
                    lifetime=customentity.LifeTime.TIMEVARIANT,
                    type=customentity.FieldType.DECIMAL,
                    collection_type=customentity.CollectionType.ARRAY,
                    required=False,
                    description="Second field"
                )
            ]
        )
        # when we dump it
        dumped = sut.model_dump(
            by_alias=True,
            round_trip=True,
            exclude_none=True,
            context={"style": "dump"}
        )
        # then the dumped state is correct
        assert dumped == {
            "entityTypeName": "TestEntity",
            "displayName": "Test Entity Type",
            "description": "A test entity type",
            "fieldSchema": [
                {
                    "name": "field1",
                    "lifetime": "Perpetual",
                    "type": "String",
                    "collectionType": "Single",
                    "required": True,
                    "description": "First field"
                },
                {
                    "name": "field2",
                    "lifetime": "TimeVariant",
                    "type": "Decimal",
                    "collectionType": "Array",
                    "required": False,
                    "description": "Second field"
                }
            ]
        }

    def test_undump(self):
        # given a dumped entity type state
        dumped = {
            "entityTypeName": "TestEntity",
            "displayName": "Test Entity Type",
            "description": "A test entity type",
            "fieldSchema": [
                {
                    "name": "field1",
                    "lifetime": "Perpetual",
                    "type": "String",
                    "collectionType": "Single",
                    "required": True,
                    "description": "First field"
                },
                {
                    "name": "field2",
                    "lifetime": "TimeVariant",
                    "type": "Decimal",
                    "collectionType": "Array",
                    "required": False,
                    "description": "Second field"
                }
            ]
        }
        # when we undump it
        sut = customentity.EntityTypeResource.model_validate(
            dumped,
            context={
                "style": "undump",
                "$refs": {},
                "id": "et1",
            }
        )
        # then the id has been extracted from the context
        assert sut.id == "et1"
        assert sut.entity_type_name == "TestEntity"
        assert sut.display_name == "Test Entity Type"
        assert sut.description == "A test entity type"
        # and the field schema is correctly reconstructed
        assert len(sut.field_schema) == 2
        # first field
        assert sut.field_schema[0].name == "field1"
        assert sut.field_schema[0].lifetime == customentity.LifeTime.PERPETUAL
        assert sut.field_schema[0].type == customentity.FieldType.STRING
        assert sut.field_schema[0].collection_type == customentity.CollectionType.SINGLE
        assert sut.field_schema[0].required is True
        assert sut.field_schema[0].description == "First field"
        # second field
        assert sut.field_schema[1].name == "field2"
        assert sut.field_schema[1].lifetime == customentity.LifeTime.TIMEVARIANT
        assert sut.field_schema[1].type == customentity.FieldType.DECIMAL
        assert sut.field_schema[1].collection_type == customentity.CollectionType.ARRAY
        assert sut.field_schema[1].required is False
        assert sut.field_schema[1].description == "Second field"
