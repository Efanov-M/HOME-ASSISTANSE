import os
from dotenv import load_dotenv
import secrets

load_dotenv()



secret_key = secrets.token_urlsafe(32)