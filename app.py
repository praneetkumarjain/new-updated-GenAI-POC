import pandas as pd
import warnings
import os, time, json

from flask import Flask, render_template, request
from flask_cors import CORS

from utils import get_chat_response_json_withtitle
import config

warnings.filterwarnings("ignore")
 
app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    ans =  get_chat_response_json_withtitle(input)
    print("api response is  :: ",ans)
    return ans

@app.route('/query_json_withtitle',methods=['POST'])
def api_query_json_withtitle():
    start_time = time.time()
    data = request.json
    question = data.get('query')
    print(f'question: {question}')
    answer =  get_chat_response_json_withtitle(question)
    end_time = time.time()
    print(f'api response time: {end_time - start_time}')
    return answer

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.FLASK_PORT_NUMBER,debug=False)
