---
name: crisp-dm
load-when: Starting a data science project, planning ML workflow, structuring data analysis
skip-when: Specific techniques (see model-cards, nist-ai-rmf), data transformation (see dbt-best-practices)
---

# CRISP-DM

## Quick Reference
- 6 phases: Business Understanding → Data Understanding → Data Preparation → Modeling → Evaluation → Deployment
- Iterative: phases overlap and repeat
- Business understanding drives everything
- Document each phase for reproducibility
- Evaluation includes business impact, not just model accuracy

## Deep Dive

### Phase 1: Business Understanding
- Define business objectives
- Assess situation (resources, risks, constraints)
- Determine data mining goals
- Produce project plan

### Phase 2: Data Understanding
- Collect initial data
- Describe data (types, volume, quality)
- Explore data (distributions, correlations)
- Verify data quality

### Phase 3: Data Preparation
- Select data (relevant features)
- Clean data (handle missing values, outliers)
- Construct data (feature engineering)
- Integrate data (merge sources)
- Format data (normalization, encoding)

### Phase 4: Modeling
- Select modeling technique
- Design test (train/validation/test split)
- Build model (train, tune hyperparameters)
- Assess model (metrics, validation)

### Phase 5: Evaluation
- Evaluate results (technical metrics)
- Review process (did we meet goals?)
- Determine next steps (deploy, iterate, or restart)

### Phase 6: Deployment
- Plan deployment (integration, monitoring)
- Plan monitoring and maintenance
- Produce final report
- Review project

### Key Principles
- **Iterative**: don't expect linear progression
- **Business-driven**: technical success ≠ business success
- **Document everything**: reproducibility is critical
- **Validate rigorously**: avoid overfitting, test on held-out data

## See Also
- **model-cards** — Documenting model results
- **nist-ai-rmf** — AI risk management framework
- **great-expectations** — Data quality validation
- **dbt-best-practices** — Data transformation practices
