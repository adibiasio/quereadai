import gradio as gr

# Gradio Function
def greet(name):
    return "Hello " + name + "!"

# Create Gradio interface with share=True to get the URL
gr.Interface(fn=greet, inputs="text", outputs="text", live=True).launch(share=True)
