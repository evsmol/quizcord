from core.client import client
from core.config import token, version

print(f"[BOT] The bot version {version} has been launched")
print("[BOT] Connecting to Discord...")
client.run(token)
