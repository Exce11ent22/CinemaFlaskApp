from app import db
from flask_sqlalchemy import BaseQuery
from werkzeug.utils import cached_property
from flask_principal import RoleNeed, UserNeed, Permission
from flask_login import UserMixin


admin = Permission(RoleNeed('admin'))
member = Permission(RoleNeed('member'))


class UserQuery(BaseQuery):

    __tablename__ = 'user'

    def from_identity(self, identity):
        try:
            user = self.get(int(identity.name))
        except ValueError:
            user = None

        if user:
            identity.provides.update(user.provides)

        identity.user = user

        return user


class User(UserMixin, db.Model):

    query_class = UserQuery

    MEMBER = 0
    ADMIN = 1

    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.Integer, default=MEMBER)

    @cached_property
    def permissions(self):
        return self.Permissions(self)

    @cached_property
    def provides(self):
        needs = [RoleNeed('authenticated'), UserNeed(self.id)]
        if self.is_member:
            needs.append(RoleNeed('member'))
        if self.is_admin:
            needs.append(RoleNeed('admin'))
        return needs

    @property
    def is_member(self):
        return self.role == self.MEMBER

    @property
    def is_admin(self):
        return self.role == self.ADMIN


if __name__ == '__main__':
    db.create_all()
    db.session.commit()
