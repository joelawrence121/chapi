# CHessAPI (Work in progress)
## Overview 
Backend API for the Chexplanations project. Will serve data to chex-web. 

## Setup
1. Clone the repository.
2. Ensure you have an instance of MySQL configured and running.
3. Setup and run [chess-jenny](https://github.com/joelawrence121/chess-jenny) to populate database.
4. Copy your config.ini file from chess-jenny to the root directory.
```
[DB_CREDENTIALS]
host=localhost
user=root
password=password
```
4. Run chapi.py
