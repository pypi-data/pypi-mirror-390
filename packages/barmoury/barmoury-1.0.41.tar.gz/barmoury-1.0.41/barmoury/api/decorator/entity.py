

from peewee import Database
from ...util import field_util
from typing import Dict, Any, Callable, List
from ..exception import InvalidArgumentException


class Entity(field_util.MetaObject):
    schema: str = None
    options: Dict = None
    depends_on: Any = None
    table_name: str = None
    temporary: bool = None
    primary_key: Any = None
    indexes: List[Any] = None
    database: Database = None
    without_rowid: bool = None
    strict_tables: bool = None
    only_save_dirty: bool = None
    constraints: List[Any] = None
    legacy_table_names: bool = None
    table_function: Callable = None
    table_settings: List[Any] = None


def entity(**args_options: Dict[str, Any]):
    options = Entity(args_options)
    
    def entity_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The entity decorator is only applicable to a class")
        if options.schema != None: obj._meta.schema = options.schema
        if options.options != None: obj._meta.options = options.options
        if options.indexes != None: obj._meta.indexes = options.indexes
        if options.database != None: obj._meta.database = options.database
        if options.temporary != None: obj._meta.temporary = options.temporary
        if options.depends_on != None: obj._meta.depends_on = options.depends_on
        if options.table_name != None: obj._meta.table_name = options.table_name
        if options.primary_key != None: obj._meta.primary_key = options.primary_key
        if options.constraints != None: obj._meta.constraints = options.constraints
        if options.without_rowid != None: obj._meta.without_rowid = options.without_rowid
        if options.strict_tables != None: obj._meta.strict_tables = options.strict_tables
        if options.table_settings != None: obj._meta.table_settings = options.table_settings
        if options.table_function != None: obj._meta.table_function = options.table_function
        if options.only_save_dirty != None: obj._meta.only_save_dirty = options.only_save_dirty
        if options.legacy_table_names != None: obj._meta.legacy_table_names = options.legacy_table_names
        return obj
    return entity_impl
