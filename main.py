
import streamlit as st
import pandas as pd
from gen_file import generate_timetable_image
import io
from datetime import time, timedelta, datetime

# --- App Configuration ---
st.set_page_config(page_title="Timetable Generator", layout="wide")

# --- Session State Initialization ---
if 'courses_df' not in st.session_state:
    from gen_file import sample_courses
    st.session_state.courses_df = pd.DataFrame(sample_courses, columns=["Course", "Day", "Start", "End", "Location"])

# --- Sidebar ---
with st.sidebar:
    st.header("Timetable Controls")

    selected_style = st.selectbox("Choose a style", ["modern", "cute", "cool", "fresh"])

    st.header("Add a New Course")
    with st.form("new_course_form", clear_on_submit=True):
        # Course Name Input
        unique_courses = st.session_state.courses_df['Course'].unique().tolist()
        add_new_option = "--- Add New Course ---"
        course_selection = st.selectbox("Course Name", [add_new_option] + unique_courses)
        
        new_course_name = ""
        if course_selection == add_new_option:
            new_course_name = st.text_input("Enter New Course Name")

        day = st.selectbox("Day of the Week", options=list(range(1, 8)), format_func=lambda x: f"周{x}")
        
        # Time Inputs
        start_time_obj = st.slider(
            "Start Time",
            min_value=time(8, 0),
            max_value=time(21, 0),
            value=time(9, 0),
            step=timedelta(minutes=10),
            format="HH:mm"
        )
        
        duration_hours = st.selectbox("Duration", [0.5, 1.0, 1.5, 2.0], format_func=lambda x: f"{x} hours")

        location = st.text_input("Location (Optional)")
        
        submitted = st.form_submit_button("Add Course")
        if submitted:
            course_name = new_course_name if course_selection == add_new_option else course_selection
            
            if course_name and day and start_time_obj and duration_hours:
                # Calculate end time
                start_datetime = datetime.combine(datetime.today(), start_time_obj)
                end_datetime = start_datetime + timedelta(hours=duration_hours)
                end_time_str = end_datetime.strftime("%H:%M")
                start_time_str = start_time_obj.strftime("%H:%M")

                new_course = pd.DataFrame([[course_name, day, start_time_str, end_time_str, location]], columns=["Course", "Day", "Start", "End", "Location"])
                st.session_state.courses_df = pd.concat([st.session_state.courses_df, new_course], ignore_index=True)
                st.success("Course added successfully!")
            else:
                st.error("Please fill in all required fields.")

# --- Main Section ---
st.title("Timetable Preview")

# Display and edit current courses
st.header("Current Courses")
edited_df = st.data_editor(st.session_state.courses_df, use_container_width=True, num_rows="dynamic")

# Update session state if the dataframe is edited
if not edited_df.equals(st.session_state.courses_df):
    st.session_state.courses_df = edited_df
    st.rerun()

# Generate and display the timetable
if not st.session_state.courses_df.empty:
    courses_list = [tuple(row) for row in st.session_state.courses_df.to_numpy()]
    
    final_img = generate_timetable_image(courses=courses_list, selected_style=selected_style)

    st.header("Generated Timetable")
    st.image(final_img)

    # In-memory files for download
    png_buffer = io.BytesIO()
    final_img.save(png_buffer, format="PNG")
    png_buffer.seek(0)

    pdf_buffer = io.BytesIO()
    final_img.save(pdf_buffer, format="PDF")
    pdf_buffer.seek(0)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download PNG Image",
            data=png_buffer,
            file_name=f"timetable_{selected_style}.png",
            mime="image/png"
        )
    with col2:
        st.download_button(
            label="Download PDF",
            data=pdf_buffer,
            file_name=f"timetable_{selected_style}.pdf",
            mime="application/octet-stream"
        )
else:
    st.warning("No courses to display. Please add a course using the sidebar.")
