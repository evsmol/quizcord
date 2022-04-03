import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ['DATABASE_URL']
VERSION = os.environ['VERSION']
BOT_ID = os.environ['BOT_ID']
BOT_TOKEN = os.environ['BOT_TOKEN']
