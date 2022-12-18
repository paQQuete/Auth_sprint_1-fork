from datetime import datetime

import sqlalchemy.orm
from flask import abort
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from db.pg_base import PostgresService
from models.user_model import User, Role, UserRole, Resource, ResourceRole
from utils.orm_wraps import engine_session


class RoleService(PostgresService):
    def __init__(self):
        super().__init__()

    @engine_session()
    def add_role(self, name, description, session: sqlalchemy.orm.Session = None):
        if not name:
            abort(400)
        try:
            role = session.query(Role).filter(Role.name == name).one()
            if role:
                abort(400)
        except NoResultFound:
            added_role = Role()
            added_role.name = name
            added_role.description = description
            session.add(added_role)
            session.commit()
            return session.query(Role).filter(Role.name == name).one()

    @engine_session()
    def del_role(self, role_id, session: sqlalchemy.orm.Session = None):
        try:
            role = session.query(Role).filter(Role.id == role_id).one()
            session.query(Role).filter(Role.id == role.id).delete()
            session.commit()
            return role
        except NoResultFound:
            abort(404)

    @engine_session()
    def update_role(self, role_id, name, description, session: sqlalchemy.orm.Session = None):
        if not name and not description:  # check if name and description presented in request
            abort(400)
        try:  # check if ID exist
            session.query(Role).filter(Role.id == role_id).one()
        except NoResultFound:
            abort(404)
        try:  # check if name exist - if exist aborting
            role = session.query(Role).filter(Role.name == name).one()
            if role:
                abort(400)
        except MultipleResultsFound:
            abort(400)
        except NoResultFound:
            if not name:  # only description presented
                session.query(Role).filter(Role.id == role_id).update(
                    {'description': description, 'modified': datetime.utcnow()}
                )
                session.commit()
                role = session.query(Role).filter(Role.id == role_id).one()
            elif not description:  # only name presented
                session.query(Role).filter(Role.id == role_id).update(
                    {'name': name, 'modified': datetime.utcnow()}
                )
                session.commit()
                role = session.query(Role).filter(Role.id == role_id).one()
            else:  # name and description presented
                session.query(Role).filter(Role.id == role_id).update(
                    {'name': name, 'description': description, 'modified': datetime.utcnow()}
                )
                session.commit()
                role = session.query(Role).filter(Role.id == role_id).one()

            return role

    @engine_session()
    def show_all_roles(self, session: sqlalchemy.orm.Session = None):
        return session.query(Role).all()

    @engine_session()
    def show_role(self, role_id, session: sqlalchemy.orm.Session = None):
        try:
            return session.query(Role).filter(Role.id == role_id).one()
        except NoResultFound:
            abort(404)

    @engine_session()
    def user_add_role(self, user_id, role_id, session: sqlalchemy.orm.Session = None):
        try:  # check User model for user_id exist, if not - aborting
            session.query(User).filter(User.id == user_id).one()
        except NoResultFound:
            abort(404)

        try:  # check Role model for role_id exist, if not - aborting
            session.query(Role).filter(Role.id == role_id).one()
        except NoResultFound:
            abort(404)
        try:  # check if relationship user_id__role_id exist in UserRole model, if not - add new
            session.query(UserRole).filter(UserRole.user_id == user_id,
                                           UserRole.role_id == role_id).one()
            abort(400)
        except MultipleResultsFound:  # this exceptions occurs if UserRole model has multiple identical entries
            abort(400)
        except NoResultFound:
            user_add_role = UserRole()
            user_add_role.user_id = user_id
            user_add_role.role_id = role_id
            session.add(user_add_role)
            session.commit()
            return session.query(UserRole).filter(UserRole.user_id == user_id,
                                                  UserRole.role_id == role_id).one()

    @engine_session()
    def user_remove_role(self, user_id, role_id, session: sqlalchemy.orm.Session = None):
        if not user_id or not role_id:  # check if user_id or role_id presented in request
            abort(400)
        try:
            user_role = session.query(UserRole). \
                filter(UserRole.user_id == user_id,
                       UserRole.role_id == role_id).one()
            session.query(UserRole).filter(UserRole.id == user_role.id).delete()
            session.commit()
            return user_role
        except NoResultFound:
            abort(404)

    @engine_session()
    def user_check_role(self, user_id, session: sqlalchemy.orm.Session = None):
        try:
            user_role = session.query(UserRole).filter(UserRole.user_id == user_id).all()
            if len(user_role) == 0:
                abort(404)
            return user_role
        except NoResultFound:
            abort(404)

    @engine_session()
    def role_check_user(self, role_id, session: sqlalchemy.orm.Session = None):
        try:
            role_user = session.query(UserRole).filter(UserRole.role_id == role_id).all()
            if len(role_user) == 0:
                abort(404)
            return role_user
        except NoResultFound:
            abort(404)

    @engine_session()
    def user_role_show_all(self, session: sqlalchemy.orm.Session = None):
        return session.query(UserRole).all()
