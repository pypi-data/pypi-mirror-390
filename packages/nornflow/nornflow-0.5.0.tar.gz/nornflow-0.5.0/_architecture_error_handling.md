# NornFlow Error Handling - Architectural Design

## Overview

This document outlines the architectural approach for implementing error handling policies in NornFlow. The feature will allow users to control workflow behavior when tasks fail, with options to immediately fail, continue with unaffected hosts, or run all tasks before reporting failures.

## Core Architecture Decision

**Implementation through a dedicated processor: `NornFlowErrorHandlingProcessor`**

This processor will be automatically included in every workflow execution, similar to how the `NornFlowVariableProcessor` is currently handled, ensuring error handling is available regardless of user-defined processor configurations.

## Key Components

### 1. Error Policy Enum

A new enum in `constants.py` will define the supported policies:
- `CONTINUE`: Skip failed hosts in subsequent tasks, continue with others (default)
- `FAIL_FAST`: Stop execution immediately on first error
- `FAIL_AT_END`: Run all tasks on all hosts, report failures at completion

### 2. Model & Settings Updates

- Add `error_policy` field to the `Workflow` model, defaulting to `CONTINUE`
- Add error handling configuration to `NornFlowSettings`
- Implement validation for error policy values

### 3. NornFlowErrorHandlingProcessor

A new processor class with the following capabilities:
- Track task execution results and failures by host/task
- Control exception propagation based on active policy
- Filter the Nornir inventory to remove failed hosts in `CONTINUE` mode (default behavior)
- Collect comprehensive error information for reporting
- Generate summary reports for `CONTINUE` and `FAIL_AT_END` modes

### 4. Workflow Integration

Modify the `Workflow._with_processors` method to:
- Always include `NornFlowErrorHandlingProcessor` in the processor chain
- Pass the active error policy to the processor
- Ensure the error handler is positioned appropriately in the processor chain

### 5. CLI Extensions

Add a new `--error-policy` option to the CLI run command that:
- Accepts values matching the supported policies
- Overrides workflow and global settings
- Provides appropriate help text and validation
- Defaults to `CONTINUE` when not specified

## Implementation Sequence

1. Create the `ErrorPolicy` enum and update models/settings
2. Implement the `NornFlowErrorHandlingProcessor` class
3. Modify the `Workflow._with_processors` method
4. Add CLI parameter handling
5. Implement error summary reporting
6. Add tests for all components

## Error Handling Workflow

1. User specifies an error policy (CLI, workflow YAML, or global settings)
2. When a task generates an exception:
   - `FAIL_FAST`: The exception propagates up, stopping execution
   - `CONTINUE` (default): The processor catches the exception, logs it, and removes the host from inventory
   - `FAIL_AT_END`: The processor catches the exception, logs it, but keeps the host in inventory
3. For non-`FAIL_FAST` modes, the processor generates a summary of failures at workflow completion
4. For `FAIL_AT_END`, the workflow still exits with an error status if any tasks failed

## Advantages of This Approach

- **Industry alignment:** Default `CONTINUE` behavior matches expectations from tools like Ansible
- **Practical efficiency:** By default, failures on individual hosts won't stop automation for others
- **Guaranteed functionality:** Works regardless of user processor choices
- **Separation of concerns:** Error handling logic is isolated and focused
- **User flexibility:** Maintains user choice to override error handling at multiple levels
- **Progressive complexity:** Simple workflows work intuitively, while advanced options are available when needed

This architecture ensures that NornFlow's error handling is robust, consistent, and aligns with user expectations while maintaining compatibility with existing workflows and custom processors. The default `CONTINUE` policy provides a balance between resilience and safety that's appropriate for most automation scenarios.




-----


# Error Handling Policies Implementation Plan

Based on the architectural design and documentation, here's a comprehensive list of code changes needed to implement the error handling policies feature:

## 1. Add ErrorPolicy Enum in constants.py
- Create an enum class for the three error policies: CONTINUE (default), FAIL_FAST, and FAIL_AT_END

## 2. Update Models and Settings
- Add `error_policy` field to the `Workflow` model in models.py
- Add error handling configuration to `NornFlowSettings` in settings.py
- Add validation for error policy values

## 3. Create NornFlowErrorHandlingProcessor
- Create a new processor class in the builtins/processors directory
- Implement task/host tracking logic
- Implement error catching and host filtering for CONTINUE mode
- Implement error collection for FAIL_AT_END mode
- Add results summary generation

## 4. Update Workflow._with_processors
- Modify the method to always include the error handling processor
- Position it appropriately in the processor chain
- Pass the active error policy to the processor

## 5. Add CLI Parameter Support
- Add `--error-policy` option to the CLI run command
- Implement validation and help text
- Update workflow creation to honor the CLI parameter

## 6. Add Error Summary Reporting
- Implement detailed error summary formatting
- Add support for showing which hosts/tasks failed
- Create methods for displaying summaries at workflow completion

## 7. Add Tests
- Create tests for each error policy
- Test CLI parameter handling
- Test workflow-level configuration
- Test global settings configuration
- Test error summary reporting

## 8. Update Documentation
- Finalize error_handling.md with any implementation details
- Update any other relevant docs that reference error handling

Let me know which component you'd like me to implement first, and I'll provide the complete code for that file.