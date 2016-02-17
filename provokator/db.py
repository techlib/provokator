#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

from sqlalchemy import *
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base

__all__ = ['reflect']


def reflect(engine):
    Base = declarative_base()
    metadata = MetaData(bind=engine)

    Table('dated_messages', metadata,
          Column('id', VARCHAR, primary_key=True),
          autoload=True)

    Table('monthly_counts', metadata,
          Column('year', INT, primary_key=True),
          Column('month', INT, primary_key=True),
          autoload=True)

    Table('daily_stats', metadata,
          Column('year', INT, primary_key=True),
          Column('month', INT, primary_key=True),
          Column('day', INT, primary_key=True),
          autoload=True)

    metadata.reflect(views=True)

    return metadata


# vim:set sw=4 ts=4 et:
