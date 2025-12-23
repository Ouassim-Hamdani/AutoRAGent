import streamlit as st
import requests
import uuid, os, json

st.set_page_config("AutoRAGent", page_icon="🤖")
st.title("🤖 AutoRAGent - Autonomous Knowledge Assistant")

API_URL = "http://localhost:2003"

# STATE MANEGEMENT
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []  # downgraded version of messages to not abuse context, save user messages and only before final answer code blcok

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    print("Session ID : " + st.session_state.session_id)

# MESSAGE LOADING
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
            if 'files_names' in message:
                for file in message['files_names']:
                    st.info(f"📄 {file}")

        else:  # assistant
            with st.container():
                with st.expander("Coding Steps"):
                    st.markdown(message["content"][1])
            st.markdown(message["content"][0])
            if "images" in message:
                for image_path in message["images"]:
                    try:
                        st.image(image_path, caption=os.path.basename(image_path), use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not re-load image {os.path.basename(image_path)} from history: {e}")

# NEW USER MESSAGE & RESPONSE
if prompt := st.chat_input("What is up?", accept_file="multiple", file_type=["csv", "xlsx", "txt", "pdf"]):
    uploaded_files = prompt.files

    # Prepare files for API upload
    files_to_send = []
    file_names = []
    
    # We don't save files locally in frontend, we send them to backend
    if uploaded_files:
        for file in uploaded_files:
            files_to_send.append(('files', (file.name, file.getvalue(), file.type)))
            file_names.append(file.name)

    # Add user message to chat history
    st.session_state.messages.append(
        {"role": "user", "content": prompt.text, "files_names": file_names, "files_paths": []}) # paths are handled by backend now
    
    # Prepare history for API (exclude large content if needed, but here we send full history)
    # We need to make sure history format matches what backend expects
    # Backend expects: [{"role": "user", "content": "...", "files_paths": [...]}, ...]
    # Our session_state.history seems to match this structure roughly
    
    # Update history with current turn
    current_turn = {"role": "user", "content": prompt.text, "files_paths": []} # Backend will fill files_paths
    st.session_state.history.append(current_turn)
    
    images_path = []

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt.text)
        for uploaded_file in uploaded_files:
            st.info(f"📄 {uploaded_file.name}")

    # ASSISTANT MESSAGE HANDLER
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            with st.container():
                with st.expander("Coding Steps"):
                    step_placeholder = st.empty()
            final_answer_placeholder = st.empty()
            step_details = ""
            final_answer = ""
            counter = 1
            code_blocks = [] 
            
            try:
                # Prepare payload
                payload = {
                    "session_id": st.session_state.session_id,
                    "history": json.dumps(st.session_state.history)
                }
                
                # Call API
                with requests.post(f"{API_URL}/chat", data=payload, files=files_to_send, stream=True) as response:
                    response.raise_for_status()
                    
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            try:
                                data = json.loads(decoded_line)
                                resp_type = data.get("type")
                                resp = data.get("content")
                                
                                if resp:
                                    if resp_type == "code":
                                        step_details += f"**Step {counter}**\n\n{resp}\n---\n"
                                        counter += 1
                                        code_blocks.append(resp)
                                        step_placeholder.markdown(step_details)
                                    elif resp_type == "final":
                                        final_answer = resp
                                        final_answer_placeholder.markdown(final_answer)
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                st.error(f"Error communicating with backend: {e}")



    st.session_state.messages.append(
        {"role": "assistant", "content": [final_answer, step_details], "images": images_path})
    
    if len(code_blocks) >= 2:
        st.session_state.history.append({"role": "assistant",
                                         "content": f"Before Last code block : \n{code_blocks[-2]}\n\nLast code block : \n{code_blocks[-1]}"})
    elif len(code_blocks) == 1:
        st.session_state.history.append({"role": "assistant", "content": code_blocks[-1]})
    else:
         st.session_state.history.append({"role": "assistant", "content": final_answer})



