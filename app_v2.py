"""
1. This version works but it outputs text like this 
Text(annotations=[], value='The')The dataset contains several columns, 
including one for the submission date (SubmitDate) and a column indicating 
whether the deal was funded (funded).

To determine how many deals were funded in 2024, 
I'll filter the dataset for records where the SubmitDate falls within the year 2024 and 
the funded column indicates that the deal was funded (with a value of 1). Let's carry out this analysis.
Text(annotations=[], value='A')A total of 64 deals were funded in 2024.

Assistant used tool: code_interpreter


2. We can only have one message at a time, I can not scroll up to see past messages

3. It is creating a new assistant and database every time I run it 
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
                def __init__(self):
                    super().__init__()
                    self.text_buffer = []
                    self.code_buffer = []
                    self.text_display = st.empty()  # Create an empty container for dynamic text display

                @override
                def on_text_created(self, text) -> None:
                    self.text_buffer.append(str(text))
                
                @override
                def on_text_delta(self, delta, snapshot):
                    self.text_buffer.append(str(delta.value))
                    # Update the UI dynamically with the accumulated text
                    self.text_display.markdown("".join(self.text_buffer))
                
                def on_run_end(self):
                    # Final flush of the text buffer
                    self.text_display.markdown("".join(self.text_buffer))
                    self.text_buffer = []

                def on_tool_call_created(self, tool_call):
                    st.write(f"Assistant used tool: {tool_call.type}")
                    self.code_buffer = []  # Reset code buffer for new tool call
                
                def on_tool_call_delta(self, delta, snapshot):
                    if delta.type == 'code_interpreter':
                        if delta.code_interpreter.input:
                            self.code_buffer.append(delta.code_interpreter.input)
                        if delta.code_interpreter.outputs:
                            st.write("Running code:")
                            st.code("".join(self.code_buffer))  # Show the full code once it's fully received
                            st.write("Output:")
                            for output in delta.code_interpreter.outputs:
                                if output.type == "logs":
                                    st.write(f"{output.logs}")

            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                event_handler=EventHandler(),
            ) as stream:
                stream.until_done()
