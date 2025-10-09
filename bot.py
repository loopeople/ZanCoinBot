# bot.py
import os
import logging
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from deep_translator import GoogleTranslator

# ---------- Logging ----------
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Supported languages (display name, code) ----------
LANG_CHOICES = [
    ("English", "en"),
    ("Türkçe", "tr"),
    ("العربية", "ar"),
    ("Español", "es"),
    ("Français", "fr"),
    ("Deutsch", "de"),
    ("Русский", "ru"),
    ("فارسی", "fa"),
    ("हिन्दी", "hi"),
    ("اردو", "ur"),
]
SUPPORTED_CODES = {code for _, code in LANG_CHOICES}


# ---------- Translation helper ----------
def translate_text(text: str, target_lang: str) -> str:
    try:
        if not target_lang or target_lang == "en":
            return text
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        logger.exception("Translation failed, returning original text. Error: %s", e)
        return text


def normalize_lang_code(code: str) -> str:
    if not code:
        return "en"
    code = code.lower()
    if "-" in code:
        code = code.split("-")[0]
    if code in SUPPORTED_CODES:
        return code
    if len(code) >= 2 and code[:2] in SUPPORTED_CODES:
        return code[:2]
    return "en"


# ---------- Keyboard builder ----------
def build_keyboard(buttons_config, lang_code: str):
    kb = []
    for row in buttons_config:
        kb_row = []
        for btn in row:
            label_en = btn.get("text", "")
            label = translate_text(label_en, lang_code)
            if btn.get("url"):
                kb_row.append(InlineKeyboardButton(label, url=btn["url"]))
            else:
                kb_row.append(InlineKeyboardButton(label, callback_data=btn.get("callback")))
        kb.append(kb_row)
    return InlineKeyboardMarkup(kb)


# ---------- Helpers to get user's language ----------
def get_user_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    lang = context.user_data.get("lang")
    if lang:
        return lang
    tg_code = getattr(update.effective_user, "language_code", None)
    return normalize_lang_code(tg_code)


async def send_translated(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, buttons_config=None):
    user_lang = get_user_lang(update, context)
    translated_text = translate_text(text, user_lang)
    if update.callback_query:
        try:
            await update.callback_query.answer()
        except Exception:
            pass
        if buttons_config:
            markup = build_keyboard(buttons_config, user_lang)
            await update.callback_query.edit_message_text(translated_text, reply_markup=markup)
        else:
            await update.callback_query.edit_message_text(translated_text)
    else:
        if buttons_config:
            markup = build_keyboard(buttons_config, user_lang)
            await update.message.reply_text(translated_text, reply_markup=markup)
        else:
            await update.message.reply_text(translated_text)


# ---------- Menu / Content (English originals) ----------
MAIN_MENU_TEXT = "👋 Welcome! Please choose an option below:"
WHAT_IS_PROMPT = "Choose an option below:"
EXPLAIN_TEXT = (
    "🔹 IN SUMMARY:\n\n"
    "Zan Coin is the first crypto project aiming to create coins with unique identity numbers, "
    "similar to banknotes and NFTs. The presale has started.\n\n"
    "When you send USDT to create Zan Coin, our system generates two unique IDs and assigns them to you. "
    "You receive 1 ZanCoin immediately. To get the second one, click the WhatsApp share button. "
    "After both are activated, ZC Network Marketing and ZC Game become available in your profile."
)
NETWORK_TEXT = (
    "💼 ZC Network Marketing\n\n"
    "To move our project to the next step, we aim to reach 25,000 members. "
    "Instead of spending our marketing budget on ads, we give it to you!\n\n"
    "In the Network Marketing section, you’ll find your unique referral link. "
    "For every user who registers and creates a Zan Coin through your link, you earn $25 instantly."
)
GAME_TEXT = (
    "🎮 ZC Game\n\n"
    "Compete with other users to achieve the highest score and win $500. "
    "The game resets every ~2–3 weeks at a random time. The user at the top when it resets wins the reward.\n\n"
    "If you win, we’ll email your registered address and request a wallet number to send your reward."
)
EARN_TEXT = (
    "💰 HOW CAN I EARN?\n\n"
    "You can sell your Zan Coins once they are listed on crypto exchanges. "
    "Additionally, you can earn instantly through ZC Network Marketing and ZC Game, and withdraw your money."
)


# ---------- Button configs (English labels & callback/url) ----------
def main_menu_buttons():
    return [
        [
            {"text": "Register", "callback": "register"},
            {"text": "Login", "callback": "login"},
        ],
        [
            {"text": "What is ZanCoin?", "callback": "what_is"},
        ],
        [
            {"text": "How can I earn?", "callback": "earn"},
        ],
        [
            {"text": "Support Email", "url": "mailto:support@zancoinmint.com"},
        ],
        [
            {"text": "Change Language", "callback": "change_lang"},
        ],
    ]


def what_is_buttons():
    return [
        [
            {"text": "Visit Website", "url": "https://zancoinmint.com"},
        ],
        [
            {"text": "Tell me about it", "callback": "explain"},
        ],
        [
            {"text": "Back", "callback": "back_main"},
        ],
    ]


def explain_buttons():
    share_msg = urllib.parse.quote_plus("I joined ZanCoin! Create your ZanCoin now: https://zancoinmint.com")
    whatsapp_url = f"https://wa.me/?text={share_msg}"
    return [
        [
            {"text": "ZC Network Marketing", "callback": "network"},
            {"text": "ZC Game", "callback": "game"},
        ],
        [
            {"text": "Share on WhatsApp", "url": whatsapp_url},
        ],
        [
            {"text": "Register", "callback": "register"},
            {"text": "Login", "callback": "login"},
        ],
        [
            {"text": "Back", "callback": "back_main"},
        ],
    ]


def network_buttons():
    return [
        [
            {"text": "Learn about ZC Game", "callback": "game"},
        ],
        [
            {"text": "Back", "callback": "explain"},
        ],
    ]


def game_buttons():
    return [
        [
            {"text": "Back", "callback": "explain"},
        ],
    ]


def earn_buttons():
    return [
        [
            {"text": "Back", "callback": "back_main"},
        ],
    ]


def register_buttons():
    return [
        [
            {"text": "Go to Registration", "url": "https://zancoinmint.com/panel/dist/auth-register.php"},
        ],
        [
            {"text": "Back", "callback": "back_main"},
        ],
    ]


def login_buttons():
    return [
        [
            {"text": "Go to Login", "url": "https://zancoinmint.com/panel/dist/auth-login.html"},
        ],
        [
            {"text": "Back", "callback": "back_main"},
        ],
    ]


# ---------- Language selection UI ----------
def language_selection_buttons():
    rows = []
    row = []
    for i, (name, code) in enumerate(LANG_CHOICES):
        row.append({"text": name, "callback": f"setlang_{code}"})
        if (i % 2) == 1:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    # add back button
    rows.append([{"text": "Back", "callback": "back_main"}])
    return rows


# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "lang" not in context.user_data:
        detected = getattr(update.effective_user, "language_code", None)
        context.user_data["lang"] = normalize_lang_code(detected)
    await send_translated(update, context, MAIN_MENU_TEXT, main_menu_buttons())


async def what_is(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_translated(update, context, WHAT_IS_PROMPT, what_is_buttons())


async def explain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_translated(update, context, EXPLAIN_TEXT, explain_buttons())


async def network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_translated(update, context, NETWORK_TEXT, network_buttons())


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_translated(update, context, GAME_TEXT, game_buttons())


async def earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_translated(update, context, EARN_TEXT, earn_buttons())


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_translated(update, context, "🌐 Redirecting to registration page...", register_buttons())


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_translated(update, context, "🔐 Redirecting to login page...", login_buttons())


async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_translated(update, context, "What would you like to do next?", main_menu_buttons())


async def change_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_translated(update, context, "Please choose your language:", language_selection_buttons())


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data if update.callback_query else ""
    if not data.startswith("setlang_"):
        await update.callback_query.answer()
        return
    code = data.split("_", 1)[1]
    if code not in SUPPORTED_CODES:
        code = "en"
    context.user_data["lang"] = code
    confirm_en = f"✅ Language set to {code}. Returning to main menu..."
    translated = translate_text(confirm_en, code)
    try:
        await update.callback_query.answer(text=translated, show_alert=False)
    except Exception:
        pass
    # After setting language, show main menu (translated)
    await send_translated(update, context, MAIN_MENU_TEXT, main_menu_buttons())


# ---------- Error handler ----------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Exception while handling an update: %s", context.error)
    # optional: notify user
    try:
        if isinstance(update, Update) and update.effective_user:
            lang = get_user_lang(update, context)
            msg = translate_text("⚠️ An error occurred. Please try again later.", lang)
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.message.reply_text(msg)
            elif update.message:
                await update.message.reply_text(msg)
    except Exception:
        pass


# ---------- Main ----------
def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN environment variable is required")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(what_is, pattern="^what_is$"))
    app.add_handler(CallbackQueryHandler(explain, pattern="^explain$"))
    app.add_handler(CallbackQueryHandler(network, pattern="^network$"))
    app.add_handler(CallbackQueryHandler(game, pattern="^game$"))
    app.add_handler(CallbackQueryHandler(earn, pattern="^earn$"))
    app.add_handler(CallbackQueryHandler(register, pattern="^register$"))
    app.add_handler(CallbackQueryHandler(login, pattern="^login$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(change_lang, pattern="^change_lang$"))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^setlang_"))
    app.add_error_handler(error_handler)

    logger.info("Starting ZanCoin Bot (polling)...")
    app.run_polling()


if __name__ == "__main__":
    main()
