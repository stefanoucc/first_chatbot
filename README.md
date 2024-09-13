This project provides a Credit Risk Assistant powered by OpenAI's GPT model and Streamlit. The assistant is designed to help users analyze financial data, interact with the model, and upload files for processing.

Features:
OpenAI GPT Integration: The assistant uses the gpt-4o-mini model to provide credit risk insights.
Session Management: Each session has a unique ID to track interactions.
File Upload: Supports CSV, XLS, and XLSX file uploads for data analysis.
Data Preview: Uploaded data is displayed in a table format for user review.
Chat Interface: Users can interact with the assistant via a chat interface.
File Attachment: Attach uploaded files for assistant review during the chat.
How to Run:
Set up Streamlit secrets with your OpenAI API key (OPENAI_API_KEY).
Launch the app in Streamlit: streamlit run app.py.
Upload a CSV/XLS file via the sidebar for analysis.
Use the chat to ask questions related to credit risk.
Notes:
The app retries API calls up to 3 times in case of failures.
Images from the assistant’s responses are displayed directly within the app.
