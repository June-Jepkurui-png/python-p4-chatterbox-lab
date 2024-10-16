from datetime import datetime
from app import app
from models import db, Message
import pytest

@pytest.fixture
def setup_teardown():
    '''Setup and teardown for each test.'''
    with app.app_context():
        # Delete existing message with body "Hello 👋" and username "Liza"
        Message.query.filter_by(body="Hello 👋", username="Liza").delete()
        db.session.commit()

        yield

        # Cleanup: Delete any messages created during tests
        Message.query.filter_by(body="Hello 👋", username="Liza").delete()
        db.session.commit()

class TestMessage:
    '''Tests for the Message model.'''

    def test_has_correct_columns(self, setup_teardown):
        '''has columns for message body, username, and creation time.'''
        with app.app_context():
            # Create a new message
            hello_from_liza = Message(body="Hello 👋", username="Liza")
            db.session.add(hello_from_liza)
            db.session.commit()

            # Assertions
            assert hello_from_liza.body == "Hello 👋"
            assert hello_from_liza.username == "Liza"
            assert isinstance(hello_from_liza.created_at, datetime)

            # Cleanup the created message
            db.session.delete(hello_from_liza)
            db.session.commit()
