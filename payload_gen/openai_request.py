from openai import OpenAI, NotFoundError
from openai.resources.responses import Responses
from openai.types.responses.response_create_params import ResponseCreateParams
from openai._types import NOT_GIVEN
import json
import httpx
import os

SAVE_FILEPATH = "tmp.json"


cli = Responses(OpenAI())


def save_request(request: httpx.Request):
    save_dir = os.path.dirname(SAVE_FILEPATH)
    os.makedirs(save_dir, exist_ok=True)
    with open(SAVE_FILEPATH, "w+") as f:
        payload = json.loads(request.content.decode("utf-8"))
        json.dump(payload, f, indent=2)
    # save headers
    headers_filename = os.path.join(save_dir, "headers.json")
    with open(headers_filename, "w+") as f:
        json.dump(dict(request.headers), f, indent=2)


def get_item(obj, item):
    if isinstance(obj, dict):
        return obj.get(item, None)
    return getattr(obj, item, None)

def set_item(obj, item, value):
    if isinstance(obj, dict):
        obj[item] = value
    else:
        setattr(obj, item, value)


def get_dict(obj) -> dict:
    if isinstance(obj, dict):
        return obj
    return obj.model_dump()


def validate_response_create_args(response_create_args: ResponseCreateParams):
    if (get_item(response_create_args, "previous_response_id") is not None and
        get_item(response_create_args, "conversation") is not None):
        # set `previous_response_id` to None so that full set of options for
        # `conversation` can be iterated over
        set_item(response_create_args, "previous_response_id", None)
    if get_item(response_create_args, "stream_options") is not None:
        set_item(response_create_args, "stream", True)
    # conversation ID
    if isinstance(get_item(response_create_args, "conversation"), str):
        set_item(response_create_args, "conversation", "conv_abc123")
    # response ID
    if get_item(response_create_args, "previous_response_id"):
        set_item(response_create_args, "previous_response_id", "resp_abc123")
    # serialize without NOT_GIVEN
    print(json.dumps(get_dict(response_create_args), indent=2))
    for k, v in get_dict(response_create_args).items():
        if v is None:
            set_item(response_create_args, k, NOT_GIVEN)
    return response_create_args


def create_response(save_path: str, response_create_args: ResponseCreateParams):
    global SAVE_FILEPATH
    SAVE_FILEPATH = save_path
    try:
        return cli.create(**validate_response_create_args(response_create_args))
    except NotFoundError as e:
        print(repr(e))
