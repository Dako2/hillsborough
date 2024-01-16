from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import threading
import requests
import core

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Configure the SQLAlchemy part
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///symptom.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backup_symptom.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create an event to signal when the recommendation is available
recommendation_event = threading.Event()


class Symptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    #user_ip = db.Column(db.String(15))  # Assuming IPv4 format
    description = db.Column(db.String(5000), nullable=False)
    recommendation = db.Column(db.String(5000))

    def __repr__(self):
        return f'<Symptom {self.id} - {self.timestamp}>'
    
class BackupSymptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(500), nullable=False)
    recommendation = db.Column(db.String(500))

    def __repr__(self):
        return f'<BackupSymptom {self.id} - {self.timestamp}>'

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

# Function to call the third-party API and fetch a recommendation
def fetch_recommendation(symptoms_description):

    # Make an API request to the third-party service
    try:
        messages = core.recommend(symptoms_description)
        recommendation = ""
        for m in messages:
            recommendation += f"{m.content[0].text.value}"
    except:
        recommendation = "Recommendation not available at the moment."
        app.logger.error(f"Error fetching recommendation: {e}")

    # Update the database with the recommendation (if needed)
    # You can add code here to save the recommendation to the database
    # Store the recommendation in the shared variable
    global shared_recommendation
    shared_recommendation = recommendation

    # Set the event to signal that the recommendation is available
    recommendation_event.set()        

    
@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        symptoms_description = data['symptoms']
        user_ip = request.remote_addr  # Get user's IP address
 
        app.logger.info(f"User IP: {user_ip}, Symptoms: {symptoms_description}")
        # Create a new Symptom instance
        new_symptom = Symptom(description=symptoms_description)
        # Create a new BackupSymptom instance with the same data
        backup_symptom = BackupSymptom(description=symptoms_description)
        # Add and commit both instances to their respective databases
        db.session.add(new_symptom)
        db.session.add(backup_symptom)

        # Start a background thread to fetch the recommendation
        recommendation_thread = threading.Thread(target=fetch_recommendation, args=(symptoms_description,))
        recommendation_thread.start()
        # Wait for the background thread to finish and get the recommendation
        recommendation_thread.join()

        # Check if the event is set, indicating that the recommendation is available
        if recommendation_event.is_set():
            recommendation = shared_recommendation
        else:
            recommendation = "Recommendation not available at the moment."

        new_symptom.recommendation = recommendation
        backup_symptom.recommendation = recommendation

        db.session.commit()

        return jsonify(description=symptoms_description, recommendation=recommendation)
    
    except Exception as e:
        app.logger.error(f"Error in /submit: {e}")
        return jsonify({"error": "Error processing request"}), 500

@app.route('/get-latest-data', methods=['GET'])
def get_latest_data():
    latest_entries = Symptom.query.order_by(Symptom.id.desc()).limit(10).all()
    data = [{
        'id': entry.id,
        'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # Formatting datetime for JSON serialization
        'description': entry.description,
        'recommendation': entry.recommendation
    } for entry in latest_entries]

    return jsonify(data)

@app.route('/get-usage-info', methods=['GET'])
def get_usage_info():
    try:
        usage_count = len(Symptom.query.all())  # Replace with your database query as needed
        # Return the usage count as JSON response
        return jsonify({'usageCount': usage_count})
    except Exception as e:
        # Handle any exceptions or errors
        return jsonify({'error': str(e)}), 500  # Return a 500 Internal Server Error status code if there's an error

@app.route('/delete-entry/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    entry = Symptom.query.get(entry_id)
    app.logger.info(f"delete entry: {entry_id}")

    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"success": "Entry deleted"}), 200
    else:
        return jsonify({"error": "Entry not found"}), 404


@app.teardown_appcontext
def teardown_server(exception=None):
    try:
        db.session.remove()
        if exception:
            app.logger.error("Error during teardown: %s", exception)
    except Exception as e:
        app.logger.error("Teardown error: %s", e)

if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=80)