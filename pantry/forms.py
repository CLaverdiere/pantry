from pantry.models import *

from flask.ext.wtf import Form
from wtforms.fields import TextField, PasswordField
from wtforms.validators import *

class LoginForm(Form):
    username = TextField(validators=[required()])
    password = PasswordField(validators=[required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        # rv = Form.validate(self)
        # if not rv:
        #     return False

        user = User.query.filter_by(username=self.username.data).first()

        if user is None:
            #self.username.errors.append('Unknown username')
            return False

        if not user.check_password(self.password.data):
            #self.username.errors.append('Invalid password')
            return False

        self.user = user
        return True

    def get_user(self, db):
        return db.session.query(User).filter_by(username=self.username.data).first()
