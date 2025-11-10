# Migration Plan: Consolidating Workflow into NornFlow

## Overview
The goal is to eliminate the `Workflow` class and merge its functionality into NornFlow, creating a single, unified class that handles all workflow execution. This will eliminate redundancy, simplify the codebase, and make the architecture clearer.

## Core Architectural Changes

### 1. **Single Runtime Class Structure**
- **NornFlow** becomes the sole runtime class for workflow execution
- **WorkflowModel** remains as a PydanticSerdes model for data validation/serialization
- **TaskModel** keeps its `run()` method to maintain separation of concerns
- **NornFlowBuilder** continues to provide fluent interface for building NornFlow instances
- **WorkflowFactory** gets completely removed (its functionality moves to NornFlow/NornFlowBuilder)
- **workflow.py** file is entirely deleted after moving necessary code

### 2. **Key Consolidations**
- All workflow orchestration logic from `Workflow.run()` moves into `NornFlow.run()`
- Variable management, filtering, and processor handling happen directly in NornFlow
- No more passing of CLI vars/filters/failure_strategy between classes - single source of truth
- NornFlow directly works with WorkflowModel for workflow definition
- Task execution remains in TaskModel.run() for separation of concerns

## Migration Order Strategy

The migration must be done in a specific order to maintain a working state as much as possible during the transition. Here's the recommended approach:

### **Phase 1: Core File Updates (Foundation)**
1. **models.py** - Keep TaskModel.run() but ensure it only handles task execution logic
2. **nornflow.py** - Absorb Workflow functionality, work directly with WorkflowModel
3. **workflow.py** - Delete entirely after moving necessary code to nornflow.py
4. **__init__.py** (root) - Update exports to remove Workflow/WorkflowFactory

### **Phase 2: Supporting Systems**
5. **settings.py** - No changes needed (already independent)
6. **nornir_manager.py** - No changes needed (already independent)
7. **utils.py** - Minor updates if any Workflow-specific utilities exist
8. **validators.py** - No changes needed (works with models)
9. **constants.py** - No changes needed
10. **exceptions.py** - No changes needed
11. **catalogs.py** - No changes needed

### **Phase 3: Variable System**
12. **manager.py** - Update any Workflow references to NornFlow
13. **processors.py** - Update any Workflow references to NornFlow
14. **proxy.py** - No changes needed
15. **context.py** - No changes needed
16. **constants.py** - No changes needed
17. **exceptions.py** - No changes needed
18. **__init__.py** - No changes needed

### **Phase 4: Builtins**
19. **tasks.py** - No changes needed
20. **filters.py** - No changes needed
21. **processors.py** - No changes needed
22. **utils.py** - No changes needed
23. **__init__.py** - No changes needed

### **Phase 5: CLI Updates**
24. **run.py** - Update to use new NornFlow structure, remove WorkflowFactory usage
25. **show.py** - Update any Workflow references
26. **init.py** - Update any Workflow references
27. **entrypoint.py** - No changes needed
28. **constants.py** - No changes needed
29. **exceptions.py** - No changes needed
30. **__init__.py** - No changes needed

### **Phase 6: Test Updates**
31. **test_workflow.py** - Delete or merge relevant tests into test_nornflow.py
32. **test_nornflow.py** - Expand to cover consolidated functionality
33. **test_workflow_filtering.py** - Merge into test_nornflow.py or rename
34. **test_models.py** - Update to reflect model changes
35. **conftest.py** - Update fixtures to use NornFlow instead of Workflow
36. **Other core tests** - Update imports and references
37. **test_run.py** - Update to reflect new structure
38. **test_show.py** - Update if needed
39. **test_init.py** - Update if needed
40. **conftest.py** - Update fixtures if needed
41. **tests/unit/vars/** - Update any Workflow references to NornFlow
42. **tests/unit/builtins/** - Likely no changes needed
43. **tests/unit/settings/** - Likely no changes needed

## Detailed Changes Per Key File

### **nornflow.py**
- Absorb all workflow orchestration methods from Workflow class:
  - `_check_tasks()` 
  - `_get_filtering_kwargs()`
  - `_process_custom_filter()`
  - `_handle_dict_parameters()`
  - `_apply_filters()`
  - `_init_variable_manager()`
  - `_with_processors()`
- Add `workflow_model` property to hold WorkflowModel instance
- Modify `run()` to orchestrate task execution (but delegate actual execution to TaskModel.run())
- Remove redundant properties that were duplicated between classes
- Constructor now accepts either a WorkflowModel or creates one from dict/file

### **models.py**
- Keep TaskModel.run() for task-specific execution logic
- Potentially enhance TaskModel.run() to better handle task hooks (like set_to, print_output, etc.)
- WorkflowModel remains unchanged (already pure data model)

### **run.py**
- Remove WorkflowFactory import and usage
- Update `get_nornflow_builder()` to work with new structure
- Simplify workflow creation logic since NornFlow handles everything

### **NornFlowBuilder**
- Remove `with_workflow_object()` method
- Update other workflow-related methods to work with WorkflowModel directly
- Simplify `build()` method since no Workflow intermediary exists

## Benefits After Migration

1. **Cleaner API**: One class (NornFlow) for workflow orchestration
2. **No State Duplication**: Single source of truth for CLI vars, filters, failure strategy
3. **Separation of Concerns**: 
   - WorkflowModel = workflow definition data
   - NornFlow = workflow orchestration
   - TaskModel = task execution
4. **Reduced Code**: Elimination of pass-through methods and duplicate state management
5. **Easier Testing**: Cleaner boundaries between components
6. **Better Encapsulation**: Task-specific logic stays with TaskModel

## Task Execution Architecture

The revised architecture for task execution:

1. **NornFlow** orchestrates the workflow and provides dependencies:
   - Manages task sequence and workflow state
   - Provides Nornir manager, variable manager, and other services
   - Handles filtering and processor integration

2. **TaskModel** handles task-specific execution:
   - Processes arguments and variables for the task
   - Implements task hooks (set_to, when, print_output, etc.)
   - Calls the actual task function via Nornir
   - Returns results to NornFlow

This maintains separation of concerns while eliminating redundancy.

## Testing Strategy During Migration

- After Phase 1: Basic workflow execution should work
- After Phase 2-4: All non-CLI functionality should work
- After Phase 5: CLI commands should work
- After Phase 6: All tests should pass

## Rollback Points

If issues arise:
- Phase 1 completion: Can revert to dual-class if needed
- Phase 5 completion: CLI still works, can fix tests incrementally
- Each phase is designed to leave the system in a working state

This plan provides a systematic approach to consolidating the codebase while minimizing risk and maintaining functionality throughout the migration process.