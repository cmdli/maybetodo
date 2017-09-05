
import os

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def tasklist_key(author_id):
    return ndb.Key('MaybeTodo', author_id)

class Task(ndb.Model):
    """A model to represent one task on the ToDo"""
    task_id = ndb.StringProperty(indexed=False)
    author = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect("/login")
            return
        tasklist_query = Task.query(ancestor=tasklist_key(user.user_id())).order(-Task.date)
        tasklist = tasklist_query.fetch()
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        logout_url = users.create_logout_url('/')
        template_params = {
            'user_nickname' : user.nickname(),
            'tasklist' : tasklist,
            'logout_url': users.create_logout_url('/login')
        }
        self.response.write(template.render(template_params))

class MaybeTodo(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if not user:
            self.redirect('/login')
            return
        if self.request.path == '/addtask':
            task = Task(parent=tasklist_key(user.user_id()))
            task.author = user.user_id()
            task.content = self.request.get('content')
            task.put()
        elif self.request.path == '/delete':
            author_id = self.request.get('author')
            if user.user_id() == author_id:
                task_id = int(self.request.get('task'))
                task_key = ndb.Key('MaybeTodo',author_id,'Task',task_id)
                print task_key, task_key.get()
                task_key.delete()
        self.redirect('/')

class LoginPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect('/')
            return
        template = JINJA_ENVIRONMENT.get_template('login.html')
        login_redirect = users.create_login_url('/')
        self.response.write(template.render({'login_redirect': login_redirect }))

app = webapp2.WSGIApplication([('/',MainPage),
                               ('/login', LoginPage),
                               ('/addtask', MaybeTodo),
                               ('/delete', MaybeTodo)],
                              debug=True)
