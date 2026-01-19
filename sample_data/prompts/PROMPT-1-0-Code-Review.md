---
version: "1.0"
type: PROMPT
---

# Code Review Checklist

Use this prompt when reviewing pull requests or code changes.

## Functionality

- [ ] Does the code work as intended?
- [ ] Are all acceptance criteria met?
- [ ] Are edge cases handled?
- [ ] Is error handling appropriate?

## Code Quality

- [ ] Is the code readable and self-documenting?
- [ ] Are variable and function names descriptive?
- [ ] Is there unnecessary complexity?
- [ ] Are there any code smells or anti-patterns?

## Testing

- [ ] Are there tests for new functionality?
- [ ] Do existing tests still pass?
- [ ] Is test coverage adequate?
- [ ] Are tests meaningful (not just for coverage)?

## Security

- [ ] Is user input properly validated?
- [ ] Are there any security vulnerabilities?
- [ ] Are secrets/credentials properly managed?
- [ ] Is authentication/authorization correct?

## Performance

- [ ] Are there any obvious performance issues?
- [ ] Are database queries optimized?
- [ ] Is caching used appropriately?
- [ ] Are there any unnecessary loops or operations?

## Documentation

- [ ] Is code adequately commented?
- [ ] Are complex algorithms explained?
- [ ] Is public API documented?
- [ ] Is README updated if needed?

## Best Practices

- [ ] Does code follow project conventions?
- [ ] Are dependencies used appropriately?
- [ ] Is code DRY (Don't Repeat Yourself)?
- [ ] Are there any TODO/FIXME comments to address?

## Review Comments

When providing feedback:
- Be constructive and specific
- Explain *why*, not just *what*
- Suggest alternatives
- Acknowledge good practices
- Ask questions to understand intent

---

**Example Review Comment**:
```
Consider using list comprehension here for better readability:

items = [process(x) for x in data if x.is_valid]

This is more Pythonic than a for-loop with append.
```
