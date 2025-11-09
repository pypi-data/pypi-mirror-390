
import re
import traceback
from ..cache import *
from ..api import timeo
from threading import Thread
from datetime import datetime
from urllib.parse import urlencode
from traceback import StackSummary
from starlette.applications import Request as StarletteRequest
from typing import Sequence, Any, Literal, Pattern, Callable, Dict
    
def cache_write_along[T](buffer_size: int, date_last_flushed: datetime, cache: Cache[T], entry: T) -> bool:
    cache.cache(entry)
    diff = timeo.date_diff_in_minutes(date_last_flushed, datetime.now())
    return buffer_size >= cache.max_buffer_size() or diff >= cache.interval_before_flush()


def str_format(fmt: str, *args: Sequence[Any]) -> str:
    try:
        return fmt.format(*args) # TODO escape braces with value in between
    except:
        return fmt

def stack_trace(skip: int = 0) -> str:
    index = 0
    stacks = []
    traces = StackSummary.from_list(traceback.extract_stack()).format()
    traces_length = len(traces)
    for trace in traces:
        stacks.append(trace)
        if index == ((traces_length - 1) - skip):
            break
        index += 1
    return stacks


def stack_trace_as_string(skip: int = 0) -> Sequence[str]:
    result = ""
    stacks = stack_trace(skip)
    for stack in stacks:
        result += stack
    return result


def find_matches_by_regex(regex: Literal[""], value: str) -> List[str]:
    return re.compile(regex).findall(value)


def replace_by_regex(value: str, search: Literal[""], replace: str) -> str:
    return re.sub(search, replace, value)


def pattern_to_regex(pattern: str) -> Pattern:
    terminator = "" if pattern.endswith("**") else r"$"
    pattern = replace_by_regex(pattern, r"{([\w])+}", r"(\\w|[-~@#$%^&*\(\)-=+,./?<>;:'])+")
    pattern = replace_by_regex(replace_by_regex(replace_by_regex(pattern, r"\*\*", "(.)+"), r"\?", "(.)"), r"\*", "((?!(\\/)).)+") + terminator
    return re.compile(pattern)


def pattern_match_entry(entries: Dict[str, Any], search: str, separator_to_match_count: str = None) -> Dict[str, Any]:
    for key, value in entries.items():
        if pattern_to_regex(key).match(search) and (separator_to_match_count == None or key.count(separator_to_match_count) == search.count(separator_to_match_count)):
            return { "value": value, "match": key }
    return None


def extract_pattern_values(pattern: str, search: str, regex: str = r"{([\w])+}") -> Dict[str, Any]:
    result = {}
    offset = 0
    pattern_length = len(pattern)
    items = re.finditer(regex, pattern)
    for item in items:
        next_char = None
        end = item.end()-1
        template_key = pattern[item.start():item.end()]
        start = item.start() + offset
        template_length = len(template_key)
        if end < pattern_length-1:
            next_char = pattern[end+1]
        if next_char != None:
            end = search.index(next_char, start)
        else:
            if search.find("/", start) == -1:
                end = len(search)
        search_value = search[start:end]
        search_value_length = len(search_value)
        if template_length >= search_value_length:
            offset += search_value_length - template_length
        else:
            offset += search_value_length
        result[template_key[1:-1]] = search_value
    return result


def ip_address_from_request(request: StarletteRequest) -> str:
    return f"{request.client.host}{(':' + str(request.client.port)) if request.client.port else ""}"


def execute_in_thread(function: Callable[[Any], None], *args) -> str:
    thread = Thread(target = function, args = args)
    thread.start()
    

def merge_arrays(*sources: List[Any]):
    result = []
    for source in sources:
        if not source:
            continue
        result = result + source
    return result
    

def merge_objects(recurse: bool = False, *sources: Dict[str, Any]):
    result = {}
    
    if not recurse:
        for source in sources:
            if not source:
                continue
            result = { **result, **source }
    
    for source in sources:
        if not source:
            continue
        for key, value in source.items():
            if key not in result:
                result[key] = value
            elif type(result[key]) == list and type(result[key]) == type(value):
                result[key] = result[key] + value
            elif type(result[key]) == dict and type(result[key]) == type(value):
                result[key] = merge_objects(recurse, result[key], value)

    return result


def py_type_to_schema_type(tipe: Any):
    if tipe == int: return "number"
    if tipe == str: return "string"
    if tipe == list: return "array"
    if tipe == object or tipe == dict: return "object"
    return ""


def class_to_schema_properties(clazz: Any):
    properties = {}
    for key, value in clazz.__annotations__.items():
        properties[key] = {
            "type": py_type_to_schema_type(value)
        }
    return properties


def append_request_query_params(request: Any, entries: Dict[str, Any]):
    q_params = dict(request.query_params)
    delattr(request, "_query_params")
    for key, value in entries.items():
        q_params[key] = value
    request.scope['query_string'] = urlencode(q_params).encode('utf-8')
    return request