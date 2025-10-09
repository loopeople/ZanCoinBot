import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from deep_translator import GoogleTranslator
from aiohttp import web

# ---------- Logging ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------- Translation Helper ----------
def translate_text(text, target_lang):
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception:
        return text

# ---------- Send Translated Text ----------
async def send_translated(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, buttons=None):
    user_lang = update.effective_user.language_code or "en"
    translated_text = translate_text(text, user_lang)
    if update.message:
        await update.message.reply_text(
            translated_text,
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )
    else:
        await update.callback_query.message.edit_text(
            translated_text,
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )

# ---------- Start / Main Menu ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "👋 Welcome! Please choose an option below:"
    buttons = [
        [
            InlineKeyboardButton("🧑‍💻 Register", callback_data="register"),
            InlineKeyboardButton("🔑 Login", callback_data="login"),
        ],
        [
            InlineKeyboardButton("💰 What is ZanCoin?", callback_data="what_is"),
        ],
        [
            InlineKeyboardButton("💵 How can I earn?", callback_data="earn"),
        ],
        [
            InlineKeyboardButton("📧 Support Email", url="mailto:support@zancoinmint.com"),
        ],
    ]
    await send_translated(update, context, text, buttons)

# ---------- ZanCoin Overview ----------
async def what_is(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Choose an option below:"
    buttons = [
        [
            InlineKeyboardButton("🎬 Visit Website", url="https://zancoinmint.com"),
        ],
        [
            InlineKeyboardButton("🗣️ Tell me about it", callback_data="explain"),
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="back_main"),
        ],
    ]
    await send_translated(update, context, text, buttons)

# ---------- ZanCoin Detailed Explanation ----------
async def explain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔹 **In summary:**\n\n"
        "Zan Coin is the first crypto project aiming to create coins with unique identity numbers, "
        "similar to banknotes and NFTs. The presale has started.\n\n"
        "When you send USDT to create Zan Coin, our system generates two unique IDs and assigns them to you. "
        "You receive 1 ZanCoin immediately. To get the second one, click the WhatsApp share button. "
        "After both are activated, ZC Network Marketing and ZC Game become available in your profile."
    )
    buttons = [
        [
            InlineKeyboardButton("🌐 ZC Network Marketing", callback_data="network"),
            InlineKeyboardButton("🎮 ZC Game", callback_data="game"),
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="what_is"),
        ],
    ]
    await send_translated(update, context, text, buttons)

# ---------- ZC Network Marketing ----------
async def network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💼 **ZC Network Marketing**\n\n"
        "To move our project to the next step, we aim to reach 25,000 members. "
        "Instead of spending our marketing budget on ads, we give it to you!\n\n"
        "In the Network Marketing section, you’ll find your unique referral link. "
        "For every user who registers and creates a Zan Coin through your link, you earn **$25 instantly**. "
        "This way, great earnings await you."
    )
    buttons = [
        [
            InlineKeyboardButton("🎮 Learn about ZC Game", callback_data="game"),
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="explain"),
        ],
    ]
    await send_translated(update, context, text, buttons)

# ---------- ZC Game ----------
async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎮 **ZC Game**\n\n"
        "Compete with other users to achieve the highest score and win **$500**. "
        "The game resets every 2–3 weeks randomly. The user at the top of the leaderboard when it resets wins the reward.\n\n"
        "If you win, we’ll send an email to your registered address to collect your wallet number for the reward. "
        "Good luck and have fun!"
    )
    buttons = [
        [
            InlineKeyboardButton("🔙 Back", callback_data="explain"),
        ],
    ]
    await send_translated(update, context, text, buttons)

# ---------- How to Earn ----------
async def earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💰 **How can I earn?**\n\n"
        "You can sell your Zan Coins once they are listed on crypto exchanges. "
        "Additionally, you can earn instantly through **ZC Network Marketing** and **ZC Game**, "
        "and withdraw your money immediately."
    )
    buttons = [
        [
            InlineKeyboardButton("🔙 Back", callback_data="back_main"),
        ],
    ]
    await send_translated(update, context, text, buttons)

# ---------- Back to Main ----------
async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "What would you like to do next?"
    buttons = [
        [
            InlineKeyboardButton("🧑‍💻 Register", callback_data="register"),
            InlineKeyboardButton("🔑 Login", callback_data="login"),
        ],
        [
            InlineKeyboardButton("🏠 Back to Start", callback_data="start"),
        ],
    ]
    await send_translated(update, context, text, buttons)

# ---------- Register / Login ----------
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🌐 Redirecting to registration page..."
    buttons = [
        [InlineKeyboardButton("🧾 Go to Registration", url="https://zancoinmint.com/panel/dist/auth-register.php")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ]
    await send_translated(update, context, text, buttons)

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔐 Redirecting to login page..."
    buttons = [
        [InlineKeyboardButton("🔑 Go to Login", url="https://zancoinmint.com/panel/dist/auth-login.html")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ]
    await send_translated(update, context, text, buttons)

# ---------- Main ----------
async def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    APP_URL = os.getenv("APP_URL")  # Render public URL
    
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(what_is, pattern="^what_is$"))
    app.add_handler(CallbackQueryHandler(explain, pattern="^explain$"))
    app.add_handler(CallbackQueryHandler(network, pattern="^network$"))
    app.add_handler(CallbackQueryHandler(game, pattern="^game$"))
    app.add_handler(CallbackQueryHandler(earn, pattern="^earn$"))
    app.add_handler(CallbackQueryHandler(register, pattern="^register$"))
    app.add_handler(CallbackQueryHandler(login, pattern="^login$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(start, pattern="^start$"))

    # Set webhook
    await app.bot.set_webhook(f"{APP_URL}/webhook/{TOKEN}")

    # Run aiohttp server for webhook
    async def handle(request):
        update = Update.de_json(await request.json(), app.bot)
        await app.update_queue.put(update)
        return web.Response(text="ok")

    web_app = web.Application()
    web_app.router.add_post(f"/webhook/{TOKEN}", handle)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 10000)))
    await site.start()
    print("Webhook running...")
    await app.run_polling()  # Only keeps app alive

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
