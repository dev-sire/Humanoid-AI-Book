"""
Apply database schema to Neon Postgres.
"""

import asyncio
import asyncpg
from pathlib import Path


async def apply_schema():
    """Apply the database schema."""
    # Database URL from .env
    database_url = "postgresql://neondb_owner:npg_sPr9m4yDvSXt@ep-fancy-credit-a4t7sk70-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

    # Read schema file
    schema_path = Path(__file__).parent.parent.parent / "specs" / "011-rag-chatbot-integration" / "contracts" / "database-schema.sql"

    print(f"Reading schema from: {schema_path}")
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    # Connect and apply schema
    print("Connecting to Neon Postgres...")
    conn = await asyncpg.connect(database_url)

    try:
        print("Checking existing tables...")
        existing_tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
        existing_table_names = [t['tablename'] for t in existing_tables]

        if 'chat_sessions' in existing_table_names and 'chat_messages' in existing_table_names:
            print("⚠️  Tables already exist. Skipping schema creation.")
            print(f"\nExisting tables:")
            for table in existing_table_names:
                print(f"  - {table}")
            return

        print("Applying database schema...")
        # Execute the entire schema as a transaction
        async with conn.transaction():
            await conn.execute(schema_sql)

        # Verify tables were created
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )

        print("\n✅ Schema applied successfully!")
        print(f"\nCreated tables:")
        for table in tables:
            print(f"  - {table['tablename']}")

    except Exception as e:
        print(f"\n❌ Error applying schema: {e}")
        print("\nTrying to check if tables exist anyway...")
        try:
            tables = await conn.fetch(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            )
            if tables:
                print(f"\nExisting tables:")
                for table in tables:
                    print(f"  - {table['tablename']}")
        except:
            pass
        raise
    finally:
        await conn.close()
        print("\nDatabase connection closed.")


if __name__ == "__main__":
    asyncio.run(apply_schema())
