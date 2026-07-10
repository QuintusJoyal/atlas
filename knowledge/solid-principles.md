---
name: solid-principles
load-when: Reviewing code design, refactoring, evaluating architecture
skip-when: Specific refactoring (see refactoring-patterns), clean code details (see clean-code-practices)
---

# SOLID Principles

## Quick Reference
- **S**ingle Responsibility: one class = one reason to change
- **O**pen/Closed: open for extension, closed for modification
- **L**iskov Substitution: subtypes must be substitutable for base types
- **I**nterface Segregation: many specific interfaces > one general interface
- **D**ependency Inversion: depend on abstractions, not concretions

## Deep Dive

### Single Responsibility (SRP)
A class should have only one reason to change.
- Bad: `User` class handles auth, profile, and notifications
- Good: `AuthService`, `UserProfile`, `NotificationService`

### Open/Closed (OCP)
Software entities should be open for extension, closed for modification.
- Bad: modify existing class to add behavior
- Good: extend via inheritance, composition, or plugins

### Liskov Substitution (LSP)
Objects of a superclass should be replaceable with objects of a subclass without breaking the program.
- Bad: `Square` extends `Rectangle` but breaks `setWidth`/`setHeight`
- Good: separate `Shape` interface with `area()` method

### Interface Segregation (ISP)
No client should be forced to depend on methods it doesn't use.
- Bad: `IWorker` interface with `work()`, `eat()`, `sleep()`
- Good: `IWorkable`, `IFeedable`, `ISleepable`

### Dependency Inversion (DIP)
High-level modules should not depend on low-level modules. Both should depend on abstractions.
- Bad: `OrderService` directly instantiates `MySQLDatabase`
- Good: `OrderService` depends on `IDatabase` interface

### Applying SOLID
- Start with SRP (most common violation)
- Use DIP to enable testability
- Apply OCP when you anticipate change
- Apply ISP when interfaces grow too large
- Verify LSP with polymorphic code

## See Also
- **clean-code-practices** — Code quality fundamentals
- **refactoring-patterns** — How to apply SOLID in practice
- **test-driven-development** — TDD naturally enforces SOLID
- **swebok** — Software engineering knowledge areas
