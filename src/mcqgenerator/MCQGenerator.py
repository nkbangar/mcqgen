import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,get_table_data
from src.mcqgenerator.logger import logging
#import necessary package from langchain
#from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
#from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
##from langchain.callbacks import get_openai_callback


# Load environment variable form the .env file
load_dotenv()

#Access the environment variable just like you would with os.environment
KEY=os.getenv("OPENAI_API_KEY")

llm= ChatOpenAI(openai_api_key=KEY,model_name="gpt-3.5-turbo", temperature=0.8)

#input prompt
TEMPLATE = """
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone.
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like RESPONSE_JSON below and user it as a guide. \
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}
"""
quiz_genration_prompt =  PromptTemplate(input_variables=["text","number","subject","tone","response_json"], template=TEMPLATE)

quiz_chain = LLMChain(llm=llm, prompt=quiz_genration_prompt, output_key="quiz", verbose=True)

#Output Prompt
TEMPLATE2="""
You are an expert english grammarian and writer. Given a Mutiple choice Quiz for {subject} students. \
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity.
if the quiz is not at per with the cognitive and analytical abilities of the students, \
update the quiz questions which needs to be changed and change the tone such that is perfectly fits the students ability.
Quiz_MCQa:
{quiz}

Check from an expert English writer of the above quiz:
"""

quiz_evaluation_prompt =  PromptTemplate(input_variables=["subject","quiz"], template=TEMPLATE2)

review_chain = LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)

#This is Overall chain where we run the two chains i
generate_evaluate_chain  = SequentialChain(chains=[quiz_chain,review_chain],input_variables=["text","number","subject","tone","response_json"],output_variables=["quiz","review"], verbose=True)