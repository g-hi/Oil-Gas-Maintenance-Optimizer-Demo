import pandas as pd


def validate_required_columns(df: pd.DataFrame, required_columns: list[str], table_name: str) -> list[str]:
    errors = []

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        errors.append(
            f"{table_name} is missing required columns: {missing_columns}"
        )

    return errors


def validate_assets(assets: pd.DataFrame) -> list[str]:
    required_columns = [
        "asset_id",
        "asset_name",
        "asset_type",
        "location",
        "operation_area",
        "criticality",
    ]

    errors = validate_required_columns(assets, required_columns, "assets.csv")

    if "asset_id" in assets.columns and assets["asset_id"].duplicated().any():
        errors.append("assets.csv contains duplicate asset_id values.")

    if "criticality" in assets.columns:
        invalid_criticality = assets[
            (assets["criticality"] < 1) | (assets["criticality"] > 5)
        ]

        if not invalid_criticality.empty:
            errors.append("assets.csv contains criticality values outside the range 1-5.")

    return errors


def validate_technicians(technicians: pd.DataFrame) -> list[str]:
    required_columns = [
        "tech_id",
        "tech_name",
        "skills",
        "shift_start",
        "shift_end",
        "max_hours",
        "base_location",
    ]

    errors = validate_required_columns(technicians, required_columns, "technicians.csv")

    if "tech_id" in technicians.columns and technicians["tech_id"].duplicated().any():
        errors.append("technicians.csv contains duplicate tech_id values.")

    if {"shift_start", "shift_end"}.issubset(technicians.columns):
        invalid_shifts = technicians[
            technicians["shift_start"] >= technicians["shift_end"]
        ]

        if not invalid_shifts.empty:
            errors.append("technicians.csv contains invalid shifts where shift_start >= shift_end.")

    return errors


def validate_tasks(tasks: pd.DataFrame, assets: pd.DataFrame, technicians: pd.DataFrame) -> list[str]:
    required_columns = [
        "task_id",
        "asset_id",
        "task_name",
        "required_skill",
        "duration_hours",
        "priority",
        "earliest_start",
        "latest_finish",
    ]

    errors = validate_required_columns(tasks, required_columns, "maintenance_tasks.csv")

    if "task_id" in tasks.columns and tasks["task_id"].duplicated().any():
        errors.append("maintenance_tasks.csv contains duplicate task_id values.")

    if {"asset_id"}.issubset(tasks.columns) and "asset_id" in assets.columns:
        invalid_assets = set(tasks["asset_id"]) - set(assets["asset_id"])

        if invalid_assets:
            errors.append(
                f"maintenance_tasks.csv contains asset_id values not found in assets.csv: {sorted(invalid_assets)}"
            )

    if {"duration_hours"}.issubset(tasks.columns):
        invalid_duration = tasks[tasks["duration_hours"] <= 0]

        if not invalid_duration.empty:
            errors.append("maintenance_tasks.csv contains tasks with duration_hours <= 0.")

    if {"priority"}.issubset(tasks.columns):
        invalid_priority = tasks[
            (tasks["priority"] < 1) | (tasks["priority"] > 5)
        ]

        if not invalid_priority.empty:
            errors.append("maintenance_tasks.csv contains priority values outside the range 1-5.")

    if {"earliest_start", "latest_finish", "duration_hours"}.issubset(tasks.columns):
        impossible_windows = tasks[
            tasks["earliest_start"] + tasks["duration_hours"] > tasks["latest_finish"]
        ]

        if not impossible_windows.empty:
            bad_tasks = impossible_windows["task_id"].tolist()
            errors.append(
                f"Some tasks cannot fit inside their maintenance windows: {bad_tasks}"
            )

    # Check if every required skill exists among at least one technician
    if "required_skill" in tasks.columns and "skills" in technicians.columns:
        all_skills = set()

        for skills in technicians["skills"]:
            all_skills.update(str(skills).split(";"))

        required_skills = set(tasks["required_skill"])
        missing_skills = required_skills - all_skills

        if missing_skills:
            errors.append(
                f"No technician has the following required skills: {sorted(missing_skills)}"
            )

    return errors


def validate_all_data(data: dict) -> dict:
    assets = data["assets"]
    technicians = data["technicians"]
    tasks = data["tasks"]

    errors = []

    errors.extend(validate_assets(assets))
    errors.extend(validate_technicians(technicians))
    errors.extend(validate_tasks(tasks, assets, technicians))

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
    }