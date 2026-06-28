from optimizer.data_loader import load_all_data
from optimizer.scheduler import solve_maintenance_schedule


def test_scheduler_returns_optimal_or_feasible_solution():
    data = load_all_data()

    result = solve_maintenance_schedule(
        tasks=data["tasks"],
        technicians=data["technicians"],
        solver_config=data["solver_config"],
    )

    assert result["status"] in ["OPTIMAL", "FEASIBLE"]
    assert len(result["schedule"]) == len(data["tasks"])


def test_all_tasks_have_technicians_assigned():
    data = load_all_data()

    result = solve_maintenance_schedule(
        tasks=data["tasks"],
        technicians=data["technicians"],
        solver_config=data["solver_config"],
    )

    for item in result["schedule"]:
        assert item["technician_id"] is not None
        assert item["start"] < item["end"]


def test_no_technician_overlap():
    data = load_all_data()

    result = solve_maintenance_schedule(
        tasks=data["tasks"],
        technicians=data["technicians"],
        solver_config=data["solver_config"],
    )

    schedule = result["schedule"]

    for i in range(len(schedule)):
        for j in range(i + 1, len(schedule)):
            first = schedule[i]
            second = schedule[j]

            if first["technician_id"] == second["technician_id"]:
                no_overlap = (
                    first["end"] <= second["start"]
                    or second["end"] <= first["start"]
                )
                assert no_overlap