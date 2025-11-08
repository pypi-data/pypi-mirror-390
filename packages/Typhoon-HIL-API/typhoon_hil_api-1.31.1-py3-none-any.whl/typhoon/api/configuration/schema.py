from typing import TypedDict, Literal, Any


class JSONSchemaSnippet(TypedDict):
    label: str
    description: str
    body: Any  # an object that will be JSON serialized
    bodyText: str  # an already serialized JSON object that can contain new lines (\n) and tabs (\t)


JSONSchemaType = Literal[
    "string", "number", "integer", "boolean", "null", "array", "object"
]

JSONSchemaValue = str | float | int | bool | dict | list | None

JSONSchemaMap = dict[str, "JSONSchema"]

# https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-01
JSONSchema = TypedDict(
    "JSONSchema",
    {
        "id": str,
        "$id": str,
        "$schema": str,
        "type": JSONSchemaType | list[JSONSchemaType],
        "title": str,
        "default": Any,
        "definitions": JSONSchemaMap,
        "description": str,
        "properties": JSONSchemaMap,
        "patternProperties": JSONSchemaMap,
        "additionalProperties": "bool | JSONSchema",
        "minProperties": int,
        "maxProperties": int,
        "dependencies": "dict[str, JSONSchema] | dict[str, list[str]]",
        "items": "JSONSchema | list[JSONSchema]",
        "minItems": int,
        "maxItems": int,
        "uniqueItems": bool,
        "additionalItems": "bool | JSONSchema",
        "pattern": str,
        "minLength": int,
        "maxLength": int,
        "minimum": float,
        "maximum": float,
        "exclusiveMinimum": bool | float,
        "exclusiveMaximum": bool | float,
        "multipleOf": float,
        "required": list[str],
        "$ref": str,
        "anyOf": list["JSONSchema"],
        "allOf": list["JSONSchema"],
        "oneOf": list["JSONSchema"],
        "not": "JSONSchema",
        "enum": list,
        "format": str,
        # schema draft 06
        "const": Any,
        "contains": "JSONSchema",
        "propertyNames": "JSONSchema",
        "examples": list,
        # schema draft 07
        "$comment": str,
        "if": "JSONSchema",
        "then": "JSONSchema",
        "else": "JSONSchema",
        # schema 2019-09
        "unevaluatedProperties": "bool | JSONSchema",
        "unevaluatedItems": "bool | JSONSchema",
        "minContains": int,
        "maxContains": int,
        "deprecated": bool,
        "dependentRequired": dict[str, list[str]],
        "dependentSchemas": JSONSchemaMap,
        "$defs": JSONSchemaMap,
        "$anchor": str,
        "$recursiveRef": str,
        "$recursiveAnchor": str,
        "$vocabulary": Any,
        # schema 2020-12
        "prefixItems": list["JSONSchema"],
        "$dynamicRef": str,
        "$dynamicAnchor": str,
        # extensions
        "defaultSnippets": list[JSONSchemaSnippet],
        "errorMessage": str,
        "patternErrorMessage": str,
        "deprecationMessage": str,
        "markdownDeprecationMessage": str,
        "enumDescriptions": list[str],
        "markdownEnumDescriptions": list[str],
        "markdownDescription": str,
        "doNotSuggest": bool,
        "suggestSortText": str,
        "allowComments": bool,
        "allowTrailingCommas": bool,
    },
    total=False,
)
