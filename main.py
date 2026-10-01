import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

# ------------------- الإعدادات الرئيسية -------------------
MAIN_TOKEN = "6941144530:AAEDOz4PVOXmFv9n_rCS5Sx8EpkFpkGj4QE"

CHANNEL_USERNAME = "@on1mix"
CHANNEL_LINK = "https://t.me/on1mix"

RIGHTS_NAME = "👑 مستر أحمد | ON.Mix"
RIGHTS = f"\n\n—\n{RIGHTS_NAME}"

WAITING_FOR_TOKEN = 1

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# تخزين البوتات المشغلة في الذاكرة
RUNNING_BOTS = {}

# ------------------- قوائم قوالب البوتات (5 صفحات) -------------------
TEMPLATES_PAGES = {
    1: [
        [InlineKeyboardButton("تواصل (شغال ✅)", callback_data="tpl_contact")],
        [InlineKeyboardButton("بوت الازرار (شغال ✅)", callback_data="tpl_buttons")],
        [InlineKeyboardButton("زخرفة (شغال ✅)", callback_data="tpl_zakhrafa")],
        [InlineKeyboardButton("معاني اسماء (شغال ✅)", callback_data="tpl_names")],
        [InlineKeyboardButton("تحويل صيغ", callback_data="tpl_convert")],
        [InlineKeyboardButton("استخراج روابط القنوات", callback_data="tpl_extract")],
        [InlineKeyboardButton("ناسخ الكتابة", callback_data="tpl_copy")],
        [InlineKeyboardButton("➡️️ الصفحة التالية", callback_data="page_2")]
    ],
    2: [
        [InlineKeyboardButton("سمسمي", callback_data="tpl_simsimi")],
        [InlineKeyboardButton("تحقق من الوهمي", callback_data="tpl_check_fake")],
        [InlineKeyboardButton("صانع كودات جاهزة", callback_data="tpl_code_maker")],
        [InlineKeyboardButton("صانع لوجو", callback_data="tpl_logo")],
        [InlineKeyboardButton("ترجمه", callback_data="tpl_translate")],
        [InlineKeyboardButton("حساب العمر", callback_data="tpl_age")],
        [
            InlineKeyboardButton("⬅️", callback_data="page_1"),
            InlineKeyboardButton("2/5", callback_data="noop"),
            InlineKeyboardButton("➡️", callback_data="page_3")
        ]
    ],
    3: [
        [InlineKeyboardButton("البلورة السحرية", callback_data="tpl_ball")],
        [InlineKeyboardButton("بروكسي", callback_data="tpl_proxy")],
        [InlineKeyboardButton("تحويل صوت ⇄ كتابة", callback_data="tpl_speech_text")],
        [InlineKeyboardButton("إصلاح جودة الصورة", callback_data="tpl_fix_img")],
        [InlineKeyboardButton("صارحني", callback_data="tpl_sarahne")],
        [
            InlineKeyboardButton("⬅️", callback_data="page_2"),
            InlineKeyboardButton("3/5", callback_data="noop"),
            InlineKeyboardButton("➡️", callback_data="page_4")
        ]
    ],
    4: [
        [InlineKeyboardButton("الجني الازرق", callback_data="tpl_akinator")],
        [InlineKeyboardButton("ايميل موقت", callback_data="tpl_temp_mail")],
        [InlineKeyboardButton("التحدث مع الذكاء الاصطناعي", callback_data="tpl_ai_chat")],
        [InlineKeyboardButton("حماية القنوات", callback_data="tpl_protect_channel")],
        [
            InlineKeyboardButton("⬅️", callback_data="page_3"),
            InlineKeyboardButton("4/5", callback_data="noop"),
            InlineKeyboardButton("➡️", callback_data="page_5")
        ]
    ],
    5: [
        [InlineKeyboardButton("بوت المسابقات", callback_data="tpl_contests")],
        [InlineKeyboardButton("تمويل قنوات", callback_data="tpl_funding")],
        [
            InlineKeyboardButton("⬅️", callback_data="page_4"),
            InlineKeyboardButton("5/5", callback_data="noop")
        ]
    ]
}

# ------------------- محرك تشغيل البوتات الفرعية -------------------
async def start_sub_bot(token: str, template_type: str, owner_id: int):
    try:
        sub_app = Application.builder().token(token).build()

        async def sub_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(f"أهلاً بك في البوت! هذا البوت مصنوع عبر شبكة {RIGHTS_NAME}")

        sub_app.add_handler(CommandHandler("start", sub_start))

        if template_type == "tpl_zakhrafa":
            async def zakhrafa_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
                text = update.message.text
                res = f"✨ **زخرفة نصك:**\n\n1️⃣ `{text}`\n2️⃣ `★ {text} ★`\n3️⃣ `✧ {text} ✧`"
                await update.message.reply_text(res, parse_mode="Markdown")
            sub_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, zakhrafa_handler))

        elif template_type == "tpl_contact":
            async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
                if update.effective_user.id != owner_id:
                    await context.bot.send_message(chat_id=owner_id, text=f"📩 **رسالة جديدة من:** {update.effective_user.first_name}\n\n{update.message.text}")
                    await update.message.reply_text("✅ تم إرسال رسالتك للمالك بنجاح!")
            sub_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, contact_handler))

        elif template_type == "tpl_buttons":
            async def buttons_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
                kb = [[InlineKeyboardButton("قناة المالك", url=CHANNEL_LINK)]]
                await update.message.reply_text("مرحباً بك! اضغط على الزر أدناه:", reply_markup=InlineKeyboardMarkup(kb))
            sub_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons_handler))

        await sub_app.initialize()
        await sub_app.start()
        await sub_app.updater.start_polling()
        
        RUNNING_BOTS[token] = sub_app
        return True
    except Exception as e:
        logging.error(f"Error starting sub-bot: {e}")
        return False

# ------------------- فحص الاشتراك الإجباري -------------------
async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception:
        return False

async def send_sub_request(update: Update):
    keyboard = [
        [InlineKeyboardButton("📢 اشترك في قناة ON.Mix", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"⚠️ **عذراً يا صديقي!**\n\nيجب عليك الاشتراك في قناة البوت أولاً لاستخدام الخدمات:\n{CHANNEL_LINK}{RIGHTS}"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def check_sub_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    is_subbed = await check_subscription(query.from_user.id, context)
    if is_subbed:
        await query.message.reply_text("✅ شكراً لاشتراكك! يمكنك الآن استخدام البوت بالكامل أرسل /start")
    else:
        await query.message.reply_text("❌ لم تشترك في القناة بعد! يرجى الاشتراك ثم المحاولة مرة أخرى.")

# ------------------- الأوامر ومعالجة القوائم -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not await check_subscription(user.id, context):
        await send_sub_request(update)
        return

    main_keyboard = [
        ["🤖 إنشاء بوت جديد", "📋 البوتات الخاصة بي"],
        ["⚙️ إعدادات عامة لجميع البوتات"],
        ["📊 إحصائيات البوتات الخاصة بي"],
        ["🌐 تغيير اللغة"],
        ["🚀 قناة التحديثات"],
        ["❓ ما هو صانع خدمات ON.Mix؟", "📜 شروط الخدمة"]
    ]
    reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

    message_text = (
        f"🚀 **أنشئ بوتك الآن بسهولة وسرعة!**\n"
        f"اختر القالب، أضف التوكن، وسيكون البوت جاهزاً للعمل ⚡\n\n"
        f"✨ **المميزات:**\n"
        f"• بدون الحاجة إلى أكواد أو تعقيدات\n"
        f"• قوالب ذكية وجاهزة\n"
        f"• استضافة آمنة وفورية\n\n"
        f"💡 **ابدأ الآن وصمم بوتك في أقل من نصف دقيقة!**{RIGHTS}"
    )
    await update.message.reply_text(text=message_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_templates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup(TEMPLATES_PAGES[1])
    text = f"💡 **نصيحة:** اضغط على اسم الخدمة أو القالب لبدء إنشائه{RIGHTS}"
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# معالجة التنقل بين صفحات القوالب
async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("page_"):
        page_num = int(data.split("_")[1])
        reply_markup = InlineKeyboardMarkup(TEMPLATES_PAGES[page_num])
        text = f"💡 **نصيحة:** اضغط على اسم الخدمة أو القالب لبدء إنشائه (الصفحة {page_num}/5){RIGHTS}"
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    elif data == "noop":
        pass

# معالجة اختيار القالب لبدء المحادثة واستلام التوكن
async def template_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['selected_template'] = query.data
    template_name = query.data.replace("tpl_", "")
    
    await query.message.reply_text(
        f"تم اختيار القالب بنجاح (`{template_name}`).\n\n"
        f"أرسل الآن **التوكن (Token)** الخاص ببوتك من @BotFather للبدء في تشغيله فوراً:\n"
        f"*(أو أرسل /cancel للإلغاء)*",
        parse_mode="Markdown"
    )
    return WAITING_FOR_TOKEN

async def receive_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_token = update.message.text.strip()
    selected_tpl = context.user_data.get('selected_template', 'tpl_zakhrafa')
    owner_id = update.effective_user.id

    if ":" not in user_token or len(user_token) < 20:
        await update.message.reply_text("❌ التوكن غير صحيح، تأكد منه من BotFather وأرسل مجدداً أو أرسل /cancel للإلغاء.")
        return WAITING_FOR_TOKEN

    await update.message.reply_text("⏳ جاري فحص التوكن وتشغيل البوت في الخلفية...")
    
    success = await start_sub_bot(user_token, selected_tpl, owner_id)
    
    if success:
        with open("user_bots.txt", "a") as f:
            f.write(f"{owner_id}:{user_token}:{selected_tpl}\n")
        await update.message.reply_text(f"🎉 **مبروك! تم تشغيل بوتك بنجاح وهو يعمل الآن على تليجرام!**{RIGHTS}", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ فشل تشغيل البوت. تأكد من صحة التوكن أو أنه غير مستخدم في مكان آخر.")

    return ConversationHandler.END

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"❌ تم إلغاء عملية إنشاء البوت.{RIGHTS}")
    return ConversationHandler.END

async def my_bots_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_bots = []
    
    try:
        with open("user_bots.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith(user_id + ":"):
                    parts = line.strip().split(":")
                    user_bots.append(parts[1])
    except FileNotFoundError:
        pass

    if user_bots:
        bots_text = "📋 **قائمة بوتاتك النشطة والمصنوعة:**\n\n"
        for idx, bot_token in enumerate(user_bots, 1):
            bots_text += f"{idx}. `...{bot_token[-10:]}` 🟢 (شغال)\n"
        bots_text += f"{RIGHTS}"
    else:
        bots_text = f"❌ **ليس لديك أي بوتات مصنوعة حتى الآن.**\nيمكنك الضغط على '🤖 إنشاء بوت جديد' لإضافة بوتك الأول!{RIGHTS}"

    await update.message.reply_text(bots_text, parse_message='Markdown')

def main():
    app = Application.builder().token(MAIN_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(template_select_callback, pattern="^tpl_")],
        states={
            WAITING_FOR_TOKEN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_token),
                CommandHandler("cancel", cancel_conversation)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_sub_button, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(handle_pagination, pattern="^(page_|noop)$"))
    app.add_handler(conv_handler)
    
    # معالجات الأزرار النصية السفليّة بمرونة تامة
    app.add_handler(MessageHandler(filters.Regex("إنشاء بوت جديد"), show_templates))
    app.add_handler(MessageHandler(filters.Regex("البوتات الخاصة بي"), my_bots_list))

    print("البوت الرئيسي ومحرك تشغيل البوتات يعملان بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()
        
