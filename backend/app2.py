from flask import Flask, jsonify, request, session, abort, redirect
from flask_cors import CORS
from readEmailsGoogle import  plainEmails, getEmails, emailsBySender, getSenderAnalysis
from regexes import replaceLinks
from readEmailsGoogle import summarizeEmail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import google.auth.transport.requests 
from google.oauth2.credentials import Credentials
from google.oauth2 import id_token
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import requests
from pip._vendor import cachecontrol
import json
from datetime import timedelta
import time
from flask_migrate import Migrate
import hashlib
from sqlalchemy.orm.exc import NoResultFound
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials= True)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'# GOOGLE will error if redirect to non http if dont have this
FRONTEND_URL = os.getenv("FRONTEND_URL")
BACKEND_URL = os.getenv("BACKEND_URL")



app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
# "postgresql://emailtest_user:T9hg0mcrtPiRm5cAdhfwO4IupLNiKjzu@dpg-cq1ml0bv2p9s73d4ajgg-a.singapore-postgres.render.com/emailtest"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("APP_SECRET_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=4)   
 
db = SQLAlchemy(app)
migrate = Migrate(app,db)

DEV_GMAIL_TOKEN_PATH = "creds/gmail_token.json"
# for deploy
DEV_CLIENT_SECRET_PATH = "web_google.json"
#  # for on machine
# DEV_CLIENT_SECRET_PATH = "creds/client_secret.json"

GOOGLE_CLIENT_ID = None
try:
    with open(DEV_CLIENT_SECRET_PATH, 'r') as file:
        data = json.load(file)
        GOOGLE_CLIENT_ID = data.get('client_id')
        # Continue with your code that uses GOOGLE_CLIENT_ID
except FileNotFoundError:
    print(f"File not found: {DEV_CLIENT_SECRET_PATH}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")

SCOPES = ["openid","https://www.googleapis.com/auth/userinfo.email",  "https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/gmail.readonly"]


# credentials come from flow.credentials
#store flow.credentials into token and use for authToken in getEmail
# check credentials validity using credentials.valid, credentials.expired, credentials.refresh_token
# if os.path.exists(gmail_token_path):
    #     creds = Credentials.from_authorized_user_file(gmail_token_path, SCOPES)
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = Flow.from_client_secrets_file(
        #     client_secrets_file= DEV_CLIENT_SECRET_PATH,
        #     scopes=SCOPES,
        #     redirect_uri="http://127.0.0.1:5000/callback"
# )
    #         creds = flow.credentials
# GENERAL FLOW:
# 1) react page redirects to login
# 2) login finishes and callback
# 3) email, credentials and a generated unique id is stored into database
# 4) hash the email and pass it back to react 
# 5) email stored as cookie
flow = Flow.from_client_secrets_file(
    client_secrets_file= DEV_CLIENT_SECRET_PATH,
    scopes=SCOPES,
    redirect_uri= f"{BACKEND_URL}/callback"
)

class UserToken(db.Model): #userid uses the gmail
    __tablename__ = "userTokens"

    user_id = db.Column(db.String(100), primary_key = True)
    gmail_token = db.Column(db.String(1000), unique = True) #stores in json format, to use in email, use json.loads
    hashedEmail = db.Column(db.String(1000), unique = True)

    def __init__(self, user_id, gmail_token):
        self.user_id = user_id
        self.gmail_token = gmail_token
        self.hashedEmail = hashlib.sha256(self.user_id.encode()).hexdigest()


def insert_token(user_id, gmail_token):
    newToken = UserToken(user_id= user_id, gmail_token= gmail_token)
    db.session.add(newToken)
    db.session.commit()


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

@app.route("/login")
def login():
   
    
    
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)



#is passed a user ID and returns a list of lists of emails sorted by sender  
@app.route("/overview", methods = ["GET", "POST"])
def overview():
    # gives the top 5 people sending emails within last 14 days
    # get all emails within last 14 days
    # sort by unique email senders
    # create a hashtable 
    data = request.get_json()
    app.logger.info(data)
    if data == None:
        return jsonify({"error": "invalid data/ no token"}, 401)
    else:
        userHash = data['userHash']
        app.logger.info(userHash)
        # return jsonify({"status" : userHash})
        try: 
            user = UserToken.query.filter_by(hashedEmail = userHash).one()
            userToken = user.gmail_token
            #pass into email
            authToken = json.loads(userToken)
            senders =  emailsBySender(authToken)
            data = {"userEmail" : user.user_id, "senders" : senders}
            return jsonify(data)
        except NoResultFound as e:
            return {"error" : e}, 401
        
@app.route("/analysis", methods = ["POST", "GET"])
def analysis():
    data = request.get_json()
   
    if not data['userHash']:
        return {"error" : "no userHash"},401
    
    userHash = data['userHash']
    try:
        regUser = UserToken.query.filter_by(hashedEmail = userHash).one()
        analysis = getSenderAnalysis(data['emails'])
        return jsonify({"analysis" : analysis})
    except NoResultFound as e:
        return {"error" : e}, 401

@app.route("/callback")
def callback():
    
    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        return {"error" : e} , 401

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    if credentials == None:
        return 'credentials None', 500
    
    if not credentials.id_token:

        return f'id token none {credentials}', 500
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    retries = 0
    while retries < 5:
        try:
            id_info = id_token.verify_oauth2_token(
                id_token=credentials._id_token,
                request=token_request,
                audience=GOOGLE_CLIENT_ID
            )
            break
        # except ValueError as e:
        #     return jsonify({"error" : "Invalid Token"}, 401)
        except google.auth.exceptions.InvalidValue as e:
            if "Token used too early" in str(e):
                retries += 1
                time.sleep(5)
            else:
                return {"error" : str(e)} ,401

   
    userGmailToken = credentials.to_json()
    userEmail = id_info.get("email")


    # add to the database
    try: 
        existingUser = UserToken.query.filter_by(user_id = userEmail).one()
        existingUser.gmail_token  = userGmailToken
        db.session.commit()
        app.logger.info("added to database new token")
        
        # return jsonify({"message" : "account updated", "userHash" : existingUser.hashedEmail} , 200)
        return redirect(f"{FRONTEND_URL}/confirmation?success=true&userHash={existingUser.hashedEmail}")


    except NoResultFound as e:
        newUser = UserToken(user_id= userEmail, gmail_token= userGmailToken)
        db.session.add(newUser)
        db.session.commit()
        return redirect(f"{FRONTEND_URL}/confirmation?success=true&userHash={newUser.hashedEmail}")
        # return jsonify({"message" : "new account created", "userHash" : newUser.hashedEmail} , 200)

  
        
  
    


    



@app.route("/emails/secure", methods = ["POST", "GET"])
def emailSecure():
    data = request.get_json()
    app.logger.info(data)
    if data == None:
        return jsonify({"error": "invalid data/ no token"}, 401)
    else:
        userHash = data['userHash']
        app.logger.info(userHash)
        # return jsonify({"status" : userHash})
        user = UserToken.query.filter_by(hashedEmail = userHash).one()
        userToken = user.gmail_token
        #pass into email
        authToken = json.loads(userToken)
        emails =  getEmails(authToken)
        data = {"userEmail" : user.user_id, "emails" : emails}
        return jsonify(data)
    








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



if __name__ == "__main__":
    
    with app.app_context():
        db.create_all()


 
    app.run(debug = True)
