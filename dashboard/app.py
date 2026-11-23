
import sqlite3
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Chicago Crime Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "database" / "chicago_crime.db"
REPORTS_DIR = PROJECT_DIR / "reports"
CHARTS_DIR = REPORTS_DIR / "charts"

sns.set_theme(style="whitegrid", context="notebook")


# ============================================================
# 2. PROFESSIONAL DASHBOARD STYLING
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #F4F7FB;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background-color: #102A43;
}

[data-testid="stSidebar"] * {
    color: white;
}

h1, h2, h3 {
    color: #102A43;
    font-weight: 700;
}

[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #E1E8F0;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 2px 7px rgba(16,42,67,0.05);
}

[data-testid="stDataFrame"] {
    border: 1px solid #E1E8F0;
    border-radius: 10px;
}

hr {
    border-color: #D9E2EC;
}

.small-note {
    color: #627D98;
    font-size: 13px;
}

.finding-panel {
    background-color: white;
    border: 1px solid #E1E8F0;
    border-left: 4px solid #2874A6;
    border-radius: 9px;
    padding: 15px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================

def section_heading(number, title, description):
    st.markdown(f"## {number}. {title}")
    st.markdown(
        f'<p class="small-note">{description}</p>',
        unsafe_allow_html=True
    )


def display_chart_with_findings(
    title,
    fig,
    findings,
    interpretation=None
):
    """Display chart on the left and findings on the right."""

    st.markdown(f"### {title}")

    chart_col, findings_col = st.columns(
        [1.65, 1],
        gap="large"
    )

    with chart_col:
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with findings_col:
        st.markdown("#### Key findings")

        for finding in findings:
            st.markdown(
                f'<div class="finding-panel">{finding}</div>',
                unsafe_allow_html=True
            )

        if interpretation:
            st.info(interpretation)

    st.divider()


def safe_percentage(numerator, denominator):
    if denominator == 0:
        return 0
    return numerator / denominator * 100


def clean_boolean(series):
    """Convert SQLite Boolean/integer/text values to True/False."""

    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .isin(["1", "true", "yes"])
    )


# ============================================================
# 4. LOAD DATABASE
# ============================================================

if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()


@st.cache_data
def load_crime_data(db_path):

    with sqlite3.connect(db_path) as conn:

        crime = pd.read_sql_query(
            "SELECT * FROM chicago_crime",
            conn
        )

        # Add crime category descriptions
        iucr = pd.read_sql_query(
            'SELECT IUCR, "PRIMARY_TYPE " AS primary_type '
            'FROM iucr',
            conn
        )

        # Add community names
        communities = pd.read_sql_query(
            """
            SELECT community_code, community_name
            FROM city_community
            """,
            conn
        )

        # Database table information
        table_info = pd.read_sql_query(
            "PRAGMA table_info(chicago_crime)",
            conn
        )

    crime["iucr_code"] = crime["iucr_code"].astype(str)
    iucr["IUCR"] = iucr["IUCR"].astype(str)

    crime = crime.merge(
        iucr,
        left_on="iucr_code",
        right_on="IUCR",
        how="left"
    )

    crime["community_code"] = pd.to_numeric(
        crime["community_code"],
        errors="coerce"
    )

    communities["community_code"] = pd.to_numeric(
        communities["community_code"],
        errors="coerce"
    )

    crime = crime.merge(
        communities,
        on="community_code",
        how="left"
    )

    crime["date"] = pd.to_datetime(
        crime["date"],
        errors="coerce"
    )

    crime["Year"] = crime["date"].dt.year
    crime["Month"] = crime["date"].dt.month
    crime["DayOfWeek"] = crime["date"].dt.day_name()

    crime["arrest_flag"] = clean_boolean(crime["arrest"])
    crime["domestic_flag"] = clean_boolean(crime["domestic"])

    return crime, table_info


try:
    crime_data, table_info = load_crime_data(str(DB_PATH))

except Exception as e:
    st.error(f"Unable to load database data: {e}")
    st.stop()


# ============================================================
# 5. DASHBOARD HEADER
# ============================================================

st.markdown(
    """
    <div style="
        background-color:#102A43;
        padding:28px;
        border-radius:14px;
        margin-bottom:20px;
    ">
        <h1 style="color:white; margin-bottom:5px;">
            CHICAGO CRIME ANALYTICS
        </h1>
        <p style="color:#D9EAF7; margin:0;">
            Data Intelligence | Exploratory Analysis |
            Statistical Insights | SQL Analytics
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Historical Chicago crime dataset analysis | "
    "Source: project CSV and SQLite database"
)


# ============================================================
# 6. SIDEBAR FILTERS AND NAVIGATION
# ============================================================

st.sidebar.title("📊 Navigation")

navigation = [
    "Project Overview",
    "Use Case 1 - Data Quality",
    "Use Case 2 - EDA",
    "Use Case 3 - Statistics",
    "Use Case 4 - SQL Analysis",
    "Final Findings"
]

selected_section = st.sidebar.radio(
    "Navigate to section",
    navigation
)

st.sidebar.divider()
st.sidebar.subheader("Data Filters")

all_years = sorted(
    crime_data["Year"].dropna().unique().astype(int).tolist()
)

selected_years = st.sidebar.multiselect(
    "Select year",
    all_years,
    default=all_years
)

all_categories = sorted(
    crime_data["primary_type"].dropna().unique().tolist()
)

selected_categories = st.sidebar.multiselect(
    "Crime category",
    all_categories,
    default=all_categories
)

all_communities = sorted(
    crime_data["community_name"].dropna().unique().tolist()
)

selected_communities = st.sidebar.multiselect(
    "Community area",
    all_communities,
    default=all_communities
)

arrest_filter = st.sidebar.selectbox(
    "Arrest status",
    ["All", "Arrested", "Not arrested"]
)

st.sidebar.caption(
    "Filters affect the analytical sections. "
    "Data-quality and database validation metrics describe "
    "the complete stored dataset."
)


# Apply filters
filtered_data = crime_data.copy()

filtered_data = filtered_data[
    filtered_data["Year"].isin(selected_years)
]

filtered_data = filtered_data[
    filtered_data["primary_type"].isin(selected_categories)
]

filtered_data = filtered_data[
    filtered_data["community_name"].isin(selected_communities)
    | filtered_data["community_name"].isna()
]

if arrest_filter == "Arrested":
    filtered_data = filtered_data[
        filtered_data["arrest_flag"]
    ]

elif arrest_filter == "Not arrested":
    filtered_data = filtered_data[
        ~filtered_data["arrest_flag"]
    ]


# ============================================================
# 7. PROJECT OVERVIEW
# ============================================================

if selected_section == "Project Overview":

    section_heading(
        "01",
        "Project Overview",
        "An end-to-end analysis of the Chicago crime dataset."
    )

    total_records = len(crime_data)
    total_arrests = int(crime_data["arrest_flag"].sum())
    arrest_rate = safe_percentage(total_arrests, total_records)
    total_categories = crime_data["primary_type"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Crime Records", f"{total_records:,}")
    col2.metric("Recorded Arrests", f"{total_arrests:,}")
    col3.metric("Overall Arrest Rate", f"{arrest_rate:.2f}%")
    col4.metric("Crime Categories", total_categories)

    st.divider()

    st.subheader("Project Objectives")

    objective_col, scope_col = st.columns(2)

    with objective_col:
        st.markdown("#### Objectives")
        st.markdown("""
        - Inspect and clean historical crime data.
        - Explore crime category and time distributions.
        - Examine statistical patterns and outliers.
        - Integrate data with a relational database.
        - Present insights through an interactive dashboard.
        """)

    with scope_col:
        st.markdown("#### Technology Stack")
        st.markdown("""
        - Python and Pandas
        - NumPy
        - Matplotlib and Seaborn
        - SQLite database
        - SQL queries and views
        - Streamlit dashboard
        """)

    st.divider()

    st.subheader("Dataset Snapshot")

    info_col, limitation_col = st.columns(2)

    with info_col:
        st.metric("Rows", total_records)
        st.metric("Columns in cleaned database table", len(table_info))

    with limitation_col:
        st.markdown("#### Important dataset limitations")
        st.warning("""
        - The dataset is heavily concentrated in 2016.
        - Records cover only six observed months.
        - The date field does not contain time-of-day.
        - 29 records have missing geographic coordinates.
        """)


# ============================================================
# 8. USE CASE 1 - DATA INSPECTION AND CLEANING
# ============================================================

elif selected_section == "Use Case 1 - Data Quality":

    section_heading(
        "02",
        "Use Case 1 — Data Inspection and Cleaning",
        "Dataset structure, quality checks, cleaning decisions "
        "and relational database preparation."
    )

    total_records = len(crime_data)
    total_columns = len(table_info)
    missing_cases = crime_data["case_number"].isna().sum()
    missing_dates = crime_data["date"].isna().sum()

    coordinate_columns = [
        "latitude", "longitude",
        "x_coordinate", "y_coordinate"
    ]

    missing_coordinates = crime_data[
        coordinate_columns
    ].isna().all(axis=1).sum()

    duplicate_cases = crime_data[
        "case_number"
    ].duplicated().sum()

    # KPI cards
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Crime Records", total_records)
    c2.metric("Database Columns", total_columns)
    c3.metric("Missing Case Numbers", missing_cases)
    c4.metric("Missing Coordinates", missing_coordinates)

    st.divider()

    # Schema and quality
    schema_col, quality_col = st.columns([1.2, 1])

    with schema_col:
        st.subheader("Database Schema")

        st.dataframe(
            table_info[
                ["name", "type", "notnull", "pk"]
            ],
            use_container_width=True,
            hide_index=True,
            height=360
        )

    with quality_col:
        st.subheader("Data Validation")

        validation = pd.DataFrame({
            "Validation": [
                "Total records",
                "Missing case numbers",
                "Missing dates",
                "Duplicate case numbers",
                "Records missing all coordinates"
            ],
            "Result": [
                total_records,
                missing_cases,
                missing_dates,
                duplicate_cases,
                missing_coordinates
            ]
        })

        st.dataframe(
            validation,
            use_container_width=True,
            hide_index=True
        )

        st.success("Validation summary loaded from database.")

    st.divider()

    # Missing value analysis
    st.subheader("Missing Value Analysis")

    missing_summary = pd.DataFrame({
        "Column": crime_data.columns,
        "Missing Values": crime_data.isna().sum().values,
        "Missing Percentage": (
            crime_data.isna().mean().values * 100
        )
    })

    missing_summary = missing_summary.sort_values(
        "Missing Percentage",
        ascending=False
    )

    missing_col, missing_chart_col = st.columns([1.1, 1])

    with missing_col:
        st.dataframe(
            missing_summary.style.format({
                "Missing Percentage": "{:.2f}%"
            }),
            use_container_width=True,
            hide_index=True,
            height=330
        )

    with missing_chart_col:
        missing_plot = missing_summary[
            missing_summary["Missing Values"] > 0
        ].head(12)

        if not missing_plot.empty:

            fig, ax = plt.subplots(figsize=(7, 4))

            sns.barplot(
                data=missing_plot,
                x="Missing Percentage",
                y="Column",
                ax=ax
            )

            ax.set_title("Missing Values by Column")
            ax.set_xlabel("Missing (%)")
            ax.set_ylabel("")

            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        else:
            st.success("No missing values found.")

    st.info(
        "The four geographic coordinate fields each have "
        "29 missing values (5.82%). These records were retained "
        "rather than removed or imputed."
    )

    st.divider()

    # Cleaning decisions
    st.subheader("Data Cleaning and Preparation")

    cleaning_summary = pd.DataFrame({
        "Activity": [
            "Malformed CSV records",
            "Date conversion",
            "Missing case numbers",
            "Duplicate case numbers",
            "Missing coordinates",
            "Categorical standardization",
            "Derived date fields",
            "Original raw CSV"
        ],
        "Action": [
            "Two malformed records repaired in processed copy",
            "Dates converted to datetime",
            "No missing case numbers",
            "No duplicate case numbers",
            "29 records retained",
            "Categorical values standardized",
            "Year, Month and DayOfWeek derived",
            "Original file preserved"
        ],
        "Status": [
            "Completed",
            "Completed",
            "Passed",
            "Passed",
            "Retained",
            "Completed",
            "Completed",
            "Preserved"
        ]
    })

    st.dataframe(
        cleaning_summary,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Reference table summary
    st.subheader("Database Reference Tables")

    reference_tables = {
        "city_community": "Community Areas",
        "district_ps_info": "Police Districts",
        "police_beat_info": "Police Beats",
        "ward_office": "Ward Offices",
        "iucr": "IUCR Crime Codes"
    }

    reference_results = []

    with sqlite3.connect(DB_PATH) as conn:

        for table_name, description in reference_tables.items():

            count = pd.read_sql_query(
                f'SELECT COUNT(*) AS total FROM "{table_name}"',
                conn
            ).iloc[0]["total"]

            reference_results.append({
                "Table": table_name,
                "Description": description,
                "Records": count
            })

    st.dataframe(
        pd.DataFrame(reference_results),
        use_container_width=True,
        hide_index=True
    )

    st.info("""
    Database design note: Ward numbers are not unique in the
    ward-office reference data. Therefore, the ward-office
    table uses its own synthetic primary key, and no direct
    ward-office foreign key is assigned to crime records.
    """)


# ============================================================
# 9. USE CASE 2 - EXPLORATORY DATA ANALYSIS
# ============================================================

elif selected_section == "Use Case 2 - EDA":

    section_heading(
        "03",
        "Use Case 2 — Exploratory Data Analysis",
        "Explore crime patterns by year, category, arrest status, "
        "month, weekday and community area."
    )

    df = filtered_data.copy()

    st.caption(
        f"Filtered records: {len(df):,} of {len(crime_data):,}"
    )

    if df.empty:
        st.warning("No records match the selected filters.")

    else:

        # Annual crime trends
        yearly = (
            df.groupby("Year")
            .size()
            .reset_index(name="Crime_Count")
        )

        fig, ax = plt.subplots(figsize=(8, 4))

        sns.barplot(
            data=yearly,
            x="Year",
            y="Crime_Count",
            ax=ax
        )

        ax.set_title("Annual Crime Trends")
        ax.set_xlabel("Year")
        ax.set_ylabel("Recorded Crimes")

        display_chart_with_findings(
            "Requirement 1 — Annual Crime Trends",
            fig,
            [
                f"{int(yearly.loc[yearly['Crime_Count'].idxmax(), 'Year'])} "
                "has the highest count among the selected records.",
                f"{len(df):,} records are included after filters.",
                "Earlier years have very small sample sizes."
            ],
            "The complete dataset is heavily concentrated in 2016. "
            "Year-to-year comparisons should be interpreted cautiously."
        )

        # Top crime categories
        top_categories = (
            df["primary_type"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        top_categories.columns = [
            "Primary_Type", "Crime_Count"
        ]

        fig, ax = plt.subplots(figsize=(8, 5))

        sns.barplot(
            data=top_categories,
            x="Crime_Count",
            y="Primary_Type",
            ax=ax
        )

        ax.set_title("Top 10 Crime Categories")
        ax.set_xlabel("Recorded Crimes")
        ax.set_ylabel("")

        most_common = top_categories.iloc[0]

        display_chart_with_findings(
            "Requirement 2 — Top 10 Crime Categories",
            fig,
            [
                f"{most_common['Primary_Type']} is the most frequent category.",
                f"It accounts for {int(most_common['Crime_Count'])} records.",
                "The chart ranks the ten most common categories."
            ],
            "Category counts describe this dataset and are not "
            "population-adjusted crime rates."
        )

        # Arrest rates by year
        yearly_arrests = (
            df.groupby("Year")
            .agg(
                Total_Crimes=("case_number", "count"),
                Total_Arrests=("arrest_flag", "sum")
            )
            .reset_index()
        )

        yearly_arrests["Arrest_Rate"] = (
            yearly_arrests["Total_Arrests"]
            / yearly_arrests["Total_Crimes"] * 100
        )

        fig, ax = plt.subplots(figsize=(8, 4))

        sns.barplot(
            data=yearly_arrests,
            x="Year",
            y="Arrest_Rate",
            ax=ax
        )

        ax.set_title("Yearly Arrest Rates")
        ax.set_ylabel("Arrest Rate (%)")
        ax.set_ylim(0, 105)

        overall_rate = safe_percentage(
            int(df["arrest_flag"].sum()),
            len(df)
        )

        display_chart_with_findings(
            "Requirement 3 — Yearly Arrest Rates",
            fig,
            [
                f"Overall arrest rate in filtered records: {overall_rate:.2f}%.",
                "Arrest rates vary across observed years.",
                "Small yearly samples can produce unstable percentages."
            ],
            "An arrest does not necessarily imply a conviction. "
            "The dataset records arrest status only."
        )

        # Monthly crime distribution
        monthly = (
            df.groupby("Month")
            .size()
            .reset_index(name="Crime_Count")
        )

        month_labels = {
            1: "January", 2: "February",
            3: "March", 4: "April",
            5: "May", 6: "June",
            7: "July", 8: "August",
            9: "September", 10: "October",
            11: "November", 12: "December"
        }

        monthly["Month_Name"] = monthly["Month"].map(month_labels)

        fig, ax = plt.subplots(figsize=(8, 4))

        sns.barplot(
            data=monthly,
            x="Month_Name",
            y="Crime_Count",
            ax=ax
        )

        ax.set_title("Monthly Crime Distribution")
        ax.set_xlabel("")
        ax.set_ylabel("Recorded Crimes")
        ax.tick_params(axis="x", rotation=35)

        peak_month = monthly.loc[
            monthly["Crime_Count"].idxmax()
        ]

        display_chart_with_findings(
            "Requirement 4 — Monthly Crime Distribution",
            fig,
            [
                f"{peak_month['Month_Name']} has the highest count.",
                f"{int(peak_month['Crime_Count'])} records occur in that month.",
                f"{monthly['Month'].nunique()} distinct months appear in the selected data."
            ],
            "The complete dataset contains records for only six months. "
            "This is not a complete annual seasonal pattern."
        )

        # Community area counts
        community_counts = (
            df.dropna(subset=["community_name"])
            .groupby("community_name")
            .size()
            .sort_values(ascending=False)
            .head(10)
            .reset_index(name="Crime_Count")
        )

        fig, ax = plt.subplots(figsize=(8, 5))

        sns.barplot(
            data=community_counts,
            x="Crime_Count",
            y="community_name",
            ax=ax
        )

        ax.set_title("Top 10 Community Areas")
        ax.set_xlabel("Recorded Crimes")
        ax.set_ylabel("")

        top_community = community_counts.iloc[0]

        display_chart_with_findings(
            "Requirement 5 — Top 10 Community Areas",
            fig,
            [
                f"{top_community['community_name']} has the highest count.",
                f"It has {int(top_community['Crime_Count'])} records.",
                "Counts are based on recorded incidents, not population."
            ],
            "These counts should not be interpreted as proof that "
            "one community is more dangerous than another."
        )

        # Monthly weekday heatmap
        heatmap_data = pd.crosstab(
            df["Month"],
            df["DayOfWeek"]
        )

        weekday_order = [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ]

        heatmap_data = heatmap_data.reindex(
            columns=weekday_order,
            fill_value=0
        )

        fig, ax = plt.subplots(figsize=(8, 5))

        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt="d",
            cmap="YlOrRd",
            ax=ax
        )

        ax.set_title("Crime by Month and Day of Week")
        ax.set_xlabel("Weekday")
        ax.set_ylabel("Month")

        display_chart_with_findings(
            "Requirement 6 — Month and Weekday Heatmap",
            fig,
            [
                "The heatmap shows the distribution across weekdays.",
                "May and Wednesday are especially prominent in the complete sample.",
                "Some month-weekday combinations have few or no records."
            ],
            "The observed concentration should not be treated as "
            "a general citywide weekly or seasonal pattern."
        )


# ============================================================
# 10. USE CASE 3 - STATISTICAL ANALYSIS
# ============================================================

elif selected_section == "Use Case 3 - Statistics":

    section_heading(
        "04",
        "Use Case 3 — Statistical Analysis",
        "Examine community-area outliers, numeric relationships "
        "and limitations in the available date information."
    )

    df = filtered_data.copy()

    if df.empty:
        st.warning("No records match the selected filters.")

    else:

        # Community area boxplot
        community_counts = (
            df.dropna(subset=["community_code"])
            .groupby("community_code")
            .size()
            .reset_index(name="Crime_Count")
        )

        q1 = community_counts["Crime_Count"].quantile(0.25)
        q3 = community_counts["Crime_Count"].quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = community_counts[
            (community_counts["Crime_Count"] < lower_bound)
            | (community_counts["Crime_Count"] > upper_bound)
        ]

        fig, ax = plt.subplots(figsize=(7, 4))

        sns.boxplot(
            y=community_counts["Crime_Count"],
            ax=ax
        )

        ax.set_title("Community Area Crime Count Distribution")
        ax.set_ylabel("Recorded Crimes")

        display_chart_with_findings(
            "Requirement 1 — Community Area Outlier Analysis",
            fig,
            [
                f"Q1: {q1:.2f}",
                f"Q3: {q3:.2f}",
                f"IQR: {iqr:.2f}",
                f"Upper outlier threshold: {upper_bound:.2f}",
                f"Number of outlier areas: {len(outliers)}"
            ],
            "IQR outliers identify unusually high counts in this sample. "
            "They do not independently establish elevated crime risk."
        )

        st.markdown("#### Identified outlier community codes")
        st.dataframe(
            outliers,
            use_container_width=True,
            hide_index=True
        )

        # Hourly analysis limitation
        st.markdown("### Requirement 2 — Hourly Crime Distribution")

        st.warning(
            "The available date field contains dates without time-of-day. "
            "A meaningful hourly crime distribution cannot be calculated."
        )

        st.markdown(
            "Extracting an hour from a date-only value would produce "
            "an artificial constant value and misleading results."
        )

        # Correlation analysis
        st.markdown("### Requirement 3 — Correlation Analysis")

        correlation_columns = [
            "latitude",
            "longitude",
            "Year",
            "Month"
        ]

        correlation_data = df[
            correlation_columns
        ].copy()

        correlation_data["Arrest"] = (
            df["arrest_flag"].astype(int)
        )

        correlation_data["Domestic"] = (
            df["domestic_flag"].astype(int)
        )

        correlation_matrix = correlation_data.corr(
            numeric_only=True
        )

        fig, ax = plt.subplots(figsize=(7, 5))

        sns.heatmap(
            correlation_matrix,
            annot=True,
            cmap="coolwarm",
            center=0,
            fmt=".2f",
            ax=ax
        )

        ax.set_title("Correlation Heatmap")

        display_chart_with_findings(
            "Correlation Heatmap",
            fig,
            [
                "Arrest and domestic status are encoded as 0 and 1.",
                "Latitude and longitude describe geographic position.",
                "Year and month are time-related variables."
            ],
            "Correlation does not establish causation. "
            "Coordinates and calendar fields are not direct measures "
            "of crime risk. Missing values reduce available pairs."
        )


# ============================================================
# 11. USE CASE 4 - SQL ANALYSIS
# ============================================================

elif selected_section == "Use Case 4 - SQL Analysis":

    section_heading(
        "05",
        "Use Case 4 — SQL Database Integration",
        "Review SQL summary views, annual crime counts, category "
        "percentages and annual arrest summaries."
    )

    try:

        with sqlite3.connect(DB_PATH) as conn:

            yearly_view = pd.read_sql_query(
                "SELECT * FROM vw_crime_yearly ORDER BY Year",
                conn
            )

            category_view = pd.read_sql_query(
                """
                SELECT *
                FROM vw_crime_by_category
                ORDER BY Crime_Count DESC
                LIMIT 10
                """,
                conn
            )

            database_views = pd.read_sql_query(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'view'
                """,
                conn
            )

        st.subheader("SQL Views")

        st.dataframe(
            database_views,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Yearly Crime Summary")

        st.dataframe(
            yearly_view,
            use_container_width=True,
            hide_index=True
        )

        if "Year" in yearly_view.columns:

            count_column = next(
                (
                    c for c in yearly_view.columns
                    if c.lower() == "total_crimes"
                ),
                None
            )

            if count_column:

                fig, ax = plt.subplots(figsize=(8, 4))

                sns.barplot(
                    data=yearly_view,
                    x="Year",
                    y=count_column,
                    ax=ax
                )

                ax.set_title("SQL View - Yearly Crime Counts")
                ax.set_ylabel("Total Crimes")

                display_chart_with_findings(
                    "SQL Requirement 1 — Yearly Crime Counts",
                    fig,
                    [
                        "The yearly view summarizes crime records.",
                        "The view also includes annual arrest information.",
                        "The 2016 sample dominates the total."
                    ],
                    "The SQL view provides a reusable summary "
                    "for downstream reporting."
                )

        st.subheader("Crime Category SQL Summary")

        st.dataframe(
            category_view,
            use_container_width=True,
            hide_index=True
        )

        if not category_view.empty:

            category_count_column = next(
                (
                    c for c in category_view.columns
                    if c.lower() == "crime_count"
                ),
                None
            )

            category_name_column = next(
                (
                    c for c in category_view.columns
                    if c.lower() == "crime_category"
                ),
                None
            )

            if category_count_column and category_name_column:

                fig, ax = plt.subplots(figsize=(8, 5))

                sns.barplot(
                    data=category_view,
                    x=category_count_column,
                    y=category_name_column,
                    ax=ax
                )

                ax.set_title("SQL View - Top Crime Categories")

                display_chart_with_findings(
                    "SQL Requirement 2 — Category Summary",
                    fig,
                    [
                        f"{category_view.iloc[0][category_name_column]} "
                        "is the leading category in the SQL summary.",
                        "The view provides category counts and percentages.",
                        "The result can support reusable reporting."
                    ],
                    "SQL summaries should be interpreted in the context "
                    "of the sample's uneven time coverage."
                )

    except Exception as e:
        st.error(f"SQL analysis section could not load: {e}")


# ============================================================
# 12. FINAL FINDINGS AND LIMITATIONS
# ============================================================

elif selected_section == "Final Findings":

    section_heading(
        "06",
        "Final Findings and Recommendations",
        "Summary of analytical observations, data limitations "
        "and responsible interpretation."
    )

    st.subheader("Key Analytical Findings")

    findings = [
        (
            "Crime category concentration",
            "Theft and Battery are the two most frequent categories "
            "in the complete sample."
        ),
        (
            "Arrest outcomes",
            "124 of 498 incidents have an arrest recorded, "
            "an overall rate of approximately 24.90%."
        ),
        (
            "Time distribution",
            "447 records occur in May. The available dates cover "
            "only six months."
        ),
        (
            "Community area counts",
            "Austin has the highest recorded community-area count "
            "in the analyzed sample."
        ),
        (
            "Statistical outliers",
            "Austin, Humboldt Park and Near North Side exceed "
            "the earlier community-count IQR upper threshold."
        ),
        (
            "Database integration",
            "The crime data and reference tables are integrated "
            "in SQLite, with reusable SQL summary views."
        )
    ]

    for title, description in findings:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(description)

    st.divider()

    st.subheader("Data Limitations")

    limitations = [
        "The dataset contains only 498 records.",
        "490 records belong to 2016, so annual comparisons are unreliable.",
        "The data includes records for only six months.",
        "The date field does not contain hour or minute information.",
        "29 records have missing geographic coordinates.",
        "Crime counts are not adjusted for community population.",
        "Historical sample data does not represent a live crime feed."
    ]

    for item in limitations:
        st.markdown(f"- {item}")

    st.divider()

    st.subheader("Recommendations")

    st.markdown("""
    1. Obtain a larger and more consistently sampled dataset
       before making long-term trend comparisons.
    2. Obtain timestamp-level data before performing hourly analysis.
    3. Consider population-adjusted measures for geographic comparisons.
    4. Preserve missing source records and document data-quality decisions.
    5. Extend the database pipeline with scheduled ingestion if
       near-real-time analysis is required.
    6. Use the dashboard as an analytical support tool, not as
       a standalone measure of community safety.
    """)


# ============================================================
# 13. FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#627D98; padding:15px;">
        Chicago Crime Analytics Dashboard |
        Python • Pandas • SQLite • Streamlit
        <br>
        Historical dataset analysis — not a live crime monitoring system
    </div>
    """,
    unsafe_allow_html=True
)
