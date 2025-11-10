# Documentation Update Requirements Analysis

After thoroughly analyzing the codebase and existing documentation, here are the required changes to align docs with the current implementation:

## 1. **NEW DOCUMENT REQUIRED: `hooks_guide.md`**

**Rationale:** The hooks system is a major feature that has evolved significantly. It deserves dedicated documentation.

**Required Content:**
- Explanation of hooks as Nornir processors in disguise
- Hook architecture (processor-based, flyweight pattern)
- Lifecycle methods available to hooks
- Creating custom hooks (registration, validation, exception handling)
- Built-in hooks detailed reference:
  - `if` hook (filter-based AND Jinja2 expression modes)
  - `set_to` hook (simple storage AND extraction paths, including special prefixes like `_failed`, `_changed`, `_result`)
  - `shush` hook (output suppression signaling mechanism)
- Hook execution scopes (`run_once_per_task`)
- Hook context injection mechanism
- Custom exception handling in hooks
- Performance characteristics (Flyweight pattern, caching)
- Examples of each built-in hook with real-world use cases

---

## 2. **core_concepts.md - CRITICAL UPDATES REQUIRED**

### Section: Architecture Overview - Component Relationships

**Issue:** Mentions `RunnableModel` which no longer exists (renamed to `HookableModel`)

**Required Changes:**
- Update all references from `RunnableModel` to `HookableModel`
- Update the component diagram if it shows `RunnableModel`
- Add explanation that `HookableModel` is now the base for hook-supporting models
- Clarify that `HookableModel` is abstract and focused on hook management, not execution

### Section: Processors

**Issue:** Does not mention `NornFlowHookProcessor` which is now a critical built-in processor

**Required Changes:**
- Add `NornFlowHookProcessor` to the list of built-in processors
- Explain its role as the orchestrator for all hooks
- Document that hooks are registered and executed through this processor
- Explain the two-tier context system (workflow context + task-specific context)
- Document that it's automatically added when hooks are present

### NEW Section Required: Hooks

**Required Content:**
- Introduction to hooks as a task extension mechanism
- Explain hooks vs processors distinction
- Reference to the new `hooks_guide.md` for details
- Brief overview of built-in hooks
- Explain hook registration system

---

## 3. **variables_basics.md - MODERATE UPDATES REQUIRED**

### Section: Runtime Variables (#6)

**Issue:** Does not explain `set_to` hook's extraction capabilities or special prefixes

**Required Changes:**
- Expand the `set_to` hook section significantly
- Document the two modes: simple storage vs. extraction
- Document extraction path syntax (dot notation, bracket indexing, nested access)
- Document special prefixes: `_failed`, `_changed`, `_result`
- Provide examples of complex extractions like `environment.cpu.0.%usage`
- Explain the difference between storing complete Result vs extracting specific data

### Section: Accessing Nornir's Inventory Variables

**Issue:** This section is accurate but should cross-reference the host proxy implementation

**Required Changes:**
- Add a note about the `NornirHostProxy` class providing read-only access
- Mention that this is managed by `NornFlowVariableProcessor`

---

## 4. **api_reference.md - EXTENSIVE UPDATES REQUIRED**

### Section: Model Classes

**Issue:** Still references `RunnableModel` instead of `HookableModel`

**Required Changes:**
- Replace all `RunnableModel` references with `HookableModel`
- Document `HookableModel` class:
  - Purpose: Abstract base for models supporting hooks
  - Key methods: `get_hooks()`, `run_hook_validations()`, `get_task_args()`, `validate_hooks_and_set_task_context()`
  - Properties: hooks, `_hooks_cache`, `_hook_processor_cache`
  - Explain Flyweight pattern implementation for hook instances
- Document `TaskModel` changes:
  - Note that it now inherits from `HookableModel` instead of `RunnableModel`
  - Update method signatures if changed
  - Document immutability constraints (CRITICAL - hashable models)

### NEW Section Required: Hook Classes

**Required Content:**
- `Hook` base class documentation:
  - Constructor signature and parameters
  - Lifecycle methods (all processor methods)
  - `hook_name` class attribute requirement
  - `run_once_per_task` class attribute
  - `exception_handlers` class attribute
  - `context` property and context injection
  - `should_execute()` method
  - `execute_hook_validations()` method
- Built-in hook classes:
  - `IfHook`: Configuration formats, validation, execution flow
  - `SetToHook`: Configuration formats, extraction paths, special prefixes
  - `ShushHook`: Configuration, processor compatibility check

### Section: Built-in Processors

**Issue:** Missing `NornFlowHookProcessor`

**Required Changes:**
- Add `NornFlowHookProcessor` documentation:
  - Purpose and role in hook system
  - Context management (workflow + task-specific)
  - Properties: `workflow_context`, `task_specific_context`, `context`, `task_hooks`
  - Hook delegation mechanism
  - Exception handling delegation

### Section: Variable System Classes

**Issue:** Missing details about `NornirHostProxy` and its role

**Required Changes:**
- Add `NornirHostProxy` class documentation:
  - Read-only access to Nornir inventory
  - Properties: `current_host`, `nornir`, `current_host_name`
  - `__getattr__` magic method behavior
  - Error handling for missing attributes

---

## 5. **jinja2_filters.md - MINOR UPDATES REQUIRED**

### Section: NornFlow Python Wrapper Filters

**Issue:** Table shows outdated filter names and descriptions

**Required Changes:**
- Verify all filter names match actual implementation in py_wrapper_filters.py
- Update examples if filter behavior has changed
- Ensure all filters from `PY_WRAPPER_FILTERS` dict are documented

### Section: NornFlow Custom Filters

**Issue:** Should verify all custom filters are documented

**Required Changes:**
- Cross-check with `CUSTOM_FILTERS` dict in custom_filters.py
- Ensure all filters have examples
- Verify filter signatures match implementation

---

## 6. **failure_strategies.md - NO CHANGES REQUIRED**

**Status:** This document accurately reflects the current implementation. The failure strategies logic has not changed.

---

## 7. **nornflow_settings.md - MINOR UPDATES REQUIRED**

### Section: Optional Settings

**Issue:** Should document `local_hooks_dirs` setting

**Required Changes:**
- Add `local_hooks_dirs` documentation:
  - Description: Directories containing custom hook implementations
  - Type: `list[str]`
  - Default: `["hooks"]`
  - Example configuration
  - Note about recursive search

---

## 8. **quick_start.md - MODERATE UPDATES REQUIRED**

### Section: Initialize Your Project

**Issue:** Does not mention hooks directory in the created structure

**Required Changes:**
- Add `📁 hooks` to the list of directories created by `nornflow init`
- Update the description of what each directory contains

### NEW Section Required: Using Hooks

**Required Content:**
- Brief introduction to hooks as task extensions
- Simple example using `shush` hook
- Simple example using `if` hook with Jinja2 expression
- Simple example using `set_to` hook
- Reference to `hooks_guide.md` for comprehensive documentation

---

## 9. **NEW DOCUMENT REQUIRED: `design_patterns.md`**

**Rationale:** The codebase demonstrates sophisticated use of design patterns. This deserves documentation for developers extending NornFlow.

**Required Content:**
- Builder Pattern (NornFlowBuilder)
- Proxy Pattern (NornirHostProxy)
- Strategy Pattern (FailureStrategy)
- Template Method Pattern (Hook base class)
- Flyweight Pattern (Hook instance caching)
- Decorator Pattern (hook_delegator, skip_if_condition_flagged)
- Facade Pattern (NornFlow class)
- Registry Pattern (HOOK_REGISTRY)
- Observer Pattern (Processor protocol)
- Factory Method Pattern (load_hooks, load_processor)
- For each pattern:
  - Theory explanation
  - Implementation location in codebase
  - Why this pattern was chosen
  - Code examples

---

## Summary of Required Actions

### New Documents (2):
1. `hooks_guide.md` - Comprehensive hook system documentation
2. `design_patterns.md` - Software engineering patterns used in NornFlow

### Major Updates (2):
1. core_concepts.md - RunnableModel → HookableModel, add hooks section, update processors
2. api_reference.md - Model class updates, new Hook classes section, processor updates

### Moderate Updates (2):
1. variables_basics.md - Expand set_to hook documentation with extraction capabilities
2. quick_start.md - Add hooks directory, add hooks usage section

### Minor Updates (2):
1. jinja2_filters.md - Verify filter names and examples match implementation
2. nornflow_settings.md - Add local_hooks_dirs setting

### No Changes (1):
1. failure_strategies.md - Accurate as-is

---

## Prioritization Recommendation

**Phase 1 (Critical):**
1. Create `hooks_guide.md` - This is entirely new functionality
2. Update core_concepts.md - Fixes incorrect references and adds critical concepts
3. Update api_reference.md - Developers need accurate API documentation

**Phase 2 (Important):**
4. Update variables_basics.md - Users need to understand set_to extraction
5. Update quick_start.md - First-time users need to know about hooks
6. Update nornflow_settings.md - Complete settings reference

**Phase 3 (Nice to Have):**
7. Create `design_patterns.md` - For advanced users/contributors
8. Update jinja2_filters.md - Verification pass