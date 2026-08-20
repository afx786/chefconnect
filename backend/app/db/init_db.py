"""Initialize the database: create tables and seed mock data.

Usage (from the backend/ directory):
    python -m app.db.init_db
"""

from app.db.database import Base, engine
from app.db.session import SessionLocal
from app.seed.seed_data import seed_database


def init_db() -> None:
    import app.models  # noqa: F401  (register all models on Base.metadata)

    Base.metadata.create_all(bind=engine)


def main() -> None:
    init_db()
    with SessionLocal() as session:
        seed_database(session)
    print("Database initialized and seeded.")


if __name__ == "__main__":
    main()