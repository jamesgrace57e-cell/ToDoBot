import os
import asyncio
import logging
import sqlite3
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # You'll set this in Railway

if not TOKEN:
    logger.error("No BOT_TOKEN found!")
    raise ValueError("No BOT_TOKEN found!")

# Database setup
def init_db():
    try:
        conn = sqlite3.connect("todo.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tasks
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      task TEXT,
                      completed INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

def add_task(user_id, task):
    try:
        conn = sqlite3.connect("todo.db")
        c = conn.cursor()
        c.execute("INSERT INTO tasks (user_id, task) VALUES (?, ?)", (user_id, task))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        return False

def get_tasks(user_id):
    try:
        conn = sqlite3.connect("todo.db")
        c = conn.cursor()
        c.execute("SELECT id, task, completed FROM tasks WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        tasks = c.fetchall()
        conn.close()
        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return []

def complete_task(user_id, task_id):
    try:
        conn = sqlite3.connect("todo.db")
        c = conn.cursor()
        c.execute("UPDATE tasks SET completed = 1 WHERE id = ? AND user_id = ?", (task_id, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return False

def delete_task(user_id, task_id):
    try:
        conn = sqlite3.connect("todo.db")
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return False

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Add Task", callback_data="add")],
        [InlineKeyboardButton("📋 My Tasks", callback_data="list")],
        [InlineKeyboardButton("✅ Complete Task", callback_data="complete")],
        [InlineKeyboardButton("🗑️ Delete Task", callback_data="delete")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎯 *Welcome to ToDoMateBot!*\n\n"
        "I'll help you manage your tasks efficiently.\n"
        "Choose an option below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "*📖 Available Commands:*\n\n"
        "/start - Show main menu\n"
        "/add [task] - Add a new task\n"
        "/list - Show all tasks\n"
        "/complete [id] - Mark task as complete\n"
        "/delete [id] - Delete a task\n"
        "/clear - Delete all completed tasks\n"
        "/help - Show this help message\n\n"
        "*Example:*\n"
        "/add Buy groceries\n"
        "/complete 1\n"
        "/delete 2"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Add task command
async def add_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please provide a task.\nExample: `/add Buy groceries`", parse_mode="Markdown")
        return

    task = " ".join(context.args)
    user_id = update.effective_user.id

    if add_task(user_id, task):
        await update.message.reply_text(f"✅ Task added successfully!\n\n📝 *{task}*", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Failed to add task. Please try again.")

# List tasks command
async def list_tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = get_tasks(user_id)

    if not tasks:
        await update.message.reply_text("🎉 No tasks found! Your to-do list is empty.")
        return

    active_tasks = [t for t in tasks if t[2] == 0]
    completed_tasks = [t for t in tasks if t[2] == 1]

    message = "*📋 Your Tasks:*\n\n"

    if active_tasks:
        message += "*Active Tasks:*\n"
        for task in active_tasks:
            message += f"`{task[0]}`. {task[1]}\n"
    else:
        message += "✅ No active tasks.\n"

    if completed_tasks:
        message += f"\n*Completed Tasks:* ({len(completed_tasks)})\n"
        for task in completed_tasks[:5]:
            message += f"`{task[0]}`. ~~{task[1]}~~\n"
        if len(completed_tasks) > 5:
            message += f"... and {len(completed_tasks) - 5} more\n"

    await update.message.reply_text(message, parse_mode="Markdown")

# Complete task command
async def complete_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please provide the task ID.\nExample: `/complete 1`", parse_mode="Markdown")
        return

    try:
        task_id = int(context.args[0])
        user_id = update.effective_user.id
        if complete_task(user_id, task_id):
            await update.message.reply_text(f"✅ Task #{task_id} marked as complete!")
        else:
            await update.message.reply_text(f"❌ Task #{task_id} not found or already completed.")
    except ValueError:
        await update.message.reply_text("⚠️ Please provide a valid task ID (number).")

# Delete task command
async def delete_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please provide the task ID.\nExample: `/delete 1`", parse_mode="Markdown")
        return

    try:
        task_id = int(context.args[0])
        user_id = update.effective_user.id
        if delete_task(user_id, task_id):
            await update.message.reply_text(f"🗑️ Task #{task_id} deleted successfully!")
        else:
            await update.message.reply_text(f"❌ Task #{task_id} not found.")
    except ValueError:
        await update.message.reply_text("⚠️ Please provide a valid task ID (number).")

# Clear completed tasks
async def clear_tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE user_id = ? AND completed = 1", (user_id,))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    await update.message.reply_text(f"🗑️ {deleted} completed task(s) cleared!")

# Button callback handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add":
        await query.edit_message_text(
            "📝 *Add a Task*\n\n"
            "Send a message with:\n`/add [your task]`\n\n"
            "Example: `/add Buy milk`",
            parse_mode="Markdown"
        )
    elif query.data == "list":
        user_id = update.effective_user.id
        tasks = get_tasks(user_id)

        if not tasks:
            await query.edit_message_text("🎉 No tasks found! Your to-do list is empty.")
            return

        active_tasks = [t for t in tasks if t[2] == 0]
        message = "*📋 Your Tasks:*\n\n"

        if active_tasks:
            for task in active_tasks:
                message += f"`{task[0]}`. {task[1]}\n"
        else:
            message += "✅ No active tasks."

        await query.edit_message_text(message, parse_mode="Markdown")
    elif query.data == "complete":
        await query.edit_message_text(
            "✅ *Complete a Task*\n\n"
            "Send a message with:\n`/complete [task ID]`\n\n"
            "Example: `/complete 1`",
            parse_mode="Markdown"
        )
    elif query.data == "delete":
        await query.edit_message_text(
            "🗑️ *Delete a Task*\n\n"
            "Send a message with:\n`/delete [task ID]`\n\n"
            "Example: `/delete 1`",
            parse_mode="Markdown"
        )
    elif query.data == "help":
        await query.edit_message_text(
            "*📖 Available Commands:*\n\n"
            "/start - Show main menu\n"
            "/add [task] - Add a new task\n"
            "/list - Show all tasks\n"
            "/complete [id] - Mark task as complete\n"
            "/delete [id] - Delete a task\n"
            "/clear - Delete all completed tasks\n"
            "/help - Show this help message",
            parse_mode="Markdown"
        )

# Flask app for webhook
app = Flask(__name__)

# Initialize bot application
application = Application.builder().token(TOKEN).build()

# Add command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("add", add_task_command))
application.add_handler(CommandHandler("list", list_tasks_command))
application.add_handler(CommandHandler("complete", complete_task_command))
application.add_handler(CommandHandler("delete", delete_task_command))
application.add_handler(CommandHandler("clear", clear_tasks_command))
application.add_handler(CallbackQueryHandler(button_callback))


@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming updates"""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
        return '', 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return '', 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return 'OK', 200


async def setup_bot():
    """Initialize the bot and register the webhook with Telegram"""
    await application.initialize()
    await application.start()

    if WEBHOOK_URL:
        webhook_full_url = f"{WEBHOOK_URL}/webhook"
        logger.info(f"Setting webhook to: {webhook_full_url}")
        await application.bot.set_webhook(url=webhook_full_url)
    else:
        logger.warning("WEBHOOK_URL not set! Bot will work but webhook won't be configured.")


def main():
    try:
        init_db()

        # Run async setup (initialize application + register webhook) before Flask starts
        asyncio.run(setup_bot())

        # Start Flask server
        logger.info(f"🤖 Bot is starting on port {PORT}...")
        app.run(host='0.0.0.0', port=PORT)

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    main()
