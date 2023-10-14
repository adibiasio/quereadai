from flask import Flask, render_template, redirect, url_for
from authlib.integrations.flask_client import OAuth
import gradio as gr
import chromadb
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from chromadb.utils import embedding_functions
from chromadb.config import Settings
from langchain.vectorstores import Chroma
import threading
import random
import time
import io
import os
os.environ['OPENAI_API_KEY'] = "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"

app = Flask(__name__)
app.secret_key = '1u2h3h5h1985h1b'

oauth = OAuth(app)
chroma_client = chromadb.HttpClient(host='3.84.129.6', port=8000)
openai_embed_function = embedding_functions.OpenAIEmbeddingFunction("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")
collection = None

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
 
# def get_secret(secret_name): 

#     region_name = "us-east-1"

#     # Create a Secrets Manager client
#     session = boto3.session.Session()
#     client = session.client(
#         service_name='secretsmanager',
#         region_name=region_name
#     )

#     try:
#         get_secret_value_response = client.get_secret_value(
#             SecretId=secret_name
#         )
#     except ClientError as e:
#         raise e

#     return get_secret_value_response['SecretString']


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
    global user_email
    user = token['userinfo']
    user_email = user["given_name"]
    # print(get_secret("OPENAI_API_KEY"))
    threading.Thread(target=initialize_gradio).start()
    collection = chroma_client.get_or_create_collection(name=user_email, embedding_function=openai_embed_function)
    return redirect(url_for('gradio'))


def upload_file(files):
    collection = chroma_client.get_or_create_collection(name=user_email, embedding_function=openai_embed_function)
    for file in files:
        loader = PyPDFLoader(file.name)
        documents = loader.load()
        # Splitting Recitation Guide into text chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
    collection.add(documents=[text.page_content for text in texts], ids=[file.name + str(i) for i in range(len(texts))])
    file_paths = [file.name for file in files]
    return file_paths


def respond(message, chat_history):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    custom_func = OpenAIEmbeddings()
    vectorchrom = Chroma(client=chroma_client, collection_name=user_email, embedding_function=custom_func)
    qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0), vectorchrom.as_retriever(), memory=memory)
    chat_history.append((message, qa.run(message)))
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
                file_output = gr.File(elem_id="upload", interactive=False, file_count="multiple")
                upload_button = gr.UploadButton("Click to Upload a File", file_types=["pdf"], file_count="multiple")
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

application = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)
