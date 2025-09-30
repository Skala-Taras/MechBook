# Joins all models
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import wszystkich modeli, aby SQLAlchemy wiedział o nich przy create_all()
from app.models.mechanics import Mechanics  # noqa
from app.models.clients import Clients  # noqa
from app.models.vehicles import Vehicles  # noqa
from app.models.repairs import Repairs  # noqa
from app.models.password_reset_tokens import PasswordResetTokens  # noqa