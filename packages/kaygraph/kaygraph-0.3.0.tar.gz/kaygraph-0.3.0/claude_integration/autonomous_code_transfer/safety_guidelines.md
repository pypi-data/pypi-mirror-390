# Safety Guidelines for Autonomous Code Transfer

> **CRITICAL**: These rules MUST be followed at all times during autonomous execution.

## Core Principles

1. **Fail Safe, Not Silent** - Report all issues immediately, never hide errors
2. **Validate Before Commit** - Always check syntax and tests before finalizing changes
3. **Preserve Functionality** - Existing features must continue to work
4. **Document Everything** - Every action must be logged with reasoning

## MUST DO - Required Actions

### Before Every File Modification
- [ ] Create git checkpoint with meaningful message
- [ ] Read and understand the file's current purpose
- [ ] Verify this is the correct file to modify

### When Creating/Modifying Files
- [ ] Follow existing code conventions (indentation, naming, structure)
- [ ] Validate syntax before saving (run linter/compiler)
- [ ] Add appropriate comments for complex logic
- [ ] Update related tests if modifying logic
- [ ] Check for breaking changes to existing APIs

### After File Changes
- [ ] Run relevant tests (unit, integration)
- [ ] Check for compilation/lint errors
- [ ] Verify no regressions in existing functionality
- [ ] Update documentation if public APIs changed
- [ ] Log what was changed and why

### When Installing Dependencies
- [ ] Verify dependency is necessary and safe
- [ ] Check compatibility with existing dependencies
- [ ] Use specific versions, not "latest"
- [ ] Update both package.json/requirements.txt AND lock files
- [ ] Run security audit if available (npm audit, safety check)

### When Running Commands
- [ ] Understand what the command does before executing
- [ ] Check if command requires sudo (never use sudo)
- [ ] Verify command will not delete data
- [ ] Capture and log output
- [ ] Check exit code for success/failure

## NEVER DO - Forbidden Actions

### File Operations
- ❌ NEVER delete files without explicit backup
- ❌ NEVER modify more than 5 files in a single step
- ❌ NEVER overwrite files without reading them first
- ❌ NEVER commit without running tests
- ❌ NEVER ignore syntax/lint errors

### Dependencies
- ❌ NEVER install dependencies without checking compatibility
- ❌ NEVER use `--force` flags when installing packages
- ❌ NEVER modify package manager files without validation
- ❌ NEVER install beta/alpha versions without explicit approval

### Security
- ❌ NEVER commit secrets, API keys, or passwords
- ❌ NEVER disable security features (CSP, CORS, auth)
- ❌ NEVER expose sensitive data in logs
- ❌ NEVER create public endpoints without authentication
- ❌ NEVER use eval() or similar dangerous functions

### Testing
- ❌ NEVER skip test execution
- ❌ NEVER ignore test failures
- ❌ NEVER comment out failing tests
- ❌ NEVER mock out critical security checks

### Code Quality
- ❌ NEVER use hard-coded values for config (use environment variables)
- ❌ NEVER use TODO/FIXME as permanent solution
- ❌ NEVER copy-paste code without understanding it
- ❌ NEVER introduce code smells (long functions, deep nesting)

## Error Handling Requirements

### When Errors Occur
1. **Log the error** with full context (file, line, operation)
2. **Attempt rollback** to last known good state (checkpoint)
3. **Report to monitoring** with alert level appropriate to severity
4. **Pause execution** if error is critical
5. **Never continue** if tests fail or syntax is invalid

### Rollback Triggers
Automatically rollback if:
- Syntax errors in modified files
- Test failures introduced by changes
- Compilation fails
- Dependencies fail to install
- Runtime errors in basic operations

## Validation Checklist

After EACH step, verify:

- [ ] **Syntax Valid**: All modified files have valid syntax
- [ ] **Tests Pass**: All relevant tests passing
- [ ] **No Regressions**: Existing functionality still works
- [ ] **Conventions Followed**: Code matches codebase style
- [ ] **Dependencies Resolved**: All imports/requires work
- [ ] **Documentation Updated**: If public APIs changed
- [ ] **Checkpoint Created**: Git commit with clear message

## Step Size Limits

To maintain safety and rollback capability:

- **Maximum 5 files** modified per step
- **Maximum 1 hour** execution time per step
- **Maximum 500 lines** changed per file per step
- **One logical change** per step (don't mix concerns)

## Context Engineering

### Always Return to Goal
If you ever feel "lost" or uncertain:
1. Read `task.md` to remember the original goal
2. Read `research.md` to recall findings
3. Read `plan.md` to see the current step
4. Never proceed without clear understanding

### Markdown File Usage
- `task.md` - The source of truth for what we're doing
- `research.md` - Context from analysis phase
- `plan.md` - Step-by-step execution plan
- `implementation.md` - Execution log
- Return to these files frequently

## Cost and Resource Limits

- **Respect max_cost_usd**: Stop if budget exceeded
- **Respect max_runtime**: Timeout if exceeded
- **Check rate limits**: Space API calls appropriately
- **Monitor memory**: Don't load huge files into memory
- **Clean up resources**: Close files, connections, etc.

## Human Escalation

Pause and request human intervention if:
- **Critical test failures** that can't be automatically fixed
- **Breaking changes** required to existing public APIs
- **Security concerns** discovered in codebase
- **Ambiguous requirements** that need clarification
- **Budget or time limits** about to be exceeded
- **Unexpected errors** that occur repeatedly

## Success Criteria

A step is only complete when:
1. All files syntactically valid
2. All tests passing
3. Git checkpoint created
4. Execution log updated
5. No errors in output
6. Progress toward goal confirmed

---

**Remember**: Safety > Speed. Better to pause for clarification than to introduce bugs or break existing functionality.

**When in doubt**: Pause, log the situation, and request human review.
