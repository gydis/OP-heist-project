import streamlit as st
import asyncio
import sys
import os
from gpt_nerd.gpt_researcher.master.agent import GPTResearcher

st.set_page_config(page_title="Assistant chat", page_icon="🤖", layout="wide")
st.title("Test Researcher")

#initialize the chat history with an empty list
if "messages" not in st.session_state:
    st.session_state.messages = []

#three option atm: research_report, outline_report, and resources_report
research_type = st.selectbox("Select the type of report you want",
                             ("research_report", "outline_report", "resource_report"),
                             placeholder = "Select...")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
#create a async function to run the researcher.
async def run_model(agent):
    report = await agent.run()
    return report

#get user input and add it to the messages list
if prompt := st.chat_input("What can I do for you?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    #create the Researcher instance and get the response from the researcher model
    researcher = GPTResearcher(prompt, research_type)  
    full_response = asyncio.run(run_model(researcher))
    st.chat_message("assistant").markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})



