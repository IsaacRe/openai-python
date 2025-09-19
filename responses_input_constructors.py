"""
Sample input constructors for OpenAI Responses.create() method.

This module provides constructors to generate sample inputs for each argument
in the Responses.create() call signature by recursively creating constructors
for all types from which that input's type is composed.
"""

import random
import string
from typing import Any, Dict, List, Optional, Union


def random_string(length: int = 10) -> str:
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def random_id() -> str:
    """Generate a random ID string."""
    return f"id_{random_string(12)}"


def shell_call_output_id() -> str:
    return f"lsho-123"


def random_url() -> str:
    """Generate a random URL."""
    return f"https://example.com/{random_string(8)}"


def random_base64_image() -> str:
    """Generate a sample base64 encoded image string."""
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


def random_base64() -> str:
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


# Basic type constructors
def construct_str() -> str:
    """Construct a sample string."""
    return random_string()


def construct_int(min_val: int = 0, max_val: int = 100) -> int:
    """Construct a sample integer."""
    return random.randint(min_val, max_val)


def construct_float(min_val: float = 0.0, max_val: float = 2.0) -> float:
    """Construct a sample float."""
    return random.uniform(min_val, max_val)


def construct_bool() -> bool:
    """Construct a sample boolean."""
    return random.choice([True, False])


def construct_optional(x: Any) -> Optional[Any]:
    return random.choice([None, x])


# Metadata constructor
def construct_metadata() -> Dict[str, str]:
    """Construct sample metadata (Dict[str, str])."""
    return {
        f"key_{i}": f"value_{i}"
        for i in range(random.randint(1, 5))
    }


# ResponsesModel constructor
def construct_responses_model() -> str:
    """Construct a sample ResponsesModel."""
    models = [
        "gpt-4o",
        "gpt-4o-mini",
        "o1-pro",
        "o1-pro-2025-03-19",
        "o3-pro",
        "o3-pro-2025-06-10",
        "o3-deep-research",
        "o3-deep-research-2025-06-26",
        "o4-mini-deep-research",
        "o4-mini-deep-research-2025-06-26",
        "computer-use-preview",
        "computer-use-preview-2025-03-11",
    ]
    return random.choice(models)


# ResponseIncludable constructor
def construct_response_includable() -> str:
    """Construct a sample ResponseIncludable."""
    includables = [
        "web_search_call.action.sources",
        "code_interpreter_call.outputs",
        "computer_call_output.output.image_url",
        "file_search_call.results",
        "message.input_image.image_url",
        "message.output_text.logprobs",
        "reasoning.encrypted_content",
    ]
    return random.choice(includables)


def construct_image_detail() -> str:
    """Construct a sample image detail."""
    return random.choice(["low", "high", "auto"])


def construct_audio_input() -> Dict[str, Any]:
    """Construct a sample audio input."""
    return {
        "data": random_base64(),
        "format": random.choice(["wav", "mp3"])
    }


# ResponseInputMessageContentListParam constructor
def construct_response_input_message_content_list_param() -> List[Dict[str, Any]]:
    """Construct sample ResponseInputMessageContentListParam."""
    content_types = [
        {"type": "input_text", "text": construct_str()},
        {"type": "input_image", "detail": construct_image_detail(), "id": random_id(), "image_url": random_url()},
        {"type": "input_file", "file_data": construct_str(), "file_id": random_id(), "file_url": random_url(), "filename": random_string()},
        {"type": "input_audio", "input_audio": construct_audio_input()},
    ]
    return [random.choice(content_types) for _ in range(random.randint(1, 3))]


# EasyInputMessageParam constructor
def construct_easy_input_message_param() -> Dict[str, Any]:
    """Construct sample EasyInputMessageParam."""
    content = random.choice([
        construct_str(),
        construct_response_input_message_content_list_param()
    ])
    
    return {
        "content": content,
        "role": random.choice(["user", "system", "developer"]),  #  "assistant" included in api but leads to errors
        "type": "message"
    }


# ResponseOutputTextParam constructor
def construct_response_output_text_param() -> Dict[str, Any]:
    """Construct sample ResponseOutputTextParam."""
    # Construct annotations
    annotation_types = [
        {
            "file_id": random_id(),
            "filename": f"file_{random_string(5)}.txt",
            "index": random.randint(0, 10),
            "type": "file_citation"
        },
        {
            "end_index": random.randint(50, 100),
            "start_index": random.randint(0, 49),
            "title": f"Web Resource {random_string(5)}",
            "type": "url_citation",
            "url": random_url()
        },
        {
            "container_id": random_id(),
            "end_index": random.randint(50, 100),
            "file_id": random_id(),
            "filename": f"container_{random_string(5)}.zip",
            "start_index": random.randint(0, 49),
            "type": "container_file_citation"
        },
        {
            "file_id": random_id(),
            "index": random.randint(0, 10),
            "type": "file_path"
        }
    ]
    
    # Construct logprobs
    def construct_logprob():
        return {
            "token": random_string(3),
            "bytes": [random.randint(0, 255) for _ in range(random.randint(1, 4))],
            "logprob": random.uniform(-10.0, 0.0),
            "top_logprobs": [
                {
                    "token": random_string(3),
                    "bytes": [random.randint(0, 255) for _ in range(random.randint(1, 4))],
                    "logprob": random.uniform(-10.0, 0.0)
                }
                for _ in range(random.randint(1, 5))
            ]
        }
    
    return {
        "annotations": [random.choice(annotation_types) for _ in range(random.randint(0, 3))],
        "text": construct_str(),
        "type": "output_text",
        "logprobs": [construct_logprob() for _ in range(random.randint(0, 5))] if random.choice([True, False]) else None
    }


def construct_response_output_refusal_param() -> Dict[str, Any]:
    """Construct sample ResponseOutputRefusalParam."""
    return {
        "refusal": f"I cannot provide that information because {construct_str()}",
        "type": "refusal"
    }


def construct_response_output_content() -> Dict[str, Any]:
    """Construct sample Content (Union[ResponseOutputTextParam, ResponseOutputRefusalParam])."""
    return random.choice([
        construct_response_output_text_param(),
        construct_response_output_refusal_param()
    ])


# ResponseOutputMessageParam constructor
def construct_response_output_message_param() -> Dict[str, Any]:
    """Construct sample ResponseOutputMessageParam."""
    return {
        "id": random_id(),
        "content": [construct_response_output_content() for _ in range(random.randint(1, 3))],
        "role": "assistant",
        "status": random.choice(["in_progress", "completed", "incomplete"]),
        "type": "message"
    }


# Message constructor (from ResponseInputParam)
def construct_message() -> Dict[str, Any]:
    """Construct sample Message."""
    return {
        "content": construct_response_input_message_content_list_param(),
        "role": random.choice(["user", "system", "developer"]),
        "type": "message",
        "status": random.choice(["in_progress", "completed", "incomplete"])
    }


# ComputerCallOutput constructor
def construct_computer_call_output() -> Dict[str, Any]:
    """Construct sample ComputerCallOutput."""
    return {
        "call_id": random_id(),
        "output": {
            "type": "screenshot",
            "image_url": random_base64_image()
        },
        "type": "computer_call_output",
        "id": "cuo_abc123",
        "acknowledged_safety_checks": construct_optional([
            {
                "id": f"safety_check_{random_string(8)}",
                "code": construct_optional(random.choice(["CONTENT_POLICY", "SAFETY_VIOLATION", "HARMFUL_REQUEST"])),
                "message": construct_optional(f"Safety check message: {construct_str()}")
            }
            for _ in range(random.randint(0, 2))
        ]),
        "status": random.choice(["in_progress", "completed", "incomplete"])
    }


# FunctionCallOutput constructor
def construct_function_call_output() -> Dict[str, Any]:
    """Construct sample FunctionCallOutput."""
    return {
        "call_id": random_id(),
        "output": '{"result": "success", "data": "sample_output"}',
        "type": "function_call_output",
        "id": "fc_abc123",
        "status": random.choice(["in_progress", "completed", "incomplete"])
    }


# Tool call constructors
def construct_response_file_search_tool_call_param() -> Dict[str, Any]:
    """Construct sample ResponseFileSearchToolCallParam."""
    return {
        "id": random_id(),
        "type": "file_search_call",
        "queries": [construct_str() for _ in range(random.randint(1, 3))],
        "status": random.choice(["in_progress", "searching", "completed", "incomplete", "failed"]),
        "results": construct_optional([
            {
                "attributes": construct_optional({
                    f"attr_{i}": random.choice([construct_str(), construct_float(), construct_bool()])
                    for i in range(random.randint(1, 4))
                }),
                "file_id": construct_optional(f"file_{random_string(8)}"),
                "filename": construct_optional(f"document_{random_string(5)}.pdf"),
                "score": construct_optional(random.uniform(0.0, 1.0)),
                "text": construct_optional(f"Retrieved text content: {construct_str()}")
            }
            for _ in range(random.randint(0, 3))
        ])
    }


def construct_response_computer_tool_call_param() -> Dict[str, Any]:
    """Construct sample ResponseComputerToolCallParam."""
    return {
        "id": random_id(),
        "type": "computer_call",
        "action": {
            "type": random.choice(["screenshot", "click", "type", "scroll"]),
            "coordinate": [random.randint(0, 1920), random.randint(0, 1080)] if random.choice([True, False]) else None,
            "text": construct_str() if random.choice([True, False]) else None
        },
        "status": random.choice(["in_progress", "completed", "incomplete"])
    }


def construct_response_function_web_search_param() -> Dict[str, Any]:
    """Construct sample ResponseFunctionWebSearchParam."""
    return {
        "id": random_id(),
        "type": "web_search_call",
        "query": construct_str(),
        "status": random.choice(["in_progress", "completed", "incomplete"])
    }


def construct_response_function_tool_call_param() -> Dict[str, Any]:
    """Construct sample ResponseFunctionToolCallParam."""
    return {
        "id": random_id(),
        "type": "function_call",
        "function": {
            "name": f"function_{random_string(5)}",
            "arguments": '{"param1": "value1", "param2": 42}'
        },
        "status": random.choice(["in_progress", "completed", "incomplete"])
    }


def construct_response_reasoning_item_param() -> Dict[str, Any]:
    """Construct sample ResponseReasoningItemParam."""
    return {
        "id": random_id(),
        "summary": construct_str(),
        "type": "reasoning",
        "content": [{"text": construct_str(), "type": "reasoning_text"}],
        "encrypted_content": construct_optional(random_base64()),
        "status": random.choice(["in_progress", "completed", "incomplete"])
    }


def construct_image_generation_call() -> Dict[str, Any]:
    """Construct sample ImageGenerationCall."""
    return {
        "id": random_id(),
        "result": random_base64_image() if random.choice([True, False]) else None,
        "status": random.choice(["in_progress", "completed", "generating", "failed"]),
        "type": "image_generation_call"
    }


def construct_response_code_interpreter_tool_call_param() -> Dict[str, Any]:
    """Construct sample ResponseCodeInterpreterToolCallParam."""
    return {
        "id": random_id(),
        "type": "code_interpreter_call",
        "code": f"print('{construct_str()}')",
        "status": random.choice(["in_progress", "completed", "incomplete"])
    }


def construct_local_shell_call() -> Dict[str, Any]:
    """Construct sample LocalShellCall."""
    return {
        "id": random_id(),
        "action": {
            "command": ["echo", construct_str()],
            "env": {"PATH": "/usr/bin", "HOME": "/home/user"},
            "type": "exec",
            "timeout_ms": random.randint(1000, 30000),
            "working_directory": "/tmp"
        },
        "call_id": random_id(),
        "status": random.choice(["in_progress", "completed", "incomplete"]),
        "type": "local_shell_call"
    }


def construct_local_shell_call_output() -> Dict[str, Any]:
    """Construct sample LocalShellCallOutput."""
    return {
        "id": shell_call_output_id(),
        "output": f"Command output: {construct_str()}",
        "type": "local_shell_call_output",
        "status": random.choice(["in_progress", "completed", "incomplete"]),
        "call_id": random_id()  # this is apparently necessary despite not being referenced in types
    }


def construct_mcp_list_tools() -> Dict[str, Any]:
    """Construct sample McpListTools."""
    return {
        "id": random_id(),
        "server_label": f"server_{random_string(5)}",
        "tools": [
            {
                "input_schema": {"type": "object", "properties": {"param": {"type": "string"}}},
                "name": f"tool_{random_string(5)}",
                "description": f"Tool description: {construct_str()}"
            }
        ],
        "type": "mcp_list_tools",
        "error": construct_str() if random.choice([True, False]) else None
    }


def construct_mcp_approval_request() -> Dict[str, Any]:
    """Construct sample McpApprovalRequest."""
    return {
        "id": random_id(),
        "arguments": '{"param": "value"}',
        "name": f"tool_{random_string(5)}",
        "server_label": f"server_{random_string(5)}",
        "type": "mcp_approval_request"
    }


def construct_mcp_approval_response() -> Dict[str, Any]:
    """Construct sample McpApprovalResponse."""
    return {
        "approval_request_id": random_id(),
        "approve": construct_bool(),
        "type": "mcp_approval_response",
        "id": "mcpa_abc123",
        "reason": construct_str() if random.choice([True, False]) else None
    }


def construct_mcp_call() -> Dict[str, Any]:
    """Construct sample McpCall."""
    return {
        "id": random_id(),
        "arguments": '{"param": "value"}',
        "name": f"tool_{random_string(5)}",
        "server_label": f"server_{random_string(5)}",
        "type": "mcp_call",
        "error": construct_str() if random.choice([True, False]) else None,
        "output": construct_str() if random.choice([True, False]) else None
    }


def construct_response_custom_tool_call_output_param() -> Dict[str, Any]:
    """Construct sample ResponseCustomToolCallOutputParam."""
    return {
        "call_id": random_id(),
        "output": construct_str(),
        "type": "custom_tool_call_output",
        "id": "ctco_abc123",
        "status": random.choice(["in_progress", "completed", "incomplete"])
    }


def construct_response_custom_tool_call_param() -> Dict[str, Any]:
    """Construct sample ResponseCustomToolCallParam."""
    return {
        "id": random_id(),
        "call_id": random_id(),
        "type": "custom_tool_call",
        "name": f"custom_tool_{random_string(5)}",
        "status": random.choice(["in_progress", "completed", "incomplete"])
    }


def construct_item_reference() -> Dict[str, Any]:
    """Construct sample ItemReference."""
    return {
        "id": random_id(),
        "type": "item_reference"
    }


# ResponseInputItemParam constructor (union type)
def construct_response_input_item_param() -> Dict[str, Any]:
    """Construct sample ResponseInputItemParam using random.choice for union types."""
    constructors = [
        construct_easy_input_message_param,
        construct_message,
        construct_response_output_message_param,
        construct_response_file_search_tool_call_param,
        construct_response_computer_tool_call_param,
        construct_computer_call_output,
        construct_response_function_web_search_param,
        construct_response_function_tool_call_param,
        construct_function_call_output,
        construct_response_reasoning_item_param,
        construct_image_generation_call,
        construct_response_code_interpreter_tool_call_param,
        construct_local_shell_call,
        construct_local_shell_call_output,
        construct_mcp_list_tools,
        construct_mcp_approval_request,
        construct_mcp_approval_response,
        construct_mcp_call,
        construct_response_custom_tool_call_output_param,
        construct_response_custom_tool_call_param,
        construct_item_reference,
    ]
    return random.choice(constructors)()


# ResponseInputParam constructor
def construct_response_input_param() -> List[Dict[str, Any]]:
    """Construct sample ResponseInputParam (List[ResponseInputItemParam])."""
    return [
        construct_response_input_item_param()
        for _ in range(random.randint(1, 5))
    ]


# Input parameter constructor (Union[str, ResponseInputParam])
def construct_input() -> Union[str, List[Dict[str, Any]]]:
    """Construct sample input parameter."""
    return random.choice([
        construct_str(),
        construct_response_input_param()
    ])


# Conversation parameter constructor
def construct_conversation() -> Optional[Union[str, Dict[str, Any]]]:
    """Construct sample conversation parameter."""
    return random.choice([
        "conv_abc123",  # conversation ID
        {
            "id": "conv_abc123",
        }
    ])


# StreamOptions constructor
def construct_stream_options() -> Optional[Dict[str, Any]]:
    """Construct sample StreamOptions."""
    return {
        "include_obfuscation": construct_bool()
    }


# Tool-related constructors
def construct_tool_param() -> Dict[str, Any]:
    """Construct sample ToolParam."""
    tool_types = [
        # Apparently this format is invalid
        # {
        #     "type": "function",
        #     "function": {
        #         "name": f"function_{random_string(5)}",
        #         "description": f"Function description: {construct_str()}",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "param1": {"type": "string", "description": "Parameter 1"},
        #                 "param2": {"type": "integer", "description": "Parameter 2"}
        #             },
        #             "required": ["param1"]
        #         },
        #         "strict": construct_optional(construct_bool())
        #     }
        # },
        # {
        #     "type": "function",
        #     "name": f"function_{random_string(5)}",
        #     "description": construct_optional(f"Function description: {construct_str()}"),
        #     "parameters": construct_optional({
        #         "type": "object",
        #         "properties": {
        #             "param1": {"type": "string", "description": "Parameter 1"},
        #             "param2": {"type": "integer", "description": "Parameter 2"}
        #         },
        #         "required": ["param1"]
        #     }),
        #     "strict": construct_optional(construct_bool())
        # },
        {
            "type": "file_search",
            "vector_store_ids": [f"vs_abc12{i}" for i in range(random.randint(1, 3))],
            "filters": construct_optional(random.choice([
                # ComparisonFilter
                {
                    "type": random.choice(["eq", "ne", "gt", "gte", "lt", "lte"]),
                    "key": random.choice(["filename", "file_id", "created_at", "size"]),
                    "value": random.choice([construct_str(), construct_float(), construct_bool()])
                },
                # CompoundFilter
                {
                    "type": random.choice(["and", "or"]),
                    "filters": [
                        {
                            "type": random.choice(["eq", "ne", "gt", "gte", "lt", "lte"]),
                            "key": random.choice(["filename", "file_id", "created_at", "size"]),
                            "value": random.choice([construct_str(), construct_float(), construct_bool()])
                        }
                        for _ in range(random.randint(1, 3))
                    ]
                }
            ])),
            "max_num_results": construct_optional(random.randint(1, 50)),
            "ranking_options": construct_optional({
                "ranker": random.choice(["auto", "default-2024-11-15"]),
                "score_threshold": construct_optional(random.uniform(0.0, 1.0))
            })
        },
        # {
        #     "type": "code_interpreter",
        #     "container": random.choice([
        #         random_id(),  # container ID
        #         {
        #             "type": "auto",
        #             "file_ids": construct_optional([f"file_abc12{i}" for i in range(random.randint(0, 3))])
        #         }
        #     ])
        # },
        # {
        #     "type": "web_search",
        #     "filters": construct_optional({
        #         "allowed_domains": construct_optional([f"{random_string(5)}.com" for _ in range(random.randint(1, 3))])
        #     }),
        #     "search_context_size": construct_optional(random.choice(["low", "medium", "high"])),
        #     "user_location": construct_optional({
        #         "city": construct_optional(f"City_{random_string(5)}"),
        #         "country": construct_optional(random.choice(["US", "CA", "GB", "DE", "FR"])),
        #         "region": construct_optional(f"Region_{random_string(5)}"),
        #         "timezone": construct_optional(random.choice(["America/Los_Angeles", "America/New_York", "Europe/London"])),
        #         "type": construct_optional("approximate")
        #     })
        # },
        # {
        #     "type": "mcp",
        #     "server_label": f"mcp_server_{random_string(5)}",
        #     "allowed_tools": construct_optional(random.choice([
        #         [f"tool_{random_string(3)}" for _ in range(random.randint(1, 3))],
        #         {
        #             "read_only": construct_optional(construct_bool()),
        #             "tool_names": construct_optional([f"tool_{random_string(3)}" for _ in range(random.randint(1, 3))])
        #         }
        #     ])),
        #     "authorization": construct_optional(f"Bearer {random_string(32)}"),
        #     "connector_id": construct_optional(random.choice([
        #         "connector_dropbox", "connector_gmail", "connector_googlecalendar",
        #         "connector_googledrive", "connector_microsoftteams", "connector_outlookcalendar",
        #         "connector_outlookemail", "connector_sharepoint"
        #     ])),
        #     "headers": construct_optional({f"X-{random_string(5)}": random_string(10)}),
        #     "require_approval": construct_optional(random.choice([
        #         "always", "never",
        #         {
        #             "always": {
        #                 "read_only": construct_optional(construct_bool()),
        #                 "tool_names": construct_optional([f"tool_{random_string(3)}" for _ in range(random.randint(1, 2))])
        #             }
        #         }
        #     ])),
        #     "server_description": construct_optional(f"MCP server description: {construct_str()}"),
        #     "server_url": construct_optional(f"https://mcp-server-{random_string(5)}.com")
        # },
        # {
        #     "type": "image_generation",
        #     "background": construct_optional(random.choice(["transparent", "opaque", "auto"])),
        #     "input_fidelity": construct_optional(random.choice(["high", "low"])),
        #     "input_image_mask": construct_optional({
        #         "file_id": construct_optional(f"file_{random_string(8)}"),
        #         "image_url": construct_optional(random_base64_image())
        #     }),
        #     "model": construct_optional("gpt-image-1"),
        #     "moderation": construct_optional(random.choice(["auto", "low"])),
        #     "output_compression": construct_optional(random.randint(1, 100)),
        #     "output_format": construct_optional(random.choice(["png", "webp", "jpeg"])),
        #     "partial_images": construct_optional(random.randint(0, 3)),
        #     "quality": construct_optional(random.choice(["low", "medium", "high", "auto"])),
        #     "size": construct_optional(random.choice(["1024x1024", "1024x1536", "1536x1024", "auto"]))
        # },
        # {
        #     "type": "local_shell"
        # },
        # {
        #     "type": "custom",
        #     "name": f"custom_tool_{random_string(5)}",
        #     "description": construct_optional(f"Custom tool description: {construct_str()}"),
        #     "parameters": construct_optional({
        #         "type": "object",
        #         "properties": {
        #             "param1": {"type": "string", "description": "Custom parameter 1"},
        #             "param2": {"type": "number", "description": "Custom parameter 2"}
        #         },
        #         "required": ["param1"]
        #     })
        # },
        # {
        #     "type": random.choice(["web_search_preview", "web_search_preview_2025_03_11"]),
        #     "search_context_size": construct_optional(random.choice(["low", "medium", "high"])),
        #     "user_location": construct_optional({
        #         "type": "approximate",
        #         "city": construct_optional(f"City_{random_string(5)}"),
        #         "country": construct_optional(random.choice(["US", "CA", "GB", "DE", "FR"])),
        #         "region": construct_optional(f"Region_{random_string(5)}"),
        #         "timezone": construct_optional(random.choice(["America/Los_Angeles", "America/New_York", "Europe/London"]))
        #     })
        # },
        # {
        #     "type": "computer_use_preview",
        #     "display_height": random.randint(600, 1440),
        #     "display_width": random.randint(800, 1920),
        #     "environment": random.choice(["windows", "mac", "linux", "ubuntu", "browser"])
        # }
    ]
    return random.choice(tool_types)


def construct_tool_choice() -> Union[str, Dict[str, Any]]:
    """Construct sample ToolChoice."""
    choices = [
        "none",
        "auto",
        "required",
        {
            "type": "function",
            "function": {"name": f"function_{random_string(5)}"}
        },
        {
            "type": "file_search"
        }
    ]
    return random.choice(choices)


def construct_response_text_config_param() -> Dict[str, Any]:
    """Construct sample ResponseTextConfigParam."""
    format_options = [
        {"type": "text"},
        {"type": "json_object"},
        {
            "type": "json_schema",
            "name": f"response_schema_{random_string(5)}",
            "schema": {
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "status": {"type": "string", "enum": ["success", "error"]},
                    "data": {"type": "object"}
                },
                "required": ["result", "status"]
            },
            "description": construct_optional(f"Schema description: {construct_str()}"),
            "strict": construct_optional(construct_bool())
        }
    ]
    
    return {
        "format": random.choice(format_options),
        "verbosity": construct_optional(random.choice(["low", "medium", "high"]))
    }


def construct_response_prompt_param() -> Optional[Dict[str, Any]]:
    """Construct sample ResponsePromptParam."""
    return {
        "id": "pmpt_abc123",
        "variables": {
            f"var_{i}": construct_str()
            for i in range(random.randint(1, 3))
        } if random.choice([True, False]) else None
    }


def construct_reasoning() -> Optional[Dict[str, Any]]:
    """Construct sample Reasoning parameter."""
    return {
        "effort": random.choice(["low", "medium", "high"])
    }


# Main constructor function for Responses.create() arguments
def construct_responses_create_args() -> Dict[str, Any]:
    """
    Construct sample arguments for Responses.create() method.
    
    Returns a dictionary with all possible arguments that can be passed
    to the Responses.create() method, with sample values.
    """
    return {
        # Required parameters
        "input": construct_input(),
        "model": construct_responses_model(),
        
        # Optional parameters
        "background": construct_optional(construct_bool()),
        "conversation": construct_optional(construct_conversation()),
        "include": construct_optional([construct_response_includable() for _ in range(random.randint(0, 3))]),
        "instructions": construct_optional(construct_str()),
        "max_output_tokens": construct_optional(construct_int() + 1),
        "max_tool_calls": construct_optional(construct_int() + 1),
        "metadata": construct_optional(construct_metadata()),
        "parallel_tool_calls": construct_optional(construct_bool()),
        "previous_response_id": construct_optional("resp_abc123"),
        "prompt": construct_optional(construct_response_prompt_param()),
        "prompt_cache_key": construct_optional(construct_str()),
        "reasoning": construct_optional(construct_reasoning()),
        "safety_identifier": construct_optional(construct_str()),
        "service_tier": construct_optional(random.choice(["auto", "default", "flex", "scale", "priority"])),
        "store": construct_optional(construct_bool()),
        "stream": construct_optional(random.choice([False, True])),
        "stream_options": construct_optional(construct_stream_options()),
        "temperature": construct_optional(construct_float(0.0, 2.0)),
        "text": construct_optional(construct_response_text_config_param()),
        "tool_choice": construct_optional(construct_tool_choice()),
        "tools": construct_optional([construct_tool_param() for _ in range(random.randint(0, 5))]),
        "top_logprobs": construct_optional(random.randint(0, 20)),
        "top_p": construct_optional(construct_float(0.0, 1.0)),
        "truncation": construct_optional(random.choice(["auto", "disabled"])),
        "user": construct_optional(construct_str()),
    }


DISABLE_PARAMS = [
    "conversation",
    "temperature",
    "prompt",
    "previouse_response_id",
]

def validate_args(args: Dict[str, Any]) -> Dict[str, Any]:
    valid_args = {}
    for key, value in args.items():
        if value is not None:
            valid_args[key] = value
    if valid_args.get("previous_response_id") is not None and valid_args.get("conversation") is not None:
        del valid_args["conversation"]
    if valid_args.get("stream_options"):
        valid_args["stream"] = True
    for p in DISABLE_PARAMS:
        if p in valid_args:
            del valid_args[p]
    return valid_args


def create_validated_responses_create_args() -> Dict[str, Any]:
    args = construct_responses_create_args()
    return validate_args(args)


def main():
    import os
    import json
    from openai.resources.responses import Responses
    from openai import OpenAI
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-n", type=int, default=1)
    parser.add_argument("-d", "--save-dir", type=str, default="save-responses-inputs")
    parser.add_argument("--test-client", action="store_true")
    args = parser.parse_args()
    
    os.makedirs(args.save_dir, exist_ok=True)

    import openai._models
    openai._models.SAVE_PAYLOAD_DIR = args.save_dir

    if args.test_client:
        responses_cli = Responses(OpenAI())

        for i in range(args.n):
            save_path = os.path.join(args.save_dir, f"create-args-{i}.json")
            responses_create_args = create_validated_responses_create_args()
            with open(save_path, "w") as f:
                json.dump(responses_create_args, f, indent=2)
            responses_cli.create(**responses_create_args)

            try:
                responses_cli.create(**responses_create_args)
            except:
                pass
    else:
        from openai.types.responses.response_create_params import ResponseCreateParamsBase

        for i in range(args.n):
            save_path = os.path.join(args.save_dir, f"parsed-args-{i}.json")
            responses_create_args = create_validated_responses_create_args()
            with open(save_path, "w") as f:
                json.dump(responses_create_args, f, indent=2)
            parsed = ResponseCreateParamsBase(**responses_create_args)
            with open(save_path, "w") as f:
                json.dump(parsed, f, indent=2)


if __name__ == "__main__":
    main()
