"""
Sententia Core - Streamlit UI for Requirements Management

This module provides a Streamlit-based frontend for interacting with the backend
Requirements Management API, enabling users to view, add, edit, validate, approve,
and export requirements dynamically.

Author: Chris Senanayake
"""
import pathlib, sys
this_dir = pathlib.Path(__file__).resolve().parent       # /.../requirements_ui
repo_root = this_dir.parent                              # /... (contains 'sententia')
sys.path.insert(0, str(repo_root))
import streamlit as st
import httpx
import pandas as pd
import io
import json
from sententia.render import render_doc


# Backend service URL
BACKEND_URL = "http://app:8000"

# Configure Streamlit page
st.set_page_config(page_title="Requirements Management System", layout="wide")

# Sidebar menu navigation
menu = st.sidebar.radio(
    "Navigation",
    ["View/Edit Requirements", "Add New Requirement", "Validate & Approve", "Export Requirements", "Preview & Export", "Load Demo Data"]
)

# ---------------- API Helpers ----------------

def fetch_requirements():
    """
    Fetch all requirements from the backend.

    Returns
    -------
    list
        List of requirement dictionaries.
    """
    with httpx.Client() as client:
        response = client.get(f"{BACKEND_URL}/requirements")
        if response.status_code == 200:
            return response.json()
        return []

def fetch_metadata(field: str):
    """
    Fetch allowed metadata values for a specific field.

    Parameters
    ----------
    field : str
        Field name ('types', 'priority', 'source', 'status').

    Returns
    -------
    list
        List of valid values, or empty list if error.
    """
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/metadata/{field}")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        st.error(f"Error fetching metadata for {field}: {e}")
    return []

def create_requirement(data):
    """Create a new requirement."""
    with httpx.Client() as client:
        return client.post(f"{BACKEND_URL}/requirements", json=data)

def update_requirement(display_id, data):
    """Update an existing requirement."""
    with httpx.Client() as client:
        return client.put(f"{BACKEND_URL}/requirements/{display_id}", json=data)

def delete_requirement(display_id):
    """Delete a requirement."""
    with httpx.Client() as client:
        return client.delete(f"{BACKEND_URL}/requirements/{display_id}")

def trigger_demo_load(demo_name: str):
    """Triggers the backend to load specified demo data."""
    with httpx.Client() as client:
        return client.post(f"{BACKEND_URL}/load-demo/{demo_name}") # Updated endpoint

def validate_fields(type_, description, source, priority, status):
    """Validate mandatory requirement fields."""
    errors = []
    if not type_:
        errors.append("Type is required.")
    if not description.strip():
        errors.append("Description is required.")
    if not source:
        errors.append("Source is required.")
    if not priority:
        errors.append("Priority is required.")
    if not status:
        errors.append("Status is required.")
    return errors

# ---------------- UI Sections ----------------


# ---------------- Preview & Export Doc ----------------
def preview_and_export():
    """
    Preview a document rendered by Sententia templates and allow download.
    """
    st.header("Preview & Export Document")
    
    # Mapping document types to requirement layers
    doc_layer_map = {
        "srd": "Business",
        "sss": "System",
        "srs": "Software",
        "std": "Test"
    }
    
    doc_type = st.selectbox(
        "Document type",
        list(doc_layer_map.keys()),
        index=0,
        help="Select which template to render."
    )

    # Fetch all requirements
    all_requirements = fetch_requirements()
    
    # Filter requirements based on the selected document type
    filtered_requirements = [
        {
            "id": req.get("display_id", ""),
            "title": req.get("title", ""),
            "description": req.get("description", "")
        }
        for req in all_requirements 
        if req.get("layer", "").lower() == doc_layer_map[doc_type].lower()
    ]

    ctx = {
        "project_name": "Demo Project",
        "requirements": filtered_requirements or [
            {"id": "No Requirements", "title": f"No {doc_layer_map[doc_type]} layer requirements found"}
        ]
    }

    try:
        md_output = render_doc(doc_type, ctx)
    except Exception as exc:
        st.error(f"Render error: {exc}")
        return

    st.subheader("Preview")
    st.markdown(md_output)

    st.download_button(
        "Download Markdown",
        data=md_output.encode("utf-8"),
        file_name=f"{doc_type}.md",
        mime="text/markdown"
    )

def load_demo_data_ui(): # Renamed function
    """UI to select and load different demo datasets."""
    st.title("📥 Load Demo Data")
    st.warning("⚠️ Loading demo data will clear all existing requirements. This action cannot be undone.")

    demo_options = {
        "Ice Cream Shop": "ice_cream",
        "Death Star Project": "death_star"
    }
    selected_demo_display_name = st.selectbox("Select Demo to Load:", options=list(demo_options.keys()))

    if st.button(f"Load {selected_demo_display_name} Demo"):
        demo_name_param = demo_options[selected_demo_display_name]
        try:
            result = trigger_demo_load(demo_name_param) # Call updated trigger function
            if result.status_code == 200:
                st.success(f"{selected_demo_display_name} demo data loaded successfully! Existing requirements have been cleared.")
                # Optionally clear parts of session state if needed, e.g., editing/deleting states
                st.session_state['editing'] = {}
                st.session_state['deleting'] = {}
                st.rerun() # Rerun to refresh the view immediately
            else:
                st.error(f"Failed to load demo data: {result.status_code} - {result.text}")
        except httpx.RequestError as e:
            st.error(f"Error connecting to backend: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")


def view_edit_requirements():
    st.title("📜 View/Edit Requirements")

    all_reqs = fetch_requirements()
    if not all_reqs:
        st.info("No requirements found.")
        return

    layer_options = [
        "All layers",
        "Unspecified layer",
        "Business",
        "System",
        "Software",
        "Test",
    ]
    selected_layer = st.selectbox("Filter by layer", layer_options, index=0)

    if selected_layer == "All layers":
        requirements = all_reqs
    elif selected_layer == "Unspecified layer":
        requirements = [r for r in all_reqs if not r.get("layer")]
    else:
        requirements = [r for r in all_reqs if r.get("layer") == selected_layer]

    # show quick count badge
    st.caption(f"{len(requirements)} requirement(s) shown")

    for req in requirements:
        disp_id = req.get("display_id", "UNKNOWN")
        layer_lbl = req.get("layer", "Unspecified")
        with st.expander(f"[{layer_lbl}] {disp_id}: {req['description']}"):
            if st.session_state['deleting'].get(disp_id, False):
                confirm_delete_ui(req)
            elif not st.session_state['editing'].get(disp_id, False):
                view_requirement_ui(req)
            else:
                edit_requirement_ui(req)

def confirm_delete_ui(req):
    """Show delete confirmation UI."""
    st.warning(f"Are you sure you want to delete {req['display_id']}?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"✅ Confirm Delete {req['display_id']}", key=f"confirm_delete_{req['display_id']}"):
            result = delete_requirement(req["display_id"])
            if result.status_code == 200:
                st.success("Requirement deleted successfully.")
                st.session_state['deleting'][req['display_id']] = False
                st.rerun()
            else:
                st.error("Deletion failed.")
    with col2:
        if st.button(f"❌ Cancel", key=f"cancel_delete_{req['display_id']}"):
            st.session_state['deleting'][req['display_id']] = False
            st.rerun()

def view_requirement_ui(req):
    """Display requirement details in read-only mode."""
    st.markdown(f"**Layer:** {req.get('layer', 'Unspecified')}")
    st.markdown(f"**Type:** {req['type']}")
    st.markdown(f"**Priority:** {req['priority']}")
    st.markdown(f"**Status:** {req['status']}")
    st.markdown(f"**Rationale:** {req.get('rationale', '')}")
    st.markdown(f"**Source:** {req.get('source', '')}")
    st.markdown(f"**Verification:** {req.get('verification', '')}")

    links = req.get("links", [])
    if links:
        st.markdown("**Links:**")
        for link in links:
            st.markdown(f"- {link['type']} ➞ `{link['target_id']}`")

    if req.get("versions"):
        st.markdown("---")
        st.subheader("📜 Version History")
        for v in reversed(req["versions"]):
            st.markdown(f"- **{v['timestamp']}**")
            st.json(v["data"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"✏️ Edit {req['display_id']}", key=f"edit_btn_{req['display_id']}"):
            st.session_state['editing'][req['display_id']] = True
            st.rerun()
    with col2:
        if st.button(f"🗑️ Delete {req['display_id']}", key=f"delete_btn_{req['display_id']}"):
            st.session_state['deleting'][req['display_id']] = True
            st.rerun()

def edit_requirement_ui(req):
    """Provide a form to edit a requirement."""
    type_options = fetch_metadata("types")
    priority_options = fetch_metadata("priority")
    source_options = fetch_metadata("source")
    status_options = fetch_metadata("status")
    all_requirements = fetch_requirements()
    available_target_ids = [r["display_id"] for r in all_requirements if r["display_id"] != req["display_id"]]
    link_types = ["DependsOn", "Satisfies", "Refines"]

    session_key = f"link_rows_{req['display_id']}"
    if session_key not in st.session_state:
        st.session_state[session_key] = req.get("links", [])

    link_rows = st.session_state[session_key]

    with st.form(f"edit_form_{req['display_id']}"):
        st.text_input("Display ID", value=req["display_id"], disabled=True)
        type_ = st.selectbox("Type", type_options, index=type_options.index(req["type"]))
        description = st.text_area("Description", value=req["description"])
        rationale = st.text_area("Rationale", value=req.get("rationale", ""))
        source = st.selectbox("Source", source_options, index=source_options.index(req.get("source", source_options[0])))
        priority = st.selectbox("Priority", priority_options, index=priority_options.index(req["priority"]))
        status = st.selectbox("Status", status_options, index=status_options.index(req["status"]))
        verification = st.text_area("Verification", value=req.get("verification", ""))

        st.markdown("**Edit Links**")
        updated_links = []
        for i, link in enumerate(link_rows):
            col1, col2, col3 = st.columns([2, 1, 0.5])
            with col1:
                target = st.selectbox(f"Target {i+1}", ["None"] + available_target_ids,
                                      index=(available_target_ids.index(link["target_id"]) + 1)
                                      if link["target_id"] in available_target_ids else 0,
                                      key=f"edit_target_{req['display_id']}_{i}")
            with col2:
                type_val = st.selectbox(f"Type {i+1}", link_types,
                                        index=link_types.index(link["type"]),
                                        key=f"edit_type_{req['display_id']}_{i}")
            with col3:
                if st.form_submit_button(f"Remove Link {i+1}"):
                    st.session_state[session_key].pop(i)
                    st.rerun()
            if target != "None":
                updated_links.append({"target_id": target, "type": type_val})

        if st.form_submit_button("➕ Add Link"):
            st.session_state[session_key].append({"target_id": "", "type": "DependsOn"})
            st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            save = st.form_submit_button("Save Changes")
        with col2:
            cancel = st.form_submit_button("Cancel")

        if save:
            errors = validate_fields(type_, description, source, priority, status)
            if errors:
                for error in errors:
                    st.warning(error)
            else:
                updated_req = {
                    "type": type_,
                    "description": description,
                    "rationale": rationale,
                    "source": source,
                    "priority": priority,
                    "status": status,
                    "verification": verification,
                    "links": updated_links
                }
                result = update_requirement(req["display_id"], updated_req)
                if result.status_code == 200:
                    st.success("Requirement updated successfully.")
                    st.session_state['editing'][req['display_id']] = False
                    st.session_state.pop(session_key, None)
                    st.rerun()
                else:
                    st.error("Update failed.")

        if cancel:
            st.session_state['editing'][req['display_id']] = False
            st.session_state.pop(session_key, None)
            st.rerun()



def add_new_requirement():
    """UI to add a new requirement."""
    st.title("➕ Add New Requirement")

    type_options = fetch_metadata("types")
    priority_options = fetch_metadata("priority")
    source_options = fetch_metadata("source")
    status_options = fetch_metadata("status")

    with st.form(key="requirement_form"):
        type_ = st.selectbox("Type", type_options)
        description = st.text_area("Description")
        rationale = st.text_area("Rationale")
        source = st.selectbox("Source", source_options)
        priority = st.selectbox("Priority", priority_options)
        status = st.selectbox("Status", status_options)
        verification = st.text_area("Verification")
        submit = st.form_submit_button("Save")

        if submit:
            errors = validate_fields(type_, description, source, priority, status)
            if errors:
                for error in errors:
                    st.warning(error)
            else:
                payload = {
                    "type": type_,
                    "description": description,
                    "rationale": rationale,
                    "source": source,
                    "priority": priority,
                    "status": status,
                    "verification": verification
                }
                result = create_requirement(payload)
                if result.status_code == 200:
                    st.success("Requirement created successfully.")
                else:
                    st.error("Failed to create requirement.")

def validate_and_approve():
    """UI to validate and approve/reject draft requirements."""
    st.title("✅ Validate & Approve Requirements")
    requirements = fetch_requirements()
    draft_reqs = [r for r in requirements if r["status"] == "Draft"]
    if not draft_reqs:
        st.info("No draft requirements.")
        return

    for req in draft_reqs:
        with st.expander(f"{req['display_id']}: {req['description']}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Approve {req['display_id']}", key=f"approve_{req['display_id']}"):
                    req["status"] = "Approved"
                    result = update_requirement(req["display_id"], req)
                    if result.status_code == 200:
                        st.success("Approved successfully.")
                        st.rerun()
                    else:
                        st.error("Approval failed.")
            with col2:
                if st.button(f"Reject {req['display_id']}", key=f"reject_{req['display_id']}"):
                    req["status"] = "Rejected"
                    result = update_requirement(req["display_id"], req)
                    if result.status_code == 200:
                        st.success("Rejected successfully.")
                        st.rerun()
                    else:
                        st.error("Rejection failed.")

def export_requirements():
    """UI to export all requirements and traceability matrix as CSV.

    Includes:
    - CSV download of all current requirements
    - Preview and download of the traceability matrix from the backend
    """
    st.title("📤 Export Requirements")

    # Requirements Export
    requirements = fetch_requirements()
    if requirements:
        df = pd.DataFrame(requirements)
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Requirements as CSV",
            data=csv,
            file_name="requirements_export.csv",
            mime="text/csv"
        )
    else:
        st.info("No requirements to export.")

    st.markdown("---")
    st.subheader("📊 Traceability Matrix Preview")

    # Traceability Matrix Export
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/export/traceability")
            if response.status_code == 200:
                matrix_text = response.text
                df_matrix = pd.read_csv(io.StringIO(matrix_text))
                st.dataframe(df_matrix, use_container_width=True)
                st.download_button(
                    label="⬇️ Download Traceability Matrix",
                    data=matrix_text,
                    file_name="traceability_matrix.csv",
                    mime="text/csv"
                )
            else:
                st.error("Failed to fetch traceability matrix.")
    except Exception as e:
        st.error(f"Error loading matrix: {e}")


# ---------------- Main Application Logic ----------------

if 'editing' not in st.session_state:
    st.session_state['editing'] = {}
if 'deleting' not in st.session_state:
    st.session_state['deleting'] = {}
if 'menu' not in st.session_state: # Ensure menu state is initialized
    st.session_state.menu = "View/Edit Requirements"

# Persist the selected menu in session state
if menu: # menu can be None if nothing is selected, though radio usually has a default
    st.session_state.menu = menu

if st.session_state.menu == "View/Edit Requirements":
    view_edit_requirements()
elif st.session_state.menu == "Add New Requirement":
    add_new_requirement()
elif st.session_state.menu == "Validate & Approve":
    validate_and_approve()
elif st.session_state.menu == "Export Requirements":
    export_requirements()
elif st.session_state.menu == "Preview & Export":
    preview_and_export()
elif st.session_state.menu == "Load Demo Data": # Updated menu check
    load_demo_data_ui() # Call new UI function