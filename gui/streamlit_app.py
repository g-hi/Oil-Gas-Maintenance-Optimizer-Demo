import streamlit as st
import requests
import pandas as pd


API_URL = "http://127.0.0.1:8001"


st.set_page_config(
    page_title="Oil & Gas Maintenance Optimizer",
    layout="wide",
)

st.title("Oil & Gas Maintenance Scheduling Optimizer")

st.write(
    "A Google OR-Tools CP-SAT dashboard for scheduling oil-and-gas "
    "maintenance tasks based on technician skills, availability, task duration, "
    "priority, maintenance windows, and operational scenarios."
)

st.info("Make sure the FastAPI backend is running before using the dashboard.")


def get_scenarios():
    try:
        response = requests.get(f"{API_URL}/scenarios")
        if response.status_code == 200:
            return response.json().get("available_scenarios", [])
    except requests.exceptions.ConnectionError:
        return []

    return []


scenarios = get_scenarios()

st.subheader("Scenario Selection")

run_mode = st.radio(
    "Choose optimization mode",
    ["Default maintenance optimization", "Scenario-based optimization"],
)

selected_scenario = None

if run_mode == "Scenario-based optimization":
    if scenarios:
        selected_scenario = st.selectbox(
            "Select scenario",
            scenarios,
        )
    else:
        st.warning("No scenarios available or FastAPI backend is not running.")


if st.button("Run Optimization"):
    with st.spinner("Running optimization..."):
        try:
            if run_mode == "Scenario-based optimization" and selected_scenario:
                response = requests.post(
                    f"{API_URL}/optimize-scenario/{selected_scenario}"
                )
            else:
                response = requests.post(f"{API_URL}/optimize-maintenance")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to FastAPI. Start the backend first.")
            st.stop()

    if response.status_code != 200:
        st.error("Failed to run optimization.")
        st.write(response.text)
    else:
        result = response.json()
        diagnostics = result["diagnostics"]

        st.subheader("Solver Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Solver Status", result["status"])
        col2.metric("Objective Value", result["objective_value"])
        col3.metric("Runtime Seconds", result["runtime_seconds"])
        col4.metric(
            "Scheduled Tasks",
            diagnostics.get("scheduled_tasks", 0),
        )

        scenario_name = diagnostics.get("scenario_name")
        scenario_description = diagnostics.get("scenario_description")

        if scenario_name:
            st.subheader("Scenario Details")
            st.write(f"**Scenario:** {scenario_name}")
            st.write(f"**Description:** {scenario_description}")

        if result.get("errors"):
            st.subheader("Validation / Feasibility Issues")
            for error in result["errors"]:
                st.error(error)

        st.subheader("Optimized Maintenance Schedule")

        schedule_df = pd.DataFrame(result["schedule"])

        if not schedule_df.empty:
            st.dataframe(schedule_df, use_container_width=True)
        else:
            st.warning("No schedule returned.")

        st.subheader("Technician Workload")

        workload = diagnostics.get("technician_workload_hours", {})

        if workload:
            workload_df = pd.DataFrame(
                [
                    {
                        "Technician ID": tech_id,
                        "Workload Hours": hours,
                        "Utilization %": round((hours / 8) * 100, 1),
                    }
                    for tech_id, hours in workload.items()
                ]
            )

            st.dataframe(workload_df, use_container_width=True)
            st.bar_chart(workload_df.set_index("Technician ID")["Workload Hours"])
        else:
            st.warning("No workload data returned.")

        st.subheader("Diagnostics Summary")

        diag_col1, diag_col2, diag_col3, diag_col4 = st.columns(4)

        diag_col1.metric("Total Tasks", diagnostics.get("num_tasks", 0))
        diag_col2.metric("Technicians", diagnostics.get("num_technicians", 0))
        diag_col3.metric(
            "Decision Variables",
            diagnostics.get("num_decision_variables", 0),
        )
        diag_col4.metric("Time Limit (sec)", diagnostics.get("time_limit_seconds", 0))

        st.subheader("Scenario Diagnostics")

        scenario_df = pd.DataFrame(
            [
                {
                    "Scenario Name": scenario_name or "default",
                    "Scenario Description": scenario_description
                    or "Default maintenance optimization",
                    "Solver Status": result.get("status"),
                    "Scheduled Tasks": diagnostics.get("scheduled_tasks", 0),
                    "Runtime Seconds": result.get("runtime_seconds", 0),
                }
            ]
        )

        st.dataframe(scenario_df, use_container_width=True)

        with st.expander("View Raw Diagnostics JSON"):
            st.json(diagnostics)