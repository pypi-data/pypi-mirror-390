============
sqlamixin
============

.. code-block:: python

   from flask_sqlalchemy import SQLAlchemy
   from sqlalchemy.orm import DeclarativeBase
   
   from python_plugins.models.mixins import PrimaryKeyMixin
   from python_plugins.models.mixins import UserMixin
   from python_plugins.models.mixins import DataMixin
   from python_plugins.models.mixins import TimestampMixin

   class Base(DeclarativeBase):
      pass

   db = SQLAlchemy(model_class=Base)

   class User(db.Model,PrimaryKeyMixin, DataMixin, TimestampMixin, UserMixin):
      __tablename__ = "users"