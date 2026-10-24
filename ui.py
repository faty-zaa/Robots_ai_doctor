
import streamlit as st

from src.Agent.agent import RoboDoctor

st.set_page_config(page_title="RoboDoctor", page_icon="🤖")
st.title("🤖 RoboDoctor")
st.write("AI-powered robotics troubleshooting assistant")

problem = st.text_area(
    "Describe the robot problem:",
    placeholder="Example: My robot does not move...",
)

if st.button("Diagnose"):
    if not problem.strip():
        st.warning("Please describe the problem.")
    else:
        with st.spinner("Analyzing the problem..."):
            try:
                doctor = RoboDoctor()
                result = doctor.diagnose(problem)
                st.markdown(result)
            except Exception as error:
                st.error(f"Something went wrong: {error}")
