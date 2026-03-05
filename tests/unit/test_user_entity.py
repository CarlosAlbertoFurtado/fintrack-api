import pytest

from app.domain.entities.user import User, UserRole


class TestUser:
    @pytest.fixture
    def props(self):
        return {"email": "carlos@gmail.com", "name": "Carlos Jr", "role": UserRole.USER}

    def test_create_valid(self, props):
        user = User(**props)
        assert user.email == "carlos@gmail.com"
        assert user.name == "Carlos Jr"
        assert user.role == UserRole.USER

    def test_invalid_email(self, props):
        props["email"] = "not-an-email"
        with pytest.raises(ValueError, match="Invalid email"):
            User(**props)

    def test_empty_email(self, props):
        props["email"] = ""
        with pytest.raises(ValueError, match="Invalid email"):
            User(**props)

    def test_short_name(self, props):
        props["name"] = "A"
        with pytest.raises(ValueError, match="at least 2"):
            User(**props)

    def test_admin_role(self, props):
        props["role"] = UserRole.ADMIN
        assert User(**props).is_admin()

    def test_non_admin(self, props):
        assert not User(**props).is_admin()
