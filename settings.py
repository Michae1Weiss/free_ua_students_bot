import os
import logging

import dotenv

dotenv.load_dotenv()

# Bot token
TOKEN = os.getenv("TOKEN")

# Database
DATABASE = "students.db"

# Other
LOGGING_LEVEL = logging.INFO
