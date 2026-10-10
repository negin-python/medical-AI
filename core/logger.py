import logging 
from pathlib import Path


#make log directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

#make logger
logger = logging.getLogger("medical_api")
logger.setLevel(logging.INFO)

#Preventing duplicate message logging
logger.propagate = False

#messages format
formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(name)s|%(message)s")

#show log in terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

#save log in file
file_handler = logging.FileHandler(
    LOG_DIR/"medical_api.log",
    encoding="utf_8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

#connecting handlers to logger
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

