import streamlit as st
import requests
import pandas as pd
import plotly.express as px


API_URL = "https://oil-gas-maintenance-optimizer-demo.onrender.com"


st.set_page_config(
    page_title="Oil & Gas Maintenance Optimizer",
    layout="wide",
)


def get_scenarios():
    try:
        response = requests.get(f"{API_URL}/scenarios")
        if response.status_code == 200:
            return response.json().get("available_scenarios", [])
    except requests.exceptions.ConnectionError:
        return []
    return []


def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def run_optimization(run_mode, selected_scenario):
    if run_mode == "Scenario-based optimization" and selected_scenario:
        return requests.post(f"{API_URL}/optimize-scenario/{selected_scenario}")
    return requests.post(f"{API_URL}/optimize-maintenance")


def show_business_summary(result, diagnostics, scenario_name):
    scheduled_tasks = diagnostics.get("scheduled_tasks", 0)
    total_tasks = diagnostics.get("num_tasks", 0)
    workload = diagnostics.get("technician_workload_hours", {})

    st.subheader("Business Summary")

    if result["status"] in ["OPTIMAL", "FEASIBLE"] and workload:
        busiest_tech = max(workload, key=workload.get)
        busiest_hours = workload[busiest_tech]

        st.success(
            f"The optimizer scheduled {scheduled_tasks} out of {total_tasks} "
            f"maintenance tasks successfully. The busiest technician is "
            f"{busiest_tech} with {busiest_hours} workload hours. "
            f"No technician exceeds the configured 8-hour shift limit."
        )

        if scenario_name == "emergency_maintenance":
            st.info(
                "The emergency maintenance scenario was handled successfully by "
                "adding the urgent compressor task into the optimized schedule."
            )

        if scenario_name == "tight_shutdown_window":
            st.info(
                "The tight shutdown window scenario was solved successfully, showing "
                "that the optimizer can adapt when selected tasks have reduced time windows."
            )

    elif result["status"] == "VALIDATION_FAILED":
        st.error(
            "The scenario could not be optimized because the input data failed validation. "
            "This is useful in deployed systems because operational issues are detected "
            "before the solver runs."
        )


def show_schedule(schedule_df):
    st.subheader("Optimized Maintenance Schedule")

    if not schedule_df.empty:
        st.dataframe(schedule_df, use_container_width=True)
    else:
        st.warning("No schedule returned.")


def show_gantt(schedule_df):
    st.subheader("Maintenance Schedule Gantt Chart")

    if schedule_df.empty:
        st.warning("No schedule available for Gantt chart.")
        return

    gantt_df = schedule_df.copy()
    gantt_df["Start Time"] = gantt_df["start"]
    gantt_df["End Time"] = gantt_df["end"]
    gantt_df["Task Label"] = gantt_df["task_id"] + " - " + gantt_df["task_name"]

    fig = px.timeline(
        gantt_df,
        x_start="Start Time",
        x_end="End Time",
        y="technician_id",
        color="priority",
        hover_data=[
            "task_id",
            "asset_id",
            "task_name",
            "start",
            "end",
            "priority",
        ],
        title="Optimized Maintenance Schedule by Technician",
    )

    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Technician",
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)


def show_workload(diagnostics):
    st.subheader("Technician Workload")

    workload = diagnostics.get("technician_workload_hours", {})

    if not workload:
        st.warning("No workload data returned.")
        return

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


def show_diagnostics(result, diagnostics, scenario_name, scenario_description):
    st.subheader("Diagnostics Summary")

    diag_col1, diag_col2, diag_col3, diag_col4 = st.columns(4)

    diag_col1.metric("Total Tasks", diagnostics.get("num_tasks", 0))
    diag_col2.metric("Technicians", diagnostics.get("num_technicians", 0))
    diag_col3.metric("Decision Variables", diagnostics.get("num_decision_variables", 0))
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


def compare_all_scenarios(scenarios):
    st.subheader("Scenario Comparison")

    comparison_rows = []

    with st.spinner("Running all scenarios..."):
        for scenario in scenarios:
            try:
                response = requests.post(f"{API_URL}/optimize-scenario/{scenario}")

                if response.status_code == 200:
                    result = response.json()
                    diagnostics = result.get("diagnostics", {})
                    errors = result.get("errors")
                    error_text = "; ".join(errors) if errors else ""

                    comparison_rows.append(
                        {
                            "Scenario": scenario,
                            "Status": result.get("status"),
                            "Objective Value": result.get("objective_value"),
                            "Runtime Seconds": result.get("runtime_seconds"),
                            "Scheduled Tasks": diagnostics.get("scheduled_tasks"),
                            "Total Tasks": diagnostics.get("num_tasks"),
                            "Technicians": diagnostics.get("num_technicians"),
                            "Decision Variables": diagnostics.get(
                                "num_decision_variables"
                            ),
                            "Errors": error_text,
                        }
                    )
                else:
                    comparison_rows.append(
                        {
                            "Scenario": scenario,
                            "Status": "API_ERROR",
                            "Objective Value": None,
                            "Runtime Seconds": None,
                            "Scheduled Tasks": None,
                            "Total Tasks": None,
                            "Technicians": None,
                            "Decision Variables": None,
                            "Errors": response.text,
                        }
                    )

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI backend.")
                st.stop()

    comparison_df = pd.DataFrame(comparison_rows)

    st.dataframe(comparison_df, use_container_width=True)

    successful = comparison_df[
        comparison_df["Status"].isin(["OPTIMAL", "FEASIBLE"])
    ]

    failed = comparison_df[
        ~comparison_df["Status"].isin(["OPTIMAL", "FEASIBLE"])
    ]

    col_a, col_b, col_c = st.columns(3)

    col_a.metric("Successful Scenarios", len(successful))
    col_b.metric("Failed / Invalid Scenarios", len(failed))
    col_c.metric("Total Scenarios", len(comparison_df))

    if not successful.empty:
        st.subheader("Objective Value by Scenario")
        objective_chart_df = successful.dropna(subset=["Objective Value"])
        st.bar_chart(objective_chart_df.set_index("Scenario")["Objective Value"])

    if not failed.empty:
        st.subheader("Failed or Invalid Scenario Details")
        st.dataframe(
            failed[["Scenario", "Status", "Errors"]],
            use_container_width=True,
        )


st.subheader("Oil & Gas Maintenance Scheduling Optimizer — Technical Proof of Concept")

st.write(
    "A technical proof-of-concept demonstrating how constraint optimization "
    "can support oil-and-gas maintenance planning. "
    "Google OR-Tools was used to assign maintenance tasks to qualified technicians while "
    "respecting skills, shifts, maintenance windows, priorities, and operational "
    "scenarios."
)

api_ok = check_api_health()

with st.sidebar:
    st.title("Optimization Console")

    if api_ok:
        st.success("Connected")
    else:
        st.error("Backend not Reachable")

    st.caption(f"API URL: {API_URL}")

    scenarios = get_scenarios()

    run_mode = st.radio(
        "Optimization Mode",
        ["Scenario-based optimization","Default maintenance optimization"],
    )

    selected_scenario = None

    if run_mode == "Scenario-based optimization":
        if scenarios:
            selected_scenario = st.selectbox("Select Scenario", scenarios)
        else:
            st.warning("No scenarios available.")

    run_button = st.button("Run Optimization", use_container_width=True)
    compare_button = st.button("Compare All Scenarios", use_container_width=True)


if not api_ok:
    st.warning("Start the FastAPI backend before using the dashboard.")
    st.stop()


if compare_button:
    compare_all_scenarios(scenarios)


if run_button:
    with st.spinner("Running optimization..."):
        response = run_optimization(run_mode, selected_scenario)

    if response.status_code != 200:
        st.error("Failed to run optimization.")
        st.write(response.text)
        st.stop()

    result = response.json()
    diagnostics = result["diagnostics"]

    scenario_name = diagnostics.get("scenario_name")
    scenario_description = diagnostics.get("scenario_description")

    st.subheader("Solver Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Solver Status", result["status"])
    col2.metric("Objective Value", result["objective_value"])
    col3.metric("Runtime Seconds", result["runtime_seconds"])
    col4.metric("Scheduled Tasks", diagnostics.get("scheduled_tasks", 0))

    if scenario_name:
        st.subheader("Scenario Details")
        st.write(f"**Scenario:** {scenario_name}")
        st.write(f"**Description:** {scenario_description}")

    if result.get("errors"):
        st.subheader("Validation / Feasibility Issues")
        for error in result["errors"]:
            st.error(error)

    show_business_summary(result, diagnostics, scenario_name)

    schedule_df = pd.DataFrame(result["schedule"])

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Schedule Table", "Gantt Chart", "Workload", "Diagnostics"]
    )

    with tab1:
        show_schedule(schedule_df)

    with tab2:
        show_gantt(schedule_df)

    with tab3:
        show_workload(diagnostics)

    with tab4:
        show_diagnostics(result, diagnostics, scenario_name, scenario_description)


if not run_button and not compare_button:
    st.info(
        "Use the control panel on the left to run an optimization scenario or compare all scenarios."
    )