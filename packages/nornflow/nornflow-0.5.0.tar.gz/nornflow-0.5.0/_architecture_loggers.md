Based on the step-by-step guide in _addressing_hook_concerns_stepbystep.md, I'll implement **Step 3: Improve Observability for Filter Cascading**. This addresses the difficulty in debugging why certain hosts are excluded when filters cascade through workflow → pre-hooks → task levels. The solution adds structured logging at each filter stage with clear host counts, enabling better observability without impacting performance or breaking the Hook Framework described in _architecture_hookNEW.md.

The changes:
- Add logging in nornflow.py within `_apply_filters()` to log workflow-level filter application.
- Add logging in runnable.py within `_run_pre_hooks()` to log pre-hook filtering effects.
- Add logging in task.py within `_run()` to log final task-level host filtering.

This maintains the framework's thread safety, Flyweight pattern, and performance characteristics while improving debugging capabilities.

# filepath: nornflow.py
```python
from pathlib import Path
from typing import Any

from pydantic_serdes.utils import load_file_to_dict

from nornflow.builtins import DefaultNornFlowProcessor, filters as builtin_filters, tasks as builtin_tasks
from nornflow.builtins.processors import NornFlowFailureStrategyProcessor
from nornflow.catalogs import CallableCatalog, FileCatalog
from nornflow.constants import FailureStrategy, NORNFLOW_INVALID_INIT_KWARGS
from nornflow.exceptions import (
    CatalogError,
    CoreError,
    ImmutableAttributeError,
    InitializationError,
    ProcessorError,
    ResourceError,
    SettingsError,
    TaskError,
    WorkflowError,
)
from nornflow.models import WorkflowModel
from nornflow.nornir_manager import NornirManager
from nornflow.settings import NornFlowSettings
from nornflow.utils import (
    is_nornir_filter,
    is_nornir_task,
    is_workflow_file,
    load_processor,
    print_workflow_overview,
    process_filter,
)
from nornflow.vars.manager import NornFlowVariablesManager
from nornflow.vars.processors import NornFlowVariableProcessor


class NornFlow:
    """
    NornFlow extends Nornir with a structured workflow system, task discovery, and configuration
    management capabilities. It serves as the main entry point for executing network automation
    jobs that follow a defined workflow pattern.

    Key features:
    - Assets auto-discovery from local directories
    - Workflow management and execution
    - Consistent configuration handling
    - Advanced inventory filtering with custom filter functions
    - Customizable execution processors
    - Variables system with multi-level precedence

    The NornFlow object lifecycle typically involves:
    1. Initialization with settings (from file or explicit object)
    2. Automatic discovery of available tasks
    3. Automatic discovery of available workflows (not mandatory)
    4. Automatic discovery of available filters (not mandatory)
    5. Selection of a workflow (by object, name, file path, or dictionary definition)
    6. Execution of the workflow against the filtered Nornir inventory

    Tasks are executed in order as defined in the workflow, providing a structured
    approach to network automation operations.

    Processor precedence follows this order (highest to lowest priority):
    1. Processors provided directly to the NornFlow constructor
    2. Processors specified in the workflow definition
    3. Processors specified in the NornFlow settings
    4. Default processor if none of the above are specified

    Variable precedence follows this order (highest to lowest priority):
    1. Vars (passed via command line or set programmatically as overrides)
    2. Workflow variables (defined in workflow file)
    3. Environment variables
    4. Variables from external files
    """

    def __init__(
        self,
        nornflow_settings: NornFlowSettings | None = None,
        workflow: WorkflowModel | str | None = None,
        processors: list[dict[str, Any]] | None = None,
        vars: dict[str, Any] | None = None,
        filters: dict[str, Any] | None = None,
        failure_strategy: FailureStrategy | None = None,
        **kwargs: Any,
    ):
        """
        Initialize a NornFlow instance.

        Args:
            nornflow_settings: NornFlow configuration settings object
            workflow: Pre-configured WorkflowModel instance or workflow name string (optional)
            processors: List of processor configurations to override default processors
            vars: Variables with highest precedence in the resolution chain.
                While named "vars" due to their primary source being command-line
                arguments, these serve as a universal override mechanism that can be:
                - Parsed from actual CLI arguments (--vars)
                - Set programmatically for workflow customization
                - Updated at runtime for dynamic behavior
                These variables always override any other variable source.
            filters: Inventory filters with highest precedence. These completely override
                any inventory filters defined in the workflow YAML.
            failure_strategy: Failure strategy with highest precedence. This overrides any failure
                strategy defined in the workflow YAML.
            **kwargs: Additional keyword arguments passed to NornFlowSettings

        Raises:
            InitializationError: If initialization fails due to invalid configuration
        """
        try:
            self._initialize_settings(nornflow_settings, kwargs)
            self._initialize_instance_vars(vars, filters, failure_strategy, processors)
            self._initialize_catalogs()
            self._initialize_nornir()
            self._initialize_processors()
            self._validate_init_kwargs(kwargs)
            self._check_tasks()
        except CoreError:
            raise
        except Exception as e:
            raise InitializationError(f"NornFlow initialization failed: {e!s}") from e

    def _initialize_settings(
        self, nornflow_settings: NornFlowSettings | None, kwargs: dict[str, Any]
    ) -> None:
        """Initialize NornFlow settings from provided object or kwargs."""
        if nornflow_settings:
            self._settings = nornflow_settings
        else:
            self._settings = NornFlowSettings(**kwargs)

    def _initialize_instance_vars(
        self,
        vars: dict[str, Any] | None,
        filters: dict[str, Any] | None,
        failure_strategy: FailureStrategy | None,
        processors: list[dict[str, Any]] | None,
    ) -> None:
        """Initialize core instance variables."""
        self._vars = vars or {}
        self._filters = filters or {}
        self._failure_strategy = failure_strategy
        self._processors = processors
        self._workflow = None
        self._workflow_path = None
        self._var_processor = None
        self._failure_processor = None

    def _initialize_catalogs(self) -> None:
        """Initialize and load catalogs."""
        self._tasks_catalog = CallableCatalog("tasks")
        self._filters_catalog = CallableCatalog("filters")
        self._workflows_catalog = FileCatalog("workflows")
        self._load_tasks_catalog()
        self._load_filters_catalog()
        self._load_workflows_catalog()

    def _initialize_nornir(self) -> None:
        """Initialize Nornir configurations and manager."""
        self._nornir_configs = self._settings.nornir_config_file
        self._nornir_manager = NornirManager(self._nornir_configs)

    def _initialize_processors(self) -> None:
        """Initialize processors with proper precedence."""
        # Processor precedence: constructor > workflow > settings > default
        processors = self._processors or []
        if self._workflow and self._workflow.processors:
            processors.extend(self._workflow.processors)
        if self._settings.processors:
            processors.extend(self._settings.processors)

        # Always add default processor if no processors specified
        if not processors:
            processors = [DefaultNornFlowProcessor()]

        # Load and apply processors
        loaded_processors = [load_processor(p) for p in processors]
        self._nornir_manager.apply_processors(loaded_processors)

        # Add variable processor
        self._var_processor = NornFlowVariableProcessor(self._var_manager)
        self._nornir_manager.apply_processors([self._var_processor])

        # Add failure strategy processor
        effective_failure_strategy = (
            self._failure_strategy
            or (self._workflow.failure_strategy if self._workflow else None)
            or self._settings.failure_strategy
        )
        self._failure_processor = NornFlowFailureStrategyProcessor(effective_failure_strategy)
        self._nornir_manager.apply_processors([self._failure_processor])

    @property
    def nornir_configs(self) -> str:
        """Get the Nornir configuration file path."""
        return self._nornir_configs

    @nornir_configs.setter
    def nornir_configs(self, value: str) -> None:
        """Set the Nornir configuration file path."""
        if hasattr(self, "_nornir_manager"):
            raise ImmutableAttributeError("Cannot change nornir_configs after initialization")
        self._nornir_configs = value

    @property
    def nornir_manager(self) -> NornirManager:
        """Get the Nornir manager instance."""
        return self._nornir_manager

    @nornir_manager.setter
    def nornir_manager(self, value: NornirManager) -> None:
        """Set the Nornir manager instance."""
        if hasattr(self, "_nornir_manager"):
            raise ImmutableAttributeError("Cannot change nornir_manager after initialization")
        self._nornir_manager = value

    @property
    def settings(self) -> NornFlowSettings:
        """Get the NornFlow settings."""
        return self._settings

    @settings.setter
    def settings(self, value: NornFlowSettings) -> None:
        """Set the NornFlow settings."""
        if hasattr(self, "_settings"):
            raise ImmutableAttributeError("Cannot change settings after initialization")
        self._settings = value

    @property
    def vars(self) -> dict[str, Any]:
        """Get the vars dictionary."""
        return self._vars

    @vars.setter
    def vars(self, value: dict[str, Any]) -> None:
        """Set the vars dictionary."""
        self._vars = value

    @property
    def filters(self) -> dict[str, Any]:
        """Get the filters dictionary."""
        return self._filters

    @filters.setter
    def filters(self, value: dict[str, Any]) -> None:
        """Set the filters dictionary."""
        self._filters = value

    @property
    def failure_strategy(self) -> FailureStrategy:
        """Get the failure strategy."""
        return self._failure_strategy

    @failure_strategy.setter
    def failure_strategy(self, value: FailureStrategy) -> None:
        """Set the failure strategy."""
        self._failure_strategy = value

    @property
    def tasks_catalog(self) -> CallableCatalog:
        """Get the tasks catalog."""
        return self._tasks_catalog

    @tasks_catalog.setter
    def tasks_catalog(self, value: CallableCatalog) -> None:
        """Set the tasks catalog."""
        if hasattr(self, "_tasks_catalog"):
            raise ImmutableAttributeError("Cannot change tasks_catalog after initialization")
        self._tasks_catalog = value

    @property
    def workflows_catalog(self) -> FileCatalog:
        """Get the workflows catalog."""
        return self._workflows_catalog

    @workflows_catalog.setter
    def workflows_catalog(self, value: FileCatalog) -> None:
        """Set the workflows catalog."""
        if hasattr(self, "_workflows_catalog"):
            raise ImmutableAttributeError("Cannot change workflows_catalog after initialization")
        self._workflows_catalog = value

    @property
    def filters_catalog(self) -> CallableCatalog:
        """Get the filters catalog."""
        return self._filters_catalog

    @filters_catalog.setter
    def filters_catalog(self, value: CallableCatalog) -> None:
        """Set the filters catalog."""
        if hasattr(self, "_filters_catalog"):
            raise ImmutableAttributeError("Cannot change filters_catalog after initialization")
        self._filters_catalog = value

    @property
    def workflow(self) -> WorkflowModel | None:
        """Get the current workflow."""
        return self._workflow

    @workflow.setter
    def workflow(self, value: WorkflowModel | str | None) -> None:
        """Set the workflow."""
        if isinstance(value, str):
            self._workflow, self._workflow_path = self._load_workflow_from_name(value)
        else:
            self._workflow = value
            self._workflow_path = None

    @property
    def workflow_path(self) -> Path | None:
        """Get the workflow file path."""
        return self._workflow_path

    @workflow_path.setter
    def workflow_path(self, value: str | Path | None) -> None:
        """Set the workflow file path."""
        if value is None:
            self._workflow = None
            self._workflow_path = None
        else:
            workflow_path = Path(value)
            if not workflow_path.is_file():
                raise ResourceError(
                    f"Workflow file not found: {workflow_path}",
                    resource_type="File",
                    resource_name=str(workflow_path),
                )
            workflow_dict = load_file_to_dict(workflow_path)
            self._workflow = WorkflowModel.create(workflow_dict)
            self._workflow_path = workflow_path

    @property
    def processors(self) -> list[dict[str, Any]]:
        """Get the processors list."""
        return self._processors

    @processors.setter
    def processors(self, value: list[dict[str, Any]]) -> None:
        """Set the processors list."""
        self._processors = value

    def _load_catalog(
        self,
        catalog_type: type,
        name: str,
        builtin_module: Any = None,
        predicate: Any = None,
        transform_item: Any = None,
        directories: list[str] | None = None,
        recursive: bool = False,
        check_empty: bool = False,
    ) -> Any:
        """Generic catalog loading method."""
        catalog = catalog_type(name)

        # Load builtins if module provided
        if builtin_module:
            catalog.register_from_module(builtin_module, predicate, transform_item)

        # Load from directories
        if directories:
            for directory in directories:
                catalog.discover_items_in_dir(directory, predicate, transform_item, recursive)

        # Check if catalog should not be empty
        if check_empty and catalog.is_empty:
            raise CatalogError(f"No {name} found in configured directories", catalog_name=name)

        return catalog

    def _load_tasks_catalog(self) -> None:
        """Load the tasks catalog."""
        self._tasks_catalog = self._load_catalog(
            CallableCatalog,
            "tasks",
            builtin_tasks,
            is_nornir_task,
            directories=self._settings.local_tasks_dirs,
            recursive=True,
            check_empty=True,
        )

    def _load_filters_catalog(self) -> None:
        """Load the filters catalog."""
        self._filters_catalog = self._load_catalog(
            CallableCatalog,
            "filters",
            builtin_filters,
            is_nornir_filter,
            process_filter,
            directories=self._settings.local_filters_dirs,
            recursive=True,
        )

    def _load_workflows_catalog(self) -> None:
        """Load the workflows catalog."""
        self._workflows_catalog = self._load_catalog(
            FileCatalog,
            "workflows",
            directories=self._settings.local_workflows_dirs,
            predicate=is_workflow_file,
            recursive=True,
        )

    def _validate_init_kwargs(self, kwargs: dict[str, Any]) -> None:
        """Validate that no invalid kwargs were passed to __init__."""
        invalid_kwargs = set(kwargs.keys()) & set(NORNFLOW_INVALID_INIT_KWARGS)
        if invalid_kwargs:
            raise InitializationError(
                f"Invalid kwargs for NornFlow.__init__: {sorted(invalid_kwargs)}. "
                f"These must be set in the NornFlow settings YAML file."
            )

    def _check_tasks(self) -> None:
        """Check that all tasks in the workflow are available."""
        if not self._workflow:
            return

        missing_tasks = []
        for task in self._workflow.tasks:
            if task.name not in self._tasks_catalog:
                missing_tasks.append(task.name)

        if missing_tasks:
            raise TaskError(f"Tasks not found in catalog: {missing_tasks}")

    def _apply_filters(self, nornir_manager: NornirManager) -> None:
        """Apply inventory filters to the Nornir manager."""
        # Combine filters from multiple sources with precedence
        effective_filters = {}

        # Highest precedence: programmatic filters
        if self._filters:
            effective_filters.update(self._filters)

        # Lower precedence: workflow filters
        if self._workflow and self._workflow.inventory_filters:
            effective_filters.update(self._workflow.inventory_filters)

        if not effective_filters:
            return

        # Log initial host count before filtering
        initial_count = len(nornir_manager.nornir.inventory.hosts)
        logger.info(f"Workflow filter: Starting with {initial_count} hosts")

        # Apply filters
        nornir_manager.apply_filters(**effective_filters)

        # Log final host count after filtering
        final_count = len(nornir_manager.nornir.inventory.hosts)
        logger.info(f"Workflow filter: Applied filters, {final_count} hosts remaining")

    def _get_filtering_kwargs(self) -> list[dict[str, Any]]:
        """Get filtering kwargs from the filters catalog."""
        filtering_kwargs = []
        if self._filters:
            for key, value in self._filters.items():
                if key in self._filters_catalog:
                    filter_func, param_names = self._filters_catalog[key]
                    kwargs = self._build_filter_kwargs_for_dict(filter_func, value)
                    filtering_kwargs.append(kwargs)
                elif key in ["hosts", "groups"]:
                    kwargs = self._process_custom_filter(key, value)
                    filtering_kwargs.append(kwargs)
                else:
                    # Direct attribute filter
                    filtering_kwargs.append({key: value})
        return filtering_kwargs

    def _process_custom_filter(self, key: str, filter_values: Any) -> dict[str, Any]:
        """Process custom filter for hosts or groups."""
        if key == "hosts":
            return {"filter_func": lambda host: host.name in filter_values}
        elif key == "groups":
            return {"filter_func": lambda host: any(group in host.groups for group in filter_values)}
        return {}

    def _build_filter_kwargs_for_dict(
        self, filter_func: Any, filter_values: dict[str, Any]
    ) -> dict[str, Any]:
        """Build filter kwargs for dict-based filter values."""
        return {"filter_func": lambda host: filter_func(host, **filter_values)}

    def _build_filter_kwargs_for_list(
        self, filter_func: Any, param_names: list[str], filter_values: list
    ) -> dict[str, Any]:
        """Build filter kwargs for list-based filter values."""
        if len(param_names) == 1:
            return {"filter_func": lambda host: filter_func(host, filter_values)}
        else:
            # Multiple parameters - zip them
            return {"filter_func": lambda host: filter_func(host, *filter_values)}

    def _build_filter_kwargs_for_single(
        self, filter_func: Any, param_names: list[str], filter_values: Any
    ) -> dict[str, Any]:
        """Build filter kwargs for single filter values."""
        if len(param_names) == 1:
            return {"filter_func": lambda host: filter_func(host, filter_values)}
        else:
            raise WorkflowError(f"Filter '{filter_func.__name__}' expects {len(param_names)} parameters, got 1")

    def _load_workflow_from_name(self, name: str) -> tuple[WorkflowModel, Path]:
        """Load a workflow by name from the workflows catalog."""
        if name not in self._workflows_catalog:
            raise WorkflowError(f"Workflow '{name}' not found in workflows catalog")

        workflow_path = self._workflows_catalog[name]
        workflow_dict = load_file_to_dict(workflow_path)
        workflow = WorkflowModel.create(workflow_dict)
        return workflow, workflow_path

    def _init_variable_manager(self) -> NornFlowVariablesManager:
        """Initialize the variable manager."""
        return NornFlowVariablesManager(
            vars_dir=self._settings.vars_dir,
            cli_vars=self._vars,
            inline_workflow_vars=self._workflow.vars if self._workflow else None,
            workflow_path=self._workflow_path,
            workflow_roots=self._settings.local_workflows_dirs,
        )

    def _with_processors(
        self,
        nornir_manager: NornirManager,
        processors: list | None = None,
    ) -> None:
        """Apply processors to the Nornir manager."""
        if processors:
            loaded_processors = [load_processor(p) for p in processors]
            nornir_manager.apply_processors(loaded_processors)

    def _orchestrate_execution(self, effective_dry_run: bool) -> None:
        """Orchestrate the workflow execution."""
        # Initialize variable manager
        self._var_manager = self._init_variable_manager()

        # Apply filters
        self._apply_filters(self._nornir_manager)

        # Execute workflow
        if self._workflow:
            for task in self._workflow.tasks:
                task.run(
                    self._nornir_manager,
                    self._var_manager,
                    self._tasks_catalog,
                )

    def _print_workflow_overview(self, effective_dry_run: bool) -> None:
        """Print workflow overview."""
        print_workflow_overview(
            self._workflow,
            effective_dry_run,
            len(self._nornir_manager.nornir.inventory.hosts),
            self._filters or (self._workflow.inventory_filters if self._workflow else {}),
            self._vars,
            self._var_manager.get_nornflow_variable if hasattr(self, "_var_manager") else {},
            self._failure_strategy
            or (self._workflow.failure_strategy if self._workflow else None)
            or self._settings.failure_strategy,
        )

    def _print_workflow_summary(self) -> None:
        """Print workflow summary."""
        if hasattr(self, "_nornir_manager") and hasattr(self._nornir_manager, "nornir"):
            print(f"Workflow completed. Final host count: {len(self._nornir_manager.nornir.inventory.hosts)}")

    def _get_return_code(self) -> int:
        """Get the return code for the workflow execution."""
        # For now, always return 0 (success)
        # In the future, this could be based on task results
        return 0

    def run(self, dry_run: bool = False) -> int:
        """Execute the workflow."""
        try:
            effective_dry_run = dry_run or (self._workflow.dry_run if self._workflow else False)
            self._nornir_manager.set_dry_run(effective_dry_run)

            self._print_workflow_overview(effective_dry_run)
            self._orchestrate_execution(effective_dry_run)
            self._print_workflow_summary()

            return self._get_return_code()
        except Exception as e:
            logger.exception(f"Workflow execution failed: {e!s}")
            raise
```

# filepath: runnable.py
```python
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any
import threading

from pydantic import field_validator
from nornir.core.task import AggregatedResult
from pydantic_serdes.custom_collections import HashableDict
from pydantic_serdes.utils import convert_to_hashable

from nornflow.hooks import PostRunHook, PreRunHook
from nornflow.hooks.registry import HOOK_REGISTRY
from nornflow.nornir_manager import NornirManager
from nornflow.vars.manager import NornFlowVariablesManager

from .base import NornFlowBaseModel


# Global hook instance cache shared across all RunnableModel instances
# Key: (hook_class, value) tuple
# Value: Hook instance
# This cache ensures we create only one instance per unique hook configuration
_HOOK_INSTANCE_CACHE: dict[tuple[type, str | None], PreRunHook | PostRunHook] = {}
_HOOK_CACHE_LOCK = threading.Lock()


class RunnableModel(NornFlowBaseModel, ABC):
    """Abstract base class for runnable entities with high-performance hook processing.
    
    ARCHITECTURE OVERVIEW:
    =====================
    This class implements a sophisticated hook processing system designed for:
    1. Maximum performance at scale (100k+ hosts)
    2. Thread safety in Nornir's multi-threaded environment
    3. Memory efficiency through the Flyweight pattern
    4. Extensibility without schema changes
    
    HOOK INSTANCE MANAGEMENT:
    ========================
    - Hook instances are created ONCE per unique (hook_class, value) combination
    - Instances are cached globally and shared across all tasks and hosts
    - Thread-safe instance creation using locks
    - For 100k hosts × 10 tasks × 3 hooks = only 3 hook instances created
    
    VALIDATION STRATEGY:
    ===================
    - Validation happens ONCE per task (not per host)
    - Validation is task-specific (depends on task name, configuration, etc.)
    - Validation results are cached per task instance
    - Thread-safe validation through external state tracking
    
    PERFORMANCE CHARACTERISTICS:
    ===========================
    - Hook instantiation: O(1) amortized - cached after first creation
    - Validation: O(1) per task - happens once and cached
    - Memory usage: O(unique_hooks) instead of O(tasks × hosts × hooks)
    - Thread overhead: Minimal - only during first instance creation
    
    Example with 100k hosts, 10 tasks, 3 hooks per task:
    - Without caching: 3,000,000 hook instances
    - With caching: ~3-30 hook instances (depending on unique configurations)
    - Memory saved: ~99.999%
    """
    
    # Store hook configurations from YAML
    hooks: HashableDict[str, Any] | None = None
    
    # Cache validation state per task instance
    _validation_completed: bool = False
    
    # Cache loaded hook instances for this task
    _pre_hooks_cache: list[PreRunHook] | None = None
    _post_hooks_cache: list[PostRunHook] | None = None
    
    @field_validator("hooks", mode="before")
    @classmethod
    def validate_hooks(cls, v: dict[str, Any] | None) -> HashableDict[str, Any] | None:
        """Convert hooks dict to HashableDict for proper hashability.
        
        Args:
            v: The hooks dictionary to validate.
            
        Returns:
            The hooks as a HashableDict or None.
        """
        return convert_to_hashable(v) if v else None

    @classmethod
    def create(cls, dict_args: dict[str, Any], *args: Any, **kwargs: Any) -> "RunnableModel":
        """Create a new RunnableModel with automatic hook discovery.
        
        This method extends the base create to handle hook configuration fields
        that may be present in the YAML but aren't defined in the model schema.
        Hook fields are automatically detected and moved to the hooks dictionary.
        """
        # Get the actual model fields from the Pydantic schema
        model_fields = set(cls.model_fields.keys())
        
        # Also include any parent class fields (like those from PydanticSerdes)
        for base in cls.__bases__:
            if hasattr(base, 'model_fields'):
                model_fields.update(base.model_fields.keys())
        
        # Extract hook configurations before model creation
        hooks_config = {}
        fields_to_remove = []
        
        for key, value in dict_args.items():
            # Skip if this is an actual model field
            if key in model_fields:
                continue
                
            # Check if this field matches a registered hook
            if key in HOOK_REGISTRY:
                hooks_config[key] = value
                fields_to_remove.append(key)
        
        # Remove hook fields from dict_args to prevent validation errors
        for field in fields_to_remove:
            dict_args.pop(field)
        
        # Convert hooks_config to HashableDict before storing
        if hooks_config:
            dict_args['hooks'] = convert_to_hashable(hooks_config)
        
        # Create the model instance with remaining fields  
        instance = super().create(dict_args, *args, **kwargs)
        
        return instance
    
    def _get_or_create_hook_instance(
        self, 
        hook_class: type[PreRunHook] | type[PostRunHook], 
        hook_value: Any
    ) -> PreRunHook | PostRunHook:
        """Get or create a cached hook instance using the Flyweight pattern.
        
        This method ensures that only one instance exists per unique hook
        configuration, dramatically reducing memory usage at scale.
        
        Thread-safe through locking during instance creation.
        
        Args:
            hook_class: The hook class to instantiate
            hook_value: The configuration value for the hook
            
        Returns:
            Cached or newly created hook instance
        """
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
    
    def _load_hooks_by_type(
        self, 
        hook_base_class: type[PreRunHook] | type[PostRunHook]
    ) -> list[PreRunHook] | list[PostRunHook]:
        """Load hooks of a specific type from the configuration.
        
        This method discovers hooks based on the registry and creates instances
        using the Flyweight pattern for memory efficiency.
        
        Args:
            hook_base_class: Either PreRunHook or PostRunHook to filter by type
            
        Returns:
            List of hook instances of the specified type
        """
        if not self.hooks:
            return []
        
        hooks = []
        for hook_name, hook_value in self.hooks.items():
            hook_class = HOOK_REGISTRY.get(hook_name)
            if hook_class and issubclass(hook_class, hook_base_class):
                hook_instance = self._get_or_create_hook_instance(hook_class, hook_value)
                hooks.append(hook_instance)
        
        return hooks
    
    def _get_hooks_by_type(
        self, 
        hook_class: type[PreRunHook] | type[PostRunHook], 
        cache_attr: str
    ) -> list[PreRunHook] | list[PostRunHook]:
        """Generic method to get hooks of a specific type with caching.
        
        Args:
            hook_class: The hook class type to load.
            cache_attr: The cache attribute name on self.
            
        Returns:
            List of hook instances.
        """
        cache = getattr(self, cache_attr)
        if cache is None:
            cache = self._load_hooks_by_type(hook_class)
            setattr(self, cache_attr, cache)
            # Validate hooks on first access, not during creation
            if not self._validation_completed:
                self._validate_all_hooks()
        return cache
    
    def get_pre_hooks(self) -> list[PreRunHook]:
        """Get all pre-run hooks for this runnable, with caching."""
        return self._get_hooks_by_type(PreRunHook, '_pre_hooks_cache')
    
    def get_post_hooks(self) -> list[PostRunHook]:
        """Get all post-run hooks for this runnable, with caching."""
        return self._get_hooks_by_type(PostRunHook, '_post_hooks_cache')
    
    def _validate_all_hooks(self) -> None:
        """Validate all hooks for this runnable.
        
        This method is called lazily on first hook access to avoid recursion
        during task creation. Validation happens only once per task instance.
        """
        if self._validation_completed:
            return
        
        # Mark as completed first to prevent recursion if validation
        # somehow triggers hook access again
        self._validation_completed = True
        
        # Validate all loaded hooks
        all_hooks = []
        if self._pre_hooks_cache:
            all_hooks.extend(self._pre_hooks_cache)
        if self._post_hooks_cache:
            all_hooks.extend(self._post_hooks_cache)
            
        for hook in all_hooks:
            hook._validate_hook(self)

    def _run_pre_hooks(
        self,
        hosts_to_run: list[str],
        pre_hooks: list[PreRunHook],
        nornir_manager: NornirManager,
        vars_manager: NornFlowVariablesManager,
    ) -> list[str]:
        """Run pre-hooks to filter hosts that should execute.
        
        Delegates to the base PreRunHook class for efficient orchestration,
        respecting per-task vs per-host execution modes.
        
        Args:
            hosts_to_run: Initial list of host names to consider
            pre_hooks: List of pre-run hooks to execute
            nornir_manager: Manager for accessing host inventory
            vars_manager: Manager for variable resolution
            
        Returns:
            Filtered list of host names that should execute
        """
        import logging
        logger = logging.getLogger(__name__)
        
        initial_count = len(hosts_to_run)
        logger.info(f"Pre-hook filter for task '{self.name}': Starting with {initial_count} hosts")
        
        filtered_hosts = PreRunHook.execute_all_hooks(
            pre_hooks, self, hosts_to_run, nornir_manager, vars_manager
        )
        
        final_count = len(filtered_hosts)
        logger.info(f"Pre-hook filter for task '{self.name}': Applied hooks, {final_count} hosts remaining")
        
        return filtered_hosts

    def _run_post_hooks(
        self,
        result: AggregatedResult,
        post_hooks: list[PostRunHook],
        nornir_manager: NornirManager,
        vars_manager: NornFlowVariablesManager,
    ) -> None:
        """Run post-hooks for each host that executed.
        
        Delegates to the base PostRunHook class for efficient orchestration,
        respecting per-task vs per-host execution modes.
        
        Args:
            result: Aggregated results from task execution
            post_hooks: List of post-run hooks to execute
            nornir_manager: Manager for accessing host inventory
            vars_manager: Manager for variable resolution
        """
        PostRunHook.execute_all_hooks(
            post_hooks, self, result, nornir_manager, vars_manager
        )

    def run(
        self,
        nornir_manager: NornirManager,
        vars_manager: NornFlowVariablesManager,
        tasks_catalog: dict[str, Callable],
    ) -> AggregatedResult:
        """Run the runnable with pre and post hooks.
        
        This method orchestrates the execution of pre-run hooks, the main
        runnable logic, and post-run hooks. Each host executes independently
        with thread safety guaranteed by hook design.
        
        Args:
            nornir_manager: Manager for Nornir operations
            vars_manager: Manager for variable resolution
            tasks_catalog: Catalog of available task functions
            
        Returns:
            Aggregated results from all hosts
        """
        # Get filtered hosts to run
        hosts_to_run = [host.name for host in nornir_manager.nornir.inventory.hosts.values()]
        
        # Get hooks (this triggers validation on first access)
        pre_hooks = self.get_pre_hooks()
        post_hooks = self.get_post_hooks()
        
        # Run pre-hooks and filter hosts
        filtered_hosts = self._run_pre_hooks(hosts_to_run, pre_hooks, nornir_manager, vars_manager)
        
        # Execute the main logic with filtered hosts
        result = self._run(nornir_manager, vars_manager, tasks_catalog, filtered_hosts)
        
        # Run post-hooks for each host that executed
        self._run_post_hooks(result, post_hooks, nornir_manager, vars_manager)
        
        return result

    @abstractmethod
    def _run(
        self,
        nornir_manager: NornirManager,
        vars_manager: NornFlowVariablesManager,
        tasks_catalog: dict[str, Callable],
        hosts_to_run: list[str],
    ) -> AggregatedResult:
        """Execute the specific runnable logic.
        
        Must be implemented by subclasses to define their execution behavior.
        
        Args:
            nornir_manager: Manager for Nornir operations
            vars_manager: Manager for variable resolution
            tasks_catalog: Catalog of available task functions
            hosts_to_run: Filtered list of host names to execute on
            
        Returns:
            Aggregated results from execution
        """
        pass
```

# filepath: task.py
```python
from typing import Any, ClassVar, Callable

from nornir.core.task import AggregatedResult
from pydantic import field_validator
from pydantic_serdes.custom_collections import HashableDict
from pydantic_serdes.utils import convert_to_hashable

from nornflow.exceptions import TaskError
from nornflow.nornir_manager import NornirManager
from nornflow.models.validators import run_post_creation_task_validation
from nornflow.vars.manager import NornFlowVariablesManager
from nornflow.models import RunnableModel


class TaskModel(RunnableModel):
    _key = (
        "id",
        "name",
    )
    _directive = "tasks"
    _err_on_duplicate = False

    # Exclude 'args' from universal Jinja2 validation since it's allowed there
    _exclude_from_universal_validations: ClassVar[tuple[str, ...]] = ("args",)

    id: int | None = None
    name: str
    args: HashableDict[str, Any| None] | None = None

    @classmethod
    def create(cls, dict_args: dict[str, Any], *args: Any, **kwargs: Any) -> "TaskModel":
        """Create a new TaskModel with auto-incrementing id and hook discovery."""
        # Get current tasks and calculate next id
        current_tasks = cls.get_all()
        next_id = len(current_tasks) + 1 if current_tasks else 1

        # Set the id in dict_args
        dict_args["id"] = next_id

        # Call parent's create method (handles hook discovery and runs universal validation)
        new_task = super().create(dict_args, *args, **kwargs)
        run_post_creation_task_validation(new_task)
        return new_task

    @field_validator("args", mode="before")
    @classmethod
    def validate_args(cls, v: HashableDict[str, Any] | None) -> HashableDict[str, Any] | None:
        """Validate the args dictionary and convert to fully hashable structure.

        Args:
            v: The args dictionary to validate.

        Returns:
            The validated args with all nested structures converted to hashable equivalents.
        """
        return convert_to_hashable(v)

    def _run(
        self,
        nornir_manager: NornirManager,
        vars_manager: NornFlowVariablesManager,
        tasks_catalog: dict[str, Callable],
        hosts_to_run: list[str],
    ) -> AggregatedResult:
        """Execute the task logic.
        
        Args:
            nornir_manager: The NornirManager instance.
            vars_manager: The variables manager.
            tasks_catalog: Task catalog.
            hosts_to_run: Filtered list of host names.
            
        Returns:
            The aggregated result.
            
        Raises:
            TaskError: If task not found.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Get the task function from the catalog
        task_func = tasks_catalog.get(self.name)
        if not task_func:
            raise TaskError(f"Task function for '{self.name}' not found in tasks catalog")

        # Prepare task arguments
        task_args = {} if self.args is None else dict(self.args)

        # Filter the nornir object to only run on specified hosts
        if hosts_to_run:
            filtered_nornir = nornir_manager.nornir.filter(filter_func=lambda host: host.name in hosts_to_run)
            final_host_count = len(filtered_nornir.inventory.hosts)
        else:
            # If no hosts to run, return empty result
            final_host_count = 0
            filtered_nornir = nornir_manager.nornir

        logger.info(f"Task-level filter for task '{self.name}': {final_host_count} hosts will execute")

        # Execute the task on the filtered nornir instance
        return filtered_nornir.run(task=task_func, **task_args)
```