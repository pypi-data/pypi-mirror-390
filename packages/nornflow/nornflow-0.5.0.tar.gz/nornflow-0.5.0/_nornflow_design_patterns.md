# Design Patterns in NornFlow: GoF Patterns Analysis

## Executive Summary

NornFlow's architecture demonstrates sophisticated implementation of 15 Gang of Four (GoF) design patterns from the canonical catalog. This analysis documents each pattern's theoretical foundation and its specific implementation within the NornFlow codebase.

## Creational Patterns

### 1. **Builder Pattern**

#### Theory
The Builder pattern separates the construction of a complex object from its representation, allowing the same construction process to create different representations. It provides step-by-step construction of complex objects, making the process explicit and flexible.

#### Implementation in NornFlow

The `NornFlowBuilder` class (`builder.py`) exemplifies this pattern:

```python
class NornFlowBuilder:
    """Constructs NornFlow instances step-by-step with various configurations."""
    
    def __init__(self):
        self._settings = None
        self._workflow = None
        self._workflow_vars = None
        self._vars = None
        self._failure_strategy = None
        
    def with_settings(self, settings_file: str) -> "NornFlowBuilder":
        """Configure settings file path."""
        self._settings = NornFlowSettings(settings_file)
        return self
        
    def with_workflow(self, workflow: WorkflowModel | str | Path) -> "NornFlowBuilder":
        """Configure workflow to execute."""
        if isinstance(workflow, str):
            workflow = Path(workflow)
        if isinstance(workflow, Path):
            self._workflow = self._load_workflow_from_file(workflow)
        else:
            self._workflow = workflow
        return self
        
    def with_vars(self, vars: dict[str, Any]) -> "NornFlowBuilder":
        """Configure runtime variables."""
        self._vars = vars
        return self
        
    def build(self) -> NornFlow:
        """Construct the final NornFlow instance."""
        return NornFlow(
            settings=self._settings,
            workflow=self._workflow,
            workflow_vars=self._workflow_vars,
            vars=self._vars,
            failure_strategy=self._failure_strategy
        )
```

The builder allows flexible, step-by-step construction of NornFlow instances with complex initialization logic.

### 2. **Factory Method Pattern**

#### Theory
The Factory Method defines an interface for creating an object but lets subclasses decide which class to instantiate. It promotes loose coupling by eliminating the need to bind application-specific classes into the code.

#### Implementation in NornFlow

Processor creation in `utils.py`:

```python
def load_processor(processor_config: dict) -> Processor:
    """Factory method for creating processor instances from configuration."""
    processor_class_path = processor_config.get("class")
    processor_args = processor_config.get("args", {})
    
    # Dynamic class resolution
    module_path, class_name = processor_class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    processor_class = getattr(module, class_name)
    
    # Factory instantiation with runtime-determined class
    return processor_class(**processor_args)
```

Hook loading in `hooks/loader.py`:

```python
def load_hooks(hooks: dict[str, Any]) -> list[Hook]:
    """Factory for creating hook instances from configuration."""
    loaded_hooks = []
    for hook_name, hook_value in hooks.items():
        # Factory determines which hook class to instantiate
        hook_class = HOOK_REGISTRY.get(hook_name)
        if not hook_class:
            raise HookNotFoundError(f"Hook '{hook_name}' not registered")
        
        hook_instance = hook_class(hook_value)
        loaded_hooks.append(hook_instance)
    
    return loaded_hooks
```

### 3. **Singleton Pattern**

#### Theory
The Singleton pattern ensures a class has only one instance and provides a global point of access to it.

#### Implementation in NornFlow

Module-level singleton for hook registry (`hooks/registry.py`):

```python
# Global singleton registry
HOOK_REGISTRY: dict[str, type[object]] = {}

def register_hook(hook_class: type[object]) -> type[object]:
    """Register a hook class in the singleton registry."""
    if not hasattr(hook_class, "hook_name"):
        raise HookRegistrationError("Hook must have 'hook_name' attribute")
    
    # Single global instance ensures all parts of the system use same registry
    HOOK_REGISTRY[hook_class.hook_name] = hook_class
    return hook_class
```

Settings singleton pattern (`settings.py`):

```python
class NornFlowSettings:
    """Singleton-like settings manager for a NornFlow instance."""
    _instance = None
    
    def __new__(cls, settings_file: str = "nornflow.yaml", **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

## Structural Patterns

### 4. **Proxy Pattern**

#### Theory
The Proxy pattern provides a placeholder or surrogate for another object to control access to it. It acts as an intermediary, adding behavior without changing the original object's interface.

#### Implementation in NornFlow

The `NornirHostProxy` class (`vars/proxy.py`):

```python
class NornirHostProxy:
    """Proxy for controlled access to Nornir host data in Jinja2 templates."""
    
    def __init__(self) -> None:
        self._current_host: Host | None = None
        self._nornir: Nornir | None = None
    
    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to the underlying host."""
        if not self._nornir:
            raise VariableError("No Nornir instance available")
        if not self._current_host:
            raise VariableError("No current host set")
        
        # Controlled access with validation
        return self._get_host_value(name)
    
    def _get_host_value(self, attribute: str) -> Any:
        """Get value from host with access control."""
        host = self._nornir.inventory.hosts[self._current_host]
        
        # Access control logic
        if attribute == "password":
            raise VariableError("Direct password access not allowed")
        
        if hasattr(host, attribute):
            return getattr(host, attribute)
        
        # Proxy to host.data dictionary
        if attribute in host.data:
            return host.data[attribute]
        
        raise AttributeError(f"Host has no attribute '{attribute}'")
```

### 5. **Adapter Pattern**

#### Theory
The Adapter pattern converts the interface of a class into another interface clients expect. It allows classes to work together that couldn't otherwise because of incompatible interfaces.

#### Implementation in NornFlow

Jinja2 filter adapters (`builtins/jinja2_filters/py_wrapper_filters.py`):

```python
def create_filter_wrapper(func: Callable, func_name: str) -> Callable:
    """Adapter that wraps Python functions for use as Jinja2 filters."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Adapt Python function interface to Jinja2 filter interface
            return func(*args, **kwargs)
        except Exception as e:
            # Adapt Python exceptions to Jinja2-friendly error format
            return f"[Error in {func_name}: {e}]"
    
    # Add Jinja2-specific metadata
    wrapper.is_safe = getattr(func, 'is_safe', False)
    wrapper.needs_environment = getattr(func, 'needs_environment', False)
    
    return wrapper

# Usage: adapting Python's built-in functions for Jinja2
jinja_env.filters['len'] = create_filter_wrapper(len, 'len')
jinja_env.filters['abs'] = create_filter_wrapper(abs, 'abs')
```

### 6. **Decorator Pattern**

#### Theory
The Decorator pattern attaches additional responsibilities to an object dynamically. It provides a flexible alternative to subclassing for extending functionality.

#### Implementation in NornFlow

Function decorator for hook delegation (`builtins/processors/decorators.py`):

```python
def hook_delegator(func: Callable) -> Callable:
    """Decorator that adds hook delegation to processor methods."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        method_name = func.__name__
        task = args[0] if args else kwargs.get('task')
        
        # Add pre-processing behavior (hook execution)
        for hook in self.task_hooks:
            if hasattr(hook, method_name):
                if not hook.should_execute(task):
                    continue
                    
                hook._current_context = self.context
                try:
                    # Dynamically add hook behavior
                    hook_method = getattr(hook, method_name)
                    hook_method(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Hook error in {method_name}: {e}")
        
        # Execute original function
        return func(self, *args, **kwargs)
    
    return wrapper
```

Task function decoration in `IfHook` (`builtins/hooks/if_hook.py`):

```python
def skip_if_condition_flagged(func: Callable) -> Callable:
    """Decorator that adds conditional skip behavior to tasks."""
    @wraps(func)
    def wrapper(task: Task, *args, **kwargs):
        # Add skip checking behavior
        if task.host.data.get('nornflow_skip_flag'):
            task.host.data.pop('nornflow_skip_flag')
            return Result(
                host=task.host,
                skipped=True,
                changed=False,
                failed=False
            )
        
        # Execute original task
        return func(task, *args, **kwargs)
    
    return wrapper
```

### 7. **Facade Pattern**

#### Theory
The Facade pattern provides a unified interface to a set of interfaces in a subsystem. It defines a higher-level interface that makes the subsystem easier to use.

#### Implementation in NornFlow

The NornFlow class acts as a facade (`nornflow.py`):

```python
class NornFlow:
    """Facade that provides simplified interface to complex subsystems."""
    
    def __init__(self, **kwargs):
        # Initialize all subsystems
        self._nornflow_settings = self._setup_settings(kwargs)
        self._tasks_catalog = self._load_tasks_catalog()
        self._filters_catalog = self._load_filters_catalog()
        self._workflows_catalog = self._load_workflows_catalog()
        self._vars_manager = self._setup_vars_manager()
        self._nornir_manager = None
        
    def run(self, workflow: WorkflowModel = None) -> int:
        """Simplified interface hiding complex orchestration."""
        # Facade coordinates multiple subsystems
        workflow = workflow or self._workflow
        
        with self._get_nornir_manager() as nm:
            # Setup phase
            self._apply_processors(nm)
            self._configure_vars(nm)
            
            # Execution phase
            return self._execute_workflow(nm, workflow)
    
    def _execute_workflow(self, nm: NornirManager, workflow: WorkflowModel) -> int:
        """Hide complexity of workflow execution."""
        failed = 0
        for task in workflow.tasks:
            result = self._execute_task(nm, task)
            if result.failed:
                failed += 1
                if self._failure_strategy == FailureStrategy.FAIL_FAST:
                    break
        return failed
```

### 8. **Composite Pattern**

#### Theory
The Composite pattern composes objects into tree structures to represent part-whole hierarchies. It lets clients treat individual objects and compositions of objects uniformly.

#### Implementation in NornFlow

Workflow and task composition (`models/workflow.py`):

```python
class WorkflowModel(NornFlowBaseModel):
    """Composite: workflow is composed of tasks."""
    name: str
    tasks: list[TaskModel]  # Composite contains components
    
    def run(self, nornir_manager: NornirManager) -> int:
        """Execute all component tasks."""
        failed_count = 0
        
        for task in self.tasks:
            # Uniform treatment of components
            result = task.run(nornir_manager)
            if result.failed:
                failed_count += 1
                
        return failed_count

class TaskModel(RunnableModel):
    """Leaf component in the composite structure."""
    name: str
    action: str
    
    def run(self, nornir_manager: NornirManager) -> AggregatedResult:
        """Execute individual task."""
        task_func = self._get_task_function()
        return nornir_manager.run(task_func, **self.args)
```

### 9. **Flyweight Pattern**

#### Theory
The Flyweight pattern uses sharing to support large numbers of fine-grained objects efficiently. It separates intrinsic (shared) state from extrinsic (context-specific) state.

#### Implementation in NornFlow

Hook instance sharing (`models/runnable.py`):

```python
class RunnableModel(NornFlowBaseModel, ABC):
    """Base class implementing flyweight pattern for hooks."""
    
    _hooks_cache: list[Hook] | None = None  # Shared hook instances
    
    def get_hooks(self) -> list[Hook]:
        """Get or create shared hook instances (flyweight objects)."""
        if self._hooks_cache is not None:
            return self._hooks_cache
        
        # Create hooks once and share across executions
        if self.hooks:
            # Each unique (hook_type, config) combination creates one instance
            hooks = load_hooks(self.hooks)
            self._hooks_cache = hooks  # Cache for reuse
        else:
            self._hooks_cache = []
            
        return self._hooks_cache
```

Variable context sharing (`vars/context.py`):

```python
class NornFlowDeviceContext:
    """Implements flyweight pattern for variable storage."""
    
    # Shared intrinsic state across all contexts
    _initial_cli_vars: ClassVar[dict[str, Any]] = {}
    _initial_workflow_inline_vars: ClassVar[dict[str, Any]] = {}
    
    def __init__(self, host_name: str):
        # Extrinsic state (per-host)
        self.host_name = host_name
        self._runtime_vars = {}  # Host-specific runtime vars
        
        # Share common data unless overridden
        self._cli_vars_override = {}  # Only created when different from shared
```

## Behavioral Patterns

### 10. **Strategy Pattern**

#### Theory
The Strategy pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable. The strategy lets the algorithm vary independently from clients that use it.

#### Implementation in NornFlow

Failure handling strategies (`constants.py` and processor implementation):

```python
class FailureStrategy(StrEnum):
    """Strategy family definition."""
    SKIP_FAILED = "skip-failed"
    FAIL_FAST = "fail-fast"  
    RUN_ALL = "run-all"

class NornFlowFailureStrategyProcessor(Processor):
    """Context that uses strategies."""
    
    def __init__(self, failure_strategy: FailureStrategy):
        self.failure_strategy = failure_strategy
        self._failed_hosts = set()
        
    def task_instance_completed(self, task: Task, host: Host, result: Result):
        """Apply selected strategy."""
        if result.failed:
            if self.failure_strategy == FailureStrategy.FAIL_FAST:
                self._apply_fail_fast_strategy(task, host)
            elif self.failure_strategy == FailureStrategy.SKIP_FAILED:
                self._apply_skip_failed_strategy(task, host)
            elif self.failure_strategy == FailureStrategy.RUN_ALL:
                self._apply_run_all_strategy(task, host)
    
    def _apply_fail_fast_strategy(self, task: Task, host: Host):
        """Fail-fast strategy: stop all execution."""
        raise FailFastError(f"Task failed on {host.name}, stopping execution")
    
    def _apply_skip_failed_strategy(self, task: Task, host: Host):
        """Skip-failed strategy: mark host for skipping."""
        self._failed_hosts.add(host.name)
        
    def _apply_run_all_strategy(self, task: Task, host: Host):
        """Run-all strategy: continue regardless."""
        pass  # No action needed
```

### 11. **Template Method Pattern**

#### Theory
The Template Method defines the skeleton of an algorithm in a base class, letting subclasses override specific steps of the algorithm without changing its structure.

#### Implementation in NornFlow

Hook base class (`hooks/base.py`):

```python
class Hook(Processor):
    """Abstract base implementing template method pattern."""
    
    def __init__(self, value: Any = None):
        self.value = value
        self._execution_count = {}
        
    def should_execute(self, task: Task) -> bool:
        """Template method: defines execution control algorithm."""
        # Step 1: Check if hook should run multiple times
        if not self.run_once_per_task:
            return True
            
        # Step 2: Check execution count
        task_id = id(task)
        if self._execution_count.get(task_id, 0) > 0:
            return False
            
        # Step 3: Increment and allow
        self._execution_count[task_id] += 1
        return True
    
    def execute_hook_validations(self, task_model: "TaskModel") -> None:
        """Hook point for subclasses to override."""
        pass  # Subclasses implement specific validation
    
    # Hook points for subclasses
    def task_started(self, task: Task) -> None:
        """Override in subclasses for task start behavior."""
        pass
        
    def task_instance_started(self, task: Task, host: Host) -> None:
        """Override in subclasses for instance start behavior."""
        pass
```

Concrete implementation in `IfHook`:

```python
class IfHook(Hook):
    """Concrete implementation of template method."""
    
    def execute_hook_validations(self, task_model: "TaskModel") -> None:
        """Implement specific validation step."""
        if isinstance(self.value, dict):
            if len(self.value) != 1:
                raise HookValidationError("if must specify exactly one filter")
        elif isinstance(self.value, str):
            if not any(marker in self.value for marker in JINJA2_MARKERS):
                raise HookValidationError("if expression must be valid Jinja2")
    
    def task_instance_started(self, task: Task, host: Host) -> None:
        """Implement specific instance start behavior."""
        if self._evaluate_condition(host):
            host.data['nornflow_skip_flag'] = True
```

### 12. **Chain of Responsibility Pattern**

#### Theory
The Chain of Responsibility pattern passes requests along a chain of handlers. Each handler decides either to process the request or pass it to the next handler in the chain.

#### Implementation in NornFlow

Processor chain (`nornir_manager.py`):

```python
class NornirManager:
    """Manages chain of processors."""
    
    def __init__(self, nornir: Nornir):
        self.nornir = nornir
        self.processors = []  # Chain of handlers
        
    def add_processor(self, processor: Processor) -> None:
        """Add handler to the chain."""
        self.processors.append(processor)
        self.nornir.processors.append(processor)
        
    def run(self, task: Callable, **kwargs) -> AggregatedResult:
        """Execute task with processor chain."""
        # Each processor in chain handles events
        # Nornir automatically calls each processor's methods in sequence
        return self.nornir.run(task, **kwargs)
```

Event propagation through processor chain:

```python
# Each processor in the chain handles the event
for processor in self.processors:
    processor.task_started(task)  # First processor handles
    # Then second processor handles
    # And so on...
```

### 13. **Observer Pattern**

#### Theory
The Observer pattern defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.

#### Implementation in NornFlow

Processor as observer interface (`nornir_manager.py` and processor implementations):

```python
class Processor(ABC):
    """Observer interface for task lifecycle events."""
    
    def task_started(self, task: Task) -> None:
        """Notification: task has started."""
        pass
    
    def task_instance_started(self, task: Task, host: Host) -> None:
        """Notification: task instance has started on a host."""
        pass
        
    def task_instance_completed(self, task: Task, host: Host, result: Result) -> None:
        """Notification: task instance has completed on a host."""
        pass
        
    def task_completed(self, task: Task, result: AggregatedResult) -> None:
        """Notification: task has completed."""
        pass

# Concrete observers
class HookProcessor(Processor):
    """Concrete observer reacting to task events."""
    
    def task_started(self, task: Task) -> None:
        """React to task start event."""
        for hook in self.hooks:
            hook.task_started(task)
            
class FailureStrategyProcessor(Processor):
    """Another concrete observer."""
    
    def task_instance_completed(self, task: Task, host: Host, result: Result) -> None:
        """React to completion events."""
        if result.failed:
            self.handle_failure(task, host)
```

### 14. **Command Pattern**

#### Theory
The Command pattern encapsulates a request as an object, thereby letting you parameterize clients with different requests, queue or log requests.

#### Implementation in NornFlow

Task as command (`models/task.py`):

```python
class TaskModel(RunnableModel):
    """Command pattern: encapsulates task execution request."""
    
    name: str  # Command identifier
    action: str  # Command to execute
    args: dict[str, Any] | None = None  # Command parameters
    
    def run(self, nornir_manager: NornirManager) -> AggregatedResult:
        """Execute the command."""
        # Get the command implementation
        task_func = self._get_task_function()
        
        # Execute with encapsulated parameters
        return nornir_manager.run(
            task=task_func,
            name=self.name,
            **self.get_resolved_args()
        )
    
    def _get_task_function(self) -> Callable:
        """Resolve command implementation."""
        if self.action in self.context["tasks_catalog"]:
            return self.context["tasks_catalog"][self.action]
        
        # Dynamic command resolution
        module_path, func_name = self.action.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, func_name)
```

### 15. **Iterator Pattern**

#### Theory
The Iterator pattern provides a way to access elements of an aggregate object sequentially without exposing its underlying representation.

#### Implementation in NornFlow

Workflow task iteration (`models/workflow.py`):

```python
class WorkflowModel(NornFlowBaseModel):
    """Aggregate containing tasks."""
    tasks: list[TaskModel]
    
    def __iter__(self):
        """Return iterator for tasks."""
        return iter(self.tasks)
    
    def run(self, nornir_manager: NornirManager) -> int:
        """Iterate over tasks using iterator pattern."""
        failed_count = 0
        
        # Iterator pattern in use
        for task in self:  # Uses __iter__
            result = task.run(nornir_manager)
            if result.failed:
                failed_count += 1
                
        return failed_count
```

Catalog iteration (`catalogs.py`):

```python
class Catalog(ABC, dict[str, Any]):
    """Catalog provides iteration over discovered items."""
    
    def __iter__(self):
        """Iterator over catalog items."""
        return super().__iter__()
    
    def items(self):
        """Iterate over key-value pairs."""
        for key in self:
            yield key, self[key]
            
    def discover_and_iterate(self, path: str):
        """Discover items and provide iterator."""
        self.discover_items_in_dir(path)
        return iter(self)
```

## Pattern Interactions

### Composite + Iterator
Workflows (Composite) use Iterator to traverse tasks:
```python
for task in workflow:  # Iterator through Composite
    task.run()  # Uniform interface
```

### Observer + Chain of Responsibility
Processors act as both Observers (receiving notifications) and handlers in a Chain:
```python
# Each processor observes and handles in sequence
for processor in chain:
    processor.task_started(task)  # Observer notification + chain handling
```

### Strategy + Template Method
Hooks use Template Method for structure while strategies handle failures:
```python
class Hook(Processor):  # Template Method
    def should_execute(self, task): ...  # Template structure
    
class FailureStrategyProcessor(Processor):  # Strategy
    def handle_failure(self, strategy): ...  # Strategy selection
```

### Facade + Builder
NornFlow (Facade) can be constructed via Builder:
```python
nf = NornFlowBuilder()
    .with_settings("config.yaml")  # Builder
    .build()  # Returns Facade
nf.run()  # Simple Facade interface
```

## Conclusion

NornFlow demonstrates mature software architecture through extensive use of 15 GoF design patterns. The implementation shows:

- **Creational flexibility** through Builder, Factory Method, and Singleton patterns
- **Structural elegance** via Proxy, Adapter, Decorator, Facade, Composite, and Flyweight patterns  
- **Behavioral sophistication** using Strategy, Template Method, Chain of Responsibility, Observer, Command, and Iterator patterns

These patterns work together cohesively to create a maintainable, extensible, and performant network automation framework that successfully abstracts complexity while preserving power and flexibility.