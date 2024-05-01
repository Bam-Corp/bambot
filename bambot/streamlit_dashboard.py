# bam/streamlit_dashboard.py
import streamlit as st
import docker

def setup_streamlit_dashboard():
    st.set_page_config(page_title="Bam AI Agent Control Center", layout="wide")
    
    st.title("Bam AI Agent Control Center")
    st.write("Welcome to the Bam AI Agent Control Center!")
    
    docker_client = docker.from_env()
    containers = docker_client.containers.list()
    
    if containers:
        st.subheader("Running Containers")
        for container in containers:
            st.write(f"- {container.name}")
    else:
        st.warning("No containers are currently running.")
    
    st.subheader("Create New Container")
    container_name = st.text_input("Container Name")
    agent_framework = st.selectbox("Agent Framework", ["langchain", "transformers", "pytorch"])
    if st.button("Create Container"):
        create_container(container_name, agent_framework)
        st.success(f"Container {container_name} created successfully!")
    
    st.subheader("Prune System Resources")
    if st.button("Prune System"):
        prune_system()
        st.success("System resources pruned successfully!")