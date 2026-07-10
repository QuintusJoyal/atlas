---
name: nielsen-heuristics
load-when: Reviewing UI design, usability testing, UX design decisions
skip-when: Accessibility requirements (see wcag-2-1-checklist), design system (see material-design-principles)
---

# Nielsen's 10 Usability Heuristics

## Quick Reference
1. Visibility of system status
2. Match between system and real world
3. User control and freedom
4. Consistency and standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility and efficiency of use
8. Aesthetic and minimalist design
9. Help users recognize and recover from errors
10. Help and documentation

## Deep Dive

### 1. Visibility of System Status
Keep users informed about what's happening through appropriate feedback within reasonable time.
- Loading indicators, progress bars, status messages

### 2. Match Between System and Real World
Use language and concepts familiar to the user, not system-oriented terms. Follow real-world conventions.
- Use "Cart" not "Shopping Basket Entity"

### 3. User Control and Freedom
Users need "emergency exit" for unwanted states. Support undo and redo.
- Back button, cancel, undo

### 4. Consistency and Standards
Follow platform conventions. Users shouldn't have to wonder if different words mean the same thing.
- Consistent navigation, consistent terminology

### 5. Error Prevention
Better than good error messages: design that prevents problems from occurring in the first place.
- Confirmation dialogs, constraints on input

### 6. Recognition Rather Than Recall
Make objects and options visible. Minimize memory load by using recognition.
- Recent items, autocomplete, visible options

### 7. Flexibility and Efficiency of Use
Accelerators for expert users that don't encumber novice users.
- Keyboard shortcuts, customization, batch operations

### 8. Aesthetic and Minimalist Design
Interfaces should not contain information that is irrelevant or rarely needed.
- Every extra unit of information competes with relevant units

### 9. Help Users Recognize and Recover from Errors
Error messages should be expressed in plain language, precisely indicate the problem, and suggest a solution.
- "Password must contain at least 8 characters" not "Error 422"

### 10. Help and Documentation
It's better if the system doesn't need documentation, but it may be necessary. Make it searchable and task-focused.

## See Also
- **wcag-2-1-checklist** — Accessibility requirements (complementary)
- **material-design-principles** — Design system implementing many heuristics
- **quality-bars** — UX quality criteria
- **review-checklists** — UX review criteria
