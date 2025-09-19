from typing import List, Union, Sequence, Iterable, Optional, Dict, Any, _GenericAlias, _TypedDictMeta, get_type_hints,  _AnnotatedAlias
from typing_extensions import Literal, Annotated, TypeAlias, Required, TypedDict
from collections import abc

from pydantic._internal._model_construction import ModelMetaclass
from openai._models import BaseModel
from openai._utils._transform import PropertyInfo

INT_VAL = 1
FLOAT_VAL = 1.0
STR_VAL = "string"

ID_PREFIX_MAP = {
}

def is_td(cls):
    return type(cls).__name__ == '_TypedDictMeta'

def get_openai_id(prefix: str) -> str:
    return f"{prefix}_abc123"


def list_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool) -> "List[Any]":
    if not len(args) == 1:
        import pdb; pdb.set_trace()
    stride, output = generate(args[0], seed, stride_dict, build)

    # if building stride_dict, update
    if build:
        stride_dict[type_name] = stride

    return [output]


def dict_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool) -> "Dict[Any, Any]":
    if not len(args) == 2:
        import pdb; pdb.set_trace()
    key_stride, key_out = generate(args[0], seed, stride_dict, build)
    val_stride, val_out = generate(args[1], seed, stride_dict, build)

    # if building stride_dict, update
    if build:
        stride_dict[type_name] = max(key_stride, val_stride)

    return {key_out: val_out}


def _union_generator_build(type_name: str, args: type, seed: int, stride_dict: Optional[dict[str, int]]) -> "Any":
    cum_stride = 0
    outputs = []
    for i in range(len(args)):
        # from openai.types.responses.easy_input_message_param import EasyInputMessageParam
        # if args[i] == EasyInputMessageParam:
        #     import pdb; pdb.set_trace()
        stride, output = generate(args[i], seed - cum_stride, stride_dict, True)
        cum_stride += stride
        outputs.append((cum_stride, output))
    
    for cum_stride, output in outputs:
        if seed < cum_stride:
            break
    
    stride_dict[type_name] = outputs[-1][0] # total cumulative stride
    return output


def _union_generator_nobuild(args: type, seed: int, stride_dict: Optional[dict[str, int]]) -> "Any":
    cum_stride = 0
    for i in range(len(args)):
        type_name = repr(args[i])
        if type_name not in stride_dict:
            import pdb; pdb.set_trace()
        stride = stride_dict[type_name]
        if seed < cum_stride + stride:
            break
        cum_stride += stride
    _, output = generate(args[i], seed - cum_stride, stride_dict, False)
    return output


def union_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool) -> "Any":
    if build:
        return _union_generator_build(type_name, args, seed, stride_dict)
    else:
        return _union_generator_nobuild(args, seed, stride_dict)


def annotated_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool) -> "Any":
    if not len(args) == 1:
        import pdb; pdb.set_trace()
    stride, output = generate(args[0], seed, stride_dict, build)

    # if building stride_dict, update
    if build:
        stride_dict[type_name] = stride

    # dont need to use metadata
    return output


def literal_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool) -> "Any":
    output = args[seed % len(args)]
    
    if build:
        stride_dict[type_name] = len(args)

    return output


def required_generator(type_name: str, args: type, metadata: tuple[Any], seed: int, stride_dict: Optional[dict[str, int]], build: bool, key_in_data: str = "", data_type: str = "") -> "Any":
    if not len(args) == 1:
        import pdb; pdb.set_trace()
    stride, output = generate(args[0], seed, stride_dict, build, key_in_data, data_type)

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
    if (
        (obj_type := cls.__pydantic_fields__.get("type")) and
        (ann := getattr(obj_type, "annotation")) and
        (type_literals := getattr(ann, "__args__", [])) and
        len(type_literals) == 1
    ):
        data_type = type_literals[0]
    elif (
        (obj_type := cls.__pydantic_fields__.get("data_type")) and
        (not getattr(obj_type, "annotation"))
    ):
        import pdb; pdb.set_trace()
    else:
        data_type = ""
    if "id" in cls.__pydantic_fields__.keys() and not data_type:
        from openai.types.responses.response_input_param import ItemReference
        if cls.__name__ == "ItemReference":
            import pdb; pdb.set_trace()
        print(f"class {cls} has id but no data type")
    for key, field_info in cls.__pydantic_fields__.items():
        if not hasattr(field_info, "annotation"):
            import pdb; pdb.set_trace()
        typ = field_info.annotation
        stride, output = generate(typ, seed, stride_dict, build, key, data_type)

        # # required = field_info.required
        # type_name = repr(typ)
        # if isinstance(typ, _GenericAlias):
        #     if not (hasattr(typ, "__origin__") and typ.__origin__ in generator_map):
        #         pdb.set_trace()
        #     if not hasattr(typ, "__args__"):
        #         pdb.set_trace()
        #     output = generator_map[typ.__origin__](type_name, typ.__args__, (), seed, stride_dict, build)
        #     if type_name not in stride_dict:
        #         pdb.set_trace()
        #     stride = stride_dict[type_name]
        # # actually this is probably not necessary
        # # elif isinstance(typ, _AnnotatedAlias):
        # #     if not (hasattr(typ, "__origin__") and typ.__origin__ in generator_map):
        # #         pdb.set_trace()
        # #     if not hasattr(typ, "__args__"):
        # #         pdb.set_trace()
        # #     if not hasattr(typ, "__metadata__"):
        # #         pdb.set_trace()
        # #     type_name = repr(typ)
        # #     return generator_map[typ.__origin__](type_name, typ.__args__, typ.__metadata__, seed, stride_dict, build)
        # elif issubclass(typ, BaseModel):
        #     output = generate_basemodel(typ, seed, stride_dict, build)
        #     if type_name not in stride_dict:
        #         pdb.set_trace()
        #     stride = stride_dict[type_name]
        # elif is_td(typ):
        #     output = generate_typeddict(typ, seed, stride_dict, build)
        #     if type_name not in stride_dict:
        #         pdb.set_trace()
        #     stride = stride_dict[type_name]
        # # handle basic python types
        # elif typ == str:
        #     if key == "id":
        #         # need to use openai id format
        #         if (
        #             (obj_type := cls.__pydantic_fields__.get("type")) and
        #             (type_literals := getattr(obj_type.annotation, "__args__", [])) and
        #             len(type_literals) == 1
        #         ):
        #             id_prefix = ID_PREFIX_MAP.get(type_literals[0], "")
        #             if not id_prefix:
        #                 print(f"MISSING ID prefix for type `{type_literals[0]}` -- update ID_PREFIX_MAP once the call to OpenAI fails")
        #         else:
        #             pdb.set_trace()

        #         id_prefix = None
        #         output = get_openai_id(id_prefix)
        #     else:
        #         output = STR_VAL
        #     stride = 1
        # elif typ == int:
        #     output = INT_VAL
        #     stride = 1
        # elif typ == float:
        #     output = FLOAT_VAL
        #     stride = 1
        # elif typ == bool:
        #     output = seed % 2 == 0
        #     stride = 2
        # else:
        #     pdb.set_trace()

        cls_kwargs[key] = output

        if build:
            max_stride = max(max_stride, stride)

    stride_dict[repr(cls)] = max_stride
    return cls(**cls_kwargs)


def generate_typeddict(cls: _TypedDictMeta, seed: int, stride_dict: Optional[dict[str, int]], build: bool) -> str:
    max_stride = 0
    cls_kwargs = {}
    type_dict = get_type_hints(cls)
    if (
        (obj_type := type_dict.get("type")) and
        (type_literals := getattr(obj_type, "__args__", [])) and
        len(type_literals) == 1
    ):
        data_type = type_literals[0]
    else:
        data_type = ""
    if "id" in type_dict and not data_type:
        from openai.types.responses.response_input_param import ItemReference
        if cls.__name__ == "ItemReference":
            import pdb; pdb.set_trace()
        print(f"class {cls} has id but no data type")
    for key, typ in type_dict.items():
        stride, output = generate(typ, seed, stride_dict, build, key, data_type)

        # # typ = field_info.annotation
        # # required = field_info.required
        # type_name = repr(typ)
        # if isinstance(typ, _GenericAlias):
        #     if not (hasattr(typ, "__origin__") and typ.__origin__ in generator_map):
        #         pdb.set_trace()
        #     if not hasattr(typ, "__args__"):
        #         pdb.set_trace()
        #     output = generator_map[typ.__origin__](type_name, typ.__args__, (), seed, stride_dict, build)
        #     if type_name not in stride_dict:
        #         pdb.set_trace()
        #     stride = stride_dict[type_name]
        # # actually this is probably not necessary
        # # elif isinstance(typ, _AnnotatedAlias):
        # #     if not (hasattr(typ, "__origin__") and typ.__origin__ in generator_map):
        # #         pdb.set_trace()
        # #     if not hasattr(typ, "__args__"):
        # #         pdb.set_trace()
        # #     if not hasattr(typ, "__metadata__"):
        # #         pdb.set_trace()
        # #     type_name = repr(typ)
        # #     return generator_map[typ.__origin__](type_name, typ.__args__, typ.__metadata__, seed, stride_dict, build)
        # elif issubclass(typ, BaseModel):
        #     output = generate_basemodel(typ, seed, stride_dict, build)
        #     if type_name not in stride_dict:
        #         pdb.set_trace()
        #     stride = stride_dict[type_name]
        # elif is_td(typ):
        #     output = generate_typeddict(typ, seed, stride_dict, build)
        #     if type_name not in stride_dict:
        #         pdb.set_trace()
        #     stride = stride_dict[type_name]
        # # handle basic python types
        # elif typ == str:
        #     if key == "id":
        #         # need to use openai id format
        #         if (
        #             (obj_type := type_dict.get("type")) and
        #             (type_literals := getattr(obj_type.annotation, "__args__", [])) and
        #             len(type_literals) == 1
        #         ):
        #             id_prefix = ID_PREFIX_MAP.get(type_literals[0], "")
        #             if not id_prefix:
        #                 print(f"MISSING ID prefix for type `{type_literals[0]}` -- update ID_PREFIX_MAP once the call to OpenAI fails")
        #         else:
        #             pdb.set_trace()

        #         id_prefix = None
        #         output = get_openai_id(id_prefix)
        #     else:
        #         output = STR_VAL
        #     stride = 1
        # elif typ == int:
        #     output = INT_VAL
        #     stride = 1
        # elif typ == float:
        #     output = FLOAT_VAL
        #     stride = 1
        # elif typ == bool:
        #     output = seed % 2 == 0
        #     stride = 2
        # else:
        #     pdb.set_trace()

        cls_kwargs[key] = output

        if build:
            max_stride = max(max_stride, stride)

    stride_dict[repr(cls)] = max_stride
    return cls(**cls_kwargs)


def generate(typ: type, seed: int, stride_dict: Optional[dict[str, int]], build: bool, key_in_data: str = "", data_type: str = "") -> "tuple[int, Any]":
    # if key_in_data == "input":
    #     import pdb; pdb.set_trace()
    type_name = repr(typ)
    if isinstance(typ, _AnnotatedAlias):
        if not hasattr(typ, "__args__"):
            import pdb; pdb.set_trace()
        if not len(typ.__args__) == 1:
            import pdb; pdb.set_trace()
        if not hasattr(typ, "__metadata__"):
            import pdb; pdb.set_trace()
        stride, output = generate(typ.__args__[0], seed, stride_dict, build)
    elif isinstance(typ, _GenericAlias):
        if not (hasattr(typ, "__origin__") and typ.__origin__ in generator_map):
            import pdb; pdb.set_trace()
        if not hasattr(typ, "__args__"):
            import pdb; pdb.set_trace()
        add_kwargs = {}
        if typ.__origin__ == Required:
            add_kwargs = {"key_in_data": key_in_data, "data_type": data_type}
        output = generator_map[typ.__origin__](type_name, typ.__args__, (), seed, stride_dict, build, **add_kwargs)
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
            if data_type:
                id_prefix = ID_PREFIX_MAP.get(data_type, "")
                if not id_prefix:
                    print(f"MISSING ID prefix for type `{data_type}` -- update ID_PREFIX_MAP once the call to OpenAI fails")
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
        output = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to perform.", # describes the paramteres to OpenAI
                },
            },
            "required": ["query"],
        }
        stride = 1
    else:
        import pdb; pdb.set_trace()

    if isinstance(output, tuple) and len(output) == 2:
        import pdb; pdb.set_trace()

    return stride, output


def main():
    from openai.types.responses.response_create_params import ResponseCreateParamsBase
    from openai.types.responses.response_code_interpreter_tool_call import ResponseCodeInterpreterToolCall
    from openai.types.responses.response_code_interpreter_tool_call_param import ResponseCodeInterpreterToolCallParam
    for i in range(100):
        generate(ResponseCodeInterpreterToolCallParam, i, {}, True)
        generate(ResponseCodeInterpreterToolCall, i, {}, True)
        generate_typeddict(ResponseCreateParamsBase, i, {}, True)


if __name__ == "__main__":
    main()
