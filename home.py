from flask import Flask, render_template, redirect, url_for
from authlib.integrations.flask_client import OAuth
import gradio as gr
import threading
import random
import time

app = Flask(__name__)
app.secret_key = '1u2h3h5h1985h1b'

oauth = OAuth(app)

CSS ="""
.contain { display: flex; flex-direction: column; }
.gradio-container { height: 100vh !important; }
#chatbot { flex-grow: 1; overflow: auto; }
#upload { flex-grow: 1; overflow: auto; }
#col1 { height: 92vh !important; }
#col2 { height: 92vh !important; }
#txt { padding-left: 5px; }
footer { display:none !important }
"""
 
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
    return oauth.google.authorize_redirect(redirect_uri)
 
 
@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    global user
    user = token['userinfo']
    print(" Google User ", user)
    threading.Thread(target=initialize_gradio).start()
    return redirect(url_for('gradio'))


def upload_file(files):
    file_paths = [file.name for file in files]
    return file_paths


def respond(message, chat_history):
    bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
    chat_history.append((message, bot_message))
    time.sleep(0.5)
    return "", chat_history


def initialize_gradio():
    with gr.Blocks(css=CSS) as demo:
        with gr.Row():
            with gr.Column(scale=1, elem_id="col1"):
                gr.Markdown(
                f"""
                # Hello, {user.given_name}. 
                # Welcome to Queread AI
                """, elem_id="txt")
                file_output = gr.File(elem_id="upload")
                upload_button = gr.UploadButton("Click to Upload a File", file_types=["image", "video"], file_count="multiple")
                upload_button.upload(upload_file, upload_button, file_output)
            with gr.Column(scale=4, elem_id="col2"):
                chatbot = gr.Chatbot(elem_id="chatbot")
                msg = gr.Textbox()
                clear = gr.ClearButton([msg, chatbot])
                msg.submit(respond, [msg, chatbot], [msg, chatbot])

    demo.launch()


# Gradio route r
@app.route('/gradio')
def gradio():
    return render_template('gradio.html')


if __name__ == '__main__':
    app.run(debug=True)
