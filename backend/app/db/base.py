# Joins all models
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# NOTE: Models are imported in app.models.__init__.py to avoid circular imports
# Do NOT import models here!