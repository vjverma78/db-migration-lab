import oracledb

CONFIG = {
    "host": "localhost",
    "port": 1521,
    "service": "XEPDB1",        # adjust if your Oracle XE service name is different
    "user": "system",
    "password": "MigrationLab123!",
}

def main():
    dsn = oracledb.makedsn(
        CONFIG["host"],
        CONFIG["port"],
        service_name=CONFIG["service"],
    )

    conn = oracledb.connect(
        user=CONFIG["user"],
        password=CONFIG["password"],
        dsn=dsn,
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM v$version WHERE banner LIKE 'Oracle%'")
    row = cur.fetchone()
    print("✓ Oracle: Connected successfully")
    print("  Version:", row[0])

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
