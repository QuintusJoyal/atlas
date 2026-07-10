---
name: refactoring-patterns
load-when: Improving code structure, fixing code smells, preparing for new features
skip-when: Writing new code (see clean-code-practices), design principles (see solid-principles)
---

# Refactoring Patterns

## Quick Reference
- Extract Method: pull code into a named function
- Rename: make names reveal intent
- Move Method/Field: place code where it belongs
- Inline: remove unnecessary indirection
- Replace Conditional with Polymorphism: use OOP for complex branching
- Always refactor with tests passing

## Deep Dive

### Code Smells and Refactoring
| Smell | Refactoring |
|-------|-------------|
| Long Method | Extract Method |
| Large Class | Extract Class |
| Long Parameter List | Introduce Parameter Object |
| Divergent Change | Split Module |
| Shotgun Surgery | Move Method/Fold In |
| Feature Envy | Move Method |
| Data Clumps | Extract Class |
| Primitive Obsession | Replace with Value Object |
| Switch Statements | Replace with Polymorphism |
| Parallel Inheritance | Extract Superclass |

### Extract Method
```python
# Before
def print_balance(account):
    print("Statement")
    print("-" * 20)
    print(f"Name: {account.name}")
    print(f"Balance: ${account.balance:.2f}")

# After
def print_balance(account):
    print_header()
    print_account_info(account)

def print_header():
    print("Statement")
    print("-" * 20)

def print_account_info(account):
    print(f"Name: {account.name}")
    print(f"Balance: ${account.balance:.2f}")
```

### Rename
Names should reveal intent. Rename when you understand the purpose better.

### Move Method
When a method uses more data from another class than its own, move it.

### Safe Refactoring Checklist
1. All tests pass before starting
2. Make one change at a time
3. Run tests after each change
4. Commit frequently
5. Use automated refactoring tools when available

## See Also
- **clean-code-practices** — Code quality fundamentals
- **solid-principles** — Design principles
- **test-driven-development** — TDD provides safety net for refactoring
- **anti-patterns** — Patterns that indicate refactoring is needed
