
from app.database import engine
from app.models import Job, Candidate, ScreeningSession, ScreeningResult
from app.database import Base

try:
    Base.metadata.create_all(bind=engine)

    print("SQLAlchemy models loaded successfully!")
    print("Tables:", list(Base.metadata.tables.keys()))

except Exception as error:
    print("Model test failed:", error)
