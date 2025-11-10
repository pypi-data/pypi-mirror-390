## 1. Architecture for `refactor/set-task-processing`

The goal is to move special-case processing out of the `NornFlowVariableProcessor` and into the `set` task itself, making the variable processor more consistent and the `set` task more self-contained.

### Current Architecture Problems

- Special-case handling in `task_instance_started()`: `if task.name == "set":`
- `_handle_set_task()` method exists only for this specific task
- `set` task function only reports what was done, doesn't actually do the setting
- Violates separation of concerns

### Proposed Architecture

1. Remove special handling from `NornFlowVariableProcessor`
2. Enhance the `set` task to handle its own variable processing
3. Use utility functions to access the variable manager from the task

### Implementation Steps

# Set Task Refactoring

## 1. Create a utility function to access the variable manager

Add to `nornflow/builtins/utils.py`:
```python
def get_task_vars_manager(task: Task) -> NornFlowVariablesManager:
    """
    Find the NornFlowVariableProcessor in the task's processor chain and return its vars_manager.
    
    Args:
        task: The Nornir Task object.
    
    Returns:
        The vars_manager instance if found, None otherwise.
    """
    for processor in task.nornir.processors:
        if hasattr(processor, "vars_manager"):
            return processor.vars_manager
    return None
```

## 2. Update the `set` task in tasks.py

```python
def set(task: Task, **kwargs) -> Result:
    """
    NornFlow built-in task to set runtime variables for the current device.
    
    This task allows you to define new NornFlow runtime variables or update existing ones
    for the specific device the task is currently operating on.
    
    Args:
        task: The Nornir Task object.
        **kwargs: Key-value pairs representing variables to set.
                  
    Returns:
        Result: A Nornir Result object with a detailed report.
    """
    vars_manager = get_task_vars_manager(task)
    
    if not vars_manager:
        return Result(
            host=task.host,
            failed=True,
            result="Could not find NornFlowVariableProcessor. Unable to set variables."
        )
    
    # Process and set each variable
    for key, value in kwargs.items():
        # Store the variable in the runtime namespace for the current host
        vars_manager.set_runtime_variable(key, value, task.host.name)
    
    # Generate a readable report of what was set
    report = build_set_task_report(task, kwargs)
    return Result(host=task.host, result=report)
```

## 3. Remove special-case handling from `NornFlowVariableProcessor`

Edit processors.py:

```python
def task_instance_started(self, task: Task, host: Host) -> None:
    """
    This method sets the current host context for variable resolution
    and processes Jinja2 templates in task parameters.
    """
    try:
        # Set the current host name in the proxy to enable {{ host. }} variable access
        self.vars_manager.nornir_host_proxy.current_host_name = host.name
        logger.debug(f"Set current_host_name to '{host.name}' for task '{task.name}'.")

        # Process task parameters for all tasks uniformly
        if task.params:  # Ensure params exist
            processed_params = self.vars_manager.resolve_data(task.params, host.name)
            task.params = processed_params
            logger.debug(f"Processed task.params for task '{task.name}' on host '{host.name}'")

    except Exception:
        logger.exception(f"Error processing variables for task '{task.name}' on host '{host.name}'")
        raise
```

## 4. Remove the `_handle_set_task` method

Delete this method from `NornFlowVariableProcessor` as it's no longer needed.
