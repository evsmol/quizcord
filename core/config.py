import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ['DB_URL']
VERSION = os.environ['VERSION']
BOT_ID = os.environ['BOT_ID']
BOT_TOKEN = os.environ['BOT_TOKEN']
DEVELOPERS_ID = eval(os.environ['DEVELOPERS_ID'])
LOGS_CHANNEL = os.environ['LOGS_CHANNEL']
