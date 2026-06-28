# Problem Formulation

## Business Problem

Oil and gas facilities operate critical assets such as pumps, compressors, separators, pipelines, valves, generators, storage tanks, and wellheads. These assets require planned maintenance, inspection, calibration, and testing.

The objective of this project is to generate an optimized maintenance schedule by assigning maintenance tasks to qualified technicians while respecting operational constraints.

## Optimization Goal

The system decides:

* Which technician should perform each maintenance task
* What time each task should start
* Whether the final schedule is feasible
* How technician workload is distributed

## Input Data

The optimizer uses four main data files:

### Assets

`data/assets.csv`

Contains oil-and-gas equipment information such as asset ID, asset name, asset type, location, operation area, and criticality.

### Technicians

`data/technicians.csv`

Contains technician information such as technician ID, skills, shift start, shift end, maximum working hours, and base location.

### Maintenance Tasks

`data/maintenance_tasks.csv`

Contains maintenance work orders such as task ID, asset ID, task name, required skill, duration, priority, earliest start, and latest finish.

### Solver Configuration

`data/solver_config.json`

Contains solver settings such as solver type, time limit, and objective weights.

## Decision Variable

The main decision variable is:

```text
x[task, technician, start_time] = 1
```

if a maintenance task is assigned to a technician at a specific start time.

Otherwise:

```text
x[task, technician, start_time] = 0
```

## Hard Constraints

The optimizer applies the following hard constraints:

1. Each task must be assigned exactly once.
2. A technician must have the required skill for the task.
3. A technician cannot work on two overlapping tasks.
4. A task must start after its earliest allowed start time.
5. A task must finish before its latest allowed finish time.
6. A task must fit inside the assigned technician's shift.

## Objective Function

The current objective is to schedule higher-priority tasks earlier while producing a feasible non-overlapping maintenance schedule.

The model minimizes a priority-weighted start-time cost:

```text
minimize Σ(priority × start_time × assignment_variable)
```

This encourages high-priority maintenance tasks to be scheduled earlier where possible.

## Solver

The project uses Google OR-Tools CP-SAT because the problem involves discrete decisions, assignment constraints, time windows, and scheduling logic.

## Output

The optimizer returns:

* Solver status
* Objective value
* Runtime
* Optimized schedule
* Assigned technician per task
* Start and end time per task
* Diagnostics such as number of tasks, technicians, decision variables, and technician workload
