import datetime
from typing import Optional

from sqlalchemy import Column, MetaData, create_engine, or_, UniqueConstraint
from sqlalchemy import Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, backref, relationship
from sqlalchemy.ext.declarative import declared_attr

from config.settings import Settings

settings = Settings()

db_connection_string = settings.PG_CONNECT_STRING
engine = create_engine(
    db_connection_string,
    isolation_level="REPEATABLE READ",
    echo=True,
)

Base = declarative_base()
metadata_obj = MetaData()


def create_partition_by_social_provider(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "social_account_vk" PARTITION OF "social_account" FOR VALUES IN ('VK')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "social_account_yandex" PARTITION OF "social_account" FOR VALUES IN ('YANDEX')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "social_account_google" PARTITION OF "social_account" FOR VALUES IN ('GOOGLE')"""
    )


def create_partition_by_device(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_smart" PARTITION OF "login_history" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_mobile" PARTITION OF "login_history" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_tablet" PARTITION OF "login_history" FOR VALUES IN ('tablet')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_pc" PARTITION OF "login_history" FOR VALUES IN ('pc')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_bot" PARTITION OF "login_history" FOR VALUES IN ('bot')"""
    )


class DefaultMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified = Column(DateTime(), nullable=True)

    @property
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class LoginRecord(DefaultMixin, Base):
    __tablename__ = 'login_history'
    __table_args__ = (
        UniqueConstraint('id', 'device_type'),
        {
            'postgresql_partition_by': 'LIST (device_type)',
            'listeners': [('after_create', create_partition_by_device)],
        }
    )
    login_time = Column(DateTime(), nullable=False)
    useragent = Column(String(256), nullable=True)
    device_type = Column(String(64), nullable=True, primary_key=True)

    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=False)

    def __repr__(self):
        return f'LoginRecord(id={self.id!r}, login_time={self.login_time!r}, ' \
               f'useragent={self.useragent!r}, device_type={self.device_type!r})'


class User(DefaultMixin, Base):
    __tablename__ = 'user_info'
    __table_args__ = (UniqueConstraint('email', 'username', name='user_email_username_unique_constr'),)
    email = Column(String(256), unique=True, nullable=False)
    username = Column(String(256), nullable=True)
    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)
    password = Column(String(512), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_adult = Column(Boolean, default=False)

    login_records = relationship('LoginRecord')
    roles = relationship('UserRole', backref='user')

    def __repr__(self):
        return f'User(id={self.id!r}, email={self.email!r})'

    @classmethod
    def get_user_by_universal_login(cls, username: Optional[str] = None, email: Optional[str] = None):
        """
        возвращает первое совпадение фильтра username OR email
        """
        return cls.query.filter(or_(cls.username == username, cls.email == email)).first()


class SocialAccount(DefaultMixin, Base):
    __tablename__ = 'social_account'
    __table_args__ = (UniqueConstraint('social_id', 'social_name', name='social_pk'),
                      UniqueConstraint('id', 'social_name'),
                      {
                          'postgresql_partition_by': 'LIST (social_name)',
                          'listeners': [('after_create', create_partition_by_social_provider)],
                      }
                      )

    user_id = Column(Integer(), ForeignKey('user_info.id'), nullable=False)
    users = relationship('User', backref=backref('social_accounts', lazy=True))

    social_id = Column(Text, nullable=False)
    social_name = Column(Text, nullable=False, primary_key=True)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'


class UserRole(DefaultMixin, Base):
    __tablename__ = 'user__role'
    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='user__role_pk'),)

    user_id = Column(Integer(), ForeignKey('user_info.id'))
    role_id = Column(Integer(), ForeignKey('role.id'))

    def __repr__(self):
        return f'User_Role(id={self.id!r}, user_id={self.user_id!r}, role_id={self.role_id!r})'


class Role(DefaultMixin, Base):
    __tablename__ = 'role'
    name = Column(String(128), nullable=False)
    description = Column(String(256), nullable=True)
    users = relationship('UserRole', backref='role')

    def __repr__(self):
        return f'Role(id={self.id!r}, name={self.name!r})'


class ResourceRole(DefaultMixin, Base):
    __tablename__ = 'resource__role'
    role_id = Column(Integer(), ForeignKey('role.id'))
    # resource_id = Column(Integer(), ForeignKey('resource.id'))
    can_create = Column(Boolean, nullable=False)
    can_read = Column(Boolean, nullable=False)
    can_update = Column(Boolean, nullable=False)
    can_delete = Column(Boolean, nullable=False)

    def __repr__(self):
        return f'ResourceRole(id={self.id!r}, role_id={self.role_id!r}, resource_id={self.resource_id!r}, ' \
               f'can_create={self.can_create!r}, can_read={self.can_read!r}, can_update={self.can_update!r}, ' \
               f'can_delete={self.can_delete!r})'


Base.metadata.create_all(bind=engine)