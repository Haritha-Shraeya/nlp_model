from flask import Flask, request, jsonify, make_response
from datetime import datetime
from model_builder.modelBuild import ModelBuilderHandle
from model_store.controller.challenge_schema import ChallengeInput
from marshmallow import ValidationError
from model_store.persistency.persistency import Challenge_esi
from model_store.controller.challenge_schema import ChallengeInput, GetChallenge
from model_store.persistency.elasticSearch import ElasticSearchInterface
# from model_builder_nlp.model_builder_nlp import Model
from model_builder_nlp.model_builder_final import Model

import requests as req
from ocr_module.OCRhandler import OCRHandler
from ocr_module.ElasticSearchHandler import ElasticSearchHandle

import os

app = Flask(__name__)

# tess_path = os.environ["TESSERACT_PATH"]
# poppler_path = os.environ["POPPLER_PATH"]
tess_path = r"C:\Users\user1\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
poppler_path = r"C:\Users\user1\Downloads\Release-22.04.0-0\poppler-22.04.0\Library\bin"

mbh = ModelBuilderHandle()
CSVfile = "C:\\Users\\user1\\SearchEngine\\repository\\data\\ChallengeData.csv"

c_esi = Challenge_esi()

esh = ElasticSearchHandle()
esi = ElasticSearchInterface()
ocr = OCRHandler(path_to_tesseract=tess_path, path_to_poppler=poppler_path)

ideas_index = 'ideas'
solutions_index = 'solutions'
challenges_index = 'challenges'
models_index = 'models'
generic_fields_index = 'generic'
all_ideas_model_id = 0
problem_index = "problem"

m = Model()
######## m.data()

@app.route('/')
def index():
    #esi.create_index(problem_index)
    return 'Hello World'

@app.route('/buildmodel', methods = ["GET"])    
def buildmodel():
    text = mbh.textProcessor(csv_file = CSVfile)
    print('got text')

    _count_vect, _tfidf_transformer, _train_tfidf = mbh.build_model(text = text)
    
    return ('processed successfully')
     
@app.route('/insertes', methods = ["POST"])    
def insert_es(): 
    #posted data in json format
    request_json = request.json
    try:
        #deserializing json request data
        data = ChallengeInput().load(request_json)
        #extracting challenge_id, challenge_title and text from posted data
        #challenge_id, challenge_title, text = data['challenge_id'], data['challenge_title'], data['text']
    except ValidationError as err: #in the case of incompatible parameters in data posted
        return jsonify(err.messages), 400   #response object and status code

    #insert into elastic search 
    #try:
    ####print(data)
    response = c_esi.insert_update_challenge(data)
    m.model_data(data) #insert model_data into models_index in elastic search
    ####print(type(response))
    return jsonify(response), 200 #response object and status code

    # except Exception as err:
    #     print(err)
    #     return "Insert/Update unsuccessful"


@app.route('/getChallenge', methods=["GET"])
def get_challenge():
    request_data = request.args
    #request.json when giving search data from body
    #request.args when giving search data from url
    #printing request directly gives <Request 'http://127.0.0.1:8080/getChallenge' [GET]>
    schema = GetChallenge()
    try:
        data = schema.load(request_data)
        challenge_id = data['challenge_id']
        ###print(challenge_id)

    except ValidationError as err:
        print("validation error")
        return jsonify(err.messages), 400

    try:
        response_data = c_esi.get_challenge(challenge_id=challenge_id)
        return jsonify(response_data), 200
    except Exception as err:
        return jsonify({'error: ': err}), 500

@app.route('/getAllChallenges', methods=["GET"])
def get_all_challenges():
    try:
        response_data = c_esi.get_all_challenges()
        return (response_data), 200
    except Exception as err:
        return jsonify({'error: ': err}), 500

@app.route("/update", methods=['POST'])
def update():
    timeobj = datetime.utcnow()
    timestr = timeobj.strftime("%Y%m%d%H%M%S%f")

    request_data = request.json
    request_keys = request_data.keys()

    try:
        sub_type = request_data["submission_type"]
    except:
        return jsonify({'Message:': "Please enter submission type or check submission_type parameter name"}), 404

    desc_dict = dict()  # stores descriptor information related to challenge/idea/solution
    desc_dict["submission_type"] = sub_type
    desc_dict["timestamp"] = timestr

    if sub_type == "challenge":

        try:
            desc_dict["challenge_id"] = request_data["challenge_id"]
        except:
            return jsonify({'Message:': "Please enter challenge id or check challenge_id parameter name"}), 404

        try:
            desc_dict["challenge_title"] = request_data["challenge_title"]
        except:
            return jsonify({'Message:': "Please enter challenge title or check challenge_title parameter name"}), 404

    try:
        desc_dict["text"] = request_data["text"]
    except:
        return jsonify({'Message:': "Please enter text or check text parameter name"}), 404

    if "text" in request_keys:
        _text = request_data["text"] + " "
    else:
        _text = ""

    # Extracting text from attached files
    try:
        if "attachments" in request_keys:
            json_object = request_data["attachments"]
            for key in json_object:
                value = json_object[key]
                r = req.get(value, allow_redirects=True)
                file_name = value.split("/")[-1].lower()
                file_type = file_name.split(".")[-1].lower()
                file_nm = file_name.removeprefix("view?attachmentid=")
                name = file_nm.split(".")[0]
                file_path = os.getcwd() + os.sep + "temp" + os.sep + name
                print("name:",name, "\n", "file_path:", file_path, "\n", "type:", file_type)

                with open(file_path, "wb") as file:
                    file.write(r.content)


                _text = _text + ocr.run_handle(file_path=file_path, file_type=file_type)
                print(_text)

    except Exception as err:
        return err

    # storing extracted data in elastic search
    try:
        esh.store_extracted_text(_text, desc_dict)
        return "extracted text stored successfully"
    except:
        return "Operation unsuccessful"

@app.route("/sentence_similarity", methods=['GET'])
def sentence_similarity():
    # search_data_text = request.json
    # schema = InputText()
    # try:
    #     data = schema.load(search_data_text)
    #     input_text = data['input_text']
    #
    # except ValidationError as err:
    #     print("validation error")
    #     return jsonify(err.messages), 400
    search_data_text = request.json
    input_text = search_data_text['input_text']
    # m.data()
    # m.training()
    m.new(input_text)
    m.sentence_similarity()
    results = m.final_sentence_similarity()
    return results.to_json(orient='records')

@app.route("/word_similarity", methods=['GET'])
def word_similarity():
    search_data_text = request.json
    input_text = search_data_text['input_text']
    # m.data()
    # m.training()
    m.new(input_text)
    results = m.word_similarity()
    return results.to_json(orient='records')



if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")
    