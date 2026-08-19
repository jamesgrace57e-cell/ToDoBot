# ToDoMateBot - Telegram Task Manager

A simple and efficient Telegram bot for managing your daily tasks and to-do lists.

## ✨ Features

- ➕ Add tasks with `/add [task]`
- 📋 View all tasks with `/list`
- ✅ Mark tasks as complete with `/complete [id]`
- 🗑️ Delete tasks with `/delete [id]`
- 🧹 Clear all completed tasks with `/clear`
- 💬 Interactive buttons for easy navigation

## 🚀 Deployment

### Prerequisites
- Python 3.8+
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

### Local Setup
1. Clone this repository
2. Create a `.env` file and add your `BOT_TOKEN`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python bot.py`

### Railway Deployment
1. Fork this repository to GitHub
2. Create an account on [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variable: `BOT_TOKEN` = your token
6. Railway will automatically deploy!

## 📝 Commands

| Command | Description |
|---------|-------------|
| `/start` | Show main menu |
| `/add [task]` | Add a new task |
| `/list` | Show all tasks |
| `/complete [id]` | Mark task as complete |
| `/delete [id]` | Delete a task |
| `/clear` | Delete all completed tasks |
| `/help` | Show help message |

## 🛠️ Technologies

- Python 3.11
- python-telegram-bot v20.7
- SQLite
- Railway for hosting

## 📄 License

MIT License - Feel free to use and modify!

## 👨‍💻 Author

Created with ❤️ for productivity enthusiasts
