import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ['DATABASE_URL']
version = os.environ['VERSION']
bot_id = os.environ['BOT_ID']
token = os.environ['BOT_TOKEN']
