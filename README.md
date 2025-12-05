# 🤖 Telegram WeatherBot

What's the weather like where you live? 🌈
Find the answer here 😉

[Go To Telegram Bot](https://t.me/Kysiolena_WeatherBot)

![Bot Start](/images/bot-1.jpg)
![Bot Empty Places](/images/bot-2.jpg)
![Bot Add to Favorite](/images/bot-3.jpg)
![Bot Error Place name](/images/bot-4.jpg)
![Bot Select Place](/images/bot-5.jpg)
![Bot Rename, Delete place](/images/bot-6.jpg)

## 🔧 Setup project

1. Create a virtual environment and activate it

    ```terminaloutput
    py -m venv .venv
    source .venv/Scripts/activate
    ```

2. Install the required package from ``requirements.txt``
    ```terminaloutput
   pip install -r requirements.txt
   ```
3. Export the required environment variables listed in the ``.env.example`` file to the virtual environment
    ```terminaloutput
   export VARIABLE_NAME="value"
   ```
4. Run project
    ```terminaloutput
   py main.py
   ```
5. Run tests
    ```terminaloutput
   coverage run -m pytest
   ```
6. Create tests ``coverage`` html or report
    ```terminaloutput
   coverage html
   coverage report
   ```

## ✅ Checklist 🎉

1. [x] Start Handler
2. [x] Location Handler
3. [x] Create and Delete User Handlers
4. [x] Favorite Locations (CRUD)
5. [x] Middleware for DB connect
6. [x] Middleware for checking User Authentication
7. [x] Errors handling
8. [x] Tests (using Gemini)
