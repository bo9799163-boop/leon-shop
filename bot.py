import telebot
import random
import os

# 1. ضع توكن البوت الخاص بك هنا (تحصل عليه من BotFather)
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(BOT_TOKEN)

# 2. معرف التليجرام الخاص بك (الأدمن) لفتح لوحة التحكم بالمخزون
ADMIN_ID = 123456789  # استبدله بـ ID حسابك الحقيقي

# ملفات نصية بسيطة لتخزين الحسابات (المخزون)
FORTNITE_STOCK_FILE = "fortnite_accounts.txt"

# إنشاء الملفات إذا لم تكن موجودة
if not os.path.exists(FORTNITE_STOCK_FILE):
    with open(FORTNITE_STOCK_FILE, "w") as f: pass

# دالة لجلب عدد الحسابات المتوفرة في المخزون
def get_stock_count():
    with open(FORTNITE_STOCK_FILE, "r") as f:
        lines = f.readlines()
    return len([l for l in lines if l.strip()])

# --- أوامر الزبائن ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👑 أهلاً بك في بوت ليون الرقمي للحسابات العشوائية!\n\n"
        "⚡ هنا يمكنك شراء حسابات فورتنايت وروكيت ليج عشوائية مع فرصة ظهور سكنات نادرة (بلاك نايت / شيطون).\n\n"
        "👇 اختر من الأزرار بالأسفل للتسوق:"
    )
    
    # إنشاء أزرار التحكم للزبون
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_buy = telebot.types.KeyboardButton("🛒 شراء حساب فورتنايت عشوائي (1$)")
    btn_stock = telebot.types.KeyboardButton("📊 فحص المخزون الحالي")
    markup.add(btn_buy, btn_stock)
    
    # إذا كان المستخدم هو الأدمن، نفتح له زر الإدارة
    if message.from_user.id == ADMIN_ID:
        btn_admin = telebot.types.KeyboardButton("⚙️ لوحة التحكم بالمخزون")
        markup.add(btn_admin)
        
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📊 فحص المخزون الحالي")
def check_stock_ui(message):
    count = get_stock_count()
    bot.reply_to(message, f"📦 المخزون المتوفر حالياً في البوت: ({count}) حساب جاهز للتسليم الفوري.")

@bot.message_handler(func=lambda message: message.text == "🛒 شراء حساب فورتنايت عشوائي (1$)")
def buy_account_logic(message):
    # قراءة الحسابات المتوفرة
    with open(FORTNITE_STOCK_FILE, "r") as f:
        accounts = f.readlines()
    
    accounts = [a.strip() for a in accounts if a.strip()]
    
    if len(accounts) == 0:
        bot.reply_to(message, "❌ نعتذر منك غالي، المخزون نافد حالياً! جاري شحن الحسابات من قبل الإدارة قريباً.")
        return

    # [ملاحظة هندسية]: هنا يتم ربط بوابة الدفع، بعد نجاح الدفع يتفعل الكود بالأسفل تلقائياً
    # سحب حساب عشوائي من القائمة
    selected_account = random.choice(accounts)
    
    # حذف الحساب المسحوب من الملف حتى لا يتكرر لزبون آخر
    accounts.remove(selected_account)
    with open(FORTNITE_STOCK_FILE, "w") as f:
        for acc in accounts:
            f.write(acc + "\n")
            
    # تسليم الحساب للزبون
    delivery_msg = (
        "✅ **تمت عملية الشراء بنجاح!**\n\n"
        "🎁 إليك معلومات حسابك العشوائي المستلم فوراً:\n"
        f"➡️ `{selected_account}`\n\n"
        "📌 *نصيحة:* قم بفحص الحساب وتغيير معلوماته فوراً. شكراً لثقتك بنا!"
    )
    bot.send_message(message.chat.id, delivery_msg, parse_mode="Markdown")

# --- أوامر لوحة التحكم للأدمن (إضافة مخزون) ---

@bot.message_handler(func=lambda message: message.text == "⚙️ لوحة التحكم بالمخزون" and message.from_user.id == ADMIN_ID)
def admin_panel_ui(message):
    admin_text = (
        "⚙️ **مرحباً بك يا ليون في لوحة التحكم الإدارية:**\n\n"
        "لإضافة حسابات جديدة للمخزون، أرسل الحسابات مباشرة بتنسيق:\n"
        "`user:pass`\n"
        "أو ارسل مجموعة حسابات كل حساب في سطر منفصل."
    )
    bot.send_message(message.chat.id, admin_text, parse_mode="Markdown")
    bot.register_next_step_handler(message, save_imported_stock)

def save_imported_stock(message):
    if message.from_user.id != ADMIN_ID: return
    
    raw_lines = message.text.split("\n")
    valid_accounts = [line.strip() for line in raw_lines if line.strip()]
    
    if len(valid_accounts) == 0:
        bot.reply_to(message, "❌ لم يتم التعرف على أي حسابات مقبولة.")
        return
        
    # كتابة الحسابات الجديدة وتخزينها بالملف
    with open(FORTNITE_STOCK_FILE, "a") as f:
        for acc in valid_accounts:
            f.write(acc + "\n")
            
    bot.reply_to(message, f"📥 تم بنجاح إضافة ({len(valid_accounts)}) حساب جديد إلى المخزون العشوائي!")

# تشغيل البوت بشكل مستمر
print("⚡ البوت يعمل الحين بذكاء وعلى أهبة الاستعداد لتسليم الحسابات...")
bot.infinity_polling()

