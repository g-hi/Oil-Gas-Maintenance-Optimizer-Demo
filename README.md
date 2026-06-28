# Oil & Gas Maintenance Scheduling Optimizer

A production-style maintenance scheduling optimizer for oil and gas operations using **Google OR-Tools CP-SAT**, **FastAPI**, **Streamlit**, and **Docker**.

## Overview

This project demonstrates how constraint optimization can be used to schedule industrial maintenance tasks for oil-and-gas assets such as pumps, compressors, separators, pipelines, storage tanks, generators, control valves, desalter units, and wellheads.

The optimizer assigns maintenance tasks to qualified technicians while respecting technician skills, shift availability, task duration, maintenance windows, asset priority, and non-overlapping work schedules.

The project is inspired by Saudi oil-and-gas operations. Since real operational maintenance work orders, technician rosters, and shutdown windows are typically confidential, this project uses realistic simulated maintenance scheduling data.

## Key Features

* Google OR-Tools CP-SAT optimization model
* FastAPI backend with Swagger documentation
* Streamlit dashboard for interactive scenario testing
* Dockerized backend deployment
* Scenario-based optimization
* Validation and feasibility diagnostics
* Technician workload analysis
* Unit tests with Pytest
* Modular project structure suitable for extension

## Tech Stack

* Python
* Google OR-Tools CP-SAT
* FastAPI
* Pydantic
* Pandas
* Pytest
* Uvicorn
* Streamlit
* Docker

## Project Structure

```text
oil-gas-maintenance-optimizer/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
│
├── optimizer/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── validator.py
│   ├── scheduler.py
│   ├── diagnostics.py
│   └── scenario_loader.py
│
├── data/
│   ├── assets.csv
│   ├── technicians.csv
│   ├── maintenance_tasks.csv
│   ├── maintenance_windows.csv
│   └── solver_config.json
│
├── scenarios/
│   ├── normal_operations.json
│   ├── emergency_maintenance.json
│   ├── technician_unavailable.json
│   └── tight_shutdown_window.json
│
├── gui/
│   └── streamlit_app.py
│
├── outputs/
│   └── sample_result.json
│
├── tests/
│   ├── test_data_validation.py
│   └── test_scheduler.py
│
├── docs/
│   ├── problem_formulation.md
│   └── architecture.md
│
├── Dockerfile
├── .dockerignore
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Optimization Problem

The system schedules maintenance tasks by deciding:

* Which technician should handle each maintenance task
* When each task should start
* Whether the schedule satisfies operational constraints
* How to prioritize urgent and high-criticality work

## Hard Constraints

1. Each task must be assigned exactly once.
2. A technician must have the required skill for the task.
3. A technician cannot work on overlapping tasks.
4. Tasks must fit inside their maintenance windows.
5. Tasks must fit inside technician shift hours.
6. Invalid scenarios must return clear validation errors.

## Objective

The current objective is to schedule higher-priority maintenance tasks earlier while producing a feasible non-overlapping schedule.

## Scenarios

The project supports multiple operational scenarios.

### Available Scenarios

```text
normal_operations
emergency_maintenance
technician_unavailable
tight_shutdown_window
```

### Scenario Descriptions

| Scenario                 | Description                                                          |
| ------------------------ | -------------------------------------------------------------------- |
| `normal_operations`      | Baseline planned maintenance schedule with all technicians available |
| `emergency_maintenance`  | Adds an urgent high-priority compressor inspection task              |
| `technician_unavailable` | Removes a technician to test validation and feasibility              |
| `tight_shutdown_window`  | Applies tighter maintenance windows to selected tasks                |

The `technician_unavailable` scenario demonstrates how the system handles infeasible or invalid operational conditions. For example, if the only compressor technician is unavailable, the API returns a validation failure with an explanatory error message.

## Running Locally

Create and activate a virtual environment:

```bash
python -m venv venv
```

Activate on Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the optimizer locally:

```bash
python main.py
```

## Running the FastAPI Backend

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check

```text
GET /health
```

### List Scenarios

```text
GET /scenarios
```

### Run Default Optimization

```text
POST /optimize-maintenance
```

### Run Scenario-Based Optimization

```text
POST /optimize-scenario/{scenario_name}
```

Example:

```text
POST /optimize-scenario/emergency_maintenance
```

## Streamlit Dashboard

The project includes a Streamlit dashboard for running default and scenario-based optimization.

First, start the FastAPI backend:

```bash
python -m uvicorn app.main:app --reload
```

Then, in a second terminal, run the dashboard:

```bash
streamlit run gui/streamlit_app.py
```

The dashboard supports:

* Default maintenance optimization
* Scenario-based optimization
* Scenario selection
* Solver status
* Objective value
* Runtime
* Scheduled task count
* Optimized schedule table
* Technician workload table
* Workload bar chart
* Diagnostics summary
* Validation and feasibility errors
* Raw diagnostics JSON in an expandable section

## Docker Deployment

Build the Docker image:

```bash
docker build -t oil-gas-maintenance-api .
```

Run the API container on port `8000`:

```bash
docker run -p 8000:8000 oil-gas-maintenance-api
```

If port `8000` is already in use, run the container on port `8001`:

```bash
docker run -d --name oil-gas-maintenance-api-container -p 8001:8000 oil-gas-maintenance-api
```

Open the Dockerized API documentation:

```text
http://127.0.0.1:8001/docs
```

Check running containers:

```bash
docker ps
```

Stop the container:

```bash
docker stop oil-gas-maintenance-api-container
```

Remove the container:

```bash
docker rm oil-gas-maintenance-api-container
```

## Using Streamlit with Docker Backend

If the Docker backend is running on port `8001`, update the API URL in `gui/streamlit_app.py`:

```python
API_URL = "http://127.0.0.1:8001"
```

Then run:

```bash
streamlit run gui/streamlit_app.py
```

This allows the Streamlit GUI to call the Dockerized FastAPI backend.

## Sample Optimization Output

```json
{
  "status": "OPTIMAL",
  "objective_value": 402,
  "runtime_seconds": 0.0497,
  "schedule": [
    {
      "task_id": "M001",
      "asset_id": "A001",
      "task_name": "Pump vibration inspection",
      "technician_id": "T001",
      "start": 10,
      "end": 13,
      "priority": 5
    }
  ],
  "diagnostics": {
    "num_tasks": 10,
    "num_technicians": 6,
    "num_decision_variables": 67,
    "time_limit_seconds": 10,
    "scheduled_tasks": 10,
    "technician_workload_hours": {
      "T001": 5,
      "T002": 6,
      "T006": 6,
      "T005": 7,
      "T004": 2,
      "T003": 2
    },
    "scenario_name": null,
    "scenario_description": null
  },
  "errors": null
}
```

## Example Validation Failure

For the `technician_unavailable` scenario, the system may return:

```json
{
  "status": "VALIDATION_FAILED",
  "objective_value": null,
  "runtime_seconds": 0,
  "schedule": [],
  "diagnostics": {
    "num_tasks": 10,
    "num_technicians": 5,
    "num_decision_variables": 0,
    "time_limit_seconds": 10,
    "scheduled_tasks": 0,
    "technician_workload_hours": {},
    "scenario_name": "technician_unavailable",
    "scenario_description": "Compressor technician T002 is unavailable, forcing reassignment or infeasibility."
  },
  "errors": [
    "No technician has the following required skills: ['compressor']"
  ]
}
```

## Testing

Run tests:

```bash
python -m pytest
```

Current tests cover:

* Data validation
* Feasible schedule generation
* Technician assignment
* No-overlap constraint

## Current Status

Completed:

* Data loading
* Data validation
* CP-SAT scheduling model
* FastAPI API layer
* Scenario-based optimization
* Streamlit dashboard
* Diagnostics dashboard
* Dockerized FastAPI backend
* Local Docker backend tested successfully
* Streamlit connected to Docker backend

## Future Improvements

* Add travel time between locations
* Add overtime penalties
* Add spare parts availability
* Add technician cost optimization
* Add scenario comparison dashboard
* Add database storage
* Add authentication
* Add cloud deployment
* Add CI/CD with GitHub Actions
* Add Gantt chart visualization
* Add REST API request body for custom task uploads
