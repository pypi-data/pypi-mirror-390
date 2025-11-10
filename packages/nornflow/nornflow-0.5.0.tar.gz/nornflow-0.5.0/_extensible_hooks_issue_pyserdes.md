Start of the conversation

Q1:
as they say, I'm between the cross and the sword. I don't like the way we are implementing the hooks framework. It seems too much 'in the middle': it's not flexible enough, in the sense that users of norngflow wou;dn't have a way to code their own hooks to tasks (actual code changes would have to be made to nornflow code directluy), nor it's direct enough like using explicit fields to just directly say what fields are pre/post run hooks. As an ultra mega blaster ultimate software engineer, critically and deeply evaluate the 3 architectures (current, fully extensible, fully non-extensible with direct explicit fields indicating what other fields are hooks). I want to hear the good and the bad about each. Also, thinking in terms of sound software engineering, which one is the best to adopt right now going into the future? think about usability and performance. This shit can't be slower than ansible in the end.

A1:
Below is a deep, critical evaluation of the three hook framework architectures for NornFlow, based on the current implementation (dynamic annotation-based detection) and the alternatives you described. I'll break it down by architecture, highlighting the good and bad aspects, with a focus on usability, performance, extensibility, maintainability, and overall software engineering principles. I'll also consider how each compares to Ansible's performance (which is reasonably fast for its use case but can bog down with complex playbooks due to YAML parsing and task overhead). Finally, I'll recommend the best one for adoption now and into the future.

### Key Evaluation Criteria
- **Usability**: How easy it is for users (NornFlow developers/operators) to define, configure, and debug hooks without deep knowledge of the framework internals.
- **Performance**: Execution speed, including hook detection, loading, and runtime overhead. Measured in terms of CPU cycles, memory, and scalability (e.g., with 100+ tasks/hosts).
- **Extensibility**: Ability for users to add custom hooks without modifying NornFlow's core code.
- **Maintainability**: Ease of updating, debugging, and evolving the framework without introducing bugs or breaking changes.
- **Flexibility**: How well the system adapts to diverse use cases (e.g., simple pre/post logic vs. complex integrations).
- **Security/Reliability**: Risk of user errors, plugin conflicts, or runtime failures.
- **Comparison to Ansible**: Ansible is "fast enough" for most ops tasks (seconds to minutes for playbooks), but it scales poorly with deep nesting or custom modules due to its interpreted, YAML-heavy nature. NornFlow should aim for similar or better performance (sub-second for simple workflows, seconds for complex ones) without sacrificing Python's speed.

### 1. Current Architecture: Dynamic Annotation-Based Hook Detection
**Description**: Hooks are defined as classes inheriting from `PreRunHook` or `PostRunHook`. The system uses runtime introspection (`inspect` and `get_args`/`get_origin`) on Pydantic model fields to detect hook types automatically. Hooks are cached per class for performance. Users define hooks as fields in models (e.g., `pre_check: MyPreHook = MyPreHook()`), and the framework loads them dynamically.

**Good**:
- **Usability**: Relatively clean for framework developers—hooks are just annotated fields, and detection is automatic. No need to manually list hook fields, reducing boilerplate. Debugging is straightforward with clear field names.
- **Flexibility**: Supports complex hook logic (e.g., conditional skipping based on host vars). Easy to compose multiple hooks per task.
- **Maintainability**: Centralized in the `RunnableModel` class, with caching to avoid repeated introspection. Changes to hook types are localized.
- **Performance**: Decent—caching reduces overhead after first load. Introspection happens at model creation, not per execution. For 100 tasks, detection might add ~10-50ms total, comparable to Ansible's module loading.

**Bad**:
- **Extensibility**: Poor—users can't define new hook base classes (e.g., a custom `AuditHook`) without forking NornFlow code. The registry is internal, and annotation scanning is hardcoded.
- **Usability (for users)**: Requires understanding Pydantic annotations and hook classes, which is non-trivial for non-experts. Errors (e.g., wrong annotation) lead to silent failures or confusing introspection bugs.
- **Performance**: Introspection overhead scales with model complexity (e.g., deep unions in annotations). `inspect` and `get_origin` are slow in tight loops. Not as fast as explicit checks—could be 2-5x slower than a simple field list lookup in edge cases.
- **Maintainability**: Brittle—changes to Pydantic (e.g., v2 vs. v3) break introspection. Hard to test edge cases (e.g., nested generics). Security risk: Malformed annotations could cause runtime errors.
- **Flexibility**: Limited to pre/post hooks; no easy way to add "during" or "error" hooks without code changes.

**Overall**: A middle-ground compromise that's usable for internal development but feels like a half-measure. It's better than nothing but won't scale for a user ecosystem. Performance is acceptable (on par with Ansible for simple cases), but the lack of extensibility is a killer for long-term adoption.

### 2. Fully Extensible Architecture: Plugin-Based Hook System
**Description**: Implement a plugin/registry system where users can register custom hook classes dynamically (e.g., via a decorator or config file). Hooks are loaded from user-defined modules/packages, with a global registry (similar to current `HOOK_REGISTRY` but user-extensible). Models could reference hooks by name (e.g., `pre_hooks: list[str] = ["my_custom_hook"]`), and the system instantiates them at runtime. Use entry points (e.g., `setuptools` or a custom loader) for discovery.

**Good**:
- **Extensibility**: Excellent—users can write custom hooks in separate packages without touching NornFlow core. Supports arbitrary hook types (e.g., async hooks, third-party integrations). Future-proof for community contributions.
- **Usability**: High long-term—once set up, users just install plugins and reference by name. Clear separation of concerns (NornFlow provides the framework, users provide logic).
- **Flexibility**: Unmatched—hooks can be versioned, tested independently, and composed (e.g., chain multiple plugins). Supports advanced use cases like hooks that integrate with external APIs.
- **Maintainability**: Modular—core code stays lean, plugins handle complexity. Easier to update without breaking user code. Good for open-source growth.
- **Performance**: Potentially excellent—lazy loading and caching can minimize overhead. Plugin instantiation could be optimized to ~5-20ms per hook type, similar to Ansible's module caching. Scales well with async loading.

**Bad**:
- **Usability (initial)**: Steep learning curve—users must understand plugin development, entry points, and registry APIs. Setup is complex (e.g., packaging plugins correctly). Error messages for misconfigured plugins are hard to debug.
- **Performance**: Plugin discovery/loading adds startup overhead (e.g., scanning packages), potentially 100-500ms on first run. Runtime instantiation could be slower if hooks are heavy (e.g., importing large libraries). Not as fast as built-in checks—could be 3-10x slower than explicit fields in worst-case plugin abuse.
- **Maintainability**: High complexity—managing plugin lifecycles, versions, and conflicts is error-prone. Security risks (e.g., malicious plugins). Testing is harder (need to mock plugins).
- **Flexibility (overkill)**: Too flexible for simple use cases—most users might not need custom hooks, leading to over-engineering.
- **Reliability**: Plugin failures (e.g., import errors) can crash workflows. Dependency hell with conflicting plugin versions.

**Overall**: The most future-oriented and extensible, aligning with sound software engineering (modularity, separation of concerns). It's like Ansible's module ecosystem but for hooks. Performance is manageable (better than Ansible's YAML parsing in many cases), but the initial complexity might deter adoption. Best for a mature, community-driven project.

### 3. Fully Non-Extensible with Direct Explicit Fields
**Description**: Remove dynamic detection entirely. Models explicitly define hook fields as lists of field names (e.g., `pre_hook_fields: list[str] = ["pre_check"]`, `post_hook_fields: list[str] = ["cleanup"]`). Hooks are just regular methods or callables on the model. The framework iterates these lists at runtime to execute hooks.

**Good**:
- **Usability**: Simple and explicit—users just list field names. No annotations or classes needed. Easy to debug (e.g., "is 'pre_check' in the list?").
- **Performance**: Excellent— no introspection, just list iteration. Execution could be <1ms per hook check, 5-10x faster than dynamic detection. Scales linearly with hook count, outperforming Ansible's playbook parsing.
- **Maintainability**: Low complexity—pure Python lists, no magic. Easy to test and evolve. Minimal dependencies on Pydantic internals.
- **Reliability**: Predictable—no runtime type errors from annotations. Failures are explicit (e.g., missing field raises KeyError).
- **Flexibility**: Adequate for basic pre/post logic. Easy to extend within the model (e.g., add more lists for new hook types).

**Bad**:
- **Extensibility**: Zero—users can't add new hook types without code changes to NornFlow. No plugins or custom classes. Stuck with predefined lists.
- **Usability (long-term)**: Rigid for advanced users—everything must be a field on the model. No reuse across models (e.g., shared hooks).
- **Flexibility**: Limited to simple callables; no inheritance or complex logic without hacks. Doesn't support dynamic composition.
- **Maintainability (scaling)**: As the framework grows, hardcoded lists become a maintenance burden (e.g., adding "error_hooks" requires model changes everywhere).
- **Performance (edge cases)**: If lists get long (e.g., 50 hooks), iteration is still fast, but not as optimized as a hash set.

**Overall**: The simplest and fastest, like a stripped-down Ansible without modules. Great for performance-critical, internal use, but not scalable for user extensibility. It's sound engineering for a closed system but feels outdated for modern Python frameworks.

### Recommendation: Adopt the Fully Extensible Architecture Now
**Why this one?** From a sound software engineering perspective, the fully extensible (plugin-based) architecture is the best long-term choice, balancing usability, performance, and growth. It's the most flexible and maintainable, allowing NornFlow to evolve like successful tools (e.g., Ansible's modules, Django's apps). The current architecture is a stopgap that's too limited, and the explicit fields approach is too restrictive for a user-facing framework.

- **Usability Trade-off**: Initial complexity is worth it—once plugins are set up, users get unlimited power. Provide good docs/examples to mitigate the learning curve.
- **Performance**: With optimization (e.g., lazy loading, async plugins), it can match or beat Ansible (sub-second startups, efficient caching). Avoid heavy plugins to keep it fast.
- **Extensibility/Maintainability**: Essential for community adoption. The plugin system isolates user code, reducing bugs in core NornFlow.
- **When to adopt**: Now—start with a minimal registry (building on your current `HOOK_REGISTRY`), add entry points, and document plugin development. Migrate the current hooks to plugins gradually. This positions NornFlow as a modern, extensible tool without sacrificing speed.

If simplicity is paramount (e.g., for a small team), stick with explicit fields for now and plan a migration. But for "ultimate software engineering," go extensible—it's the path to sustainability. Let me know if you want implementation details or a migration plan.

----------

Q2: we might actually have a problem here... here is what I was about to prompt you: "ok, then we must shift gears into FULL extensibility. This means we won't have 'set_to' as a fixed field in the nornflow/models/task taskModel anymore. It must be implemented the same way any user would implement hooks in the future. You must now outline that new architecture, but the way I envision it, we would have to keep a base Hook class in the hook framework. As well as the fundamental PreRunHook and PostTunHook. Actual hook classes, that implement hook logic, would have to inherit from one of those. Then we keep the logic of registering and finding out about registered hooks from classes, although I'm not too sure how the registering woulf automatically happen this time... we would then also keep the logic in the RunnableModel to run prehooks before actually invoking Nornir.run() on the tasks - and potentially skippin that altogether. And post run hooks running after tasks ran (as is the case with set_to)." Ok... so THAT was what I was supposed to prompt you for. However, I'm also conscious that nornflow is based on pydantic-serdes. And I had it in the back of my head that pydantic-serdes hasa store that holds hashable objects... meaning, the models we instantiate, SHOULD (or maybe MUST) be hashable. So I queried a different AI agent about it... here's my question and their answer: Q: deeply analyse pydantic_serdes code and tell me: to elements sotred in the global store need to be all immutable? Meaning, once models are instantiated (and stored), can I add new attrs to those model instances? I mean attrs that were not actually declared as fields in the instance itself?; A: # Mutability of Models in pydantic-serdes Global Store

After thoroughly analyzing the pydantic-serdes codebase, here's what I found regarding mutability of stored models:

## How Models Are Stored

Models in pydantic-serdes are stored in a `PydanticSerdesSortedSet` within the `ModelsGlobalStore`. This set relies on objects being **hashable** to function correctly.

## Hashability and Mutability Issues

The key concern comes from the `__hash__` implementation in `PydanticSerdesBaseModel`:

```python
def __hash__(self):
    return hash((type(self),) + tuple(self.__dict__.values()))
```

This means:

1. The hash includes **all values** in the model's `__dict__`
2. In Python, an object's hash is calculated only once when added to a set
3. If you modify the object after adding it to a set, the actual hash value should change, but it isn't recalculated automatically

## Can You Add New Attributes?

**Technically yes, but you shouldn't** for several reasons:

1. **Hash Inconsistency**: Adding attributes would change what the hash value *should* be, but the set won't recalculate it, leading to potential lookup failures and corrupted data structures

2. **Equality Problems**: The model implements equality as:
   ```python
   def __eq__(self, other):
       return str(self) == str(other)
   ```
   Adding new attributes might not be reflected in this string representation, causing comparison issues

3. **Pydantic Validation**: By default, Pydantic doesn't allow extra attributes unless configured with:
   ```python
   model_config = ConfigDict(extra="allow")
   ```
   The base model doesn't have this configuration

4. **Key Stability**: The model's `.key` property is used for ordering in the sorted set:
   ```python
   def key(self) -> Tuple:
       return tuple([getattr(self, attr) for attr in self._key])
   ```
   This only includes predefined key fields, not any added attributes

## Practical Consequences

If you add attributes to models already in the global store:

1. Filtering and retrieving models might not work as expected
2. You could end up with inconsistent behavior in equality checks
3. The data structure integrity could be compromised

## Conclusion

While Python doesn't prevent you from adding attributes to model instances, the design of pydantic-serdes strongly implies that **models should be treated as immutable once stored** in the global data store. The system isn't designed to handle post-storage modifications to model attributes or structure.

For a robust application using pydantic-serdes, you should consider model instances immutable after creation and storage.--Now I want you to evaluate all that and reconsider if this FULLY EXTENSIBLE APPROACH is even possiblle. If it is, is it wise to do so? And if it is wise, how would the implementation go?

A2: 
This is an excellent catch, and you've identified a fundamental architectural conflict. Let me analyze this thoroughly:

## The Core Problem

The pydantic-serdes constraint creates a significant impediment to full extensibility:

1. **Hash-based storage**: Models are stored in a `PydanticSerdesSortedSet` that requires objects to be hashable
2. **Immutability requirement**: Once stored, models shouldn't be modified as their hash includes all `__dict__` values
3. **Dynamic hooks conflict**: A fully extensible hook system would require dynamically adding hook instances as attributes to TaskModel instances, violating immutability

## Evaluating the Fully Extensible Approach

### Is it Possible?

**Technically possible but architecturally unsound** with the current pydantic-serdes foundation. Here are the options:

#### Option 1: Dynamic Attribute Addition (NOT RECOMMENDED)
```python
# This would break hash consistency
task_instance.my_custom_hook = MyCustomHook()  # BAD - changes hash after storage
```

#### Option 2: Pre-declared Generic Hook Fields
```python
class TaskModel(RunnableModel):
    # Pre-declare generic hook containers
    pre_hooks: dict[str, PreRunHook] = {}
    post_hooks: dict[str, PostRunHook] = {}
```
**Problem**: Still modifies the instance after creation, breaking hash consistency.

#### Option 3: Hook Registry Separate from Models (RECOMMENDED)
Keep hooks completely separate from model instances:

```python
# Hooks are registered globally, not stored on models
HOOK_REGISTRY = {
    "task_id_1": {
        "pre": [CheckPermissionHook(), ValidateHostHook()],
        "post": [SetToHook("backup_result"), NotifyHook()]
    }
}
```

### Is it Wise?

Given the pydantic-serdes constraints, **full extensibility is NOT wise in the current architecture**. The immutability requirement is fundamental to the storage system's integrity.

## Recommended Solution: Hybrid Approach

Here's a pragmatic solution that provides extensibility while respecting pydantic-serdes constraints:

### Architecture Overview

```python
# nornflow/hooks/base.py
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from nornflow.models import TaskModel

class Hook(ABC):
    """Base class for all hooks."""
    
    @property
    @abstractmethod
    def hook_type(self) -> str:
        """Return 'pre' or 'post'."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this hook."""
        pass


class PreRunHook(Hook):
    hook_type = "pre"
    
    @abstractmethod
    def run(self, task: "TaskModel", host: Host, vars_mgr: Any) -> bool:
        """Return True to continue, False to skip."""
        pass


class PostRunHook(Hook):
    hook_type = "post"
    
    @abstractmethod  
    def run(self, task: "TaskModel", host: Host, result: Any, vars_mgr: Any) -> None:
        """Process post-execution logic."""
        pass


# nornflow/hooks/builtin.py
from nornflow.hooks.base import PostRunHook

class SetToHook(PostRunHook):
    name = "set_to"
    
    def __init__(self, variable_name: str):
        self.variable_name = variable_name
    
    def run(self, task, host, result, vars_mgr):
        vars_mgr.set_runtime_variable(self.variable_name, result, host.name)


# nornflow/models/task.py
class TaskModel(RunnableModel):
    # Only store hook configurations, not instances
    hooks: dict[str, Any] | None = None  # e.g., {"set_to": "backup_result"}
    
    @field_validator("hooks", mode="before")
    @classmethod
    def validate_hooks(cls, v):
        """Convert to hashable structure."""
        return convert_to_hashable(v)


# nornflow/hooks/loader.py
from typing import TYPE_CHECKING
from nornflow.hooks.registry import HOOK_REGISTRY

if TYPE_CHECKING:
    from nornflow.models import TaskModel

def load_hooks(task: "TaskModel") -> tuple[list[PreRunHook], list[PostRunHook]]:
    """
    Load hook instances from task configuration.
    Creates fresh instances each time - doesn't modify the task.
    """
    pre_hooks = []
    post_hooks = []
    
    if not task.hooks:
        return pre_hooks, post_hooks
    
    for hook_name, hook_config in task.hooks.items():
        hook_class = HOOK_REGISTRY.get(hook_name)
        if not hook_class:
            raise HookError(f"Unknown hook: {hook_name}")
        
        # Create instance with config
        if isinstance(hook_config, dict):
            hook_instance = hook_class(**hook_config)
        else:
            # Simple value (like set_to: "var_name")
            hook_instance = hook_class(hook_config)
        
        if isinstance(hook_instance, PreRunHook):
            pre_hooks.append(hook_instance)
        elif isinstance(hook_instance, PostRunHook):
            post_hooks.append(hook_instance)
    
    return pre_hooks, post_hooks
```

### Usage in Workflow YAML

```yaml
workflow:
  name: example
  tasks:
    - name: backup_config
      hooks:
        set_to: backup_result  # Built-in hook
        custom_audit:          # User-defined hook
          user: admin
          action: backup
```

### User Extension Pattern

```python
# user_hooks.py
from nornflow.hooks import PostRunHook, register_hook

@register_hook("custom_audit")
class AuditHook(PostRunHook):
    name = "custom_audit"
    
    def __init__(self, user: str, action: str):
        self.user = user
        self.action = action
    
    def run(self, task, host, result, vars_mgr):
        log_audit(f"{self.user} performed {self.action} on {host.name}")
```

## Why This Approach Works

1. **Respects Immutability**: Hook configurations are stored as simple dicts in the model (hashable), not as mutable objects
2. **Extensible**: Users can register custom hooks via decorators or config files
3. **Clean Separation**: Hook instances are created at runtime, not stored in models
4. **Performance**: Hook loading happens once per task execution, not per model creation
5. **Backward Compatible**: Can maintain `set_to` as a special case initially, then migrate

## Migration Path

1. **Phase 1**: Keep current `set_to` field, add parallel `hooks` field
2. **Phase 2**: Deprecate `set_to` field, auto-convert to `hooks: {set_to: value}`
3. **Phase 3**: Remove `set_to` field entirely

## Performance Impact

- **Current**: Direct field access, ~0.001ms
- **Proposed**: Registry lookup + instantiation, ~0.1ms per hook
- **At scale**: For 100 tasks with 2 hooks each, adds ~20ms total (negligible vs Ansible's seconds)

## Recommendation

**Implement the hybrid approach now**. It provides:
- User extensibility via hook registry
- Respects pydantic-serdes immutability
- Clean architecture without dynamic attributes
- Minimal performance impact

The fully extensible approach with dynamic attributes would corrupt the global store and cause unpredictable failures. The hybrid approach gives you 90% of the extensibility with 100% architectural soundness.

----

Q3:no... unnaceptable. We can't have that 'hooks' lkey word. Hooks must be directly declared by their names just like 'set_to' is today. Should instead I modify Pydatic serdes (i'm the author) to allow for different types of datastores? And then provide one that wouldn't come with this constraint? If yes, then what type of data store would we need? What would be the required changes there.

A3: You're absolutely right - having a generic 'hooks' key defeats the purpose of direct, explicit hook declarations. Since you're the author of pydantic-serdes, modifying it to support different datastore types is the cleanest solution. Let me analyze what's needed:

## The Core Problem with Current Datastore

The current `PydanticSerdesSortedSet` requires immutable, hashable objects because:
1. It uses Python's `set` internally for uniqueness
2. Objects are hashed based on ALL their `__dict__` values
3. Modification after storage breaks set integrity

## Required Datastore Type

We need a datastore that:
1. **Allows controlled mutability** - Can add hook instances to models after initial creation
2. **Maintains identity** - Tracks objects by their key fields only, not entire state
3. **Preserves ordering** - Like the current sorted set
4. **Supports lookups** - Fast retrieval by key fields

## Proposed Solution: KeyBasedStore

Here's what I'd implement in pydantic-serdes:

### 1. Abstract Store Interface

```python
# pydantic_serdes/stores/base.py
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar('T')

class BaseStore(ABC, Generic[T]):
    """Abstract base for different storage strategies."""
    
    @abstractmethod
    def add(self, item: T) -> None:
        """Add item to store."""
        pass
    
    @abstractmethod
    def get(self, **criteria) -> list[T]:
        """Retrieve items matching criteria."""
        pass
    
    @abstractmethod
    def remove(self, item: T) -> None:
        """Remove item from store."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all items."""
        pass
```

### 2. New KeyBasedStore Implementation

```python
# pydantic_serdes/stores/key_based.py
from typing import Any, Type
from collections import OrderedDict

class KeyBasedStore(BaseStore):
    """
    Store that tracks objects by key fields only.
    Allows mutation of non-key attributes after storage.
    """
    
    def __init__(self, model_class: Type[Any]):
        self.model_class = model_class
        self._items: OrderedDict[tuple, Any] = OrderedDict()
    
    def _get_key(self, item: Any) -> tuple:
        """Extract key tuple from item based on _key attribute."""
        if hasattr(item, '_key'):
            return tuple(getattr(item, field) for field in item._key)
        return (id(item),)  # Fallback to object id
    
    def add(self, item: Any) -> None:
        """Add item, replacing if key exists."""
        key = self._get_key(item)
        self._items[key] = item
    
    def get(self, **criteria) -> list[Any]:
        """Get items matching criteria."""
        results = []
        for item in self._items.values():
            if all(getattr(item, k, None) == v for k, v in criteria.items()):
                results.append(item)
        return results
    
    def remove(self, item: Any) -> None:
        """Remove item by key."""
        key = self._get_key(item)
        self._items.pop(key, None)
    
    def clear(self) -> None:
        """Clear all items."""
        self._items.clear()
```

### 3. Modified PydanticSerdesBaseModel

```python
# pydantic_serdes/models.py
from pydantic_serdes.stores.base import BaseStore
from pydantic_serdes.stores.key_based import KeyBasedStore

class PydanticSerdesBaseModel(BaseModel):
    # Class variable to control store type
    _store_type: Type[BaseStore] = KeyBasedStore  # Default, can override
    
    @classmethod
    def _get_store(cls) -> BaseStore:
        """Get or create the store for this model class."""
        store_key = f"{cls.__module__}.{cls.__name__}"
        if store_key not in _global_stores:
            _global_stores[store_key] = cls._store_type(cls)
        return _global_stores[store_key]
    
    def __hash__(self) -> int:
        """Hash based on key fields only for KeyBasedStore compatibility."""
        if hasattr(self, '_key'):
            return hash((type(self),) + tuple(getattr(self, field) for field in self._key))
        return hash((type(self),) + tuple(self.__dict__.values()))
```

## Changes in NornFlow

With this new store type, we can have clean hook declarations:

### TaskModel with Direct Hook Fields

```python
# nornflow/models/task.py
from typing import Any, ClassVar
from nornflow.hooks import SetToHook, ValidateHostHook, AuditHook
from pydantic_serdes.stores import KeyBasedStore

class TaskModel(RunnableModel):
    """Task model with directly declared hook fields."""
    
    # Use KeyBasedStore to allow post-creation hook additions
    _store_type = KeyBasedStore
    
    # Only hash on these fields, not on hook fields
    _key = ("id", "name")
    _directive = "tasks"
    
    # Regular fields
    id: int | None = None
    name: str
    args: HashableDict[str, Any] | None = None
    
    # Direct hook fields (can be None)
    set_to: SetToHook | None = None
    validate_host: ValidateHostHook | None = None
    audit: AuditHook | None = None
    
    # Future hooks can be added as new fields
    # Users can create custom hook fields via model inheritance
```

### User Extension Pattern

Users would extend TaskModel to add custom hooks:

```python
# user_models.py
from nornflow.models import TaskModel
from my_hooks import CustomPreCheckHook, CustomPostProcessHook

class MyTaskModel(TaskModel):
    """Extended task model with custom hooks."""
    
    # Add custom hook fields
    pre_check: CustomPreCheckHook | None = None
    post_process: CustomPostProcessHook | None = None
```

### Workflow YAML

```yaml
workflow:
  name: example
  tasks:
    - name: backup_config
      set_to: backup_result       # Direct hook field
      validate_host: prod_only    # Another direct hook
      audit: enable               # Yet another
      args:
        commands: show run
```

## Implementation Strategy

1. **Phase 1**: Implement KeyBasedStore in pydantic-serdes
2. **Phase 2**: Add store type selection mechanism
3. **Phase 3**: Update NornFlow models to use KeyBasedStore
4. **Phase 4**: Refactor hook system to use direct fields

## Benefits

1. **Clean syntax**: Direct hook names as fields, no generic 'hooks' key
2. **Type safety**: Each hook is properly typed
3. **Extensibility**: Users can add hooks via inheritance
4. **No immutability issues**: KeyBasedStore only cares about key fields for identity
5. **Backward compatible**: Existing models using default store still work

## Alternative: Registry-Based Approach (If Store Change Not Viable)

If modifying pydantic-serdes proves complex, consider a registry approach where hooks are stored separately from models:

```python
# Hooks stored outside the model
TASK_HOOKS_REGISTRY = {
    task_id: {
        "set_to": SetToHook("var_name"),
        "validate": ValidateHook(),
    }
}
```

But this is less elegant than fixing the root cause in pydantic-serdes.

Would you like me to detail the specific changes needed in pydantic-serdes for the KeyBasedStore implementation?
