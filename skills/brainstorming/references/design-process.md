# Design Process

The systematic approach to transforming ideas into fully formed designs through collaborative dialogue.

## Process Overview

Effective design happens through structured dialogue, not instant solutions. Follow this process to ensure all stakeholders understand and approve the design before implementation begins.

## Phase 1: Context Gathering

Before asking questions, understand the project context:

1. **Review existing documentation** - Read relevant docs, README, recent commits
2. **Check codebase structure** - Understand current architecture and patterns
3. **Identify constraints** - Technical, time, resource, or business constraints
4. **Clarify scope** - What's in scope vs. out of scope

## Phase 2: Clarifying Questions

Ask questions one at a time to refine understanding:

### Question Types

**Multiple Choice (Preferred)**
- Easier for users to answer
- Reduces ambiguity
- Faster decision-making

**Example:**
> "Should this feature prioritize:
> a) Performance and speed
> b) Flexibility and configurability
> c) Simplicity and ease of use"

**Open-Ended (When Needed)**
- When exploring new territory
- When user needs to explain context
- When options aren't clear yet

### Key Topics to Cover

1. **Purpose** - What problem does this solve? Who benefits?
2. **Constraints** - Technical limits, business rules, timing
3. **Success Criteria** - How will we know it works?
4. **Scope** - What's included vs. what's future work
5. **Users** - Who will use this? What are their skill levels?

## Phase 3: Approaches

Always propose 2-3 approaches with trade-offs:

### Structure for Each Approach

```
### Approach 1: [Name] (Recommended)

**Pros:**
- Benefit 1
- Benefit 2

**Cons:**
- Drawback 1
- Drawback 2

**Best for:** [When this approach shines]

**Estimated complexity:** [Low/Medium/High]
```

### How to Choose Recommendations

Base your recommendation on:
- Project constraints (time, resources, complexity)
- Team expertise
- Maintenance considerations
- Long-term viability

## Phase 4: Present Design

Present design in sections, getting approval after each:

### Section Structure

1. **Architecture Overview** - High-level structure (2-3 sentences)
2. **Components** - Key pieces and their relationships
3. **Data Flow** - How data moves through the system
4. **Error Handling** - What happens when things go wrong
5. **Testing Strategy** - How we'll verify it works

### Scale Detail to Complexity

- **Simple projects** - 1-2 sentences per section
- **Medium projects** - 3-5 sentences per section
- **Complex projects** - Full paragraphs with diagrams

### Check After Each Section

> "Does this section look right so far? Any concerns or changes?"

## Phase 5: Document and Approve

1. **Write design document** - Save to `docs/plans/YYYY-MM-DD-<topic>-design.md`
2. **Get final approval** - Explicit user confirmation
3. **Transition to planning** - Invoke writing-plans skill

## Anti-Patterns

### ❌ Rushing to Implementation

Skipping design because "it's simple" leads to wasted work.

### ❌ Multiple Questions at Once

Overwhelming users with multiple questions reduces quality of answers.

### ❌ Single Approach

Only presenting one option removes user choice and buy-in.

### ❌ Vague Descriptions

"Faster performance" doesn't tell us what we're optimizing for.

### ❌ Ignoring Constraints

Designs that ignore technical or business constraints won't work.

## Tips for Success

- **One question per message** - Wait for answer before next question
- **Multiple choice preferred** - Use when options are clear
- **Propose trade-offs** - Help users understand costs/benefits
- **Get incremental approval** - Validate as you go, not at the end
- **Be flexible** - Willing to go back and clarify based on feedback
