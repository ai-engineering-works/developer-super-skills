# Design Documentation

Creating clear, actionable design documents that guide implementation.

## Document Purpose

Design documents:
- Communicate decisions to all stakeholders
- Provide implementation guidance to developers
- Document reasoning for future reference
- Ensure alignment before coding begins

## Document Structure

### Header Template

```markdown
# [Feature Name] Design Document

**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Approved | Implemented

---

## Overview

**Goal:** [One sentence describing what this builds]

**Problem Statement:** [What problem does this solve?]

**Scope:** [What's included vs. what's out of scope]

---

## Requirements

### Functional Requirements
- [Requirement 1]
- [Requirement 2]

### Non-Functional Requirements
- **Performance:** [Response time, throughput, etc.]
- **Scalability:** [User growth, data volume expectations]
- **Reliability:** [Uptime, error handling requirements]
- **Security:** [Authentication, authorization, data protection]

### Constraints
- **Technical:** [Technology limitations, compatibility]
- **Business:** [Timeline, budget, resource limits]
- **Regulatory:** [Compliance requirements]

---

## Architecture

### System Overview
[2-3 paragraphs describing the architecture]

### Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| [Name] | [What it does] | [Tech choice] |

### Data Flow
[Diagram or description of how data moves through the system]

### API/Interface Design
[Key endpoints, interfaces, or protocols]

---

## Implementation Approach

### Phases
1. **Phase 1:** [MVP features]
2. **Phase 2:** [Additional features]
3. **Phase 3:** [Future enhancements]

### Technical Decisions

| Decision | Options Chosen | Rationale |
|----------|----------------|-----------|
| [What] | [Which option] | [Why] |
| [What] | [Which option] | [Why] |

---

## Testing Strategy

### Unit Tests
[What needs unit testing]

### Integration Tests
[How components interact]

### E2E Tests
[Critical user workflows]

### Performance Tests
[Load testing, stress testing if applicable]

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| [Risk] | Low/Med/High | Low/Med/High | [How we address it] |

---

## Alternatives Considered

### Option A: [Name]
- **Pros:** [Benefits]
- **Cons:** [Drawbacks]
- **Why not chosen:** [Reason]

### Option B: [Name]
- **Pros:** [Benefits]
- **Cons:** [Drawbacks]
- **Why not chosen:** [Reason]

---

## Open Questions

| Question | Status | Resolution |
|----------|--------|------------|
| [What needs clarification] | Open/Resolved | [Answer if resolved] |

---

## Appendix

### Glossary
[Define technical terms or domain-specific language]

### References
[Links to related docs, specs, standards]
```

## Writing Guidelines

### Be Specific

**❌ Vague:**
> "The system should be fast and responsive."

**✅ Specific:**
> "API responses must return within 200ms for 95% of requests. Maximum acceptable response time is 500ms."

### Show, Don't Just Tell

**❌ Words only:**
> "The frontend will communicate with the backend via REST."

**✅ Include diagrams:**
```
[Architecture diagram showing components and connections]

Frontend → API Gateway → Service A → Database
                  ↘ Service B → Cache
```

### Document Reasoning

For each significant decision, explain:

1. **What** decision was made
2. **Why** this option was chosen
3. **What alternatives** were considered
4. **What trade-offs** were accepted

This helps future maintainers understand the context.

### Keep Sections Focused

- One main idea per section
- Use subsections for detail
- Link to external docs rather than duplicating
- Remove anything that doesn't add value

## Review Process

### Before Presenting

1. **Self-review**
   - Does this address the problem?
   - Is it implementable from this doc?
   - Are requirements testable?
   - Are trade-offs documented?

2. **Peer review**
   - Get feedback from technical peers
   - Check for overlooked edge cases
   - Verify technical feasibility

### Presenting to Stakeholders

1. **Executive summary first** - 2-minute overview
2. **Deep dive by section** - Let them ask questions
3. **Confirm after each section** - Get incremental approval
4. **Document feedback** - Capture requested changes

## Updating the Document

### When to Update

- Requirements change
- New constraints discovered
- Better approach identified
- Implementation reveals issues

### Version Control

- Commit design doc before implementation
- Create new version for significant changes
- Document what changed and why in commit message

### Change Log Format

```markdown
## Change History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| YYYY-MM-DD | 1.0 | Initial design | [Name] |
| YYYY-MM-DD | 1.1 | Added caching strategy | [Name] |
```

## Common Anti-Patterns

### ❌ Over-Documenting

Writing 50 pages for a simple feature. Keep documentation proportional to complexity.

### ❌ Premature Optimization

Designing for millions of users when you have hundreds. Solve real problems, not hypothetical ones.

### ❌ Ignoring Constraints

Designs that require resources you don't have. Always work within constraints.

### ❌ Implementation Detail Too Early

Specific function signatures before architecture is settled. Focus on what and why, not how.

### ❌ No Exit Strategy

Designs that are hard to change or revert. Always consider how to adapt or roll back.
