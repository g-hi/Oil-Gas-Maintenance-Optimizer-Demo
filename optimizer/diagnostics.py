def build_diagnostics(result: dict) -> dict:
    schedule = result.get("schedule", [])
    diagnostics = result.get("diagnostics", {})

    technician_workload = {}

    for item in schedule:
        tech_id = item["technician_id"]
        duration = item["end"] - item["start"]
        technician_workload[tech_id] = technician_workload.get(tech_id, 0) + duration

    diagnostics.update(
        {
            "scheduled_tasks": len(schedule),
            "technician_workload_hours": technician_workload,
        }
    )

    return diagnostics