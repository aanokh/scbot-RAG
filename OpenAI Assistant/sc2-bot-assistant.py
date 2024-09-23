import streamlit as st
from openai import OpenAI


API_KEY = 'YOUR_API_KEY'
MODEL = 'gpt-4o-mini'
ASSISTANT_ID = 'YOUR_ASSISTANT_ID'

st.set_page_config(
    page_title="SC2 Bot Assistant",
    page_icon="🤖",
    layout="wide")



st.title("Sc2 Bot Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [
    ]
if "thread" not in st.session_state:
    client = OpenAI(api_key=API_KEY)
    st.session_state.client = client
    st.session_state.thread = client.beta.threads.create()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("What is up?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        client = st.session_state.client
        thread = st.session_state.thread
        # create message
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )
        # create and execute run
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
        )
        # when run is completed, get the answer
        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            #for m in messages:
            #    answer = m.content[0].text.value
            #    break
            answer = next(iter(messages)).content[0].text.value
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content":answer})
        else:
            print(run.status)

        