from datetime import datetime
from app import app
from models import db, Message
import pytest

@pytest.fixture(scope='function')
def client():
    """Set up a test client with app context."""
    with app.app_context():
        yield app.test_client()
        db.session.rollback()  # Rollback changes after each test to maintain database state

@pytest.fixture(scope='function')
def setup_message():
    """Create and yield a test message, then clean up after the test."""
    with app.app_context():
        hello_from_liza = Message(
            body="Hello 👋",
            username="Liza"
        )
        db.session.add(hello_from_liza)
        db.session.commit()
        yield hello_from_liza
        db.session.delete(hello_from_liza)
        db.session.commit()

def test_has_correct_columns(setup_message):
    """Test if the message has the correct columns."""
    assert setup_message.body == "Hello 👋"
    assert setup_message.username == "Liza"
    assert isinstance(setup_message.created_at, datetime)

def test_returns_list_of_json_objects_for_all_messages_in_database(client):
    """Test if the GET /messages returns all messages as JSON."""
    response = client.get('/messages')
    records = Message.query.all()

    assert response.status_code == 200
    response_data = response.json
    assert isinstance(response_data, list)

    for message in response_data:
        assert message['id'] in [record.id for record in records]
        assert message['body'] in [record.body for record in records]

def test_creates_new_message_in_the_database(client):
    """Test if a new message is created in the database."""
    response = client.post(
        '/messages',
        json={"body": "Hello 👋", "username": "Liza"}
    )
    assert response.status_code == 201

    h = Message.query.filter_by(body="Hello 👋").first()
    assert h is not None
    assert h.username == "Liza"

def test_returns_data_for_newly_created_message_as_json(client):
    """Test if the response returns correct JSON data for the new message."""
    response = client.post(
        '/messages',
        json={"body": "Hello 👋", "username": "Liza"}
    )
    assert response.content_type == 'application/json'
    assert response.status_code == 201

    response_data = response.json
    assert response_data["body"] == "Hello 👋"
    assert response_data["username"] == "Liza"

def test_updates_body_of_message_in_database(client, setup_message):
    """Test if the message body is updated in the database."""
    response = client.patch(
        f'/messages/{setup_message.id}',
        json={"body": "Goodbye 👋"}
    )
    assert response.status_code == 200

    updated_message = Message.query.get(setup_message.id)
    assert updated_message.body == "Goodbye 👋"

def test_returns_data_for_updated_message_as_json(client, setup_message):
    """Test if the response returns correct JSON for the updated message."""
    response = client.patch(
        f'/messages/{setup_message.id}',
        json={"body": "Goodbye 👋"}
    )
    assert response.content_type == 'application/json'
    assert response.status_code == 200

    response_data = response.json
    assert response_data["body"] == "Goodbye 👋"

def test_deletes_message_from_database(client, setup_message):
    """Test if the message is deleted from the database."""
    response = client.delete(f'/messages/{setup_message.id}')
    assert response.status_code == 200

    deleted_message = Message.query.get(setup_message.id)
    assert deleted_message is None
