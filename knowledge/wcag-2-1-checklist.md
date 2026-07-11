---
name: wcag-2-1-checklist
load-when: Implementing accessibility, reviewing accessibility compliance, accessibility testing
skip-when: UX design principles (see nielsen-heuristics), design system (see material-design-principles)
---

# WCAG 2.1 Checklist

## Quick Reference
- 3 levels: A (minimum), AA (standard), AAA (enhanced)
- 4 principles: Perceivable, Operable, Understandable, Robust
- Most legal requirements target AA compliance
- Test with screen readers, keyboard navigation, and contrast checkers
- Accessibility is not optional — it's a legal requirement in many jurisdictions

## Deep Dive

### POUR Principles
| Principle | Description | Key Requirements |
|-----------|-------------|-----------------|
| Perceivable | Information must be presentable | Alt text, captions, contrast |
| Operable | Interface must be navigable | Keyboard access, no traps, timing |
| Understandable | Information must be clear | Readable, predictable, input assistance |
| Robust | Content must work with assistive tech | Valid HTML, ARIA, compatibility |

### Level AA Requirements (Most Common)
- 1.1.1 Non-text Content (alt text)
- 1.3.1 Info and Relationships (semantic HTML)
- 1.4.3 Contrast Minimum (4.5:1 normal, 3:1 large)
- 1.4.11 Non-text Contrast (3:1 UI components)
- 2.1.1 Keyboard accessible
- 2.4.1 Bypass blocks (skip links)
- 2.4.3 Focus Order
- 2.4.6 Headings and Labels
- 3.1.1 Language of Page
- 3.2.3 Consistent Navigation
- 4.1.2 Name, Role, Value

### Testing Methods
- **Automated**: axe, Lighthouse, WAVE
- **Manual**: keyboard navigation, screen reader testing
- **User testing**: with people with disabilities

### Common Failures
- Missing alt text on images
- Insufficient color contrast
- No keyboard access to interactive elements
- Missing form labels
- No skip navigation link
- Auto-playing media without controls

## See Also
- **nielsen-heuristics** — UX usability principles
- **material-design-principles** — Design system with accessibility built in
- **definition-of-done** — Completion criteria includes accessibility
- **review-checklists** — Accessibility review criteria
