import pytest
import hello_auth
from flask_login import current_user
import sys


@pytest.yield_fixture
def client():
    app = hello_auth.app
    app.config['LOGIN_DISABLED'] = True
    with app.app_context():
        with app.test_client() as c:
            yield c


@pytest.yield_fixture
def client_auth():
    app = hello_auth.app
    app.config['LOGIN_DISABLED'] = False
    with app.app_context():
        with app.test_client() as c:
            yield c


@pytest.fixture
def user_fixture():
    alice = hello_auth.User('Alice', 1,
                            passhash=b'$2b$12$6UcECs.N2rNgOJGMgK3L8O5woOSOEAyuxdCvblrVatJNRVPHTnsx6')  # diffie_rulz
    USERS = {1: alice}
    return alice, USERS


class TestRoutes:
    def test_root(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_login(self, client):
        response = client.get('/login')
        assert response.status_code == 200

    def test_secrets(self, client):
        response = client.get('/unicorns-area-51-fight-club')
        assert response.status_code == 302


class TestUserClass:
    def test_get_user_id(self, user_fixture):
        user, _ = user_fixture
        assert isinstance(user.get_id(), str) or isinstance(user.get_id(), int)

    def test_get_is_active(self, user_fixture):
        user, _ = user_fixture
        assert user.is_active

    def test_password_check_correct(self, user_fixture):
        user, _ = user_fixture
        assert user.check_pw(b'diffie_rulz')

    def test_password_check_wrong(self, user_fixture):
        user, _ = user_fixture
        assert not user.check_pw(b'diffie_rulz_wrong')

    def test_password_check_blank(self, user_fixture):
        user, _ = user_fixture
        assert not user.check_pw(None)

    def test_password_check_empty(self, user_fixture):
        user, _ = user_fixture
        user.passhash = None
        assert not user.check_pw(b'diffie_rulz')


class TestFlaskLogin:
    def test_get_user_by_name(self, user_fixture):
        user, _ = user_fixture
        assert hello_auth.user_from_name('ALICE').name == user.name


class TestLoginAuth:
    def test_secrets_auth(self, client_auth):
        client_auth.get('/unicorns-area-51-fight-club')
        assert current_user.is_anonymous

    def test_login_success(self, client_auth):
        client_auth.post('/login', data=dict(pw=u'diffie_rulz', name=u'Alice'))
        assert current_user.is_active

    def test_login_fail(self, client_auth):
        client_auth.post('/login', data=dict(pw=u'diffie_rulz_wrong', name=u'Alice'))
        assert not current_user.is_active

    def test_login_fail_no_password(self, client_auth):
        client_auth.post('/login', data=dict(name=u'Alice'))
        assert not current_user.is_active

    def test_login_fail_no_user(self, client_auth):
        client_auth.post('/login', data=dict(pw=u'diffie_rulz', name=u'Rando'))
        assert not current_user.is_active

    def test_logout(self, client_auth):
        client_auth.post('/login', data=dict(pw=u'diffie_rulz', name=u'Alice'))
        client_auth.get('/logout')
        assert current_user.is_anonymous
