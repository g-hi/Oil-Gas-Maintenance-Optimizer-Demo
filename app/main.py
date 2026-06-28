from fastapi import FastAPI, HTTPException

from optimizer.data_loader import load_all_data
from optimizer.validator import validate_all_data
from optimizer.scheduler import solve_maintenance_schedule
from optimizer.diagnostics import build_diagnostics
from optimizer.scenario_loader import list_scenarios, load_scenario, apply_scenario

from app.schemas import HealthResponse, OptimizationResponse


app = FastAPI(
    title="Oil & Gas Maintenance Scheduling Optimizer",
    description="Google OR-Tools CP-SAT optimizer for oil and gas maintenance scheduling.",
    version="1.1.0",
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "service": "oil-gas-maintenance-optimizer",
    }


@app.get("/scenarios")
def get_scenarios():
    return {
        "available_scenarios": list_scenarios()
    }


@app.post("/optimize-maintenance", response_model=OptimizationResponse)
def optimize_maintenance():
    data = load_all_data()

    validation_result = validate_all_data(data)

    if not validation_result["is_valid"]:
        return {
            "status": "VALIDATION_FAILED",
            "objective_value": None,
            "runtime_seconds": 0.0,
            "schedule": [],
            "diagnostics": {
                "num_tasks": 0,
                "num_technicians": 0,
                "num_decision_variables": 0,
                "time_limit_seconds": 0,
            },
        }

    result = solve_maintenance_schedule(
        tasks=data["tasks"],
        technicians=data["technicians"],
        solver_config=data["solver_config"],
    )

    result["diagnostics"] = build_diagnostics(result)

    return result


@app.post("/optimize-scenario/{scenario_name}", response_model=OptimizationResponse)
def optimize_scenario(scenario_name: str):
    data = load_all_data()

    try:
        scenario = load_scenario(scenario_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    scenario_data = apply_scenario(data, scenario)

    validation_result = validate_all_data(scenario_data)

    if not validation_result["is_valid"]:
     return {
        "status": "VALIDATION_FAILED",
        "objective_value": None,
        "runtime_seconds": 0.0,
        "schedule": [],
        "diagnostics": {
            "num_tasks": len(scenario_data["tasks"]),
            "num_technicians": len(scenario_data["technicians"]),
            "num_decision_variables": 0,
            "time_limit_seconds": scenario_data["solver_config"].get("time_limit_seconds", 10),
            "scheduled_tasks": 0,
            "technician_workload_hours": {},
            "scenario_name": scenario_name,
            "scenario_description": scenario.get("description", ""),
        },
        "errors": validation_result["errors"],
    }

    result = solve_maintenance_schedule(
        tasks=scenario_data["tasks"],
        technicians=scenario_data["technicians"],
        solver_config=scenario_data["solver_config"],
    )

    result["diagnostics"] = build_diagnostics(result)
    result["diagnostics"]["scenario_name"] = scenario_name
    result["diagnostics"]["scenario_description"] = scenario.get("description", "")

    return result