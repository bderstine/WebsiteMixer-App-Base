from bs4 import BeautifulSoup
from websitemixer.models import User


def first_paragraph(content=""):
    # take content and return just the first <p></p> content,
    # used in blog loop template
    soup = BeautifulSoup(content, "html.parser")
    thespan = soup.find('p')
    if thespan is None:
        return ''
    else:
        return thespan.string

def process_tags(tags):
    rettags = ''
    taglist = [x.strip() for x in tags.split(',')]
    for t in taglist:
        rettags = rettags + '<a href="/tag/'+t+'/">'+t+'</a> '
    return rettags

def is_admin():
    check = User.query.filter_by(id=session['user_id']).first()
    return check.is_admin()

def author_name(username):
    author = User.query.filter_by(username=username).first()
    if author.name is not None:
        return author.name
    else:
        return author.username
