# Clarifying Questions

Techniques for asking effective questions that reveal true user intent and requirements.

## Principles

### One Question at a Time

**❌ BAD:** Multiple questions in one message
> "What's the target audience? What platform? What's your timeline? What's your budget?"

**✅ GOOD:** Single focused question
> "Who is the primary target audience for this feature?"

### Multiple Choice When Possible

**Why:** Easier to answer, reduces ambiguity, faster decisions

**✅ GOOD:**
> "What's most important for this feature:
> a) Ease of use for non-technical users
> b) Performance and speed
> c) Flexibility and power-user features
> d) Quick development time"

### Open-Ended When Exploring

**When:** The domain is new, options aren't clear, or context is needed

**✅ GOOD:**
> "Can you describe the current workflow users follow? I want to understand what happens before and after this feature."

## Question Types by Phase

### Early Phase: Context

**Goal:** Understand the landscape

- "What problem does this solve for users?"
- "What are users currently doing instead?"
- "What's the business impact of this problem?"
- "Who are the primary stakeholders?"

### Middle Phase: Requirements

**Goal:** Specific details and constraints

**Technical:**
- "What's the expected data volume/users per day?"
- "Any latency requirements for responses?"
- "What platforms/browsers need support?"

**Business:**
- "What's the timeline for this feature?"
- "Is there a budget constraint?"
- "What defines success for this project?"

**Constraints:**
- "Are there any technical limitations we should know about?"
- "What existing systems must we integrate with?"
- "Are there regulatory/compliance requirements?"

### Late Phase: Validation

**Goal:** Confirm understanding and edge cases

- "Just to confirm: [summarize understanding]. Is that accurate?"
- "What happens if [edge case scenario]?"
- "Are there any use cases we haven't discussed?"

## Probing Techniques

### The "Why" Ladder

Ask "why" multiple times to get to root motivation:

> "Why do you need this feature?"
> → "To improve user engagement"
> → "Why is engagement down?"
> → "Users complain about slow load times"
> → Real need: Performance optimization, not new features

### Scenario-Based Questions

Put users in specific situations:

> "Imagine a user who just signed up and wants to accomplish [goal]. What steps do they take today? What should they be able to do?"

### Constraint Questions

Reveal limitations early:

> "What would make you say this project failed?"
> "What's absolutely NOT negotiable in this solution?"
> "If we had to cut one feature, which one would you cut?"

## Question Traps to Avoid

### ❌ Leading Questions

"Wouldn't you agree that X is better than Y?"

### ❌ Yes/No Questions (when complexity exists)

"Will this be fast?" (What does "fast" mean?)

### ❌ Assumption-Laden Questions

"How should we handle the database connection?" (Assumes there is one)

### ❌ Technical Jargon (with non-technical stakeholders)

"Should we use WebSockets or Server-Sent Events?"

## Handling Answers

### Confirm Understanding

Repeat back what you heard:

> "So to confirm: you need this to work on mobile devices, but desktop isn't a concern right now. Is that correct?"

### Follow-Up Naturally

Based on their answer, ask the logical next question:

> "You mentioned 10,000 users per day. Is that spread evenly, or are there peak times we need to handle?"

### Explore Contradictions

When answers conflict with previous statements:

> "Earlier you mentioned quick development was key, but now you're describing a complex architecture. Can you help me understand the priority?"

## Sample Question Sequences

### For a New Feature

1. "What problem does this solve for your users?"
2. "Who is experiencing this problem most often?"
3. "What are they currently doing to work around it?"
4. "If we could solve this perfectly, what would that look like?"
5. "What's most important: speed, cost, or quality?"
6. "Are there any technical constraints we should know about?"
7. "What's your timeline for this project?"

### For Performance Issues

1. "Where are you seeing slowness specifically?"
2. "When did this start? Was it gradual or sudden?"
3. "How many users/requests per second are we talking about?"
4. "What have you already tried to diagnose this?"
5. "Are there specific times of day when it's worse?"
6. "What's an acceptable response time for your users?"
