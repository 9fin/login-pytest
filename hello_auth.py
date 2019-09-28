from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from jinja2 import Template
import bcrypt

login_manager = LoginManager()
login_manager.login_view = 'login'
SECRET_KEY = 'not-the-actual-key-in-prod'


testing = False
debug = False
auth_disabled = False

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['TESTING'] = testing
app.config['DEBUG'] = debug
app.config['LOGIN_DISABLED'] = auth_disabled

login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, name, id, active=True, passhash=None):
        self.id = id
        self.name = name
        self.active = active
        self.passhash = passhash

    def get_id(self):
        return self.id

    @property
    def is_active(self):
        return self.active

    def check_pw(self, password):
        if not self.passhash:
            return None
        if not password:
            return None
        if bcrypt.checkpw(password, self.passhash):
            return True


alice = User('Alice', 1, passhash=b'$2b$12$6UcECs.N2rNgOJGMgK3L8O5woOSOEAyuxdCvblrVatJNRVPHTnsx6')  # diffie_rulz
bob = User('Bob', 2, passhash=b'$2b$12$UmgXcHWoxlIsrEoT54LMHeb82OVkkLzPzxVni5.GyaN17JmabRSXO')  # prng_nonce

USERS = {1: alice, 2: bob}


def user_from_name(search_name):
    for _id, user in USERS.items():
        if user.name.lower() == search_name.lower():
            return user


@login_manager.user_loader
def load_user(user_id):
    return USERS.get(user_id)


@app.route('/')
def hello_world():
    return 'Hello, World! Nothing interesting to see here...'


@app.route('/unicorns-area-51-fight-club')
@login_required
def secrets():   # pragma: no cover
    return render_template(Template("""<h1>First rule of coding tests, don't talk about coding tests.</h1><p><img src="https://cdn0.vox-cdn.com/uploads/chorus_image/image/49838227/silicon_20valley_20hbo_20tj_20miller_20unicorn.0.jpg" alt="unicorn" width="440" height="296" /></p>
    <p><img src="https://s-media-cache-ak0.pinimg.com/564x/62/16/1c/62161cb9adaf94679eb27e6ea0139c16.jpg" alt="area-51" width="440" height="440" /></p>
    <p><img src="http://vignette1.wikia.nocookie.net/villains/images/8/81/Tyler-durden.jpg/revision/latest?cb=20160109171255" alt="fight-club" width="400" height="579" /></p>
    <form method="GET" action="/logout">
        <input type="submit" value="logout">
    </form>
    """))


@app.route('/login', methods=['GET'])
def login():
    return render_template(Template("""<h3>Clearance Level</h3>
                                    <form method="POST" action="">
                                        <input type="text" name="name">
                                        <input type="password" name="pw">
                                    <input type="submit" value="Submit">
                                </form>"""))


@app.route('/login', methods=['POST'])
def login_post():
    password = request.form.get('pw').encode('utf-8') if request.form.get('pw') else None
    name = request.form.get('name').lower() if request.form.get('name') else None
    user = user_from_name(name)
    if not user:
        print('failed auth: user not found - redirecting')
        return redirect(url_for('hello_world'))
    if not password:
        print('failed auth: no password supplied - redirecting')
        return redirect(url_for('hello_world'))
    if not user.check_pw(password):
        print('failed auth: incorrect password - redirecting')
        return redirect(url_for('hello_world'))
    login_user(user)
    return redirect(url_for('secrets'))


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    print('logging out user')
    logout_user()
    return redirect(url_for('hello_world'))
