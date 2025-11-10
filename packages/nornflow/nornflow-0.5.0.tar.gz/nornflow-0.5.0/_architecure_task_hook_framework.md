## 1. Create the base hook class (`nornflow/hooks/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Any

from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult

from nornflow.vars.manager import NornFlowVariablesManager


class TaskHook(ABC):
    """Base class for all task hooks that modify task execution behavior."""
    
    hook_name: str  # Class variable identifying the hook type
    
    def pre_run(
        self,
        task_model: "TaskModel",
        host: Host,
        vars_mgr: NornFlowVariablesManager,
    ) -> bool:
        """
        Run before task execution. Return False to skip the task.
        
        Args:
            task_model: The TaskModel being executed
            host: The host being processed
            vars_mgr: The variables manager
            
        Returns:
            bool: False to skip the task, True to execute it
        """
        return True
        
    def post_run(
        self,
        task_model: "TaskModel",
        host: Host,
        result: AggregatedResult | None,
        vars_mgr: NornFlowVariablesManager,
    ) -> None:
        """
        Run after task execution.
        
        Args:
            task_model: The TaskModel that was executed
            host: The host being processed
            result: The task execution result
            vars_mgr: The variables manager
        """
        pass
```

## 2. Create hook registry (`nornflow/hooks/registry.py`)

```python
from typing import Dict, Type

from nornflow.hooks.base import TaskHook

# Registry mapping hook names to hook classes
HOOK_REGISTRY: Dict[str, Type[TaskHook]] = {}

def register_hook(hook_class: Type[TaskHook]) -> Type[TaskHook]:
    """
    Register a hook class in the global registry.
    
    Args:
        hook_class: The hook class to register
        
    Returns:
        The hook class (for decorator usage)
    """
    if not hasattr(hook_class, "hook_name") or not hook_class.hook_name:
        raise ValueError(f"Hook class {hook_class.__name__} must define a hook_name class attribute")
    
    HOOK_REGISTRY[hook_class.hook_name] = hook_class
    return hook_class
```

## 3. Implement the SetToHook (`nornflow/hooks/set_to_hook.py`)

```python
import logging

from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult

from nornflow.hooks.base import TaskHook
from nornflow.hooks.registry import register_hook
from nornflow.vars.manager import NornFlowVariablesManager

logger = logging.getLogger(__name__)

@register_hook
class SetToHook(TaskHook):
    """Hook for storing task results in a runtime variable."""
    
    hook_name = "set_to"
    
    def post_run(
        self, 
        task_model: "TaskModel",
        host: Host, 
        result: AggregatedResult | None,
        vars_mgr: NornFlowVariablesManager,
    ) -> None:
        """Store the task result in a runtime variable."""
        if task_model.set_to is None or result is None:
            return
            
        # Store the result under the variable name specified in set_to
        variable_name = task_model.set_to
        host_result = result.get(host.name)
        if host_result:
            vars_mgr.set_runtime_variable(variable_name, host_result, host.name)
            logger.info(
                f"Stored result from task '{task_model.name}' "
                f"into variable '{variable_name}' for host '{host.name}'"
            )
```

## 4. Create hook loader function (`nornflow/hooks/loader.py`)

```python
from typing import List

from nornflow.hooks.base import TaskHook
from nornflow.hooks.registry import HOOK_REGISTRY
from nornflow.models import TaskModel

def get_hooks_for_task(task_model: TaskModel) -> List[TaskHook]:
    """
    Get all hooks that should be applied to a task model.
    
    This function examines the task model for fields that match
    registered hook names and creates the appropriate hook instances.
    
    Args:
        task_model: The TaskModel to get hooks for
        
    Returns:
        List of instantiated hook objects
    """
    hooks = []
    
    # Check for each registered hook
    for hook_name, hook_class in HOOK_REGISTRY.items():
        # If task has an attribute with this hook's name and it's not None
        if hasattr(task_model, hook_name) and getattr(task_model, hook_name) is not None:
            hooks.append(hook_class())
    
    return hooks
```

## 5. Update the TaskModel run method (models.py)

```python
def run(
    self,
    nornir_manager: NornirManager,
    vars_manager: NornFlowVariablesManager,
    tasks_catalog: dict[str, Callable],
) -> AggregatedResult:
    """
    Execute the task using the provided NornirManager and tasks catalog.

    Args:
        nornir_manager: The NornirManager instance to use for execution.
        vars_manager: The NornFlowVariablesManager for variable management.
        tasks_catalog: Dictionary mapping task names to their function implementations.

    Returns:
        The results of the task execution.

    Raises:
        TaskError: If the task name is not found in the tasks catalog.
    """
    from nornflow.hooks.loader import get_hooks_for_task
    
    # Get the task function from the catalog
    task_func = tasks_catalog.get(self.name)
    if not task_func:
        raise TaskError(f"Task function for '{self.name}' not found in tasks catalog")

    # Prepare task arguments
    task_args = {} if self.args is None else dict(self.args)
    
    # Get hooks for this task
    hooks = get_hooks_for_task(self)
    result = None
    
    # Apply pre-run hooks for each host
    should_run = True
    for host_name, host in nornir_manager.nornir.inventory.hosts.items():
        for hook in hooks:
            if not hook.pre_run(self, host, vars_manager):
                should_run = False
                break
        if not should_run:
            break
    
    # Execute the task if all hooks allow it
    if should_run:
        result = nornir_manager.nornir.run(task=task_func, **task_args)
    
    # Apply post-run hooks for each host
    if result:
        for host_name, host in nornir_manager.nornir.inventory.hosts.items():
            for hook in hooks:
                hook.post_run(self, host, result, vars_manager)
    
    return result if result else AggregatedResult(nornir_manager.nornir.data.name)
```

## 6. Add package structure and initialization

Create __init__.py:
```python
"""
Task Hook Framework for NornFlow.

This package provides a structured system for extending task behavior.
"""

from nornflow.hooks.base import TaskHook
from nornflow.hooks.registry import register_hook
from nornflow.hooks.set_to_hook import SetToHook

__all__ = [
    "TaskHook",
    "register_hook",
    "SetToHook",
]
```

## 7. Example of a new hook: WhenHook

```python
@register_hook
class WhenHook(TaskHook):
    """Hook for conditional task execution based on a Jinja2 expression."""
    
    hook_name = "when"
    
    def pre_run(
        self,
        task_model: "TaskModel",
        host: Host,
        vars_mgr: NornFlowVariablesManager,
    ) -> bool:
        """
        Determine whether the task should run based on the condition.
        
        Args:
            task_model: The TaskModel being executed
            host: The host being processed
            vars_mgr: The variables manager
            
        Returns:
            bool: True if the condition evaluates to True, False otherwise
        """
        if not hasattr(task_model, "when") or not task_model.when:
            return True
            
        condition = task_model.when
        
        # Resolve the condition as a template string
        try:
            resolved = vars_mgr.resolve_string(condition, host.name)
            
            # Python expression evaluation - convert string "True"/"False" to bool
            if resolved.strip().lower() == "true":
                return True
            if resolved.strip().lower() == "false":
                return False
                
            # Try to evaluate as a Python expression
            result = bool(eval(resolved))
            return result
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
```
