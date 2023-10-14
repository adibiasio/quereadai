from flask import Flask, render_template, session, redirect, url_for
from authlib.integrations.flask_client import OAuth
import gradio as gr
import os
import threading

app = Flask(__name__)
app.secret_key = '1u2h3h5h1985h1b'

oauth = OAuth(app)
 
@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')
 
 
@app.route('/google/')
def google():     
    oauth.register(
        name='google',
        client_id='514310494310-sfr3q4obp9as81862bt291g8bombbps3.apps.googleusercontent.com',
        client_secret='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',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={ 
            'scope': 'openid email profile'
        }
    )
    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    print(redirect_uri)
    print("bal")
    return oauth.google.authorize_redirect(redirect_uri)
 
@app.route('/google/auth/')
def google_auth():
    print("ballls")
    token = oauth.google.authorize_access_token()
    global user
    user = token['userinfo']
    print(" Google User ", user)
    threading.Thread(target=initialize_gradio).start()
    return redirect(url_for('gradio'))


def greet(name):
    return "Your name is " + user.given_name + " your email is " + user.email

def initialize_gradio():
    demo = gr.Interface(fn=greet, inputs="text", outputs="text")
    demo.launch()


# Gradio route r
@app.route('/gradio')
def gradio():
    return render_template('gradio.html')



if __name__ == '__main__':
    app.run(debug=True)
