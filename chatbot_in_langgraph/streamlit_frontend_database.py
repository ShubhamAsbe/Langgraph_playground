import streamlit as st
from langgraph_database_backend import chatbot,retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid



def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_threads(st.session_state['thread_id'])
    st.session_state['message_history']=[]
    
def add_threads(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        
def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()
    
add_threads(st.session_state['thread_id'])

config={'configurable':{'thread_id': st.session_state['thread_id']}}
    
st.sidebar.title("Langgraph Chatbot with Streamlit")

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header("Chat History")

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id']=thread_id        
        messages=load_conversation(thread_id)
        
        temp_messages=[]
        # print("messages:-",messages)
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            temp_messages.append({"role": role, "content": message.content})
        st.session_state['message_history']=temp_messages

for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])
    
user_input=st.chat_input("Type your message here")

if user_input:
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)
    
    
    # st.session_state['message_history'].append({"role": "assistant", "content": ai_response})
    
    with st.chat_message("assistant"): 
        ai_message=st.write_stream(
            message_chunk.content for message_chunk,metadata in chatbot.stream(
            {'messages':[HumanMessage(content=user_input)]},
            config=config,
            stream_mode='messages'  
        ))
    
    st.session_state['message_history'].append({"role": "assistant", "content": ai_message})
    # print(st.session_state['message_history'])