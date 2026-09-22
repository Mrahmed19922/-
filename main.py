import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

# ------------------- الإعدادات الرئيسية -------------------
MAIN_TOKEN = "6941144530:AAEDOz4PVOXmFv9n_rCS5Sx8EpkFpkGj4QE"

# معرف القناة ورابطها للاشتراك الإجباري
CHANNEL_USERNAME = "@on1mix"
CHANNEL_LINK = "https://t.me/on1mix"

# حقوق البوت
RIGHTS_NAME = "👑 مستر أحمد | ON.Mix"
RIGHTS = f"\n\n—\n{RIGHTS_NAME}"

WAITING_FOR_TOKEN = 1

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ------------------- فحص الاشتراك الإجباري -------------------
async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        return True

async def send_sub_request(update: Update):
    keyboard = [
        [InlineKeyboardButton("📢 اشترك في قناة ON.Mix", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"⚠️ **عذراً يا صديقي!**\n\nيجب عليك الاشتراك في قناة البوت أولاً لاستخدام الخدمات:\n{CHANNEL_LINK}{RIGHTS}"
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ------------------- القوائم والأوامر القديمة الكاملة -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # فحص الاشتراك الإجباري أولاً
    is_subscribed = await check_subscription(user.id, context)
    if not is_subscribed:
        await send_sub_request(update)
        return

    # القائمة الرئيسية القديمة بأزرارها
    user_keyboard = [
        ["🤖 صنع بوت جديد", "📋 قائمة بوتاتك"],
        ["❓ كيف اصنع بوت؟"]
    ]
    reply_markup = ReplyKeyboardMarkup(user_keyboard, resize_keyboard=True)

    message_text = (
        f"أهلاً بك يا {user.first_name} 👋\n\n"
        f"مرحباً بك في أحدث بوتات شبكة {RIGHTS_NAME} 🚀\n"
        f"اختر من القائمة أدناه ما تريد القيام به👇"
    )
    await update.message.reply_text(text=message_text, reply_markup=reply_markup)

async def how_to_make_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    explanation_text = (
        f"📖 **شرح كيفية عمل بوت جديد عبر BotFather:**\n\n"
        f"1️⃣ اذهب إلى بوت @BotFather\n"
        f"2️⃣ أرسل الأمر `/newbot`\n"
        f"3️⃣ أدخل اسمًا للبوت الخاص بك\n"
        f"4️⃣ أدخل معرفًا (Username) ينتهي بـ `bot`\n"
        f"5️⃣ سيمنحك BotFather **توكن (Token)** خاصاً بك\n"
        f"6️⃣ انسخ التوكن وأرسله هنا عند الضغط على 'صنع بوت جديد'{RIGHTS}"
    )
    await update.message.reply_text(explanation_text, parse_mode='Markdown')

async def ask_for_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"من فضلك أرسل التوكن الخاص بـ بوتك الآن:\nمثال: `123456789:ABCdefGhIJKlmNoPQRsT`",
        parse_mode="Markdown"
    )
    return WAITING_FOR_TOKEN

async def receive_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_token = update.message.text.strip()
    if ":" not in user_token or len(user_token) < 20:
        await update.message.reply_text("❌ التوكن غير صحيح، تأكد منه وأرسله مجدداً.")
        return WAITING_FOR_TOKEN
    
    with open("user_bots.txt", "a") as f:
        f.write(f"{update.effective_user.id}:{user_token}\n")

    await update.message.reply_text(f"✅ تم حفظ التوكن بنجاح! جاري تشغيل بوتك...{RIGHTS}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(MAIN_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🤖 صنع بوت جديد$"), ask_for_token)],
        states={
            WAITING_FOR_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_token)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^❓ كيف اصنع بوت؟$"), how_to_make_bot))
    app.add_handler(conv_handler)

    print("البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()
