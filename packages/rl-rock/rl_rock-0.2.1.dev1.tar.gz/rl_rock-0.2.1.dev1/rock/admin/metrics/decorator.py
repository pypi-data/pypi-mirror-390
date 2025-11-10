import asyncio
import functools
import logging
import time
from collections.abc import Callable

from rock.admin.core.redis_key import alive_sandbox_key
from rock.admin.metrics.monitor import MetricsMonitor
from rock.utils.providers import RedisProvider


def monitor_sandbox_operation(
    func=None,
    *,
    operation_name: str = None,
    extract_sandbox_id: Callable = None,
    sandbox_id_position: int = None,
    sandbox_id_param: str = None,
    metric_prefix: str = "request",
):
    """Method decorator: Monitor specific methods"""

    def decorator(f):
        if asyncio.iscoroutinefunction(f):

            @functools.wraps(f)
            async def wrapper(self, *args, **kwargs):
                # Get metrics_monitor from self
                metrics_monitor = getattr(self, "metrics_monitor", None)

                if not metrics_monitor:
                    return await f(self, *args, **kwargs)

                # Determine operation name
                op_name = operation_name or f.__name__

                # Extract sandbox_id
                sandbox_id = "unknown"
                if extract_sandbox_id:
                    try:
                        sandbox_id = extract_sandbox_id(self, *args, **kwargs)
                    except Exception as e:
                        logging.warning(f"Failed to extract sandbox_id: {e}")
                elif sandbox_id_param and sandbox_id_param in kwargs:
                    sandbox_id = kwargs[sandbox_id_param]
                elif sandbox_id_position is not None and len(args) >= sandbox_id_position:
                    sandbox_id = str(args[sandbox_id_position - 1])  # Subtract 1 because self has been removed
                elif len(args) > 0:
                    # Default strategy: Extract from the first parameter (because self has been removed)
                    param = args[0]
                    if isinstance(param, str):
                        sandbox_id = param
                    elif hasattr(param, "container_name"):
                        sandbox_id = param.container_name
                    elif hasattr(param, "sandbox_id"):
                        sandbox_id = param.sandbox_id

                # Build attributes
                attributes = {"operation": op_name, "sandbox_id": sandbox_id, "method": f.__name__}

                redis_provider: RedisProvider = getattr(self, "_redis_provider", None)
                if redis_provider and sandbox_id != "unknown":
                    user_info = await redis_provider.json_get(alive_sandbox_key(sandbox_id), "$")
                    if user_info is not None and len(user_info) > 0:
                        user_id = user_info[0].get("user_id")
                        experiment_id = user_info[0].get("experiment_id")
                        attributes["user_id"] = user_id if user_id is not None else "default"
                        attributes["experiment_id"] = experiment_id if experiment_id is not None else "default"
                    else:
                        attributes["user_id"] = "default"
                        attributes["experiment_id"] = "default"
                else:
                    attributes["user_id"] = "default"
                    attributes["experiment_id"] = "default"

                start_time = time.perf_counter()

                try:
                    result = await f(self, *args, **kwargs)
                    if hasattr(result, "sandbox_id"):
                        result_sandbox_id = result.sandbox_id
                        if result_sandbox_id != attributes.get("sandbox_id"):
                            attributes["sandbox_id"] = result_sandbox_id
                    # Record success
                    metrics_monitor.record_counter_by_name(f"{metric_prefix}.success", 1, attributes)
                    return result
                except Exception as e:
                    # Record failure
                    error_attrs = {**attributes, "error_type": type(e).__name__}
                    metrics_monitor.record_counter_by_name(f"{metric_prefix}.failure", 1, error_attrs)
                    raise
                finally:
                    # Record response time and total requests
                    rt_ms = (time.perf_counter() - start_time) * 1000
                    metrics_monitor.record_gauge_by_name(f"{metric_prefix}.rt", rt_ms, attributes)
                    metrics_monitor.record_counter_by_name(f"{metric_prefix}.total", 1, attributes)

            return wrapper
        else:

            @functools.wraps(f)
            def wrapper(self, *args, **kwargs):
                # Get metrics_monitor from self
                metrics_monitor: MetricsMonitor = getattr(self, "metrics_monitor", None)

                if not metrics_monitor:
                    return f(self, *args, **kwargs)

                # Determine operation name
                op_name = operation_name or f.__name__

                # Extract sandbox_id
                sandbox_id = "unknown"

                if extract_sandbox_id:
                    try:
                        sandbox_id = extract_sandbox_id(self, *args, **kwargs)
                    except Exception as e:
                        logging.warning(f"Failed to extract sandbox_id: {e}")
                elif sandbox_id_param and sandbox_id_param in kwargs:
                    sandbox_id = kwargs[sandbox_id_param]

                attributes = {
                    "operation": op_name,
                    "sandbox_id": "unknown" if sandbox_id is None else sandbox_id,
                    "method": f.__name__,
                }

                redis_provider: RedisProvider = getattr(self, "_redis_provider", None)
                if redis_provider and sandbox_id != "unknown":
                    user_info = asyncio.run(redis_provider.json_get(alive_sandbox_key(sandbox_id), "$"))
                    if user_info is not None and len(user_info) > 0:
                        user_id = user_info[0].get("user_id")
                        experiment_id = user_info[0].get("experiment_id")
                        attributes["user_id"] = user_id if user_id is not None else "default"
                        attributes["experiment_id"] = experiment_id if experiment_id is not None else "default"
                    else:
                        attributes["user_id"] = "default"
                        attributes["experiment_id"] = "default"
                else:
                    attributes["user_id"] = "default"
                    attributes["experiment_id"] = "default"

                start_time = time.perf_counter()

                try:
                    result = f(self, *args, **kwargs)
                    if hasattr(result, "sandbox_id"):
                        result_sandbox_id = result.sandbox_id
                    if result_sandbox_id != attributes.get("sandbox_id"):
                        attributes["sandbox_id"] = result_sandbox_id
                    # Record success
                    metrics_monitor.record_counter_by_name(f"{metric_prefix}.success", 1, attributes)
                    return result
                except Exception as e:
                    # Record failure
                    error_attrs = {**attributes, "error_type": type(e).__name__}
                    metrics_monitor.record_counter_by_name(f"{metric_prefix}.failure", 1, error_attrs)
                    raise
                finally:
                    # Record response time and total requests
                    rt_ms = (time.perf_counter() - start_time) * 1000
                    metrics_monitor.record_gauge_by_name(f"{metric_prefix}.rt", rt_ms, attributes)
                    metrics_monitor.record_counter_by_name(f"{metric_prefix}.total", 1, attributes)

            return wrapper

    if func is not None:
        return decorator(func)
    return decorator
