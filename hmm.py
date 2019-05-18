import os
from datetime import date

today = str(date.today())

file_log_name = 'log_AAPL.txt'

with open(file_log_name, 'r') as original: data = original.read()
with open(file_log_name, 'w') as modified: modified.write(today + ":" + len(dataset) "\n" + data)