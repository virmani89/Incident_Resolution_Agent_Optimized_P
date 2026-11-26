import streamlit as st


def display_result(result):
    if isinstance(result, str):
        st.warning(result)
        return
    st.success("Closest historical incident retrieved")
    for label in ("Reference issue", "Problem Statement", "Impact", "RCA", "Resolution", "Defect ID"):
        value = result.get(label, "Not provided in the knowledge base")
        st.markdown(f"**{label}**")
        st.write(value)
   # with st.expander("Retrieval details"):
       # st.write(f"Retrieval score: {result.get('Retrieval score', 0):.4f}")
       # st.caption(result.get("Note", ""))
