from core.client import client
from core.config import BOT_TOKEN, VERSION, DATABASE_URL
from data import db_session


def main():
    print(f"[DATABASE] Database initialization")
    db_session.global_init(DATABASE_URL)

    print(f"[BOT] The bot version {VERSION} has been launched")
    print("[BOT] Connecting to Discord...")
    client.run(BOT_TOKEN)


if __name__ == '__main__':
    main()
