import json
import signal
import sys
from kafka import KafkaConsumer
import psycopg
from colorama import Fore, Style, init

init(autoreset=True)

KAFKA_BOOTSTRAP = "localhost:29092"  # from your Docker compose
TOPIC = "migrationlab-sqlserver.AdventureWorksLite.dbo.Customers"

PG_CONN = {
    "host": "localhost",
    "port": 5432,
    "dbname": "migration_target",
    "user": "postgres",
    "password": "MigrationLab123!",
}

running = True


def shutdown(signum, frame):
    global running
    print(f"\n{Fore.YELLOW}Shutting down CDC applier...{Style.RESET_ALL}")
    running = False


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)


def apply_event(cur, payload):
    op = payload.get("op")
    after = payload.get("after")
    before = payload.get("before")

    # Debezium op codes: c=create, r=read (snapshot), u=update, d=delete
    if op in ("c", "r"):
        # Insert new row
        cur.execute(
            """
            INSERT INTO customers (customer_id, first_name, last_name, email, phone, created_date, modified_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (customer_id) DO UPDATE
              SET first_name = EXCLUDED.first_name,
                  last_name = EXCLUDED.last_name,
                  email = EXCLUDED.email,
                  phone = EXCLUDED.phone,
                  created_date = EXCLUDED.created_date,
                  modified_date = EXCLUDED.modified_date;
            """,
            (
                after["CustomerID"],
                after["FirstName"],
                after["LastName"],
                after.get("Email"),
                after.get("Phone"),
                after.get("CreatedDate"),
                after.get("ModifiedDate"),
            ),
        )
    elif op == "u":
        # Update existing row
        cur.execute(
            """
            UPDATE customers
               SET first_name = %s,
                   last_name = %s,
                   email = %s,
                   phone = %s,
                   created_date = %s,
                   modified_date = %s
             WHERE customer_id = %s;
            """,
            (
                after["FirstName"],
                after["LastName"],
                after.get("Email"),
                after.get("Phone"),
                after.get("CreatedDate"),
                after.get("ModifiedDate"),
                after["CustomerID"],
            ),
        )
    elif op == "d":
        # Delete row
        key_id = before["CustomerID"] if before else after["CustomerID"]
        cur.execute(
            "DELETE FROM customers WHERE customer_id = %s;",
            (key_id,),
        )


def main():
    print(f"{Fore.CYAN}Starting CDC applier for topic: {TOPIC}{Style.RESET_ALL}")

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=[KAFKA_BOOTSTRAP],
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        # NOTE: no group_id here – simpler on Windows
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    with psycopg.connect(**PG_CONN) as conn:
        with conn.cursor() as cur:
            try:
                for record in consumer:
                    payload = record.value.get("payload") if record.value else None
                    if not payload:
                        continue
                    apply_event(cur, payload)
                    conn.commit()
                    print(f"{Fore.GREEN}Applied 1 change to PostgreSQL{Style.RESET_ALL}")
                    if not running:
                        break
            finally:
                consumer.close()
                print(f"{Fore.CYAN}CDC applier stopped.{Style.RESET_ALL}")




if __name__ == "__main__":
    main()
