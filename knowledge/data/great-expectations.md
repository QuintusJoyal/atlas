---
name: great-expectations
load-when: Validating data quality, building expectation suites, monitoring data pipelines
skip-when: Data transformation (see dbt-best-practices), pipeline orchestration (see apache-airflow-patterns)
---

# Great Expectations

## Quick Reference
- Expectations: assertions about data (column values, row counts, schema)
- Expectation Suite: collection of expectations for a dataset
- Validation: run expectations against data, get pass/fail results
- Data Docs: auto-generated documentation from expectations
- Checkpoints: automated validation in pipelines

## Deep Dive

### Core Concepts
- **Expectation**: a test on your data (e.g., `column_values_to_not_be_null`)
- **Expectation Suite**: a named collection of expectations
- **Batch**: a set of data to validate against expectations
- **Checkpoint**: an automated validation step

### Common Expectations
```python
expect_column_values_to_not_be_null("user_id")
expect_column_values_to_be_unique("email")
expect_column_values_to_be_in_set("status", ["active", "inactive"])
expect_table_row_count_to_be_between(1000, 1000000)
expect_column_values_to_match_regex("phone", r"^\+?1?\d{10,14}$")
```

### Creating Expectations
1. Connect to data source
2. Build expectation suite interactively
3. Save suite to JSON file
4. Run validation
5. Review results

### Validation Results
```python
result = context.run_checkpoint("my_checkpoint")
print(result.success)  # True/False
print(result.statistics)  # pass/fail/warning counts
```

### Integration Patterns
- **In pipeline**: add checkpoint after data load
- **Before training**: validate training data
- **On schedule**: daily validation of production data
- **On demand**: validate before release

### Data Docs
Auto-generated HTML documentation:
- Expectations by dataset
- Validation results history
- Data profiling statistics

## See Also
- **kimball-dimensional-modeling** — Dimensional model quality requirements
- **dbt-best-practices** — Testing in dbt (complementary)
- **apache-airflow-patterns** — Running validation in pipelines
- **data-anti-patterns** — Common data quality failures
