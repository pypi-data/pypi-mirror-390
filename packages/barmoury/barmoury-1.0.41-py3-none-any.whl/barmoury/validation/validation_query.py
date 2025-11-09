
import re
from peewee import Database
from typing import Dict, Any, List
from ..util import field_util, util
from ..api.exception import InvalidArgumentException
from .validated import register_validation, Validation


class Valid(field_util.MetaObject):
    table: str = None
    message: str = None
    check_is_zero: bool = None
    or_clauses: List[str] = None
    and_clauses: List[str] = None
    groups: List[str] = ["CREATE"]


def validation_query(**args_options: Dict[str, Any]):
    options = Valid(args_options)
    
    async def validate(db: Database, value: Any, opt: Any) -> bool:
        if opt["resource_id"]: return True
        query_params = []
        or_clauses = options.or_clauses
        and_clauses = options.and_clauses
        check_is_zero = options.check_is_zero
        has_or_clauses = or_clauses != None and len(or_clauses) > 0
        query_string = "SELECT count(*) FROM `" + options.table + "`"
        has_and_clauses = and_clauses != None and len(and_clauses) > 0
        if has_or_clauses or has_and_clauses:
            query_string += " WHERE ("
        if has_or_clauses:
            index = 0
            for clause in or_clauses:
                query_string += clause
                params = [p[1:] for p in util.find_matches_by_regex(r'\:\w+', clause)]
                for param in params:
                    query_params.append(value if param == "SELF" else field_util.get_value(value, param))
                if index < (len(or_clauses) - 1):
                    query_string += " OR "
                index += 1
        if has_or_clauses and has_and_clauses:
            query_string += ") AND ("
        if has_and_clauses:
            index = 0
            for clause in and_clauses:
                query_string += clause
                params = [p[1:] for p in util.find_matches_by_regex(r'\:\w+', clause)]
                for param in params:
                    query_params.append(value if param == "SELF" else field_util.get_value(value, param))
                if index < (len(and_clauses) - 1):
                    query_string += " AND "
                index += 1
        query_string += " )"
        query_string = util.replace_by_regex(query_string, r'\:\w+', "%s")
        result = db.execute_sql(query_string, query_params).fetchone()
        count = result[0]
        print("THE QUERY AFTER", query_string, query_params, count)
        return (check_is_zero == (count == 0))

    def validation_query_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @validation_query decorator can only be applied to a class")
        key = obj.__name__
        groups = options.groups
        for group in groups:
            register_validation(key, group, Validation(message=options.message, property_key="__class__", validate=validate))
        return obj

    return validation_query_impl