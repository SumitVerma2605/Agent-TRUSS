"""
Laboratory Sample Management System
=====================================
A Streamlit-based system for managing lab samples,
with SQLite storage, search, and dashboard insights.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

from database import (
    init_db,
    add_sample,
    get_all_samples,
    search_samples,
    get_sample_by_id,
    update_sample,
    delete_sample,
    get_dashboard_stats,
    sample_id_exists,
)

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LabTrack — Sample Management",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .main { background: #0f1117; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #13151e !important;
        border-right: 1px solid #1e2130;
    }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #1a1d2e 0%, #1e2235 100%);
        border: 1px solid #2a2f45;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        margin-bottom: 8px;
    }
    .kpi-card .kpi-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2.4rem;
        font-weight: 600;
        color: #4fc3f7;
        line-height: 1;
    }
    .kpi-card .kpi-label {
        font-size: 0.78rem;
        color: #8892b0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 6px;
    }

    /* Section headings */
    .section-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #4fc3f7;
        border-bottom: 1px solid #1e2130;
        padding-bottom: 8px;
        margin-bottom: 20px;
    }

    /* Status badge */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .badge-active { background: #0d2137; color: #4fc3f7; border: 1px solid #4fc3f7; }
    .badge-pending { background: #1a1300; color: #ffc107; border: 1px solid #ffc107; }

    /* Table tweaks */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.82rem;
        letter-spacing: 0.5px;
    }

    /* Success / error */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
    }

    /* Logo area */
    .logo-area {
        text-align: center;
        padding: 24px 0 16px;
    }
    .logo-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.3rem;
        font-weight: 600;
        color: #e0e6ff;
        letter-spacing: 2px;
    }
    .logo-sub {
        font-size: 0.72rem;
        color: #4fc3f7;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Initialize DB ────────────────────────────────────────────────────────────
init_db()

# ── Sidebar navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="logo-area">
            <div style="font-size:2.2rem">🔬</div>
            <div class="logo-title">LABTRACK</div>
            <div class="logo-sub">Sample Management</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "➕ Add Sample", "🔍 Search Samples", "✏️ Edit / Delete"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        "<div style='color:#556; font-size:0.72rem; text-align:center;'>v1.0 · SQLite backend</div>",
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("## 📊 Dashboard")
    st.markdown('<div class="section-header">KEY METRICS</div>', unsafe_allow_html=True)

    stats = get_dashboard_stats()
    df_all = get_all_samples()

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-value">{stats["total"]}</div>'
            f'<div class="kpi-label">Total Samples</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-value">{stats["businesses"]}</div>'
            f'<div class="kpi-label">Businesses</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-value">{stats["this_month"]}</div>'
            f'<div class="kpi-label">This Month</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-value">{stats["today"]}</div>'
            f'<div class="kpi-label">Today</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-header">SAMPLES PER BUSINESS</div>', unsafe_allow_html=True)
        if not df_all.empty:
            biz_counts = (
                df_all.groupby("business_name")
                .size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
            )
            st.bar_chart(biz_counts.set_index("business_name")["count"])
        else:
            st.info("No data yet — add your first sample.")

    with col_right:
        st.markdown('<div class="section-header">RECENT SUBMISSIONS (10)</div>', unsafe_allow_html=True)
        if not df_all.empty:
            recent = df_all.sort_values("collection_date", ascending=False).head(10)[
                ["sample_id", "business_name", "collection_date"]
            ]
            st.dataframe(recent, use_container_width=True, hide_index=True)
        else:
            st.info("No submissions yet.")

    st.markdown('<div class="section-header">SAMPLE TYPES DISTRIBUTION</div>', unsafe_allow_html=True)
    if not df_all.empty and "sample_type" in df_all.columns:
        type_counts = (
            df_all["sample_type"]
            .fillna("Unspecified")
            .value_counts()
            .reset_index()
        )
        type_counts.columns = ["Sample Type", "Count"]
        st.dataframe(type_counts, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: ADD SAMPLE
# ════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Sample":
    st.markdown("## ➕ Add New Sample")
    st.markdown('<div class="section-header">SAMPLE REGISTRATION FORM</div>', unsafe_allow_html=True)

    with st.form("add_sample_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            sample_id = st.text_input(
                "Sample ID *",
                placeholder="e.g. LAB-2024-001",
                help="Must be unique across all records",
            )
            business_name = st.text_input(
                "Business Name *",
                placeholder="e.g. Acme Pharma Ltd.",
            )
            submitted_person = st.text_input(
                "Submitted By *",
                placeholder="Full name of submitting person",
            )

        with col2:
            lab_personnel = st.text_input(
                "Laboratory Personnel *",
                placeholder="Analyst / technician name",
            )
            collection_date = st.date_input(
                "Sample Collection Date *",
                value=date.today(),
                max_value=date.today(),
            )
            sample_type = st.selectbox(
                "Sample Type",
                ["", "Water", "Soil", "Blood", "Food", "Chemical", "Pharmaceutical", "Other"],
            )

        sample_stage = st.selectbox(
            "Sample Stage",
            ["Received", "In Progress", "Analysis Complete", "Report Issued", "Archived"],
        )
        remarks = st.text_area(
            "Remarks (optional)",
            placeholder="Any additional notes about the sample...",
            height=90,
        )

        submitted = st.form_submit_button("🧪 Register Sample", use_container_width=True)

    if submitted:
        # Validation
        errors = []
        if not sample_id.strip():
            errors.append("Sample ID is required.")
        elif sample_id_exists(sample_id.strip()):
            errors.append(f"Sample ID **{sample_id}** already exists. Use a unique ID.")
        if not business_name.strip():
            errors.append("Business Name is required.")
        if not submitted_person.strip():
            errors.append("Submitted Person Name is required.")
        if not lab_personnel.strip():
            errors.append("Laboratory Personnel is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            add_sample(
                sample_id=sample_id.strip(),
                business_name=business_name.strip(),
                submitted_person=submitted_person.strip(),
                lab_personnel=lab_personnel.strip(),
                collection_date=str(collection_date),
                sample_type=sample_type or "Unspecified",
                sample_stage=sample_stage,
                remarks=remarks.strip(),
            )
            st.success(f"✅ Sample **{sample_id}** registered successfully!")
            st.balloons()

# ════════════════════════════════════════════════════════════════════════════
# PAGE: SEARCH SAMPLES
# ════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Search Samples":
    st.markdown("## 🔍 Search & Retrieve Samples")
    st.markdown('<div class="section-header">SEARCH FILTERS</div>', unsafe_allow_html=True)

    with st.expander("🔧 Filter Options", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            q_sample_id = st.text_input("Sample ID", placeholder="Partial or full ID")
            q_business = st.text_input("Business Name", placeholder="Partial match")
        with fc2:
            q_person = st.text_input("Submitted By", placeholder="Person name")
            q_stage = st.selectbox(
                "Sample Stage",
                ["All", "Received", "In Progress", "Analysis Complete", "Report Issued", "Archived"],
            )
        with fc3:
            date_from = st.date_input("Date From", value=None)
            date_to = st.date_input("Date To", value=None)

        search_btn = st.button("🔍 Search", use_container_width=True, type="primary")

    # Auto-load all on first visit
    if "search_results" not in st.session_state:
        st.session_state.search_results = get_all_samples()

    if search_btn:
        results = search_samples(
            sample_id=q_sample_id,
            business_name=q_business,
            submitted_person=q_person,
            stage=q_stage if q_stage != "All" else "",
            date_from=str(date_from) if date_from else "",
            date_to=str(date_to) if date_to else "",
        )
        st.session_state.search_results = results

    df_results = st.session_state.search_results

    st.markdown(
        f'<div class="section-header">RESULTS — {len(df_results)} RECORD(S) FOUND</div>',
        unsafe_allow_html=True,
    )

    if not df_results.empty:
        # Sorting
        sort_col = st.selectbox(
            "Sort by",
            df_results.columns.tolist(),
            index=df_results.columns.tolist().index("collection_date")
            if "collection_date" in df_results.columns
            else 0,
        )
        sort_asc = st.checkbox("Ascending", value=False)
        df_display = df_results.sort_values(sort_col, ascending=sort_asc)

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Download
        csv_buffer = io.StringIO()
        df_display.to_csv(csv_buffer, index=False)
        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv_buffer.getvalue(),
            file_name=f"lab_samples_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No records match your search criteria.")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: EDIT / DELETE
# ════════════════════════════════════════════════════════════════════════════
elif page == "✏️ Edit / Delete":
    st.markdown("## ✏️ Edit / Delete Records")
    st.markdown('<div class="section-header">SELECT RECORD TO MODIFY</div>', unsafe_allow_html=True)

    df_all = get_all_samples()

    if df_all.empty:
        st.info("No records found. Add samples first.")
    else:
        sample_ids = df_all["sample_id"].tolist()
        selected_id = st.selectbox("Select Sample ID", sample_ids)

        if selected_id:
            record = get_sample_by_id(selected_id)

            if record:
                st.markdown('<div class="section-header">EDIT RECORD</div>', unsafe_allow_html=True)

                with st.form("edit_form"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        new_business = st.text_input("Business Name", value=record["business_name"])
                        new_person = st.text_input("Submitted By", value=record["submitted_person"])
                        new_lab = st.text_input("Lab Personnel", value=record["lab_personnel"])
                    with ec2:
                        new_date = st.date_input(
                            "Collection Date",
                            value=datetime.strptime(record["collection_date"], "%Y-%m-%d").date(),
                        )
                        stage_options = ["Received", "In Progress", "Analysis Complete", "Report Issued", "Archived"]
                        new_stage = st.selectbox(
                            "Sample Stage",
                            stage_options,
                            index=stage_options.index(record["sample_stage"])
                            if record["sample_stage"] in stage_options
                            else 0,
                        )
                        type_options = ["Water", "Soil", "Blood", "Food", "Chemical", "Pharmaceutical", "Other", "Unspecified"]
                        new_type = st.selectbox(
                            "Sample Type",
                            type_options,
                            index=type_options.index(record["sample_type"])
                            if record["sample_type"] in type_options
                            else 0,
                        )
                    new_remarks = st.text_area("Remarks", value=record.get("remarks", ""), height=80)

                    save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)

                if save_btn:
                    update_sample(
                        sample_id=selected_id,
                        business_name=new_business.strip(),
                        submitted_person=new_person.strip(),
                        lab_personnel=new_lab.strip(),
                        collection_date=str(new_date),
                        sample_type=new_type,
                        sample_stage=new_stage,
                        remarks=new_remarks.strip(),
                    )
                    st.success(f"✅ Record **{selected_id}** updated successfully!")

                st.markdown("---")
                st.markdown("#### ⚠️ Danger Zone")
                with st.expander("Delete this record"):
                    st.warning(
                        f"You are about to permanently delete **{selected_id}**. This action cannot be undone."
                    )
                    confirm = st.checkbox("I confirm I want to delete this record")
                    if st.button("🗑️ Delete Record", type="primary", disabled=not confirm):
                        delete_sample(selected_id)
                        st.success(f"Record **{selected_id}** has been deleted.")
                        st.rerun()
