from openai import OpenAI, NotFoundError, BadRequestError, InternalServerError
from openai.resources.responses import Responses
from openai.types.responses.response_create_params import ResponseCreateParams
from openai.types.responses.response import Response
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
    # force_user_role = ["input_text", "input_image", "input_file", "input_audio"]
    # mutually_exclusive_pairs = [("file_id", "image_url", "file_abc123")]
    # reassign_content_vals = {"file_data": "base64"}
    # if isinstance((content := get_item((inp := get_item(response_create_args, "input")[0]), "content")), list):
    #     if get_item(content[0], "type") in force_user_role:
    #         set_item(inp, "role", "user")
    #     if isinstance(content[0], dict):
    #         inp = content[0]
    #         for a, b, set_a in mutually_exclusive_pairs:
    #             if a in inp and b in inp:
    #                 if inp.get(a) and inp.get(b):
    #                     inp[b] = None
    #                 if not (inp.get(a) or inp.get(b)):
    #                     inp[a] = set_a
    #                 set_item(inp, "role", "user")
    #         for k, v in reassign_content_vals.items():
    #             if k in inp:
    #                 inp[k] = v
    # serialize without NOT_GIVEN
    print(json.dumps(get_dict(response_create_args), indent=2))
    for k, v in get_dict(response_create_args).items():
        if v is None:
            set_item(response_create_args, k, NOT_GIVEN)
    return response_create_args


def validate_responses_output(response_output: Response):
    from openai.types.responses.response_usage import ResponseUsage, InputTokensDetails, OutputTokensDetails
    if response_output.usage is None:
        response_output.usage = ResponseUsage(
            input_tokens=0,
            input_tokens_details=InputTokensDetails(cached_tokens=0),
            output_tokens=0,
            output_tokens_details=OutputTokensDetails(reasoning_tokens=0),
            total_tokens=0
        )

def create_response(save_path: str, response_create_args: ResponseCreateParams):
    global SAVE_FILEPATH
    SAVE_FILEPATH = save_path
    try:
        return cli.create(**validate_response_create_args(response_create_args))
    except (NotFoundError, BadRequestError, InternalServerError) as e:
        print(repr(e))


def create_response_output(save_path: str, response_output: Response):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w+') as f:
        validate_responses_output(response_output)
        json.dump(response_output.model_dump(), f, indent=2)
