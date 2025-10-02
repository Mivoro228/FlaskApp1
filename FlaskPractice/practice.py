import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import Post, User
from app import app, db

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post':Post}