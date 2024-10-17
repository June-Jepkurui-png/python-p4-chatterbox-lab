from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # Fetch all messages ordered by creation time
        messages = Message.query.order_by(Message.created_at.asc()).all()
        # Serialize the messages
        serialized_messages = [message.to_dict() for message in messages]
        # Return JSON response with proper content-type and status 200
        return make_response(jsonify(serialized_messages), 200)

    elif request.method == 'POST':
        data = request.get_json()  # Ensure the request data is JSON
        # Check for required fields
        if not data or 'body' not in data or 'username' not in data:
            return make_response(jsonify({'error': 'Missing body or username'}), 400)

        try:
            # Create and save new message
            new_message = Message(body=data['body'], username=data['username'])
            db.session.add(new_message)
            db.session.commit()

            # Return the newly created message with status 201
            return make_response(jsonify(new_message.to_dict()), 201)

        except Exception as e:
            # Handle database or other errors
            return make_response(jsonify({'error': 'Unable to create message', 'details': str(e)}), 500)


@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)
    if not message:
        # Return 404 if message not found
        return make_response(jsonify({'error': 'Message not found'}), 404)

    if request.method == 'GET':
        # Return the requested message
        return make_response(jsonify(message.to_dict()), 200)

    elif request.method == 'PATCH':
        data = request.get_json()  # Ensure the request data is JSON
        # Update message body if present in the request
        if 'body' in data:
            message.body = data['body']
            db.session.commit()
            return make_response(jsonify(message.to_dict()), 200)

        return make_response(jsonify({'error': 'No valid fields to update'}), 400)

    elif request.method == 'DELETE':
        try:
            db.session.delete(message)
            db.session.commit()
            # Return a success message upon deletion
            return make_response(jsonify({'message': 'Message deleted successfully'}), 200)
        except Exception as e:
            # Handle any errors during deletion
            return make_response(jsonify({'error': 'Failed to delete message', 'details': str(e)}), 500)


if __name__ == '__main__':
    app.run(port=5555)
