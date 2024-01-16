from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import threading
import requests 
from celery import Celery

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Configure the SQLAlchemy part
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///symptom.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backup_symptom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

def fetch_recommendation(symptoms_description):
    # Create a new Symptom instance
    new_symptom = Symptom(description=symptoms_description)
    # Create a new BackupSymptom instance with the same data
    backup_symptom = BackupSymptom(description=symptoms_description)
    # Add and commit both instances to their respective databases
    db.session.add(new_symptom)
    db.session.add(backup_symptom)
    db.session.commit()

    try:
        # Make an API request to the third-party service
        response = requests.get('URL_TO_THIRD_PARTY_API', params={'symptoms': symptoms_description})

        if response.status_code == 200:
            recommendation = response.json().get('recommendation')
        else:
            recommendation = "Recommendation not available at the moment."

        new_symptom.recommendation = recommendation
        backup_symptom.recommendation = recommendation

        return recommendation

    except Exception as e:

        recommendation = "bad api"
        new_symptom.recommendation = recommendation
        backup_symptom.recommendation = recommendation

        return f"Error fetching recommendation: {str(e)}"

# Function to call the third-party API and fetch a recommendation
def fetch_recommendation2222(symptoms_description):
    try:
        # Make an API request to the third-party service
        response = requests.get('URL_TO_THIRD_PARTY_API', params={'symptoms': symptoms_description})
        # Create a new Symptom instance
        new_symptom = Symptom(description=symptoms_description)
        # Create a new BackupSymptom instance with the same data
        backup_symptom = BackupSymptom(description=symptoms_description)

        # Add and commit both instances to their respective databases
        db.session.add(new_symptom)
        db.session.add(backup_symptom)
        db.session.commit()

        if response.status_code == 200:
            recommendation = response.json().get('recommendation')
            new_symptom.recommendation = recommendation
            backup_symptom.recommendation = recommendation
        else:
            recommendation = "Recommendation not available at the moment."
            new_symptom.recommendation = recommendation
            backup_symptom.recommendation = recommendation
            
        # Update the database with the recommendation (if needed)
        # You can add code here to save the recommendation to the database

        return recommendation

    except Exception as e:
        return str(e)

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

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        symptoms_description = data['symptoms']
        user_ip = request.remote_addr  # Get user's IP address
 
        app.logger.info(f"User IP: {user_ip}, Symptoms: {symptoms_description}")

        # Start a background thread to fetch the recommendation
        #recommendation_thread = threading.Thread(target=fetch_recommendation, args=(symptoms_description,))
        #recommendation_thread.start()
        
        # Enqueue the task to fetch the recommendation
        task = fetch_recommendation.apply_async(args=[symptoms_description])

        return jsonify(description=symptoms_description, recommendation="Fetching recommendation...")
    
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
