import streamlit as st
import pandas as pd
from openai import OpenAI

# Show title and description.
st.title("💬 Credit Risk Assistant")
st.write(
    "This chatbot uses GPT-4o mini to assist with credit risk analysis. "
    "It can analyze datasets, perform calculations, generate graphs, and more."
)

# Ask user for their OpenAI API key.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Upload CSV files.
    uploaded_files = st.file_uploader("Upload your CSV files", type="csv", accept_multiple_files=True)
    if uploaded_files:
        dataframes = {file.name: pd.read_csv(file) for file in uploaded_files}
        st.write("Uploaded CSV files:")
        for filename, df in dataframes.items():
            st.write(f"**{filename}**:")
            st.dataframe(df.head())

        # Function to generate the prompt with data.
        def generate_prompt(prompt, dataframes):
            prompt += "\n\nHere are the available datasets:\n"
            for name, df in dataframes.items():
                prompt += f"- **{name}**: {', '.join(df.columns)}\n"
            prompt += "\nYou can ask questions about these datasets or request Python code to execute on them."
            return prompt

        # Create a session state variable to store the chat messages.
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display the existing chat messages.
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Create a chat input field.
        if prompt := st.chat_input("Ask me anything about the data or calculations."):

            # Store and display the current prompt.
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate the customized prompt for GPT.
            custom_prompt = generate_prompt(prompt, dataframes)

            # Enhanced system prompt with code interpretation capability
            system_prompt = """
            You are a Credit Risk Assistant embedded within an enterprise-grade browser for an equipment leasing business.
            Your primary role is to assist credit analysts and credit managers by providing accurate and insightful responses 
            to their queries related to credit originations and portfolio management.

            Capabilities include:
            - Accessing and analyzing application-level and contract-level datasets.
            - Performing calculations and generating graphs.
            - Interpreting and executing Python code to interact with provided DataFrames.

            Whenever asked, you can directly execute Python code on the provided DataFrames.
            """

            try:
                # Streamlined function to handle API call and response
                def get_gpt_response(client, custom_prompt, model="gpt-4o-mini"):
                    stream = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": custom_prompt}
                        ],
                        stream=True,
                        timeout=30  # Set a timeout for the API request
                    )
                    return stream

                # Get the response stream from the API
                stream = get_gpt_response(client, custom_prompt)

                # Stream the response to the chat and store it in session state
                with st.chat_message("assistant"):
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")

            # Allow user to execute Python code on the uploaded DataFrames
            st.subheader("Run Python Code on DataFrames")
            code_input = st.text_area("Enter Python code to execute on the DataFrames")
            if st.button("Run Code"):
                try:
                    exec(code_input, {"df": dataframes})
                except Exception as e:
                    st.error(f"Error executing code: {e}")
