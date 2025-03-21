import os
import io
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,get_table_data
import streamlit as st
#from langchain.callbacks import get_openai_callback
from langchain_community.callbacks.manager import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

#loading json file
with open('/Users/nk/WorkingDirectory/Python/mcqgen/Response.json', 'r') as file:
    RESPONSE_JSON = file.read()

#creating a title for the app
st.title("MCQ Creator Application with Langchain")
response = None 
#Create a form using st form
with st.form("user_inputs"):
    #file Upload
    uploaded_file=st.file_uploader("Upload a PDF or txt file")

    #Input Fields
    mcq_count=st.number_input("No of MCQs", min_value=3, max_value=50)

    #subject 
    subject=st.text_input("Insert Subject", max_chars=20)

    # Quiz Tone
    tone=st.text_input("Complexity Level Of Questions", max_chars=20, placeholder="Simple")

    # Add Button
    button=st.form_submit_button("Create MCQs")

    #Check if the button is clicked and all fields have input

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading...."):
            try:
                text= read_file(uploaded_file)
                #count tokens and the cost of apii call
                with get_openai_callback() as cb:
                    response=generate_evaluate_chain(
                        {
                            "text":text,
                            "number":mcq_count,
                            "subject":subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }
                    )
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error

            else:
                print(f"Total Tokens:{cb.total_tokens}")
                print(f"Prompt Tokens:{cb.prompt_tokens}")
                print(f"CompletionTokens:{cb.completion_tokens}")
                print(f"Total Cost:{cb.total_cost}")
                if isinstance(response, dict):
                    #Extract the quiz data from the response
                    quiz=response.get("quiz", None)
                    if quiz is not None:
                        table_data=get_table_data(quiz)
                        if table_data is not None:
                            df=pd.DataFrame(table_data)
                            df.index=df.index+1
                            st.table(df)
                            #Display the review in atext box as well
                            st.text_area(label="Review", value=response["review"])
                        else:
                            st.error("Error in the table data")
                    else:
                        st.write(response)

#Add Download Button
if response:
    quiz = response.get("quiz", None)

    if quiz:
        table_data = get_table_data(quiz)

        if isinstance(table_data, list) and all(isinstance(row, dict) for row in table_data):
            df = pd.DataFrame(table_data)  # Convert to DataFrame

            # Save DataFrame as CSV in-memory
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)  # Convert DataFrame to CSV

            # Download button for CSV
            st.download_button(
                label="Download MCQs",
                data=csv_buffer.getvalue(),
                file_name="MCQs.csv",
                mime="text/csv"
            )
        else:
            st.error("Error: Invalid table data format.")
