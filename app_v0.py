
"""
Works but it is unable to execute code and access de dataframe. 


"""



import streamlit as st
import pandas as pd
from openai import OpenAI



# Show title and description.
st.title("💬 Credit Risk Assistant")
st.write(
    "This chatbot uses GPT-4o mini to assist with credit risk analysis. "
    "It can analyze datasets, perform calculations, generate graphs, and more."
)

openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    client = OpenAI(api_key=openai_api_key)
    uploaded_files = st.file_uploader("Upload your CSV files", type="csv", accept_multiple_files=True)
    if uploaded_files:
        dataframes = {file.name: pd.read_csv(file) for file in uploaded_files}
        st.write("Uploaded CSV files:")
        for filename, df in dataframes.items():
            st.write(f"**{filename}**:")
            st.dataframe(df.head())

        def generate_prompt(prompt, dataframes):
            prompt += "\n\nHere are the available datasets:\n"
            for name, df in dataframes.items():
                prompt += f"- **{name}**: {', '.join(df.columns)}\n"
            prompt += "\nYou can ask questions about these datasets, and I will analyze them for you."
            return prompt

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        if prompt := st.chat_input("Ask me anything about the data or calculations."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            custom_prompt = generate_prompt(prompt, dataframes)
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
                def get_gpt_response(client, custom_prompt, model="gpt-4o-mini"):    #Here I need to add the ability to run code
                    response = client.chat.completions.create(                       #It thinks it can run code because of the system_prompt. 
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": custom_prompt}
                        ],
                        stream=False,
                        timeout=30 
                    )
                    return response.choices[0].message.content  

                response = get_gpt_response(client, custom_prompt)
                with st.chat_message("assistant"):
                    st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
