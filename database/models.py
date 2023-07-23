import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    """класс User, с информацией о пользователе Vkinder.
    ID_users - уникальный идентификатор,
    id - идентификатор пользователя ВК"""
    __tablename__ = 'User'

    ID_users = sq.Column(sq.Integer, primary_key=True)
    id = sq.Column(sq.Integer, unique=True)

    def __repr__(self):
        return f'{self.id} {self.ID_users}'


class Favorite(Base):
    """класс Objects, с полученными данными по запросу User-a.
    id - идентификатор пользователя ВК,
    ID_vk_users - идентификатор пользователя ВК таб User"""
    __tablename__ = 'favorite'

    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    ID_vk_users = sq.Column(sq.Integer, sq.ForeignKey('User.id'))

    ID_vk_user = relationship(User, backref="favorite")

    def __repr__(self):
        return f'{self.ID_object!r}, {self.id!r},'


class BlackList(Base):
    """Черный список пользователя.
    id - ид в VK пользователя ,
    ID_vk_users - вторичный ключ табл. Users"""
    __tablename__ = 'Black_list'

    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    ID_vk_users = sq.Column(sq.Integer, sq.ForeignKey('User.id'))

    ID_vk_user = relationship(User, backref="Black_list")

    def __repr__(self):
        return f'{self.id!r}, {self.ID_vk_users!r}'


class SettingSearch(Base):
    """Параметры поиска пользователя.
    ID - порядковый номер,
    id - ИД ВК из таб. User,
    age_from - нижняя граница возраста,
    age_to - верхняя граница возраста,
    hometown - родной город,
    sex - пол,
    status - статус (в активном поиске, холост и т.д.),
    offset - номер последнего просмотра"""
    __tablename__ = 'Setting_search'

    ID = sq.Column(sq.Integer, primary_key=True)
    id = sq.Column(sq.Integer, sq.ForeignKey('User.id'))
    age_from = sq.Column(sq.Integer, sq.CheckConstraint('1 < age_from' and 'age_from < 100'))
    age_to = sq.Column(sq.Integer, sq.CheckConstraint('1 < age_to' and 'age_to < 100'))
    sex = sq.Column(sq.Integer, sq.CheckConstraint('0 < sex' and 'sex < 3'))
    hometown = sq.Column(sq.String(length=30))
    status = sq.Column(sq.Integer, sq.CheckConstraint('0 <= status' and 'status <= 8'))
    offset = sq.Column(sq.Integer, default=1)

    id_ = relationship(User, backref="Setting_search")

    def __repr__(self):
        return f'{self.ID!r}, {self.id!r}, {self.age_from!r}, ' \
               f'{self.age_to!r}, {self.hometown!r}, {self.status!r}, ' \
               f'{self.offset!r}, {self.sex!r}'


def create_tables(engine):
    """Создаем Таблицы"""
    Base.metadata.create_all(engine)


def drop_tables(engine):
    """Удаляем Таблицы"""
    Base.metadata.drop_all(engine)
