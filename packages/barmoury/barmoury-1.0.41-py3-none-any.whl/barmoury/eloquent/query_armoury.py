

from ..copier import *
from ..util import field_util, util
from typing import Any, Self, List, Set
from peewee import Database, JOIN, Value
from starlette.datastructures import QueryParams
from starlette.applications import Request as StarletteRequest
from ..api.exception import EntityNotFoundException, InvalidArgumentException
from .request_param_filter import FieldsRequestParamFilterMap, RequestParamFilter, RequestParamFilter, find_request_param_filter


class QueryArmoury:
    _db: Database = None
    PERCENTAGE_CHANGE_RELAY_KEY: str = "___percentage_change____"
    BARMOURY_RAW_SQL_PARAMETER_KEY: str = "___BARMOURY__RAW__SQL___"

    def __init__(self: Self, db: Database = None):
        self._db = db

    async def page_query[T](self: Self, request: StarletteRequest, model: T, resolve_sub_entities: bool = True, pageable: bool = False, logger: Any = None) -> Any:
        count = 0
        result = []
        request_fields = self.resolve_query_fields(model, request.query_params)
        model_select = self.build_where_filter(model, model.select(), request_fields)
        page_filter = self.build_page_filter(model, model_select, request.query_params)
        if pageable:
            count = model_select.count()
        rows = page_filter["model_select"].dicts()
        page_filter["count"] = count
        for row in rows:
            model_resource = model()
            Copier.copy(model_resource, row, copy_property=CopyProperty({ "enable_dictionary_lookup": True }))
            result.append(model_resource)
        return self.paginate_result(result, page_filter) if pageable else result
    
    def build_page_filter(self: Self, model: Any, model_select: Any, query: QueryParams):
        order_bys = []
        sorted = False
        paged = "page" in query
        limit = query.get("size")
        page = int(query.get("page") or "1")
        sorts = query.getlist("sort") if "sort" in query else []
        offset = (page - 1) * (int(limit or "10"))
        
        if limit != None:
            model_select = model_select.limit(int(limit))
        if len(sorts) > 0:
            sorted = True
        for sort in sorts:
            sort_parts = sort.split(",")
            field_name = sort_parts[0]
            if field_name not in model.__dict__:
                raise InvalidArgumentException(f"Unknown field '{field_name}' in sort parameter")
            if len(sort_parts) > 1 and sort_parts[1].lower() == "desc":
                order_bys.append(-getattr(model, field_name))
            else:
                order_bys.append(getattr(model, field_name))
        return {
            "page": page,
            "paged": paged,
            "offset": offset,
            "sorted": sorted,
            "limit": int(limit) if limit != None else 10,
            "model_select": model_select.offset(offset).order_by(*order_bys),
        }

    def resolve_query_fields(self: Self, model: Any, query: QueryParams, resolve_stat_query_annotations: bool = False):
        request_fields = {}
        key = model.__name__
        fields = FieldsRequestParamFilterMap[key] if key in FieldsRequestParamFilterMap else {}
        for main_field_name, request_param_filters in fields.items():
            column_name = field_util.get_field_column_name(main_field_name, False)
            request_param_filters_count = len(request_param_filters)
            for request_param_filter in request_param_filters:
                if request_param_filter.column: column_name = request_param_filter.column
                if request_param_filter.column_is_camel_case: column_name = field_util.to_camel_case(column_name)
                
                field_name = main_field_name
                if request_param_filters_count > 1:
                    operator = request_param_filter.operator.value.lower()
                    field_name = f"{main_field_name}{'_' if request_param_filter.multi_filter_separator == '__' and (request_param_filter.accept_camel_case) else request_param_filter.multi_filter_separator}"
                    field_name += f"{operator[0]}{operator[1:]}"
                extra_field_names = []
                extra_field_names.append(field_name)
                if not resolve_stat_query_annotations:
                    extra_field_names = set(util.merge_arrays(extra_field_names, request_param_filter.aliases))
                    if request_param_filter.accept_camel_case:
                        for extra_field_name in extra_field_names:
                            extra_field_names.add(field_util.to_camel_case(extra_field_name))
                    if request_param_filter.operator == RequestParamFilter.Operator.RANGE:
                        pass
                self.resolve_query_for_single_field(model, request_fields, request_param_filter, resolve_stat_query_annotations,
                    query, extra_field_names, column_name, { "name": main_field_name, "key": key })
            # for stat query
            if resolve_stat_query_annotations:
                pass
        return request_fields

    def resolve_query_for_single_field(self: Self, model: Any, request_fields: Dict[str, Any],
                                       request_param_filter: RequestParamFilter, resolve_stat_query_annotations: bool,
                                       query: QueryParams, query_params: Set[str], column_name: str, field: Dict[str, str]):
        for query_param in query_params:
            values = []
            is_present = False
            object_filter = not resolve_stat_query_annotations and request_param_filter.operator.value.startswith("OBJECT")
            is_entity = not resolve_stat_query_annotations and request_param_filter.operator == RequestParamFilter.Operator.ENTITY
            
            if not resolve_stat_query_annotations:
                for key, e_values in query.items():
                    if key == query_param or ((object_filter or is_entity) and key.startswith(f"{query_param}.")):
                        any_value_present = False
                        if type(e_values) == str:
                            e_values = [e_values]
                        for value in e_values:
                            if not value or value == "":
                                continue
                            if request_param_filter.boolean_to_int:
                                value = "1" if value == "true" else "0"
                            values.append(value)
                            is_present = True
                            if not any_value_present:
                                any_value_present = True
                            if not any_value_present:
                                continue
                        query_param = field_util.to_camel_case(key) if object_filter and request_param_filter.column_object_fields_is_camel_case else key
                        break
                if not resolve_stat_query_annotations and not is_present and not request_param_filter.always_query:
                    continue
                if query_param in request_fields:
                    continue
            if resolve_stat_query_annotations:
                query_param = field.name
            rf_value = [
                field_util.get_class_attribute_value(model, column_name),
                is_present,
                request_param_filter,
                values,
            ]
            if resolve_stat_query_annotations:
                pass
            request_fields[query_param] = rf_value

    def build_where_filter(self: Self, model: Any, model_select: Any, request_fields: Dict[str, Any]):
        for matching_field_name, values in request_fields.items():
            column = values[0]
            request_param_filter: RequestParamFilter = values[2]
            model_select = self.get_relation_query_part(model, model_select, column, 
                                                        request_param_filter.multi_filter_separator, False, matching_field_name, request_param_filter.operator, values[3])
        #print("THE QUERY", model_select.sql())
        return model_select
    
    def get_relation_query_part(self: Self, model: Any, model_select: Any, column: Any, sep: str, 
                                is_entity_field: bool, matching_field_name: str, operator: RequestParamFilter.Operator, values: List[str]):
        matching_field_name_parts = matching_field_name.split(".")
        object_field = matching_field_name_parts[1] if len(matching_field_name_parts) > 1 else matching_field_name_parts[0]
        if operator == RequestParamFilter.Operator.EQ:
            model_select = model_select.where(column == values[0])
        elif operator == RequestParamFilter.Operator.GT:
            model_select = model_select.where(column > values[0])
        elif operator == RequestParamFilter.Operator.LT:
            model_select = model_select.where(column < values[0])
        elif operator == RequestParamFilter.Operator.NE:
            model_select = model_select.where(column != values[0])
        elif operator == RequestParamFilter.Operator.IN:
            model_select = model_select.where(column.in_(values))
        elif operator == RequestParamFilter.Operator.GT_EQ:
            model_select = model_select.where(column >= values[0])
        elif operator == RequestParamFilter.Operator.LT_EQ:
            model_select = model_select.where(column <= values[0])
        elif operator == RequestParamFilter.Operator.LIKE or operator == RequestParamFilter.Operator.CONTAINS:
            model_select = model_select.where(column.contains(values[0]))
        elif operator == RequestParamFilter.Operator.ILIKE:
            model_select = model_select.where(column.regexp(values[0]))
        elif operator == RequestParamFilter.Operator.NOT_LIKE or operator == RequestParamFilter.Operator.NOT_CONTAINS:
            model_select = model_select.where(~column.contains(values[0]))
        elif operator == RequestParamFilter.Operator.NOT_ILIKE:
            model_select = model_select.where(~column.regexp(values[0]))
        elif operator == RequestParamFilter.Operator.ENDS_WITH:
            model_select = model_select.where(column.endswith(values[0]))
        elif operator == RequestParamFilter.Operator.STARTS_WITH:
            model_select = model_select.where(column.startswith(values[0]))
        elif operator == RequestParamFilter.Operator.NOT_IN:
            model_select = model_select.where(~column.in_(values[0]))
        elif operator == RequestParamFilter.Operator.BETWEEN:
            model_select = model_select.where(column.between(*values))
        elif operator == RequestParamFilter.Operator.NOT_BETWEEN:
            model_select = model_select.where(~column.between(*values))
        elif operator == RequestParamFilter.Operator.OBJECT_EQ:
            model_select = model_select.where(column.contains(Value(f'"{object_field}": {values[0]}')) | column.endswith(Value(f'"{object_field}": {values[0]}}}')))
        elif operator == RequestParamFilter.Operator.OBJECT_NE:
            model_select = model_select.where(~column.contains(Value(f'"{object_field}": {values[0]}')) & ~column.endswith(Value(f'"{object_field}": {values[0]}}}')))
        elif operator == RequestParamFilter.Operator.OBJECT_STR_EQ:
            model_select = model_select.where(column.contains(Value(f'"{object_field}": "{values[0]}"')) | column.endswith(Value(f'"{object_field}": "{values[0]}"}}')))
        elif operator == RequestParamFilter.Operator.OBJECT_STR_NE:
            model_select = model_select.where(~column.contains(Value(f'"{object_field}": "{values[0]}"')) & ~column.endswith(Value(f'"{object_field}": "{values[0]}"}}')))
        elif operator == RequestParamFilter.Operator.OBJECT_LIKE or operator == RequestParamFilter.Operator.OBJECT_CONTAINS:
            model_select = model_select.where(column.contains(Value(f'"{object_field}":%{values[0]}%,')) | column.endswith(Value(f'"{object_field}":%{values[0]}%}}')))
        elif operator == RequestParamFilter.Operator.OBJECT_NOT_LIKE or operator == RequestParamFilter.Operator.OBJECT_NOT_CONTAINS:
            model_select = model_select.where(~column.contains(Value(f'"{object_field}":%{values[0]}%,')) & ~column.endswith(Value(f'"{object_field}":%{values[0]}%}}')))
        elif operator == RequestParamFilter.Operator.OBJECT_ENDS_WITH:
            model_select = model_select.where(column.contains(Value(f'"{object_field}":%{values[0]},')) | column.endswith(Value(f'"{object_field}":%{values[0]}}}')))
        elif operator == RequestParamFilter.Operator.OBJECT_STARTS_WITH:
            model_select = model_select.where(column.contains(Value(f'"{object_field}": {values[0]}%,')) | column.endswith(Value(f'"{object_field}": {values[0]}%}}')))
        elif operator == RequestParamFilter.Operator.OBJECT_STR_ENDS_WITH:
            model_select = model_select.where(column.contains(Value(f'"{object_field}": "%{values[0]}",')) | column.endswith(Value(f'"{object_field}": "%{values[0]}"}}')))
        elif operator == RequestParamFilter.Operator.OBJECT_STR_STARTS_WITH:
            model_select = model_select.where(column.contains(Value(f'"{object_field}": "{values[0]}%",')) | column.endswith(Value(f'"{object_field}": "{values[0]}%"}}')))
        elif operator == RequestParamFilter.Operator.ENTITY:
            og_column = column
            name_op_parts = matching_field_name_parts[1].split(sep)
            request_param_filters = find_request_param_filter(column.rel_model, name_op_parts[0])
            column = field_util.get_class_attribute_value(column, name_op_parts[0])
            op = name_op_parts[1] if len(name_op_parts) > 1 else None
            for request_param_filter in request_param_filters:
                if op == None or request_param_filter.operator.value == op:
                    model_select = model_select.join(og_column.rel_model, JOIN.LEFT_OUTER)
                    model_select = self.get_relation_query_part(model, model_select, column, sep, is_entity_field, request_param_filter.name, request_param_filter.operator, values)
                    model_select = model_select.switch(model)
                    break
        return model_select

    def paginate_result(self: Self, rows: List[Any], page_filter: Dict[str, Any]):
        rows_count = len(rows)
        sort = {
            "empty": rows_count == 0,
            "sorted": page_filter["sorted"],
            "unsorted": not page_filter["sorted"],
        }
        return {
            "content": rows,
            "pageable": {
                "sort": sort,
                "offset": page_filter["offset"],
                "page_number": page_filter["page"],
                "page_size": page_filter["limit"],
                "paged": page_filter["paged"],
                "unpaged": not page_filter["paged"],
            },
            "last": page_filter["offset"] >= (page_filter["count"] - page_filter["limit"]),
            "total_pages": int((page_filter["count"] / page_filter["limit"]) + 1),
            "total_elements":     page_filter["count"],
            "first":              page_filter["offset"] == 0,
            "size":               page_filter["limit"],
            "number":             page_filter["page"],
            "sort":               sort,
            "number_of_elements": rows_count,
            "empty":              rows_count == 0,
            
        }
    
    async def get_resource_by_column[T](self: Self, model: T, column: Any, value: Any, message: str) -> T:
        query = {}
        query[column] = value
        resource = model.select().where(column==value).limit(1).dicts()
        if resource != None and len(resource) > 0:
            model_resource = model()
            Copier.copy(model_resource, resource[0], copy_property=CopyProperty({ "enable_dictionary_lookup": True }))
            return model_resource
        raise EntityNotFoundException(message)
    
    async def get_resource_by_id[T](self: Self, model: T, value: Any, message: str) -> T:
        return await self.get_resource_by_column(model, model.id, value, message)