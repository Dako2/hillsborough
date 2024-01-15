from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.teardown_appcontext
def teardown_server(exception=None):
    """
    Cleanup function to be called when the application context is torn down.
    It can be used to release resources, such as closing the server socket.
    """
    try:
        # Add any cleanup code here
        pass
    except Exception as e:
        app.logger.error("Error during teardown: %s", e)

# Your other route and message handling code here...

if __name__ == '__main__':
    app.run(debug=True)

