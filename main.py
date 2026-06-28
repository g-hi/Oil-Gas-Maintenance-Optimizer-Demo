from optimizer.data_loader import load_all_data
from optimizer.validator import validate_all_data
from optimizer.scheduler import solve_maintenance_schedule
from optimizer.diagnostics import build_diagnostics

import json
from pathlib import Path


OUTPUT_DIR = Path("outputs")


def main():
    data = load_all_data()

    validation_result = validate_all_data(data)

    if not validation_result["is_valid"]:
        print("Data validation failed.")
        for error in validation_result["errors"]:
            print(f"- {error}")
        return

    print("Data validation passed successfully.")
    print("Running OR-Tools CP-SAT scheduler...")

    result = solve_maintenance_schedule(
        tasks=data["tasks"],
        technicians=data["technicians"],
        solver_config=data["solver_config"],
    )

    result["diagnostics"] = build_diagnostics(result)

    print("\nSolver Status:", result["status"])
    print("Objective Value:", result["objective_value"])
    print("Runtime Seconds:", result["runtime_seconds"])

    print("\nOptimized Schedule:")
    for item in result["schedule"]:
        print(
            f"- {item['task_id']} | {item['task_name']} | "
            f"Technician: {item['technician_id']} | "
            f"{item['start']}:00 - {item['end']}:00"
        )

    print("\nDiagnostics:")
    for key, value in result["diagnostics"].items():
        print(f"- {key}: {value}")

    OUTPUT_DIR.mkdir(exist_ok=True)

    output_path = OUTPUT_DIR / "sample_result.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"\nResult saved to: {output_path}")


if __name__ == "__main__":
    main()