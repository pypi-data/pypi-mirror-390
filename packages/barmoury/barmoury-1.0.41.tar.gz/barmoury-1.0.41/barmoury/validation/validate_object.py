
from peewee import Database
from typing import Dict, Any, List, Callable
from ..util import field_util, json_mapper, util
from ..api.exception import InvalidArgumentException, ConstraintValidationException
from .validated import prepare_validation_schema, get_stored_validation, register_validation, Validation, ControllersValidationMap


class ItemValidator:
    message: str
    validate: Callable[[Database, Any, Any], bool]


class ValidateObject(field_util.MetaObject):
    name: str = None
    message: str = None
    value: Callable = None
    required: List[str] = None
    min_properties: int = None
    max_properties: int = None
    groups: List[str] = ["CREATE"]
    additional_properties: bool = None
    property_names: Dict[str, Any] = None
    dependent_schemas: Dict[str, Any] = None
    pattern_properties: Dict[str, Any] = None
    properties: Callable | Dict[str, Any] = None
    dependent_required: Dict[str, List[str]] = None
    property_validators: List[ItemValidator] = None
    property_validator: Callable[[Database, Any, Any], bool] = None


def validate_object(**args_options: Dict[str, Any]):
    options = ValidateObject(args_options)
    
    def validate_object_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @validate_object decorator can only be applied to a class")
        key = obj.__name__
        name = options.name
        value = options.value
        groups = options.groups
        for group in groups:
            prepare_validation_schema(key, name, "object", group)
            if options.min_properties != None: ControllersValidationMap[key]["body"][group]["properties"][name]["minProperties"] = options.min_properties
            if options.max_properties != None: ControllersValidationMap[key]["body"][group]["properties"][name]["maxProperties"] = options.max_properties
            if options.property_names != None: ControllersValidationMap[key]["body"][group]["properties"][name]["propertyNames"] = options.property_names
            if options.pattern_properties != None: ControllersValidationMap[key]["body"][group]["properties"][name]["patternProperties"] = options.pattern_properties
            if options.additional_properties != None: ControllersValidationMap[key]["body"][group]["properties"][name]["additionalProperties"] = options.additional_properties
            if callable(options.properties):
                if field_util.is_class(options.properties):
                    ControllersValidationMap[key]["body"][group]["properties"][name]["properties"] = json_mapper.class_to_schema_properties(options.properties)
                else:
                    raise InvalidArgumentException("The @validate_object properties value must be a class or dict")
            elif type(options.properties) == dict:
                ControllersValidationMap[key]["body"][group]["properties"][name]["properties"] = options.properties
            if options.dependent_schemas != None:
                ControllersValidationMap[key]["body"][group]["properties"][name]["dependentSchemas"] = {}
                for schema_key, schema_value in options.dependent_schemas.items():
                    if callable(schema_value):
                        if field_util.is_class(schema_value):
                            ControllersValidationMap[key]["body"][group]["properties"][name]["dependentSchemas"][schema_key] = get_stored_validation(group, schema_value)
                        else:
                            schema_value(obj, name)
                            properties = ControllersValidationMap[key]["body"][group]["properties"][name]
                            ControllersValidationMap[key]["body"][group]["properties"][name]["dependentSchemas"][schema_key] = { "type": "object", "properties": properties }
            if options.required != None:
                old_required = []
                if "required" in ControllersValidationMap[key]["body"][group]["properties"][name]:
                    old_required = ControllersValidationMap[key]["body"][group]["properties"][name]["required"]
                ControllersValidationMap[key]["body"][group]["properties"][name]["required"] = util.merge_arrays(old_required, options.required)       
            if not (not options.property_validators and not options.property_validator):
                property_validators: List[Dict[str, Any]] = []
                message = options.message or "The entry value '{value}' did not pass validation"
                if options.property_validators != None:
                    for property_validator in options.property_validators:
                        property_validators.append(property_validator)
                if options.property_validator:
                    property_validators.append({ "message": message, "validate": options.property_validator })
                async def validate(db: Database, values: List[Any], opt: Dict[str, Any]) -> bool:
                    for value in values:
                        for property_validator in property_validators:
                            if not property_validator: continue
                            if not (await property_validator.validate(db, value, opt)):
                                raise ConstraintValidationException(util.replace_by_regex((property_validator.message or ""), r"{value}+", value))
                register_validation(key, group, Validation(message=options.message, property_key=name, validate=validate))
            if value:
                ControllersValidationMap[key]["body"][group]["properties"][name] = util.merge_objects(True,
                                                                                                      get_stored_validation(group, value),
                                                                                                      ControllersValidationMap[key]["body"][group]["properties"][name])

        return obj
        
    return validate_object_impl