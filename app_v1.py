
"""
This version 'works' but text is displayed weirdly:
Assistant: Text(annotations=[], value='Hello')
Hello
!
It
looks
like
getting error:
2024-08-20 18:48:09.183 Invalid arguments were passed to "st.write" function.
Support for passing such unknown keywords arguments will be dropped in future. 
Invalid arguments were: {'end': '', 'flush': True}
"""



import streamlit as st
import pandas as pd
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler

# Step 1: Create the Streamlit interface
st.title("💬 Credit Risk Assistant")
st.write(
    "This chatbot uses GPT-4o mini to assist with credit risk analysis. "
    "It can analyze datasets, perform calculations, generate graphs, and more."
)

# Ask user for their OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Initialize the OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Upload a CSV file
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded CSV file:")
        st.dataframe(df.head())

        # Step 1: Create a new Assistant
        assistant = client.beta.assistants.create(
            name="Credit Risk Assistant",
            instructions="You are a credit risk assistant. Use the code interpreter to analyze the provided dataset and answer questions related to credit risk.",
            tools=[{"type": "code_interpreter"}],
            model="gpt-4o-mini",
        )

        # Step 2: Create a Thread
        thread = client.beta.threads.create()

        # Upload the file to OpenAI
        file_id = client.files.create(file=uploaded_file, purpose='assistants').id

        # Create a chat input field for user queries
        user_query = st.chat_input("Ask me anything about the data or calculations.")

        if user_query:
            # Step 3: Add the Message to the Thread
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_query,
                attachments=[
                    {
                        "file_id": file_id,
                        "tools": [{"type": "code_interpreter"}]
                    }
                ]
            )

            # Step 4: Create and Stream a Run
            class EventHandler(AssistantEventHandler):
                @override
                def on_text_created(self, text) -> None:
                    st.write(f"Assistant: {text}")
                
                @override
                def on_text_delta(self, delta, snapshot):
                    st.write(delta.value, end="", flush=True)

                def on_tool_call_created(self, tool_call):
                    st.write(f"Assistant used tool: {tool_call.type}")
                
                def on_tool_call_delta(self, delta, snapshot):
                    if delta.type == 'code_interpreter':
                        if delta.code_interpreter.input:
                            st.write(f"Running code: {delta.code_interpreter.input}")
                        if delta.code_interpreter.outputs:
                            st.write(f"Output:")
                            for output in delta.code_interpreter.outputs:
                                if output.type == "logs":
                                    st.write(f"{output.logs}")

            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                event_handler=EventHandler(),
            ) as stream:
                stream.until_done()

