from ortools.sat.python import cp_model
import pandas as pd
import time


def solve_maintenance_schedule(
    tasks: pd.DataFrame,
    technicians: pd.DataFrame,
    solver_config: dict | None = None,
) -> dict:
    """
    Solve oil and gas maintenance task scheduling using Google OR-Tools CP-SAT.

    Decision variable:
    x[task_id, tech_id, start_time] = 1 if task is assigned to technician at start_time.
    """

    solver_config = solver_config or {}
    time_limit = solver_config.get("time_limit_seconds", 10)

    model = cp_model.CpModel()

    # Convert technicians' skills into dictionary
    technician_skills = {}
    for _, tech in technicians.iterrows():
        technician_skills[tech["tech_id"]] = set(str(tech["skills"]).split(";"))

    # Decision variables
    x = {}

    for _, task in tasks.iterrows():
        task_id = task["task_id"]
        required_skill = task["required_skill"]
        duration = int(task["duration_hours"])
        earliest_start = int(task["earliest_start"])
        latest_finish = int(task["latest_finish"])

        for _, tech in technicians.iterrows():
            tech_id = tech["tech_id"]
            shift_start = int(tech["shift_start"])
            shift_end = int(tech["shift_end"])

            # Technician must have required skill
            if required_skill not in technician_skills[tech_id]:
                continue

            # Start time must respect both task window and technician shift
            possible_start = max(earliest_start, shift_start)
            possible_end = min(latest_finish, shift_end)

            for start in range(possible_start, possible_end - duration + 1):
                x[(task_id, tech_id, start)] = model.NewBoolVar(
                    f"x_{task_id}_{tech_id}_{start}"
                )

    # Constraint 1: each task must be assigned exactly once
    for _, task in tasks.iterrows():
        task_id = task["task_id"]

        task_vars = [
            var
            for (t_id, tech_id, start), var in x.items()
            if t_id == task_id
        ]

        if task_vars:
            model.AddExactlyOne(task_vars)
        else:
            return {
                "status": "INFEASIBLE",
                "message": f"No feasible technician/time slot found for task {task_id}",
                "schedule": [],
                "diagnostics": {
                    "num_tasks": len(tasks),
                    "num_technicians": len(technicians),
                    "num_decision_variables": len(x),
                },
            }

    # Constraint 2: technician cannot do overlapping tasks
    for _, tech in technicians.iterrows():
        tech_id = tech["tech_id"]
        shift_start = int(tech["shift_start"])
        shift_end = int(tech["shift_end"])

        for hour in range(shift_start, shift_end):
            overlapping_vars = []

            for _, task in tasks.iterrows():
                task_id = task["task_id"]
                duration = int(task["duration_hours"])

                for (t_id, assigned_tech_id, start), var in x.items():
                    if assigned_tech_id != tech_id:
                        continue

                    if t_id != task_id:
                        continue

                    end = start + duration

                    if start <= hour < end:
                        overlapping_vars.append(var)

            if overlapping_vars:
                model.AddAtMostOne(overlapping_vars)

    # Objective: schedule higher-priority tasks earlier
    objective_terms = []

    for _, task in tasks.iterrows():
        task_id = task["task_id"]
        priority = int(task["priority"])

        for (t_id, tech_id, start), var in x.items():
            if t_id == task_id:
                objective_terms.append(priority * start * var)

    model.Minimize(sum(objective_terms))

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit)

    start_time = time.time()
    status = solver.Solve(model)
    runtime = round(time.time() - start_time, 4)

    status_name = solver.StatusName(status)

    schedule = []

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for _, task in tasks.iterrows():
            task_id = task["task_id"]
            duration = int(task["duration_hours"])

            for (t_id, tech_id, start), var in x.items():
                if t_id == task_id and solver.Value(var) == 1:
                    schedule.append(
                        {
                            "task_id": task_id,
                            "asset_id": task["asset_id"],
                            "task_name": task["task_name"],
                            "technician_id": tech_id,
                            "start": start,
                            "end": start + duration,
                            "priority": int(task["priority"]),
                        }
                    )

    return {
        "status": status_name,
        "objective_value": solver.ObjectiveValue()
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]
        else None,
        "runtime_seconds": runtime,
        "schedule": schedule,
        "diagnostics": {
            "num_tasks": len(tasks),
            "num_technicians": len(technicians),
            "num_decision_variables": len(x),
            "time_limit_seconds": time_limit,
        },
    }