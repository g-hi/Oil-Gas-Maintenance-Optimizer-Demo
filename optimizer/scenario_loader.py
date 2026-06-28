from pathlib import Path
import json
import pandas as pd


SCENARIO_DIR = Path(__file__).resolve().parent.parent / "scenarios"


def list_scenarios() -> list[str]:
    return sorted([path.stem for path in SCENARIO_DIR.glob("*.json")])


def load_scenario(scenario_name: str) -> dict:
    path = SCENARIO_DIR / f"{scenario_name}.json"

    if not path.exists():
        available = list_scenarios()
        raise FileNotFoundError(
            f"Scenario '{scenario_name}' not found. Available scenarios: {available}"
        )

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_scenario(data: dict, scenario: dict) -> dict:
    tasks = data["tasks"].copy()
    technicians = data["technicians"].copy()

    technician_status = scenario.get("technician_status", {})
    unavailable_technicians = [
        tech_id
        for tech_id, status in technician_status.items()
        if status == "unavailable"
    ]

    if unavailable_technicians:
        technicians = technicians[
            ~technicians["tech_id"].isin(unavailable_technicians)
        ].reset_index(drop=True)

    extra_tasks = scenario.get("extra_tasks", [])

    if extra_tasks:
        extra_tasks_df = pd.DataFrame(extra_tasks)
        tasks = pd.concat([tasks, extra_tasks_df], ignore_index=True)

    task_overrides = scenario.get("task_overrides", {})

    for task_id, overrides in task_overrides.items():
        mask = tasks["task_id"] == task_id

        for column, value in overrides.items():
            if column in tasks.columns:
                tasks.loc[mask, column] = value

    scenario_data = data.copy()
    scenario_data["tasks"] = tasks
    scenario_data["technicians"] = technicians
    scenario_data["scenario"] = scenario

    return scenario_data