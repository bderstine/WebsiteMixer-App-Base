from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from websitemixer.auth import login_required
from websitemixer.database import db_session
from websitemixer.models import User, Post

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    """Show all the posts, most recent first."""
    postData = Post.query.filter_by(slug=slug).first()
    return render_template('blog/index.html', posts=postdata)

