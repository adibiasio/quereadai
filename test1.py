from flask import Flask, render_template, session, redirect, url_for
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = '1u2h3h5h1985h1b'

# Initialize OAuth object
oauth = OAuth(app)

# Configure Google OAuth provider
oauth.register(
    name='google',
    client_id='YOUR_GOOGLE_CLIENT_ID',
    client_secret='YOUR_GOOGLE_CLIENT_SECRET',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    authorize_prompt_params=None,
    authorize_response_params=None,
    token_url='https://accounts.google.com/o/oauth2/token',
    client_kwargs={'scope': 'openid profile email'},
    redirect_uri='REDIRECT_URI_AFTER_LOGIN'  # For example, '/google-login-callback'
)

# Login page with only a login button
@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')

# Redirect to Google OAuth provider for login
@app.route('/google-login')
def google_login():
    redirect_uri = url_for('google_login_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

# Callback route after successful Google OAuth login
@app.route('/google-login-callback')
def google_login_callback():
    token = oauth.google.authorize_access_token()
    session['google_token'] = token
    return redirect(url_for('gradio'))

# Gradio route accessible after successful Google OAuth login
@app.route('/gradio')
def gradio():
    if 'google_token' in session:
        return render_template('gradio.html')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
