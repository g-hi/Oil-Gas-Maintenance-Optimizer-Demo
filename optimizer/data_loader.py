from pathlib import Path
import json
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_assets(file_path: Path | None = None) -> pd.DataFrame:
    path = file_path or DATA_DIR / "assets.csv"
    return pd.read_csv(path)


def load_technicians(file_path: Path | None = None) -> pd.DataFrame:
    path = file_path or DATA_DIR / "technicians.csv"
    return pd.read_csv(path)


def load_tasks(file_path: Path | None = None) -> pd.DataFrame:
    path = file_path or DATA_DIR / "maintenance_tasks.csv"
    return pd.read_csv(path)


def load_maintenance_windows(file_path: Path | None = None) -> pd.DataFrame:
    path = file_path or DATA_DIR / "maintenance_windows.csv"
    return pd.read_csv(path)


def load_solver_config(file_path: Path | None = None) -> dict:
    path = file_path or DATA_DIR / "solver_config.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_data() -> dict:
    return {
        "assets": load_assets(),
        "technicians": load_technicians(),
        "tasks": load_tasks(),
        "maintenance_windows": load_maintenance_windows(),
        "solver_config": load_solver_config(),
    }


if __name__ == "__main__":
    data = load_all_data()

    print("Assets:")
    print(data["assets"].head())

    print("\nTechnicians:")
    print(data["technicians"].head())

    print("\nMaintenance Tasks:")
    print(data["tasks"].head())

    print("\nSolver Config:")
    print(data["solver_config"])