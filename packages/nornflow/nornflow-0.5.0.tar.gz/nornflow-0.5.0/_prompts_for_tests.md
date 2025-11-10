# NornFlow Test Files Requiring Changes

Based on the error message and the codebase restructuring where the `workflow.py` module has been removed, here's a prioritized list of test files that need updating:

## Core Priority Files (Direct import issues)
1. ✅ conftest.py - Already partially fixed, needs verification
2. test_workflow.py - Likely heavily relies on the removed `Workflow` class
3. test_workflow_filtering.py - Tests for workflow filtering functionality
4. test_failure_strategies.py - Referenced `WorkflowFactory` class
5. test_nornflow.py - Likely has workflow class references
6. test_processors.py - May reference workflow processing

## CLI-Related Test Files
7. conftest.py - May have workflow fixtures
8. test_run.py - Command for running workflows
9. test_show.py - Command for displaying workflow information
10. test_init.py - May reference workflow initialization

## Potential Additional Files
11. Any other test files importing from `nornflow.workflow`
12. Tests for features that might interact with workflow functionality

The key changes will involve:
- Replacing `Workflow` imports with `WorkflowModel`
- Updating test methods to align with the new architecture
- Fixing any method calls that changed in the refactoring
- Ensuring all workflow-related tests reflect the current implementation

I can help you update these files one by one, starting with any file you'd like to tackle first.