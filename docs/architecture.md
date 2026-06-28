# System Architecture

## Overview

This project is structured as a small production-style optimization service for oil-and-gas maintenance scheduling.

The architecture separates data loading, validation, optimization, diagnostics, API delivery, and testing.

## High-Level Flow

```text
Input Data
    ↓
Data Loading
    ↓
Data Validation
    ↓
Optimization Model
    ↓
Google OR-Tools CP-SAT Solver
    ↓
Schedule Output
    ↓
Diagnostics
    ↓
FastAPI Endpoint
```

## Components

### 1. Data Layer

Location:

```text
data/
```

Files:

```text
assets.csv
technicians.csv
maintenance_tasks.csv
maintenance_windows.csv
solver_config.json
```

This layer stores structured maintenance scheduling inputs.

### 2. Data Loader

Location:

```text
optimizer/data_loader.py
```

Responsible for reading CSV and JSON files into Python data structures.

It loads:

* Assets
* Technicians
* Maintenance tasks
* Maintenance windows
* Solver configuration

### 3. Validation Layer

Location:

```text
optimizer/validator.py
```

Responsible for checking whether the input data is usable before optimization.

Validation checks include:

* Required columns
* Duplicate IDs
* Invalid task durations
* Invalid shift times
* Invalid priority values
* Missing asset references
* Missing technician skills
* Impossible maintenance windows

### 4. Optimization Layer

Location:

```text
optimizer/scheduler.py
```

This is the main optimization engine.

It builds a CP-SAT model using Google OR-Tools and applies:

* Assignment constraints
* Skill constraints
* Time-window constraints
* Shift constraints
* No-overlap constraints

The solver returns an optimized maintenance schedule.

### 5. Diagnostics Layer

Location:

```text
optimizer/diagnostics.py
```

Responsible for producing useful information about the optimization run.

Diagnostics include:

* Number of tasks
* Number of technicians
* Number of decision variables
* Solver time limit
* Number of scheduled tasks
* Technician workload hours

### 6. API Layer

Location:

```text
app/main.py
app/schemas.py
```

The FastAPI layer exposes the optimizer as a backend service.

Endpoints:

```text
GET /health
POST /optimize-maintenance
```

The API returns structured JSON output using Pydantic response schemas.

### 7. Testing Layer

Location:

```text
tests/
```

Tests verify that:

* Data validation works
* The scheduler returns a feasible or optimal result
* Every task is assigned
* Technicians are not assigned overlapping tasks

## Deployment Style

The current version runs locally using FastAPI and Uvicorn.

Command:

```bash
python -m uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Future Architecture Improvements

Possible future improvements include:

* Docker containerization
* Database storage for scenarios and results
* Scenario comparison
* Travel-time optimization
* Dashboard visualization
* Background optimization jobs
* Authentication and role-based access
* Integration with maintenance management systems
