import sys
from dotenv import load_dotenv

from config import Config
from database.db_connection import DatabaseConnection

load_dotenv()

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def check_database_health():
    """Check database connection and basic table stats for MySQL/Oracle."""
    print("=" * 70)
    print("🔍 DATABASE HEALTH CHECK")
    print("=" * 70)

    connection = None
    cursor = None
    try:
        db_cfg = Config.get_db_config()
        engine = db_cfg.get('engine', 'mysql')
        db_conn = DatabaseConnection(db_cfg)

        connection = db_conn.get_connection()
        cursor = connection.cursor()

        db_label = db_cfg.get('database') if engine == 'mysql' else db_cfg.get('schema')
        print(f"\n✅ Connected to: {db_label}")
        print(f"Host: {db_cfg.get('host')}:{db_cfg.get('port')}\n")

        print("-" * 70)
        print("📋 TABLES IN DATABASE:")
        print("-" * 70)

        if engine == 'oracle':
            owner = db_cfg.get('schema', db_cfg.get('user', '')).upper()
            cursor.execute(
                """
                SELECT table_name
                FROM all_tables
                WHERE owner = :1
                ORDER BY table_name
                """,
                (owner,)
            )
            tables = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]

        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")

        print("\n" + "-" * 70)
        print("📊 ROW COUNTS:")
        print("-" * 70)

        for table in tables:
            if engine == 'oracle':
                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            else:
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            status = "✅" if count > 0 else "⚠️"
            print(f"  {status} {table}: {count:,} rows")

        print("\n" + "=" * 70)
        print("✅ DATABASE CHECK COMPLETE")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n❌ Database Error: {e}")
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("\n🔌 Connection closed")


if __name__ == "__main__":
    check_database_health()
