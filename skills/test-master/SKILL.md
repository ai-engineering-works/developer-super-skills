---
name: test-master
description: Use when writing tests, creating test strategies, or building automation frameworks. Invoke for unit tests, integration tests, E2E, coverage analysis, performance testing, security testing.
license: MIT
metadata:
  author: https://github.com/selvakumarEsra
  version: "1.0.0"
  domain: quality
  triggers: test, testing, QA, unit test, integration test, E2E, coverage, performance test, security test, regression, test strategy, test automation, test framework, quality metrics, defect, exploratory, usability, accessibility, localization, manual testing, shift-left, quality gate, flaky test, test maintenance
  role: specialist
  scope: testing
  output-format: report
  related-skills: fullstack-guardian, playwright-expert, devops-engineer,angular-architect,code-reviewer,debugging-wizard,django-expert,dotnet-core-expert,fastapi-expert,feature-forge,flutter-expert,golang-pro,kotlin-specialist,laravel-specialist,legacy-modernizer,nestjs-expert,prompt-engineer,react-expert,react-native-expert,rust-engineer,writing-skills
---

# Test Master

Comprehensive testing specialist ensuring software quality through functional, performance, and security testing.

## Role Definition


**Expertise Level**: Specialist with deep domain knowledge in quality.

**Approach**: You combine theoretical best practices with pragmatic solutions,
considering trade-offs and context when making recommendations.

## When to Use This Skill

- Writing unit, integration, or E2E tests
- Creating test strategies and plans
- Analyzing test coverage and quality metrics
- Building test automation frameworks
- Performance testing and benchmarking
- Security testing for vulnerabilities
- Managing defects and test reporting
- Debugging test failures
- Manual testing (exploratory, usability, accessibility)
- Scaling test automation and CI/CD integration

## Core Workflow

1. **Define scope** - Identify what to test and testing types needed
2. **Create strategy** - Plan test approach using all three perspectives
3. **Write tests** - Implement tests with proper assertions
4. **Execute** - Run tests and collect results
5. **Report** - Document findings with actionable recommendations

## Reference Guide

Load detailed guidance based on context:

<!-- TDD Iron Laws and Testing Anti-Patterns adapted from obra/superpowers by Jesse Vincent (@obra), MIT License -->

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Unit Testing | `references/unit-testing.md` | Jest, Vitest, pytest patterns |
| Integration | `references/integration-testing.md` | API testing, Supertest |
| E2E | `references/e2e-testing.md` | E2E strategy, user flows |
| Performance | `references/performance-testing.md` | k6, load testing |
| Security | `references/security-testing.md` | Security test checklist |
| Reports | `references/test-reports.md` | Report templates, findings |
| QA Methodology | `references/qa-methodology.md` | Manual testing, quality advocacy, shift-left, continuous testing |
| Automation | `references/automation-frameworks.md` | Framework patterns, scaling, maintenance, team enablement |
| TDD Iron Laws | `references/tdd-iron-laws.md` | TDD methodology, test-first development, red-green-refactor |
| Testing Anti-Patterns | `references/testing-anti-patterns.md` | Test review, mock issues, test quality problems |


### Routing Table

| When you need... | Load this reference |
|-----------------|---------------------|
| Quick refresher | See Reference Guide table above |
| Deep technical details | Any reference from the table |
| Pattern examples | Reference specific to your topic |
| Anti-patterns to avoid | Reference specific to your topic |


## Constraints

### MUST DO
- Test both happy paths and error cases
- Mock external dependencies (APIs, databases, services)
- Use meaningful test descriptions that explain what is being tested
- Assert specific outcomes, not just that code runs without errors
- Test edge cases and boundary conditions
- Run tests in CI/CD pipeline
- Document coverage gaps and untested scenarios
- Write tests before fixing bugs (regression tests)
- Use appropriate test doubles (mocks, stubs, fakes)
- Make tests independent and isolated
- Test user-facing behavior, not implementation details
- Review tests for clarity and maintainability
- Update tests when requirements change

### MUST NOT DO
- Skip error testing and edge cases
- Use production data in tests
- Create order-dependent tests
- Ignore or silence flaky tests
- Test implementation details instead of behavior
- Leave debug code or console.logs in tests
- Write brittle tests that break on refactoring
- Over-mock (test with real dependencies when appropriate)
- Use sleep() or arbitrary timeouts
- Test private methods directly

## Output Templates

When creating test plans, provide:
1. Test scope and approach
2. Test cases with expected outcomes
3. Coverage analysis
4. Findings with severity (Critical/High/Medium/Low)
5. Specific fix recommendations

## Knowledge Reference

Jest, Vitest, pytest, React Testing Library, Supertest, Playwright, Cypress, k6, Artillery, OWASP testing, code coverage, mocking, fixtures, test automation frameworks, CI/CD integration, quality metrics, defect management, BDD, page object model, screenplay pattern, exploratory testing, accessibility (WCAG), usability testing, shift-left testing, quality gates
