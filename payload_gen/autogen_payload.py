from typing import List, Union, Sequence, Iterable, Optional, Dict, Any, _GenericAlias, _TypedDictMeta, get_type_hints,  _AnnotatedAlias
from typing_extensions import Literal, Annotated, TypeAlias, Required, TypedDict
from collections import abc
from tqdm.auto import tqdm
import os

from pydantic._internal._model_construction import ModelMetaclass
from openai._models import BaseModel
from openai._utils._transform import PropertyInfo
import openai

from openai_request import create_response, create_response_output

SAVE_PAYLOAD_DIR = "save-payloads/responses/create"
SAVE_RESPONSE_DIR = "save-payloads/responses/result"

INT_VAL = 16
FLOAT_VAL = 1.0
STR_VAL = "string"

ID_PREFIX_MAP = {
    openai.types.responses.response_input_item_param.FunctionCallOutput: 'fc',
    openai.types.responses.response_input_item.FunctionCallOutput: 'fc',
    openai.types.responses.response_input_param.FunctionCallOutput: 'fc',
    openai.types.responses.response_function_tool_call_output_item.ResponseFunctionToolCallOutputItem: 'fc',
    openai.types.responses.response_input_item_param.McpApprovalResponse: 'mcpa',
    openai.types.responses.response_input_item.McpApprovalResponse: 'mcpa',
    openai.types.responses.response_input_param.McpApprovalResponse: 'mcpa',
    openai.types.responses.response_item.McpApprovalResponse: 'mcpa',
    openai.types.responses.response_custom_tool_call_output_param.ResponseCustomToolCallOutputParam: 'ctco',
    openai.types.responses.response_custom_tool_call_output.ResponseCustomToolCallOutput: 'ctco',
    openai.types.responses.response_conversation_param.ResponseConversationParam: 'conv',
    openai.types.responses.response.Conversation: 'conv',
    openai.types.responses.response_prompt_param.ResponsePromptParam: 'pmpt',
    openai.types.responses.response_prompt.ResponsePrompt: 'pmpt',
    openai.types.responses.response_computer_tool_call_output_item.ResponseComputerToolCallOutputItem: 'cuo',
    openai.types.responses.response_input_item_param.ComputerCallOutput: 'cuo',
    openai.types.responses.response_input_item.ComputerCallOutput: 'cuo',
    openai.types.responses.response_input_param.ComputerCallOutput: 'cuo',
}

TYPELESS_ID_PREFIXES = {
    openai.types.responses.response_conversation_param.ResponseConversationParam: 'conv',
    openai.types.responses.response.Conversation: 'conv',
    openai.types.responses.response_prompt_param.ResponsePromptParam: 'pmpt',
    openai.types.responses.response_prompt.ResponsePrompt: 'pmpt',
}


def is_td(cls):
    return type(cls).__name__ == '_TypedDictMeta'

def get_openai_id(prefix: str) -> str:
    return f"{prefix}_abc123"


def schema_generator():
    # used for input schema definitions
    return {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to perform.", # describes the paramteres to OpenAI
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    }


def list_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool, key_in_data: str = "", data_cls: str = "") -> "List[Any]":
    if not len(args) == 1:
        import pdb; pdb.set_trace()
    stride, output = generate(args[0], seed, stride_dict, build)

    # if building stride_dict, update
    if build:
        stride_dict[type_name] = stride

    return [output]


def dict_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool, key_in_data: str = "", data_cls: str = "") -> "Dict[Any, Any]":
    if not len(args) == 2:
        import pdb; pdb.set_trace()

    if args[1] == object:
        # use Dict[str, object] (== object) for input schema definitions
        stride_dict[type_name] = 1
        return schema_generator()

    key_stride, key_out = generate(args[0], seed, stride_dict, build)
    val_stride, val_out = generate(args[1], seed, stride_dict, build)

    # if building stride_dict, update
    if build:
        stride_dict[type_name] = max(key_stride, val_stride)

    return {key_out: val_out}


def _union_generator_build(type_name: str, args: type, seed: int, stride_dict: Optional[dict[str, int]], key_in_data: str = "", data_cls: str = "") -> "Any":
    cum_stride = 0
    outputs = []
    # do_break = type_name == 'typing.Union[openai.types.responses.easy_input_message_param.EasyInputMessageParam, openai.types.responses.response_input_param.Message, openai.types.responses.response_output_message_param.ResponseOutputMessageParam, openai.types.responses.response_file_search_tool_call_param.ResponseFileSearchToolCallParam, openai.types.responses.response_computer_tool_call_param.ResponseComputerToolCallParam, openai.types.responses.response_input_param.ComputerCallOutput, openai.types.responses.response_function_web_search_param.ResponseFunctionWebSearchParam, openai.types.responses.response_function_tool_call_param.ResponseFunctionToolCallParam, openai.types.responses.response_input_param.FunctionCallOutput, openai.types.responses.response_reasoning_item_param.ResponseReasoningItemParam, openai.types.responses.response_input_param.ImageGenerationCall, openai.types.responses.response_code_interpreter_tool_call_param.ResponseCodeInterpreterToolCallParam, openai.types.responses.response_input_param.LocalShellCall, openai.types.responses.response_input_param.LocalShellCallOutput, openai.types.responses.response_input_param.McpListTools, openai.types.responses.response_input_param.McpApprovalRequest, openai.types.responses.response_input_param.McpApprovalResponse, openai.types.responses.response_input_param.McpCall, openai.types.responses.response_custom_tool_call_output_param.ResponseCustomToolCallOutputParam, openai.types.responses.response_custom_tool_call_param.ResponseCustomToolCallParam, openai.types.responses.response_input_param.ItemReference]'
    # if do_break:
    #     import pdb; pdb.set_trace()

    for i in range(len(args)):
        # from openai.types.responses.easy_input_message_param import EasyInputMessageParam
        # if args[i] == EasyInputMessageParam:
        #     import pdb; pdb.set_trace()
        stride, output = generate(args[i], seed - cum_stride, stride_dict, True, key_in_data, data_cls)
        cum_stride += stride
        outputs.append((cum_stride, output))
    
    for cum_stride, output in outputs:
        if seed < cum_stride:
            break
    # if do_break:
    #     import pdb; pdb.set_trace()
    stride_dict[type_name] = outputs[-1][0] # total cumulative stride
    return output


def _union_generator_nobuild(args: type, seed: int, stride_dict: Optional[dict[str, int]], key_in_data: str = "", data_cls: str = "") -> "Any":
    cum_stride = 0
    for i in range(len(args)):
        type_name = repr(args[i])
        if type_name not in stride_dict:
            import pdb; pdb.set_trace()
        stride = stride_dict[type_name]
        if seed < cum_stride + stride:
            break
        cum_stride += stride
    _, output = generate(args[i], seed - cum_stride, stride_dict, False, key_in_data, data_cls)
    return output


def union_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool, key_in_data: str = "", data_cls: str = "") -> "Any":
    if build:
        return _union_generator_build(type_name, args, seed, stride_dict, key_in_data, data_cls)
    else:
        return _union_generator_nobuild(args, seed, stride_dict, key_in_data, data_cls)


def annotated_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool, key_in_data: str = "", data_cls: str = "") -> "Any":
    if not len(args) == 1:
        import pdb; pdb.set_trace()
    stride, output = generate(args[0], seed, stride_dict, build, key_in_data, data_cls)

    # if building stride_dict, update
    if build:
        stride_dict[type_name] = stride

    # dont need to use metadata
    return output


def literal_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool, key_in_data: str = "", data_cls: str = "") -> "Any":
    output = args[seed % len(args)]
    
    if build:
        stride_dict[type_name] = len(args)

    # if output == "output_text":
    #     import pdb; pdb.set_trace()

    return output


def required_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool, key_in_data: str = "", data_cls: str = "") -> "Any":
    if not len(args) == 1:
        import pdb; pdb.set_trace()
    stride, output = generate(args[0], seed, stride_dict, build, key_in_data, data_cls)

    # if building stride_dict, update
    if build:
        stride_dict[type_name] = stride

    return output


generator_map = {
    list: list_generator,
    dict: dict_generator,
    abc.Sequence: list_generator,
    abc.Iterable: list_generator,
    Union: union_generator,
    Optional: union_generator,
    Literal: literal_generator,
    # Annotated: annotated_generator,  # __origin__ different
    # TypeAlias: None,
    Required: required_generator,
}

# annotation_map = {
#     PropertyInfo: None,
# }


def generate_basemodel(cls: ModelMetaclass, seed: int, stride_dict: Optional[dict[str, int]], build: bool) -> str:
    max_stride = 0
    cls_kwargs = {}
    type_dict = cls.__pydantic_fields__
    has_type = "type" in type_dict or cls in TYPELESS_ID_PREFIXES
    for key, field_info in type_dict.items():
        key = field_info.alias or key
        if not hasattr(field_info, "annotation"):
            import pdb; pdb.set_trace()
        typ = field_info.annotation
        stride, output = generate(typ, seed, stride_dict, build, key, cls if has_type else "")
        cls_kwargs[key] = output

        if build:
            max_stride = max(max_stride, stride)

    stride_dict[repr(cls)] = max_stride
    return cls(**cls_kwargs)


def generate_typeddict(cls: _TypedDictMeta, seed: int, stride_dict: Optional[dict[str, int]], build: bool) -> str:
    max_stride = 0
    cls_kwargs = {}
    type_dict = get_type_hints(cls)
    has_type = "type" in type_dict or cls in TYPELESS_ID_PREFIXES
    for key, typ in type_dict.items():
        stride, output = generate(typ, seed, stride_dict, build, key, cls if has_type else "")
        cls_kwargs[key] = output

        if build:
            max_stride = max(max_stride, stride)

    stride_dict[repr(cls)] = max_stride
    return cls(**cls_kwargs)


def generate(typ: type, seed: int, stride_dict: Optional[dict[str, int]], build: bool, key_in_data: str = "", data_cls: str = "") -> "tuple[int, Any]":
    # if key_in_data == "input":
    #     import pdb; pdb.set_trace()
    # from openai.types.responses.response_input_param import ResponseInputItemParam

    # if typ == ResponseInputItemParam:
    #     import pdb; pdb.set_trace()
    type_name = repr(typ)
    if isinstance(typ, _AnnotatedAlias):
        if not hasattr(typ, "__args__"):
            import pdb; pdb.set_trace()
        if not len(typ.__args__) == 1:
            import pdb; pdb.set_trace()
        if not hasattr(typ, "__metadata__"):
            import pdb; pdb.set_trace()
        stride, output = generate(typ.__args__[0], seed, stride_dict, build, key_in_data, data_cls)
    elif isinstance(typ, _GenericAlias):
        if not (hasattr(typ, "__origin__") and typ.__origin__ in generator_map):
            import pdb; pdb.set_trace()
        if not hasattr(typ, "__args__"):
            import pdb; pdb.set_trace()
        output = generator_map[typ.__origin__](type_name, typ.__args__, (), seed, stride_dict, build, key_in_data, data_cls)
        if type_name not in stride_dict:
            import pdb; pdb.set_trace()
        stride = stride_dict[type_name]
    elif is_td(typ):
        output = generate_typeddict(typ, seed, stride_dict, build)
        if type_name not in stride_dict:
            import pdb; pdb.set_trace()
        stride = stride_dict[type_name]
    elif issubclass(typ, BaseModel):
        output = generate_basemodel(typ, seed, stride_dict, build)
        if type_name not in stride_dict:
            import pdb; pdb.set_trace()
        stride = stride_dict[type_name]
    # handle basic python types
    elif typ == str:
        if key_in_data == "id":
            # need to use openai id format
            if data_cls:
                id_prefix = ID_PREFIX_MAP.get(data_cls, "")
                if not id_prefix:
                    print(f"MISSING ID prefix for type `{data_cls}` -- update ID_PREFIX_MAP once the call to OpenAI fails")
            else:
                id_prefix = ""
            output = get_openai_id(id_prefix)
        else:
            output = STR_VAL
        stride = 1
    elif typ == int:
        output = INT_VAL
        stride = 1
    elif typ == float:
        output = FLOAT_VAL
        stride = 1
    elif typ == bool:
        output = seed % 2 == 0
        stride = 2
    elif typ is type(None):
        output = None
        stride = 1
    elif typ is object:
        # used for input schema definitions
        output = schema_generator()
        stride = 1
    else:
        import pdb; pdb.set_trace()

    if isinstance(output, tuple) and len(output) == 2:
        import pdb; pdb.set_trace()

    return stride, output


def gen_response_create_params(seed: Optional[int]):
    from openai.types.responses.response_create_params import ResponseCreateParams
    if seed is None:
        num_tests, response_create_params = generate(ResponseCreateParams, 0, {}, True)
        for i in tqdm(range(num_tests)):
            save_path = os.path.join(SAVE_PAYLOAD_DIR, f"{i}.json")
            if os.path.exists(save_path):
                continue
            _, response_create_params = generate(ResponseCreateParams, i, {}, True)
            out = create_response(save_path, response_create_params)
            print(out)
    else:
        i = seed
        save_path = os.path.join(SAVE_PAYLOAD_DIR, f"{i}.json")
        _, response_create_params = generate(ResponseCreateParams, i, {}, True)
        out = create_response(save_path, response_create_params)
        print(out)


def gen_response_result_params(seed: Optional[int]):
    from openai.types.responses.response import Response
    if seed is None:
        num_tests, response_result = generate(Response, 0, {}, True)
        for i in tqdm(range(num_tests)):
            save_path = os.path.join(SAVE_RESPONSE_DIR, f"{i}.json")
            if os.path.exists(save_path):
                continue
            _, response_result = generate(Response, i, {}, True)
            create_response_output(save_path, response_result)
    else:
        i = seed
        save_path = os.path.join(SAVE_RESPONSE_DIR, f"{i}.json")
        _, response_result = generate(Response, i, {}, True)
        import pdb; pdb.set_trace()
        create_response_output(save_path, response_result)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-r', '--gen-response', action='store_true')
    parser.add_argument('-s', '--seed', type=int, default=None)
    args = parser.parse_args()
    if args.gen_response:
        gen_response_result_params(args.seed)
    else:
        gen_response_create_params(args.seed)
