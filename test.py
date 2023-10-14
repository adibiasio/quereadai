from flask import Flask, render_template, request, session, redirect, url_for
import gradio as gr
import threading
import torch

app = Flask(__name__)
app.secret_key = '1u2h3h5h1985h1b'


model2 = torch.hub.load(
    "AK391/animegan2-pytorch:main",
    "generator",
    pretrained=True,
    progress=False
)
model1 = torch.hub.load("AK391/animegan2-pytorch:main", "generator", pretrained="face_paint_512_v1")
face2paint = torch.hub.load(
    'AK391/animegan2-pytorch:main', 'face2paint', 
    size=512,side_by_side=False
)

def inference(img, ver):
    if ver == 'version 2 (🔺 robustness,🔻 stylization)':
        out = face2paint(model2, img)
    else:
        out = face2paint(model1, img)
    return out

title = "AnimeGANv2"
description = "Gradio Demo for AnimeGanv2 Face Portrait. To use it, simply upload your image, or click one of the examples to load them. Read more at the links below. Please use a cropped portrait picture for best results similar to the examples below."
article = "<p style='text-align: center'><a href='https://github.com/bryandlee/animegan2-pytorch' target='_blank'>Github Repo Pytorch</a></p> <center><img src='https://visitor-badge.glitch.me/badge?page_id=akhaliq_animegan' alt='visitor badge'></center></p>"
# Initialize Gradio interface
def initialize_gradio():
    demo = gr.Interface(
        fn=inference, 
        inputs=[gr.inputs.Image(type="pil"),gr.inputs.Radio(['version 1 (🔺 stylization, 🔻 robustness)','version 2 (🔺 robustness,🔻 stylization)'], type="value", default='version 2 (🔺 robustness,🔻 stylization)', label='version')], 
        outputs=gr.outputs.Image(type="pil"),
        title=title,
        description=description,
        article=article)
    demo.launch()

# Login page 
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == '1' and password == '1':
            session['username'] = username
            threading.Thread(target=initialize_gradio).start()
            return redirect(url_for('gradio'))
        else:
            error = 'Invalid credentials.'
    return render_template('login.html', error=error)

# Gradio 
@app.route('/gradio')
def gradio():
    if 'username' in session:
        return render_template('gradio.html')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
