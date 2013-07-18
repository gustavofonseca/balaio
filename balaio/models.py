# coding: utf-8
import datetime

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    String,
    Boolean,
)
from sqlalchemy.orm import (
    relationship,
    backref,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Session = sessionmaker()
Base = declarative_base()


def create_engine_from_config(config):
    """
    Create a sqlalchemy.engine using values from utils.Configuration.
    """
    return create_engine(config.get('app', 'db_dsn'),
                         echo=config.getboolean('app', 'debug'))


class Attempt(Base):
    __tablename__ = 'attempt'

    id = Column(Integer, primary_key=True)
    package_checksum = Column(String(length=32), unique=True)
    articlepkg_id = Column(Integer, ForeignKey('articlepkg.id'))
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime)
    collection_uri = Column(String)
    filepath = Column(String)
    is_valid = Column(Boolean)

    articlepkg = relationship('ArticlePkg',
                              backref=backref('attempts',
                              cascade='all, delete-orphan'))

    def __init__(self, *args, **kwargs):
        super(Attempt, self).__init__(*args, **kwargs)
        self.started_at = datetime.datetime.now()
        self.is_valid = True

    def __repr__(self):
        return "<Attempt('%s, %s')>" % (self.id, self.package_md5)


class ArticlePkg(Base):
    __tablename__ = 'articlepkg'

    id = Column(Integer, primary_key=True)
    article_title = Column(String, nullable=False)
    journal_pissn = Column(String, nullable=True)
    journal_eissn = Column(String, nullable=True)
    journal_title = Column(String, nullable=False)
    issue_year = Column(Integer, nullable=False)
    issue_volume = Column(Integer, nullable=False)
    issue_number = Column(Integer, nullable=False)

    def __repr__(self):
        return "<ArticlePkg('%s, %s')>" % (self.id, self.article_title)

