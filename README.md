# Chat
A FOSS Flask chatroom. It aims to be customizable without the need of modifying code.

## What can it do?
At the moment it is very limited. There is no persistence in messages. They get reset every time you reload/join.

Uses SQLAlchemy to store users and passwords. Uses [argon2](https://en.wikipedia.org/wiki/Argon2) to hash passwords.

## Features
 - [x] Send Messages
 - [x] Login with username (no password)
 - [x] Actually use passwords
 - [x] Persist Users
 - [ ] Persist chat?
 - [ ] Beautify chat
 - [ ] Emojis in chat
 - [ ] Edit account
 - [ ] Admin pages

## Contributing
You are welcome to open a PR to add functionality.
To edit or deploy, just open a venv and install the libraries in `requirements.txt`.
You can use `sqlite` as a mock db. Just enter the url in `.env` as `DATABASE_URI` and sqlalchemy should make the file for you.
Finally, run `python main.py`.