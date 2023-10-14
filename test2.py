from flask import Flask, redirect, url_for, session
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Change this to a random secret key
oauth = OAuth(app)

# OAuth configuration (example uses GitHub OAuth)
github = oauth.remote_app(
    'github',
    consumer_key='YOUR_GITHUB_CLIENT_ID',
    consumer_secret='YOUR_GITHUB_CLIENT_SECRET',
    request_token_params={'scope': 'user:email'},  # Request additional permissions if needed
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)


@app.route('/')
def index():
    return 'Welcome to the OAuth Login Page! <a href="/login">Login with GitHub</a>'


@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    response = github.authorized_response()

    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={}, error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['github_token'] = (response['access_token'], '')

    # Retrieve user data using the access token
    user_info = github.get('user')
    username = user_info.data['login']
    return 'Logged in as: <b>{}</b> <br><a href="/logout">Logout</a>'.format(username)


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


if __name__ == '__main__':
    app.run(debug=True)
