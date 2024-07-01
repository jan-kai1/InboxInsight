from flask import Flask, jsonify, request
from flask_cors import CORS
from readEmail import  plainEmails, summarizeEmail
from regexes import replaceLinks


app = Flask(__name__)
CORS(app)

@app.route('/plain/data', methods = ["GET"])
def getPlain():
    emails = plainEmails()
    return jsonify(emails)

@app.route("/test/nothing", methods = ["GET"])
def getTest():
    testObj = {"sender" : "sas"}
    testArr = [None] * 50
    for i in range(50):
        testArr[i] = testObj
    return jsonify(testArr)

@app.route("/summary/get", methods = ["POST"])
def getSummary():
    data = request.get_json()
    if data is None:
        return jsonify({"error" : "Invalid / Missing input"}) , 400
    else:
        summary = summarizeEmail(replaceLinks(data['text']))
        return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug = True)

