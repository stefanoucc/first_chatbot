import streamlit as st
import pandas as pd
from openai import OpenAI

# Constants for cost estimation
COST_PER_1000_TOKENS = 0.03  # Adjust based on actual API pricing for your model
BUDGET = 100.00  # Maximum budget in USD

# Initialize total cost tracking in session state
if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0.0

# Function to estimate cost based on token usage
def estimate_cost(tokens):
    return (tokens / 1000) * COST_PER_1000_TOKENS

# Function to get token count (mocked for this example)
def get_token_count(text):
    return len(text.split())  # Approximate token count by word count (adjust as necessary)

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
            prompt += "\nYou can ask questions about these datasets, and I will analyze them for you."
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

            # Estimate token usage and cost for this prompt
            tokens_used = get_token_count(prompt)
            cost = estimate_cost(tokens_used)
            st.session_state.total_cost += cost

            # Warn user if they are approaching or exceeding the budget
            if st.session_state.total_cost > BUDGET:
                st.warning(f"Warning: You have exceeded your budget of ${BUDGET}. Total estimated cost: ${st.session_state.total_cost:.2f}")
            elif st.session_state.total_cost > BUDGET * 0.8:
                st.warning(f"Alert: You are approaching your budget limit. Total estimated cost: ${st.session_state.total_cost:.2f}")

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

            Whenever asked, you should directly execute Python code on the provided DataFrames and return the results.
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

        # Display total cost so far
        st.write(f"Total estimated cost: ${st.session_state.total_cost:.2f}")
