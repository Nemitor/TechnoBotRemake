import os
import logging
import datetime

log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

current_date = datetime.date.today()

formatted_date = current_date.strftime("%d.%m.%Y")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(f'{log_dir}/{current_date}.log')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
