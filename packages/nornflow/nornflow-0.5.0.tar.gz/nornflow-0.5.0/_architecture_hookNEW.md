# NornFlow Hooks Framework Design Vision

## Core Philosophy

The NornFlow Hooks Framework implements a sophisticated, enterprise-grade hook processing system designed for maximum performance at scale (100k+ hosts), complete thread safety in Nornir's multi-threaded environment, and extensibility without requiring schema changes to the core models.

## Key Design Patterns

### 1. **Flyweight Pattern for Memory Efficiency**
- Hook instances are created **ONCE** per unique (hook_class, value) combination
- Instances are cached globally and shared across all tasks and hosts
- For a workflow with 100k hosts × 10 tasks × 3 hooks, only ~3-30 hook instances are created (instead of 3 million)
- Memory savings of ~99.999% at scale

### 2. **Automatic Hook Discovery**
- Hook fields in YAML are automatically detected and transformed into hook configurations
- No need to explicitly define hooks in the model schema
- The framework introspects incoming data and matches field names against the hook registry
- Matched fields are removed from the main model data and moved to a `hooks` dictionary
- This allows unlimited extensibility without modifying core model schemas

**Important**: In YAML/dict input, some key:value pairs may exist that don't directly map to expected fields in the TaskModel. If these k:v pairs represent registered hooks, they are intercepted during model creation and moved into the `hooks` field of the RunnableModel class (of which TaskModel is a child). However, extra k:v pairs that do NOT map to any registered hook are left untouched. Since NornFlowBaseModel uses `model_config = {"extra": "forbid"}`, these unmapped extra fields will trigger a Pydantic validation error, ensuring strict input validation while allowing hook extensibility.

### 3. **Lazy Validation Strategy**
- Validation happens **ONCE** per task (not per host)
- Validation is task-specific (depends on task name, configuration, etc.)
- Validation is performed lazily on first hook access, not during model creation
- This prevents recursion issues and improves initialization performance
- Validation state is cached per task instance

## Architecture Components

### Hook Registry
- Central registry mapping hook names to hook classes
- Supports field name mappings for automatic discovery
- Thread-safe singleton pattern
- Allows dynamic registration of custom hooks

### Hook Base Classes
- **PreRunHook**: Executes before task execution, can filter hosts
- **PostRunHook**: Executes after task execution, processes results
- Both implement immutable state for thread safety
- Hooks store only their configuration value, no mutable state

### RunnableModel Integration
- `hooks` field stores discovered hook configurations as HashableDict
- `create()` method extracts hook fields before Pydantic validation
- Hook instances are loaded lazily via `get_pre_hooks()` and `get_post_hooks()`
- Global cache with thread-safe locking ensures single instance creation

## Performance Characteristics

- **Hook instantiation**: O(1) amortized - cached after first creation
- **Validation**: O(1) per task - happens once and cached
- **Memory usage**: O(unique_hooks) instead of O(tasks × hosts × hooks)
- **Thread overhead**: Minimal - only during first instance creation

## Thread Safety Guarantees

1. Hook instances are immutable after creation
2. Global cache uses locks only during first instance creation
3. No shared mutable state between threads
4. Each host execution is independent
5. Validation state tracked externally, not in hook instances

## Extensibility Model

1. New hooks can be added without modifying core models
2. Hooks self-register with the registry
3. Field names in YAML automatically map to hooks
4. Custom validation logic via `validate_*` methods
5. Hook behavior determined by immutable configuration value

## Workflow Example

When a YAML file contains:
```yaml
tasks:
  - name: echo
    output: print
    set_to: some_variable
```

The framework:
1. Detects `output` and `set_to` as hook fields via registry
2. Transforms them into hook configurations
3. Removes them from task fields (preventing validation errors)
4. Stores them in the `hooks` dictionary
5. Creates/retrieves cached hook instances on first access
6. Validates hooks once per task
7. Executes hooks for each host with shared instances

If the YAML contained an unknown field like `invalid_hook: value`, it would remain in the input and cause a validation error due to `{"extra": "forbid"}`, ensuring only valid hooks or expected fields are accepted.

## Key Benefits

- **Zero Memory Bloat**: Flyweight pattern ensures minimal memory usage
- **Perfect Thread Safety**: Immutable design prevents race conditions
- **Infinite Extensibility**: Add hooks without touching core models
- **Optimal Performance**: Caching and lazy loading minimize overhead
- **Clean Separation**: Hook logic separated from business logic
- **Automatic Discovery**: No manual hook configuration required

This design ensures NornFlow can scale to massive deployments while maintaining clean, extensible code and predictable performance characteristics.
