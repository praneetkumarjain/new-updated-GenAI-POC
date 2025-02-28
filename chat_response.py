import os
import json
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_experimental.sql import SQLDatabaseChain
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.utilities import SQLDatabase
from openai import AzureOpenAI 
import config
import logging 



class OpenAiBackend:
    def __init__(self):       
        print("From OpenAiBackend constructor")
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=config.embd_model,
            azure_endpoint=config.azure_endpoint,
            openai_api_version=config.openai_api_version,
            api_key=config.api_key
        )
        
        # Load the vectorstores for different PDF sources
        self.vectorstore_pdf1 = FAISS.load_local("./vector_db/vectorstore_pdf1", self.embeddings, allow_dangerous_deserialization=True)
        self.retriever_pdf1 = self.vectorstore_pdf1.as_retriever()

        self.vectorstore_pdf2 = FAISS.load_local("./vector_db/vectorstore_pdf2", self.embeddings, allow_dangerous_deserialization=True)
        self.retriever_pdf2 = self.vectorstore_pdf2.as_retriever()
        
        self.vectorstore_pdf3 = FAISS.load_local("./vector_db/vectorstore_pdf3", self.embeddings, allow_dangerous_deserialization=True)
        self.retriever_pdf3 = self.vectorstore_pdf3.as_retriever()
        
        self.vectorstore_pdf4 = FAISS.load_local("./vector_db/vectorstore_pdf4", self.embeddings, allow_dangerous_deserialization=True)
        self.retriever_pdf4 = self.vectorstore_pdf4.as_retriever() 
        
        self.vectorstore_pdf6 = FAISS.load_local("./vector_db/vectorstore_pdf6", self.embeddings, allow_dangerous_deserialization=True)
        self.retriever_pdf6 = self.vectorstore_pdf6.as_retriever()        
        
        # Define the LLM
        llm = AzureChatOpenAI(
            azure_endpoint=config.azure_endpoint,
            openai_api_version=config.openai_api_version,
            azure_deployment=config.azure_deployment,
            api_key=config.api_key,
            verbose=True,
            temperature=0.0
        )
        
        # SQL database connection and chain
        sqlconn = f"mssql+pymssql://{config.username}:{config.password}@{config.server}:1433/{config.database}"
        db = SQLDatabase.from_uri(sqlconn)

        self.db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True, use_query_checker=True)

        # System message template for the chatbot
        system_message = """Utilize the information from the following four resources to answer any questions.
            When reporting numerical values, use only one format: either express results in percentages or round off the values to two decimal places. Do not provide both formats for the same data point. If the information is suitable for percentage representation, provide the percentage only. If not, then round off the values to two decimal places.
            If required report results in tabular format.
            Conclude your response with a brief summary.
            Provide answers from the data only don't create new answers.
            If no data is returned from the SQL query, do not include any mention of "no data" or similar messages in the output. Simply skip the SQL query output and provide an answer based only on the available data from the other sources.

            Oil2023_Including Forecast: a PDF file with text
            {source1}
            OPEC_MOMR_July_2023: a PDF file with text
            {source2}
            Operational Report: a PDF file with text
            {source3}
            Fabrication structure: a PDF file with text
            {source4}
            vision: a PDF file with text
            {source6}
        """        
        
        prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", "{question}")])

        # Define the full chain for retrieving data from multiple sources
        self.full_chain = {
            "source1": (lambda x: x['question']) | self.retriever_pdf1,
            "source2": (lambda x: x['question']) | self.retriever_pdf2,
            "source3": (lambda x: x['question']) | self.retriever_pdf3,
            "source4": (lambda x: x['question']) | self.retriever_pdf4,  
            "source6": (lambda x: x['question']) | self.retriever_pdf6, 
            "question": lambda x: x['question'],
        } | prompt | llm
        
    def ask_question(self, user_question):
        print("From OpenAiBackend class | ask_question method")
        sql_output = ''
        
        # Check the SQL query output
        try:
            sql_output = self.db_chain(user_question)['result']
        except Exception as e:
            print(e)
            sql_output = ''
        
        # Now check if the SQL output contains the unwanted phrase and clear it if found
        if "There is no data available regarding incidents of non-compliance with environmental regulations in the past quarter." in sql_output:
            sql_output = ''  # Clear it out if the unwanted message is present

        # Get the response from the other retrievers (PDFs and such)
        response = self.full_chain.invoke({"question": user_question})

        # Return only the available data from SQL output and response content (avoid the unwanted message)
        return (sql_output.strip() + "\n" + response.content).strip() if sql_output.strip() else response.content.strip()

    def get_benchmark_value(self, user_question):
        print("get_benchmark_value")

        # System message for benchmark extraction
        system_message = """Use the information from the below three sources to find the benchmark value
        for the country asked in the question. Round off any numerical or percentage values to one decimal place.
        DO NOT give your own answer.
        Stick to the provided documents for information.
        Extract only benchmark value, no other value or text output required.

        Instructions:
        - Use chain of thought.
        - You should ignore all plot instructions mentioned in the question.

        Oil2023_Including Forecast: a PDF file with text
        {source1}
        OPEC_MOMR_July_2023: a PDF file with text
        {source2}
        Operational Report: a PDF file with text
        {source3}
        Fabrication structure: a PDF file with text
        {source4}
        """
        prompt = ChatPromptTemplate.from_messages([("system", system_message), ("human", "{question}")])
        llm = AzureChatOpenAI(
            azure_endpoint=config.azure_endpoint,
            openai_api_version=config.openai_api_version,
            azure_deployment=config.azure_deployment,
            api_key=config.api_key,
            verbose=True,
            temperature=0.0
        )

        full_chain = {
            "source1": (lambda x: x['question']) | self.retriever_pdf1,
            "source2": (lambda x: x['question']) | self.retriever_pdf2,
            "source3": (lambda x: x['question']) | self.retriever_pdf3,
            "source4": (lambda x: x['question']) | self.retriever_pdf4,
            "question": lambda x: x['question'],
        } | prompt | llm

        # Get the response for the benchmark value
        response = full_chain.invoke({"question": user_question})

        # Extract and return benchmark
        output = self.extract_benchmark(response, user_question)
        print("\noutput from get_benchmark_value func:", output)
        return output

    def extract_benchmark(self, context, user_question):
        system_content = f"""You are a text analyser to extract the benchmark value from the text.
        Instructions:
        - Use your intelligence to find the benchmark and benchmark Name.
        - Return JSON only with two fields: one is benchmark, which is a floating value, and the other is the name whose benchmark is asked to calculate, which is in text.
        Exclude any symbols from the extracted fields and ensure it is concise. For example:

        "benchmarkName": "Colorado"
        "benchmarkValue": 56

        - If you don't find the answer, then return "NA"

        Context: {context}
        """
        conversation = [{"role": "system", "content": system_content}]
        user_input = {"role": "user", "content": "Extract benchmark value from the context " + user_question}
        conversation.append(user_input)

        client = AzureOpenAI(
            azure_endpoint=config.azure_endpoint, 
            api_key=config.api_key,  
            api_version=config.openai_api_version
        )
        response = client.chat.completions.create(
            model=config.model_name,
            messages=conversation,
            temperature=0
        )

        # Process the output
        output = response.choices[0].message.content
        print("output from llm:", output)
        try:
            data_dict = json.loads(output)
            benchmark = data_dict["benchmarkValue"]
            benchmark_name = data_dict["benchmarkName"]
        except:
            benchmark = 'NA'
            benchmark_name = 'NA'

        benchmark_dict = {'benchmarkValue': benchmark, 'benchmarkName': benchmark_name}
        return benchmark_dict