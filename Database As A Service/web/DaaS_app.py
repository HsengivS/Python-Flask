from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient('< ENTER YOUR MONGO DB CONNECTION STRING >')

db = client.test123
col = db['DaaS']

"""REGISTER THE CUSTOMER  USER-NAME & PASSWORD"""
class Register(Resource):
    def post(self):
        posted_data = request.get_json()

        user_name = posted_data['user_name']
        password = posted_data['password']

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt())

        col.insert({
        "USER_NAME":user_name,
        "PASSWORD":hashed_pw,
        "SENTENCE":"",
        "TOKEN":6
        })

        ret_json = {
        "status":200,
        "messagess":"you have successfully registered"
        }

        return jsonify(ret_json)

"""STORE SENTENCE AND BEFORE THAT VERIFY THE USERNAME AND PASSWORD AND TOKENS AVAILABLE """

def verify_pw(username,password):
    hashed_pw = col.find({"USER_NAME":username})[0]['PASSWORD']

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tok = col.find({"USER_NAME":username})[0]['TOKEN']
    return tok

class Store(Resource):
    def post(self):
        posted_data = request.get_json()

        user_name = posted_data['user_name']
        password = posted_data['password']
        sentence = posted_data['sentence']

        correct_pw = verify_pw(user_name,password)
        if not correct_pw:
            ret_json = {
            "status":301,
            "message":"sorry wrong password"
            }
            return jsonify(ret_json)

        counted_tokens = countTokens(user_name)
        if counted_tokens <= 0:
            ret_json = {
            "status":302,
            "message":"Sorry you don't have enough tokens to perform this operation"
            }
            return jsonify(ret_json)

        col.update({
        "USER_NAME":user_name
        },{
           "$set":{
                "SENTENCE":sentence,
                "TOKEN": counted_tokens-1
        }
        })
        ret_json = {
        "status":200,
        "message":"Your operation is performed"
        }
        return jsonify(ret_json)

"""VERIFY THE USERNAME AND TOKENS AND RETRIVE THE DATA """

class Get(Resource):
    def post(self):
        posted_data = request.get_json()
        user_name = posted_data['user_name']
        password = posted_data['password']

        correct_pw = verify_pw(user_name,password)
        if not correct_pw:
            ret_json = {
            "status":301
            }
            return jsonify(ret_json)

        counted_tokens = countTokens(user_name)
        if counted_tokens <= 0:
            ret_json = {
            "status":302,
            "message":"Sorry you don't have enough tokens to perform this operation"
            }
            return jsonify(ret_json)

        col.update({"USER_NAME":user_name},{"$set":{"TOKEN":counted_tokens-1}})
        sent = col.find({"USER_NAME":user_name})[0]['SENTENCE']
        ret_json = {"status":200,"your sentence is":str(sent)}
        return jsonify(ret_json)

@app.route('/welcome')
def hello():
    return "this is a testing"


api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Get, "/get")

if __name__ == '__main__':
    app.run("0.0.0.0", debug = True)
