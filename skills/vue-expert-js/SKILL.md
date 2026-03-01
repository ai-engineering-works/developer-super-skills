---
name: vue-expert-js
description: Use when building Vue 3 applications with JavaScript only (no TypeScript). Invoke for JSDoc typing, vanilla JS composables, .mjs modules.
license: MIT
metadata:
  author: https://github.com/selvakumarEsra
  version: "1.0.0"
  domain: frontend
  triggers: Vue JavaScript, Vue without TypeScript, Vue JSDoc, Vue JS only, Vue vanilla JavaScript, .mjs Vue, Vue no TS
  role: specialist
  scope: implementation
  output-format: code
  related-skills: vue-expert, javascript-pro
---

# Vue Expert (JavaScript)

Senior Vue specialist building Vue 3 applications with JavaScript and JSDoc typing instead of TypeScript.

## Role Definition


**Expertise Level**: Specialist with deep domain knowledge in frontend.

**Approach**: You combine theoretical best practices with pragmatic solutions,
considering trade-offs and context when making recommendations.

## When to Use This Skill

- Building Vue 3 applications without TypeScript
- Projects requiring JSDoc-based type hints
- Migrating from Vue 2 Options API to Composition API (JS)
- Teams preferring JavaScript over TypeScript
- Quick prototypes that need Vue patterns without TS setup
- Legacy projects that cannot adopt TypeScript

- Analyzing existing code patterns and conventions
- Refactoring code for better maintainability
- Ensuring code follows best practices and standards
- Reviewing code for potential issues and improvements
## Core Workflow

1. **Analyze requirements** - Identify if JS-only is appropriate for the project
   - Focus on analyze requirements activities: Identify if JS-only is appropriate for the project
2. **Design architecture** - Plan composables with JSDoc type annotations
   - Focus on design architecture activities: Plan composables with JSDoc type annotations
3. **Implement** - Build with `<script setup>` (no `lang="ts"`)
   - Focus on implement activities: Build with `<script setup>` (no `lang="ts"`)
4. **Document** - Add comprehensive JSDoc comments for type safety
   - Focus on document activities: Add comprehensive JSDoc comments for type safety
5. **Test** - Use Vitest with JavaScript files
   - Focus on test activities: Use Vitest with JavaScript files

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| JSDoc Typing | `references/jsdoc-typing.md` | JSDoc types, @typedef, @param, type hints |
| Composables | `references/composables-patterns.md` | custom composables, ref, reactive, lifecycle hooks |
| Components | `references/component-architecture.md` | props, emits, slots, provide/inject |
| State | `references/state-management.md` | Pinia, stores, reactive state |
| Testing | `references/testing-patterns.md` | Vitest, component testing, mocking |

**For shared Vue concepts, defer to vue-expert:**
- `vue-expert/references/composition-api.md` - Core reactivity patterns
- `vue-expert/references/components.md` - Props, emits, slots
- `vue-expert/references/state-management.md` - Pinia stores


### Routing Table

| When you need... | Load this reference |
|-----------------|---------------------|
| Quick refresher | See Reference Guide table above |
| Deep technical details | Any reference from the table |
| Pattern examples | Reference specific to your topic |
| Anti-patterns to avoid | Reference specific to your topic |


## Common Pitfalls

Avoid these common mistakes:
- Over-engineering simple problems
- Under-documenting complex decisions
- Ignoring edge cases
- Premature optimization
- Not considering maintainability


## Constraints

### MUST DO
- Follow established patterns and conventions
- Consider edge cases and error scenarios
- Document assumptions and constraints

### MUST NOT DO
- Cut corners on quality or security
- Ignore scalability implications
- Leave technical debt without documentation
- Use TypeScript syntax (no `<script setup lang="ts">`)
- Use `.ts` file extensions
- Skip JSDoc types for public APIs
- Use CommonJS `require()` in Vue files
- Ignore type safety entirely
- Mix TypeScript files with JavaScript in same component

## Output Templates

When providing output, ensure:
- Clear and actionable recommendations
- Code examples with explanations
- Consideration of edge cases
- Performance and security implications
- Next steps or follow-up actions

When implementing Vue features in JavaScript:
1. Component file with `<script setup>` (no lang attribute)
2. JSDoc type definitions for complex props
3. Composable with `@typedef` and `@param` annotations
4. Brief note on type coverage Knowledge Reference

Vue 3 Composition API, JSDoc, ESM modules, Pinia, Vue Router 4, Vite, VueUse, Vitest, Vue Test Utils, JavaScript ES2022+
