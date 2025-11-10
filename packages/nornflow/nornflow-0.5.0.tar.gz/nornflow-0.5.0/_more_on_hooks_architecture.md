# Comprehensive Technical Guide to NornFlow's Hooks Framework

## 1. Core Architecture and Design Patterns

NornFlow's hook system is a sophisticated framework designed for maximum performance at scale, thread safety, and memory efficiency while maintaining extensibility. Let's explore the technical underpinnings of this system.

### 1.1 Design Patterns Used

#### Flyweight Pattern
The framework implements the Flyweight pattern to minimize memory usage:
- Hook instances are created ONCE per unique (hook_class, value) combination
- These instances are cached globally and shared across all tasks and hosts
- For 100k hosts × 10 tasks × 3 hooks = only ~3-30 hook instances (vs. 3 million)
- Memory usage is reduced by ~99.999%

```python
def _get_or_create_hook_instance(self, hook_class: type[PreRunHook] | type[PostRunHook], hook_value: Any) -> PreRunHook | PostRunHook:
    cache_key = (hook_class, hook_value)
    
    # Fast path: check if instance exists without locking
    if cache_key in _HOOK_INSTANCE_CACHE:
        return _HOOK_INSTANCE_CACHE[cache_key]
    
    # Slow path: create instance with lock for thread safety
    with _HOOK_CACHE_LOCK:
        # Double-check after acquiring lock (another thread may have created it)
        if cache_key in _HOOK_INSTANCE_CACHE:
            return _HOOK_INSTANCE_CACHE[cache_key]
        
        # Create new instance
        hook_instance = hook_class(hook_value)
        _HOOK_INSTANCE_CACHE[cache_key] = hook_instance
        return hook_instance
```

#### Automatic Discovery
- Hooks are automatically discovered from fields in YAML configuration
- No explicit mapping or registration needed in workflow definitions

#### Lazy Loading and Caching
- Hook instances are loaded lazily on first access
- Validation happens only once per task

## 2. Core Components of the Hook System

The hook system is built around three critical components that work together to provide its functionality and performance characteristics:

### 2.1 HOOK_REGISTRY

**What it is**: A global dictionary in registry.py that maps hook names to their corresponding hook classes.

**Purpose**: 
- Serves as the central registration point for all available hooks in the system
- Enables automatic discovery of hooks in YAML/dict configuration
- Allows the system to look up hook classes by their names during task creation
- Makes hooks extensible without modifying core code

**How it works**:
```python
# In hooks/registry.py
HOOK_REGISTRY: dict[str, Type[Hook]] = {}

def register_hook(hook_class: Type[Hook]) -> Type[Hook]:
    """Register a hook class in the global registry."""
    HOOK_REGISTRY[hook_class.hook_name] = hook_class
    return hook_class

@register_hook
class SetToHook(PostRunHook):
    hook_name = "set_to"  # This becomes the key in HOOK_REGISTRY
```

When the system processes a field like `set_to: some_var` in YAML, it consults `HOOK_REGISTRY` to determine if "set_to" corresponds to a registered hook class.

### 2.2 _HOOK_INSTANCE_CACHE

**What it is**: A global cache in runnable.py that stores actual hook instances based on their class and configuration value.

**Purpose**:
- Implements the Flyweight pattern for extreme memory efficiency
- Ensures identical hook configurations share a single instance across all tasks and hosts
- Reduces memory usage by up to 99.999% in large-scale scenarios
- Avoids redundant hook creation and validation

**Technical details**:
```python
# In models/runnable.py
_HOOK_INSTANCE_CACHE: dict[tuple[type, str | None], PreRunHook | PostRunHook] = {}
```

The cache's key is a tuple of `(hook_class, hook_value)`, which uniquely identifies a specific hook configuration. For example, `(SetToHook, "result_var")` maps to a single instance that will be shared across all tasks using that same configuration.

Without this cache, a deployment with 100,000 hosts running 10 tasks with 3 hooks each would create 3 million hook instances. With the cache, it might create as few as 3-30 instances total (depending on unique configurations).

### 2.3 _HOOK_CACHE_LOCK

**What it is**: A thread lock in runnable.py that ensures thread-safe creation of hook instances.

**Purpose**:
- Prevents race conditions during hook instance creation in multi-threaded environments
- Ensures only one thread creates a new hook instance for a given configuration
- Implements double-checked locking pattern for maximum performance
- Minimizes lock contention by only locking during new instance creation

**Technical implementation**:
```python
# In models/runnable.py
_HOOK_CACHE_LOCK = threading.Lock()

def _get_or_create_hook_instance(self, hook_class, hook_value):
    cache_key = (hook_class, hook_value)
    
    # Fast path: no locking for cache hits (most common case)
    if cache_key in _HOOK_INSTANCE_CACHE:
        return _HOOK_INSTANCE_CACHE[cache_key]
    
    # Slow path: lock only when creating a new instance
    with _HOOK_CACHE_LOCK:
        # Double-check after acquiring lock
        if cache_key in _HOOK_INSTANCE_CACHE:
            return _HOOK_INSTANCE_CACHE[cache_key]
        
        # Create and cache new instance
        hook_instance = hook_class(hook_value)
        _HOOK_INSTANCE_CACHE[cache_key] = hook_instance
        return hook_instance
```

This sophisticated locking pattern ensures that hook creation is both thread-safe and high-performance:
- No locking for existing instances (≈99% of calls)
- Lock only briefly during new instance creation
- Double-checking prevents duplicate creation if another thread created the instance while waiting for lock

### 2.4 Interaction Between Components

These three components work together in a precise sequence:

1. **Discovery Phase**: `RunnableModel.create()` consults `HOOK_REGISTRY` to identify hook fields in input data
2. **Instantiation Phase**: `_get_or_create_hook_instance()` checks `_HOOK_INSTANCE_CACHE` for existing instances
3. **Creation Phase**: If no instance exists, the method acquires `_HOOK_CACHE_LOCK` and creates a new one
4. **Execution Phase**: The hook instance is shared across all hosts and tasks with the same configuration

## 3. Hook Registration vs. Hook Loading

These are two distinct processes that occur at different times in the hook lifecycle:

### 3.1 Hook Registration

**Registration** happens at import time through the `@register_hook` decorator:

```python
def register_hook(hook_class: Type[object]) -> Type[object]:
    """Register a hook class in the global registry."""
    if not hasattr(hook_class, "hook_name") or not hook_class.hook_name:
        raise HookRegistrationError(f"Hook class {hook_class.__name__} must define a hook_name class attribute")
    
    HOOK_REGISTRY[hook_class.hook_name] = hook_class
    return hook_class
```

When a hook class is decorated with `@register_hook`, it adds the class to the global `HOOK_REGISTRY` dictionary, mapping the hook's name to its class. This allows the system to look up hook classes by name later.

Example:
```python
@register_hook
class SetToHook(PostRunHook):
    hook_name = "set_to"
    # ...
```

### 3.2 Hook Loading

**Loading** happens at runtime in multiple phases:

1. **Discovery Phase (During `create()`)**:
   ```python
   # In RunnableModel.create()
   for key, value in dict_args.items():
       # Skip if this is an actual model field
       if key in model_fields:
           continue
           
       # Check if this field matches a registered hook
       if key in HOOK_REGISTRY:
           hooks_config[key] = value
           fields_to_remove.append(key)
   ```
   
   This code extracts fields matching hook names from the input dictionary and moves them to the `hooks` configuration.

2. **Instance Creation Phase (During `_load_hooks_by_type()` / `get_pre_hooks()` / `get_post_hooks()`)**:
   ```python
   def _load_hooks_by_type(self, hook_base_class: type[PreRunHook] | type[PostRunHook]) -> list[PreRunHook] | list[PostRunHook]:
       if not self.hooks:
           return []
       
       hooks = []
       for hook_name, hook_value in self.hooks.items():
           hook_class = HOOK_REGISTRY.get(hook_name)
           if hook_class and issubclass(hook_class, hook_base_class):
               hook_instance = self._get_or_create_hook_instance(hook_class, hook_value)
               hooks.append(hook_instance)
       
       return hooks
   ```

   Here, actual hook objects are instantiated based on the stored configuration.

## 4. The Relationship Between HOOK_REGISTRY and RunnableModel

`HOOK_REGISTRY` and `RunnableModel` work together in a component-based architecture:

1. **HOOK_REGISTRY**:
   - Global registry mapping hook names to hook classes
   - Populated at import time via `@register_hook`
   - Allows looking up hook classes by name
   - Independent of any specific model instance

2. **RunnableModel**:
   - Consumes the registry to discover hooks in configuration
   - Extracts hook fields from input and moves them to `hooks`
   - Creates and manages hook instances
   - Orchestrates hook execution during the task lifecycle

Their relationship is a consumer/provider pattern:
- `HOOK_REGISTRY` provides the mapping from names to classes
- `RunnableModel` consumes this mapping to create and manage instances

## 5. Per-Host vs. Per-Task Hook Execution

This is a crucial distinction in understanding how hooks work. The framework now abstracts execution mode control into the base `Hook` class, allowing hooks to run either once per host (default) or once per task.

### 5.1 Current Implementation

All hooks run once per host by default, but can be configured to run once per task:

```python
class SetPrintOutputHook(PreRunHook):
    hook_name = "output"
    run_once_per_task = True  # Configures per-task execution
    
    def _run_hook(self, task_model, host, vars_mgr):
        # This runs only once per task, on the first host
        if self.value is not None:
            task_model.args['print_output'] = self.value
        return True
```

The base `Hook` class handles the execution mode logic:

```python
def _execute_hook(self, task_model, default_result, *args, **kwargs):
    if self.run_once_per_task:
        if self._is_first_execution(task_model):
            return self._run_hook(task_model, *args, **kwargs)
        return default_result
    else:
        return self._run_hook(task_model, *args, **kwargs)
```

This ensures that:
- **Per-host hooks** (default): Execute `_run_hook` for every host
- **Per-task hooks** (`run_once_per_task = True`): Execute `_run_hook` only once per task, on the first eligible host

### 5.2 The Challenge with SetPrintOutputHook

Looking at `SetPrintOutputHook`:

```python
def _run_hook(self, task_model, host, vars_mgr) -> bool:
    if self.value is not None:
        # Set print_output in the task model's args
        # NOTE: This modifies shared state - acceptable for this use case
        if task_model.args is None:
            task_model.args = {}
        task_model.args['print_output'] = self.value
        logger.info(f"Set print_output to '{self.value}' for task '{task_model.name}' on host '{host.name}'")
    return True
```

This hook modifies the shared `task_model.args` object, but with `run_once_per_task = True`, it runs only once per task. This prevents redundant operations and thread safety issues.

### 5.3 Benefits of the Abstracted Execution Control

The abstracted `_execute_hook` method in the base `Hook` class provides several advantages:

1. **Consistency**: All hooks use the same execution mode logic
2. **Thread Safety**: Execution tracking uses `WeakKeyDictionary` and locks
3. **Extensibility**: New execution modes can be added without changing concrete hooks
4. **Performance**: Minimizes redundant executions for task-level operations

## 6. Adding New Hooks

To create a new hook in NornFlow:

### 6.1 Create the Hook Class

```python
from nornflow.hooks.base import PostRunHook
from nornflow.hooks.registry import register_hook

@register_hook
class MyCustomHook(PostRunHook):
    """Custom hook for special processing."""
    
    hook_name = "my_custom"  # This is the field name in YAML
    
    # Optional: Configure execution mode
    run_once_per_task = False  # Default is per-host
    
    def _run_hook(self, task_model, host, result, vars_mgr) -> None:
        """Execute custom post-task logic."""
        # Your hook implementation here
        if self.value is not None:
            # Do something with self.value
            logger.info(f"MyCustomHook executed for {host.name} with value {self.value}")
    
    def validate_task_compatibility(self, task_model) -> tuple[bool, str]:
        """Optional validation logic."""
        if task_model.name == "incompatible_task":
            return (False, "MyCustomHook is not compatible with this task")
        return (True, "")
```

### 6.2 Register the Hook

The `@register_hook` decorator adds your hook to the registry. Make sure your module is imported so the registration happens.

### 6.3 Use the Hook in Workflow YAML

```yaml
workflow:
  name: example_workflow
  tasks:
    - name: some_task
      args:
        param: value
      my_custom: custom_value  # This activates your hook
```

## 7. Thread Safety Considerations

The hooks framework is designed to be thread-safe through several mechanisms:

1. **Immutable Hook State**: Hook instances store only their configuration value
2. **Global Instance Cache**: Protected by thread locks during creation
3. **External Validation State**: Validation results aren't stored in hooks
4. **Thread-Safe Execution Tracking**: Uses `WeakKeyDictionary` and locks for per-task execution
5. **Abstracted Execution Control**: Base class handles thread-safe execution mode logic

However, developers need to be careful when:
1. Modifying shared state like `task_model.args`
2. Interacting with external systems
3. Maintaining per-task state that isn't thread-safe

## 8. Optimization Tips

For optimal hook performance:

1. **Minimize Hook Value Variations**: Fewer unique values means better cache reuse
2. **Keep Validation Light**: Validation happens once per task, but should be fast
3. **Choose Execution Mode Wisely**: Use `run_once_per_task = True` for task-level operations
4. **Avoid Shared Mutable State**: When possible, use thread-local or per-host state

## 9. Lifecycle of a Hook

To fully understand hooks, let's trace the complete lifecycle:

1. **Registration**: `@register_hook` adds the hook class to `HOOK_REGISTRY`
2. **Discovery**: `RunnableModel.create()` finds hook fields in input data
3. **Configuration**: Hook fields are moved to the `hooks` dictionary
4. **Instantiation**: Hook instances created by `_get_or_create_hook_instance()`
5. **Validation**: `_validate_all_hooks()` verifies hook configuration
6. **Execution**: Hook's `run()` method called, which delegates to `_execute_hook()` for mode control
7. **Reuse**: Same hook instance reused across hosts and tasks

This ensures maximum efficiency and minimal overhead in the hooks system.

## 10. Conclusion

NornFlow's hook system is a sophisticated, high-performance framework built on solid design patterns. By understanding the abstracted execution mode control, the per-host vs. per-task execution model, and the thread safety considerations, developers can leverage this system to create powerful, efficient extensions to task behavior.

For task-level operations, set `run_once_per_task = True` in your hook class and implement `_run_hook` accordingly. The base class will handle the rest, ensuring operations happen only once per task while maintaining thread safety and performance. This abstraction makes the framework both powerful and easy to extend.

