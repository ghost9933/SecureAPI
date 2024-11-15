from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Database connection string (updated to point to ../data directory)
DATABASE_URL = "sqlite:///../data/phonebook.db"  # Ensure the path points to your database

# Setup SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def cleanup_database():
    """Deletes all records from the database tables."""
    # Start a new session
    session = SessionLocal()
    try:
        # Initialize MetaData and reflect tables
        meta = MetaData()
        meta.reflect(bind=engine)  # Reflect tables using the engine

        # Iterate through all tables in reverse order and delete their data
        with engine.connect() as conn:
            transaction = conn.begin()
            try:
                for table in reversed(meta.sorted_tables):
                    print(f"[INFO] Deleting all records from '{table.name}'")
                    conn.execute(table.delete())
                transaction.commit()
                print("[INFO] Database cleanup complete. All tables wiped.")
            except Exception as e:
                transaction.rollback()
                print(f"[ERROR] Failed to clean up the database: {e}")
    finally:
        # Close the session
        session.close()

def main():
    """Main function to invoke database cleanup."""
    cleanup_database()

if __name__ == "__main__":
    main()
