
from peewee import Database
from ..util import field_util
from typing import Dict, Any, List
from ..api.exception import InvalidArgumentException
from .validated import register_validation, Validation


class ColumnExists(field_util.MetaObject):
    name: str = None
    table: str = None
    column: str = None
    message: str = None
    where_clause: str = None
    resource_id_column: str = "id"
    groups: List[str] = ["CREATE"]
    

def column_exists(**args_options: Dict[str, Any]):
    options = ColumnExists(args_options)

    async def validate(db: Database, value: Any, opt: Any) -> bool:
        sql_param_values = [value]
        resource_id = opt["resource_id"] if opt["resource_id"] else ""
        resource_id = ""
        if resource_id != "": sql_param_values.append(resource_id)
        result = db.execute_sql(f"""SELECT COUNT(*) FROM {options.table} 
                                WHERE `{options.column}` = %s """ + (f""" AND {options.where_clause} """ if options.where_clause != None else """""")
                                + (f""" AND {options.resource_id_column} != %s """ if resource_id != "" else """"""), sql_param_values).fetchone()
        return result[0] > 0

    def validated_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @schema decorator can only be applied to a class")
        key = obj.__name__
        name = options.name or options.column
        for group in options.groups:
            register_validation(key, group, Validation(message=options.message, property_key=name, validate=validate))
        return obj

    return validated_impl