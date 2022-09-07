# UA students assistant bot 🇺🇦

This bot sends users links to tweets that need to be commented on.</br></br>
#freeUaStudents</br>
#freeUkrainianStudents

## Features:
* **python-telegram-bot** - pure Python, asynchronous interface for the Telegram Bot API.
  * [GitHub repo](https://github.com/python-telegram-bot/python-telegram-bot)
* **PeeWee** - simple and small ORM
  * [GitHub repo](https://github.com/coleifer/peewee/blob/master/docs/index.rst)

## How to:

1. Create virtual environment
    ```bash
    # creates `venv` directory
    $ python3 -m venv venv
    ```

2. Activate virtual environment
   ```bash
   # activates virtual environment
   $ source venv/bin/activate
   ```

3. Install python dependencies
   ```bash
   # install dependencies from `requirements.txt` file
   $ pip install -r requirements
   ```

4. Create `.env` file from example and edit it
   ```bash
   # make copy of `.env_example` and save it as `.env` 
   $ cp .env_example .env
   # open editor and edit `.env` ... Example:
   $ nano .env  # use your favorite text editor
   ```
   
5. Start script to run bot:
   ```bash
   # run main script
   $ python bot.py
   ```
