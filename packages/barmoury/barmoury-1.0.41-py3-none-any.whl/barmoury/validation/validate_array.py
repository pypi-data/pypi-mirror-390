
from peewee import Database
from ..util import field_util, util
from typing import Dict, Any, List, Callable
from ..api.exception import InvalidArgumentException, ConstraintValidationException
from .validated import prepare_validation_schema, register_validation, get_stored_validation, Validation, ControllersValidationMap


class ItemValidator:
    message: str
    validate: Callable[[Database, Any, Any], bool]


class ValidateArray(field_util.MetaObject):
    name: str = None
    message: str = None
    item_type: Any = None
    min_items: int = None
    max_items: int = None
    groups: List[str] = ["CREATE"]
    nested_array_values: bool = None
    item_validators: List[ItemValidator] = None
    item_validator: Callable[[Database, Any, Any], bool] = None


def validate_array(**args_options: Dict[str, Any]):
    options = ValidateArray(args_options)
    
    def validate_array_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @validate_array decorator can only be applied to a class")
        key = obj.__name__
        name = options.name
        groups = options.groups
        for group in groups:
            prepare_validation_schema(key, name, "array", group)
            if options.min_items != None: ControllersValidationMap[key]["body"][group]["properties"][name]["minItems"] = options.min_items
            if options.max_items != None: ControllersValidationMap[key]["body"][group]["properties"][name]["maxItems"] = options.max_items
            if callable(options.item_type):
                if field_util.is_class(options.item_type):
                    ControllersValidationMap[key]["body"][group]["properties"][name]["items"] = get_stored_validation(group, options.item_type)
                else:
                    options.item_type(obj, name)
                    items = ControllersValidationMap[key]["body"][group]["properties"][name]
                    ControllersValidationMap[key]["body"][group]["properties"][name] = { "type": "array", "items": items }
            elif hasattr(options.item_type, "__len__"):
                schemas = []
                for item_type in options.item_type:
                    if callable(item_type):
                        if field_util.is_class(options.item_type):
                            schemas.append(get_stored_validation(group, item_type))
                        else:
                            cached_schema = ControllersValidationMap[key]["body"][group]["properties"][name]
                            item_type(obj, name)
                            items = ControllersValidationMap[key]["body"][group]["properties"][name]
                            ControllersValidationMap[key]["body"][group]["properties"][name] = cached_schema
                            schemas.append(items)
                    else:
                        schemas.append({ "type": item_type })
                ControllersValidationMap[key]["body"][group]["properties"][name]["items"] = {
                    "anyOf": schemas
                }
            elif options.item_type != None:
                ControllersValidationMap[key]["body"][group]["properties"][name]["items"] = {}
                ControllersValidationMap[key]["body"][group]["properties"][name]["items"]["type"] = options.item_type
            if not options.item_validators and not options.item_validator: continue
            item_validators: List[Dict[str, Any]] = []
            message = options.message or "The entry value '{value}' did not pass validation"
            if options.item_validators != None:
                for item_validator in options.item_validators:
                    item_validators.append(item_validator)
            if options.item_validator:
                item_validators.append({ "message": message, "validate": options.item_validator })
            async def validate(db: Database, values: List[Any], opt: Dict[str, Any]) -> bool:
                for value in values:
                    for item_validator in item_validators:
                        if not item_validator: continue
                        if not (await item_validator.validate(db, value, opt)):
                            raise ConstraintValidationException(util.replace_by_regex((item_validator.message or ""), r"{value}+", value))
            register_validation(key, group, Validation(message=options.message, property_key=name, validate=validate))
            
        return obj
        
    return validate_array_impl