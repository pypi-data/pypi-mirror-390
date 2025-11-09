"""
gRPC Call Decorators

Provides common gRPC call decorators to eliminate duplicate code
"""

import grpc
from functools import wraps
from typing import Callable, Optional, Any, Type, get_origin, get_args
from loguru import logger
from pydantic import BaseModel


def grpc_call(
        service_name: str,
        stub_class: type,
        method_name: str,
        response_model: Optional[Type[BaseModel]] = None,
        timeout: int = 5
):
    """
    gRPC call decorator

    Args:
        service_name: Service name, e.g., "system-service"
        stub_class: gRPC Stub class
        method_name: gRPC method name
        response_model: Pydantic model class for automatic response parsing
        timeout: Timeout in seconds

    Returns:
        Decorator function

    Example:
        @classmethod
        @grpc_call("system-service", SystemServiceStub, "GetUser", response_model=UserVo)
        def get_by_id(cls, user_id: int):
            return system_pb2.GetUserRequest(user_id=user_id)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*wrapper_args, **wrapper_kwargs) -> Optional[Any]:
            try:
                # 1. Extract cls parameter (first parameter of class method)
                cls = wrapper_args[0]
                method_args = wrapper_args[1:]

                # 2. Get gRPC client
                client = cls._get_client()

                # 3. Create stub
                stub = stub_class(client.channel)

                # 4. Call original function to get request
                request = func(cls, *method_args, **wrapper_kwargs)

                # 5. Execute gRPC call
                grpc_method = getattr(stub, method_name)
                response = grpc_method(request, timeout=timeout)

                # 6. Handle response
                if hasattr(response, 'code') and response.code == 200:
                    logger.debug(f"{method_name} call successful")

                    # If response_model is specified, auto-convert
                    if response_model:
                        return _parse_response_with_model(response, response_model, method_name)
                    else:
                        # No model specified, return original response
                        return response
                else:
                    message = getattr(response, 'message', 'Unknown error')
                    logger.warning(f"{method_name} failed: {message}")
                    return None

            except grpc.RpcError as e:
                logger.error(f"gRPC call failed [{method_name}]: {e}")
                return None
            except Exception as e:
                logger.error(f"{method_name} exception: {e}")
                return None

        return wrapper

    return decorator


def _parse_response_with_model(response, response_model: Type[BaseModel], method_name: str) -> Any:
    """
    Parse response using Pydantic model

    Args:
        response: gRPC response object
        response_model: Pydantic model class or List[Model class]
        method_name: Method name (for logging)

    Returns:
        Pydantic model instance or model list
    """
    try:
        # Check if it's a List[Model] type
        origin = get_origin(response_model)
        if origin is list:
            # Get model type in list
            args = get_args(response_model)
            if args:
                item_model = args[0]
                # Find list field in response
                data_list = _extract_list_from_response(response, method_name)
                if data_list is not None:
                    return [item_model.model_validate(item, from_attributes=True) for item in data_list]
            return []
        else:
            # Single object
            data_obj = _extract_object_from_response(response, method_name)
            if data_obj is not None:
                return response_model.model_validate(data_obj, from_attributes=True)
            return None

    except Exception as e:
        logger.error(f"Failed to parse response [{method_name}]: {e}")
        return None


def _extract_object_from_response(response, method_name: str):
    """
    Extract single object from response

    Common field names: user, member, data, result, etc.
    """
    # Try common field names
    for field_name in ['user', 'member', 'data', 'result', 'item']:
        if hasattr(response, field_name):
            return getattr(response, field_name)

    # If not found, log warning and return response itself
    logger.warning(f"[{method_name}] No data field found, returning response itself")
    return response


def _extract_list_from_response(response, method_name: str):
    """
    Extract list from response

    Common field names: users, members, data, results, items, list, etc.
    """
    # Try common list field names
    for field_name in ['users', 'members', 'data', 'results', 'items', 'list']:
        if hasattr(response, field_name):
            return getattr(response, field_name)

    # If not found, log warning
    logger.warning(f"[{method_name}] No list field found")
    return None
