# Execution Options

Two approaches for executing implementation plans: subagent-driven vs. parallel session.

## Overview

After completing a plan, offer the user two execution options. Each has different benefits.

## Option 1: Subagent-Driven (Same Session)

Execute the plan task-by-task in the current session, using subagents for each task.

### How It Works

1. You stay in the current session
2. For each task in the plan:
   - You dispatch a fresh subagent to execute that task
   - You review the subagent's work when it completes
   - You make corrections if needed
   - You move to the next task

### Benefits

- ✅ **Fast iteration** - Immediate feedback between tasks
- ✅ **Course correction** - Catch issues early
- ✅ **Oversight** - Review every step
- ✅ **Interactive** - Can adjust plan as you go

### Drawbacks

- ⚠️ **Token intensive** - Full context in main session
- ⚠️ **Slower overall** - Review overhead per task
- ⚠️ **Single session** - Must complete in one sitting

### When to Choose

- **Complex implementation** - Need careful oversight
- **Uncertain requirements** - May need to adjust approach
- **Learning project** - Want to see how each step works
- **Time-boxed work** - Have dedicated session time

### Execution Flow

```python
for task in plan.tasks:
    print(f"Starting Task {task.number}: {task.name}")

    # Dispatch subagent with the task
    subagent_result = dispatch_subagent(
        task=task,
        context=current_context
    )

    # Review the result
    review_result(subagent_result)

    # Make corrections if needed
    if needs_correction(subagent_result):
        corrected = correct(subagent_result)
        commit_changes(corrected)

    print(f"Completed Task {task.number}")
```

## Option 2: Parallel Session (Separate)

Execute the entire plan in a separate session using the executing-plans skill.

### How It Works

1. Guide user to open a new Claude Code session
2. User runs `executing-plans` skill with the plan file
3. The new session executes all tasks with checkpoints
4. User returns to original session when done

### Benefits

- ✅ **Parallel work** - Continue working in main session
- ✅ **Faster execution** - No per-task review overhead
- ✅ **Isolated context** - Clean environment for implementation
- ✅ **Batch execution** - Complete multiple tasks at once

### Drawbacks

- ⚠️ **Less oversight** - Don't see each step
- ⚠️ **Later feedback** - Issues found at checkpoints
- ⚠️ **Session management** - Need to coordinate sessions
- ⚠️ **Complex setup** - Worktree isolation needed

### When to Choose

- **Straightforward implementation** - Clear requirements
- **Well-defined plan** - Confident in approach
- **Parallel work needed** - Want to continue in main session
- **Large implementation** - Too much for one session

### Execution Flow

```python
# User opens new session
new_session = create_session(worktree=plan.worktree)

# Load executing-plans skill
new_session.load_skill("executing-plans")

# Execute plan with checkpoints
result = new_session.execute_plan(
    plan_file=plan.path,
    checkpoints=['every 3 tasks', 'on errors']
)

# Return to original session
return_when_done(new_session)
```

## Decision Guide

Choose based on these factors:

| Factor | Subagent-Driven | Parallel Session |
|--------|----------------|------------------|
| **Complexity** | Complex | Simple to moderate |
| **Uncertainty** | High uncertainty | Well-defined |
| **Oversight needed** | Yes | No |
| **Time pressure** | Have session time | Need parallel work |
| **Plan quality** | First draft | Validated plan |
| **Team preference** | Hands-on | Hands-off |

## Presenting the Choice

After saving the plan, present both options:

```markdown
## Execution Options

Plan complete and saved to `docs/plans/<filename>.md`.

**Option 1: Subagent-Driven (This Session)**

I'll dispatch a fresh subagent for each task and review their work before moving to the next task. This provides:
- Immediate feedback and correction
- Step-by-step oversight
- Interactive debugging

Best for: Complex implementations, uncertain requirements, or when learning the codebase.

**Option 2: Parallel Session (Separate)**

Open a new session with the executing-plans skill. It will execute all tasks with periodic checkpoints. This provides:
- Parallel work (continue in this session)
- Faster batch execution
- Isolated implementation environment

Best for: Straightforward implementations with clear requirements.

**Which approach would you like?**
```

## After User Chooses

### If Subagent-Driven

```markdown
Great, I'll execute the plan task-by-task in this session.

**Required:** Use subagent-driven-development skill for execution workflow.

Starting with Task 1: [Task name]...
```

### If Parallel Session

```markdown
Great! Here's how to proceed:

1. **Open a new terminal/tab** and navigate to the project worktree
2. **Start a new Claude Code session** in that directory
3. **Run this command:**
   ```
   executing-plans docs/plans/<plan-filename>.md
   ```
4. The new session will execute all tasks with checkpoints
5. **Come back here** when implementation is complete

**I'll wait here** - ping me when you're done or if you need help!
```

## Hybrid Approach

For very large implementations, you can combine both:

1. **First N tasks** - Use subagent-driven to validate approach
2. **Remaining tasks** - Switch to parallel session for bulk execution
3. **Final review** - Return to original session for acceptance

This gives you oversight during critical early tasks and efficiency for the rest.

## Checkpoints in Parallel Execution

When using parallel session, specify checkpoint frequency:

```markdown
## Execution Configuration

**Checkpoints:**
- After every 3 tasks
- On any error
- After completing each major component

**On checkpoint:**
- Commit changes
- Summarize progress
- Wait for confirmation to continue
```

## Handling Errors

### Subagent-Driven

- You see the error immediately
- Can fix it yourself or guide subagent
- Continue once resolved

### Parallel Session

- Session pauses on error
- User notified of checkpoint
- User can:
  - Fix error and continue
  - Adjust plan and restart
  - Return to original session for help
