import os
import openai

FLASK_PORT_NUMBER = 8080

# gpt_model = 'gpt-35-turbo'
# model_engine = 'gpt-4-32k'#'edwardJonesBot'
model_name = 'onggpt432k'
embd_model = "ongtextembdada2"
text_embd_model = 'text-embedding-ada-002'
OPENAI_API_TYPE = "azure"
# OPENAI_API_VERSION = "2024-02-15-preview"
# OPENAI_API_BASE = "https://swccoai0oyaoa01.openai.azure.com/%22"
# OPENAI_API_BASE = "https://openaigds.openai.azure.com/"
OPENAI_API_KEY = "188f06a6bf0446b8857e99adb1daa6d3"
# OPENAI_API_KEY="942789598f8144558809528e17d5a5b5"
# server = 'azuresqltestdb.database.windows.net'
# database = 'TestSqldb1'
# username = 'testsqldbong'
# password = 'sqldb_ong2024'
# driver= 'ODBC Driver 17 for SQL Server'
# server = 'azuresqltestdb.database.windows.net'
# database = 'TestSqldb1'
# username = 'testsqldbong'
# password = 'Ctpsandbox24'
#password = 'sqldb_ong2024'

server = 'ongsqlserver1.database.windows.net'
database = 'OngTestdb1'
username = 'testsqldbong'
password = 'Ctpsandbox24'

driver= 'ODBC Driver 18 for SQL Server'
os.environ["OPENAI_API_TYPE"] = OPENAI_API_TYPE
# os.environ["OPENAI_API_VERSION"] = OPENAI_API_VERSION
# os.environ["OPENAI_API_BASE"] = OPENAI_API_BASE
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
# openai.api_type = "azure"
# openai.api_version = os.getenv("OPENAI_API_VERSION") 
# openai.api_base = os.getenv("OPENAI_API_BASE")  # Your Azure OpenAI resource's endpoint value.
# openai.api_key = os.getenv("OPENAI_API_KEY")
azure_endpoint = "https://swccoai0oyaoa01.openai.azure.com/"
openai_api_version="2024-02-15-preview"
azure_deployment="onggpt432k"
api_key="188f06a6bf0446b8857e99adb1daa6d3"


