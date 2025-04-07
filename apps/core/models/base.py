from sqlalchemy.ext.declarative import declarative_base
from my_django_project_001.config.database import engine

Base = declarative_base()

# Bind engine to Base for all models
Base.metadata.bind = engine
