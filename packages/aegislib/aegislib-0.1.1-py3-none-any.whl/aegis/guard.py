"""Core guard decorator for tool protection."""

import functools
import inspect
from collections.abc import Callable
from typing import Any, TypeVar

from .decision import DecisionClient
from .errors import ForbiddenError
from .logging import print_allow, print_approval_needed, print_deny, print_sanitize
from .types import sanitize_map
from .util import signature_to_params

F = TypeVar("F", bound=Callable[..., Any])


def aegis_guard(
    client: DecisionClient,
    agent_id: str,
    tool_name: str | None = None,
) -> Callable[[F], F]:
    """Decorator to guard tool functions with Aegis policy decisions.

    Args:
        client: Configured DecisionClient instance
        agent_id: Agent identifier for policy evaluation
        tool_name: Tool name override (defaults to function.__name__)

    Returns:
        Decorator function

    Example:
        @aegis_guard(client, agent_id="ops-agent", tool_name="slack.post_message")
        def post_to_slack(channel: str, text: str):
            # Your tool logic here
            pass
    """

    def decorator(func: F) -> F:
        actual_tool_name = tool_name or func.__name__
        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return _guard_execution(
                func, client, agent_id, actual_tool_name, args, kwargs
            )

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = _guard_execution(
                func, client, agent_id, actual_tool_name, args, kwargs
            )
            # If result is a coroutine (from async func), await it
            if inspect.iscoroutine(result):  # pragma: no cover
                result = await result  # pragma: no cover
            return result

        return async_wrapper if is_async else sync_wrapper  # type: ignore

    return decorator


def _prepare_params(
    func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Prepare parameters from function call for decision request."""
    params = signature_to_params(func, args, kwargs)
    # Remove 'self' parameter if it exists (for method calls)
    if "self" in params:
        del params["self"]
    return params


def _handle_allow_effect(
    client: DecisionClient,
    tool_name: str,
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Handle allow decision effect."""
    print_allow(client.config, tool_name)
    result = func(*args, **kwargs)
    # If the function is async, we need to return the coroutine as-is
    # The caller (async_wrapper) will handle awaiting it
    return result


def _handle_deny_effect(client: DecisionClient, tool_name: str, decision: Any) -> None:
    """Handle deny decision effect."""
    reason = decision.final_decision.reason
    violations = decision.final_decision.violations
    print_deny(client.config, reason, violations)
    raise ForbiddenError(
        f"Tool '{tool_name}' blocked: {reason or 'Policy violation'} "
        f"due to violations: {str(violations)}"
    )


def _handle_sanitize_effect(
    client: DecisionClient,
    decision: Any,
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Handle sanitize decision effect."""
    sanitize_data = sanitize_map(decision)

    # Convert positional args to kwargs to avoid conflicts
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())

    # Build final kwargs, preferring sanitized values
    final_kwargs = {}
    for i, arg in enumerate[Any](args):
        if i < len(param_names):
            param_name = param_names[i]
            final_kwargs[param_name] = arg

    for k, v in kwargs.items():
        if k in param_names:
            final_kwargs[k] = v

    # Apply sanitization (this will override any positional args that were sanitized)
    final_kwargs.update(sanitize_data)

    print_sanitize(client.config, sanitize_data)
    return func(**final_kwargs)


def _handle_approval_needed_effect(
    client: DecisionClient, tool_name: str, decision: Any
) -> None:
    """Handle approval_needed decision effect."""
    reason = decision.final_decision.reason
    print_approval_needed(client.config, reason)
    raise ForbiddenError(
        f"Tool '{tool_name}' requires approval: "
        f"{reason or 'Manual approval needed'}"
    )


def _guard_execution(
    func: Callable[..., Any],
    client: DecisionClient,
    agent_id: str,
    tool_name: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Execute guarded function call with policy decision."""

    # Prepare parameters
    params = _prepare_params(func, args, kwargs)

    # Request decision
    try:
        decision = client.decide(agent_id, tool_name, params)
    except Exception as e:
        # If decision request fails, deny by default for security
        print_deny(client.config, f"Decision request failed: {e}", None)
        raise ForbiddenError(f"Policy decision unavailable: {e}") from e

    # Apply decision
    effect = decision.final_decision.effect

    if effect == "allow":
        return _handle_allow_effect(client, tool_name, func, args, kwargs)
    elif effect == "deny":
        _handle_deny_effect(client, tool_name, decision)
    elif effect == "sanitize":
        return _handle_sanitize_effect(client, decision, func, args, kwargs)
    elif effect == "approval_needed":
        _handle_approval_needed_effect(client, tool_name, decision)

    # Unknown effect - deny for safety (for future API extensions)
    effect_str = str(effect)
    print_deny(client.config, f"Unknown decision effect: {effect_str}", None)
    raise ForbiddenError(f"Unknown policy decision: {effect_str}")
