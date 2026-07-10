---
name: apache-airflow-patterns
load-when: Designing data pipelines, orchestrating workflows, scheduling tasks
skip-when: Data transformation (see dbt-best-practices), data warehouse design (see kimball-dimensional-modeling)
---

# Apache Airflow Patterns

## Quick Reference
- DAG: directed acyclic graph of tasks
- Operator: single unit of work (BashOperator, PythonOperator, etc.)
- Task dependency: define execution order with `>>` and `<<`
- Sensor: wait for an external condition before proceeding
- XCom: pass data between tasks

## Deep Dive

### DAG Structure
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG(
    'my_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
) as dag:
    extract = PythonOperator(task_id='extract', python_callable=extract_fn)
    transform = PythonOperator(task_id='transform', python_callable=transform_fn)
    load = PythonOperator(task_id='load', python_callable=load_fn)
    
    extract >> transform >> load
```

### Task Patterns
- **Sequential**: `task1 >> task2 >> task3`
- **Parallel**: `task1 >> [task2, task3]`
- **Branching**: `BranchPythonOperator` for conditional paths
- **Merge**: `[task1, task2] >> task3`
- **Fan-out/fan-in**: split work across parallel tasks

### Sensors
Wait for external conditions:
```python
from airflow.sensors.http import HttpSensor
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor
```

### Retry and Error Handling
```python
PythonOperator(
    task_id='my_task',
    python_callable=my_fn,
    retries=3,
    retry_delay=timedelta(minutes=5),
    on_failure_callback=notify_failure,
)
```

### Backfill
- Run historical data through the pipeline
- Set `catchup=True` to backfill from start_date
- Use `backfill` command for manual runs

### Best Practices
- Keep tasks small and focused
- Use `execute` for main logic, not `__init__`
- Avoid shared state between tasks (use XCom sparingly)
- Set explicit dependencies
- Use `catchup=False` for new DAGs
- Version your DAGs

## See Also
- **dbt-best-practices** — Running dbt within Airflow
- **kimball-dimensional-modeling** — ETL pipeline design
- **great-expectations** — Data quality checks in pipelines
- **data-anti-patterns** — Common pipeline failures
