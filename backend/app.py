from flask import Flask, jsonify, request, session
from flask_cors import CORS
from readEmailsGoogle import  plainEmails
from regexes import replaceLinks
from readEmailsGoogle import summarizeEmail
from flask_sqlalchemy import SQLAlchemy
#TODO, Create temp file and pass into 

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://emailtest_user:T9hg0mcrtPiRm5cAdhfwO4IupLNiKjzu@dpg-cq1ml0bv2p9s73d4ajgg-a.singapore-postgres.render.com/emailtest"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "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"

db = SQLAlchemy(app)
DEV_GMAIL_TOKEN_PATH = "creds/gmail_token.json"
DEV_CLIENT_SECRET_PATH = "creds/client_secret.json"
GOOGLE_CLIENT_ID = "1061349728865-lj54criebfvhp0u157dnfb1tdelhgu25.apps.googleusercontent.com"

class UserToken(db.Model):
    __tablename__ = "user_token"

    user_id = db.Column(db.String(100), primary_key = True)
    gmail_token = db.Column(db.String(500), primary_key = True)

    def __init__(self, user_id, gmail_token):
        self.user_id = user_id
        self.gmail_token = gmail_token

def insert_token(user_id, gmail_token):
    newToken = UserToken(user_id= user_id, gmail_token= gmail_token)
    db.session.add(newToken)
    db.session.commit()


@app.route("/db/test", methods = ["GET"])
def checkConnection():
    object = {"status" : check_database_connection()} 
    return jsonify(object)


@app.route('/plain/data', methods = ["GET"])
def getPlain():
    emails = plainEmails(DEV_GMAIL_TOKEN_PATH, DEV_CLIENT_SECRET_PATH)
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

def check_database_connection():
    try:
        # result = db.select(UserToken).first()
        result = UserToken.query.first()
        
        returner = {"user_id" : result.user_id, "gmail_token" : result.gmail_token}
        
        return returner
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return False

def testUser():
    
    db.session.add(UserToken("first user", "test"))
    db.session.commit()

if __name__ == "__main__":
    
    with app.app_context():
        db.create_all()
        # testUser()

 
    app.run(debug = True)
