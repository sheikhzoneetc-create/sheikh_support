import telebot
from telebot import types
import time
import threading
import random

BOT_TOKEN = "8859855010:AAEh0Rrdb8665y0v91ACP8N437B90Iu2dzk"
ADMIN_CHAT_ID = "8694336266"
OWNER_USERNAME = "sajibsheikh313"

GUIDE_APP_URL = "https://sheikhzoneetc-create.github.io/sheikh_support/guide.html"
WEBSITE_URL = "https://sheikhzone.com"
OFFICIAL_CHANNEL_URL = "https://t.me/SheikhZoneOfficial"
FB_PAGE_URL = "https://facebook.com/sheikhzone"

bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}
support_data = {}
user_map = {}
active_sessions = {}

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_guide = types.KeyboardButton("📖 টিউটোরিয়াল", web_app=types.WebAppInfo(url=GUIDE_APP_URL))
    btn_support = types.KeyboardButton("🛠️ কাস্টমার সাপোর্ট")
    btn_website = types.KeyboardButton("🌐 ওয়েবসাইট ভিজিট", web_app=types.WebAppInfo(url=WEBSITE_URL))
    btn_channel = types.KeyboardButton("📢 অফিশিয়াল চ্যানেল")
    btn_fb = types.KeyboardButton("🌐 অফিসিয়াল ফেসবুক পেইজ")

    markup.add(btn_guide, btn_support)
    markup.add(btn_website, btn_channel)
    markup.add(btn_fb)
    return markup

@bot.message_handler(commands=['start'])
def welcome_user(message):
    user_states.pop(message.chat.id, None)
    support_data.pop(message.chat.id, None)

    text = (
        f"👋 আসসালামু আলাইকুম, {message.from_user.first_name}!\n\n"
        "**Sheikh Zone হেল্পডেস্কে স্বাগতম।**\n"
        "আপনার প্রয়োজনীয় সেবা নিতে নিচের মেনু বাটন ব্যবহার করুন:"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text in ["🛠️ কাস্টমার সাপোর্ট", "🛠️ আবেদন", "🛠️ সমস্যা রিপোর্ট"])
def start_support_chat(msg):
    chat_id = msg.chat.id
    user_states[chat_id] = "WAITING_NAME"
    support_data[chat_id] = {}
    bot.send_message(
        chat_id, 
        "📋 **Sheikh Zone কাস্টমার হেল্পডেস্ক**\n"
        "────────────────────────\n"
        "👤 **ধাপ ১/৩:** অনুগ্রহ করে আপনার **নাম** লিখুন:", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda msg: msg.text == "📢 অফিশিয়াল চ্যানেল")
def send_channel_link(msg):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 চ্যানেলে প্রবেশ করুন", url=OFFICIAL_CHANNEL_URL))
    bot.send_message(msg.chat.id, "আমাদের অফিশিয়াল টেলিগ্রাম চ্যানেলে যুক্ত হতে নিচের বাটনে ক্লিক করুন:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🌐 অফিসিয়াল ফেসবুক পেইজ")
def send_fb_link(msg):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🌐 ফেসবুক পেইজে যান", url=FB_PAGE_URL))
    bot.send_message(msg.chat.id, "আমাদের অফিসিয়াল ফেসবুক পেইজ ভিজিট করতে নিচের বাটনে ক্লিক করুন:", reply_markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "WAITING_NAME")
def get_name(msg):
    chat_id = msg.chat.id
    support_data[chat_id]['name'] = msg.text.strip()
    user_states[chat_id] = "WAITING_PHONE"
    bot.send_message(
        chat_id, 
        "📱 **ধাপ ২/৩:** আপনার সচল **মোবাইল নাম্বার** প্রদান করুন:", 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "WAITING_PHONE")
def get_phone(msg):
    chat_id = msg.chat.id
    support_data[chat_id]['phone'] = msg.text.strip()
    user_states[chat_id] = "WAITING_EMAIL_CHOICE"

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_yes = types.InlineKeyboardButton("📧 জিমেইল প্রদান করব", callback_data=f"ask_mail_{chat_id}")
    btn_skip = types.InlineKeyboardButton("⏩ প্রয়োজন নেই / স্কিপ", callback_data=f"skip_mail_{chat_id}")
    markup.add(btn_yes, btn_skip)

    bot.send_message(
        chat_id, 
        "📧 **ওয়েবসাইটের জিমেইল:**\n"
        "আপনার একাউন্টের সাথে কি কোনো জিমেইল যুক্ত আছে?", 
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("ask_mail_"))
def ask_mail_input(call):
    chat_id = int(call.data.split("_")[2])
    user_states[chat_id] = "WAITING_EMAIL_TEXT"
    bot.send_message(chat_id, "✍️ আপনার **জিমেইল অ্যাড্রেসটি** লিখে পাঠান:", parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("skip_mail_"))
def skip_mail_input(call):
    chat_id = int(call.data.split("_")[2])
    support_data[chat_id]['email'] = 'প্রদান করা হয়নি'
    user_states[chat_id] = "WAITING_ISSUE"
    bot.send_message(
        chat_id, 
        "👇 **এখন আপনার সমস্যার আসল বিস্তারিত লিখুন।**\n\n"
        "📸 **Screenshot থাকলে পাঠাতে পারেন।**", 
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "WAITING_EMAIL_TEXT")
def get_email(msg):
    chat_id = msg.chat.id
    support_data[chat_id]['email'] = msg.text.strip()
    user_states[chat_id] = "WAITING_ISSUE"
    bot.send_message(
        chat_id, 
        "👇 **এখন আপনার সমস্যার আসল বিস্তারিত লিখুন।**\n\n"
        "📸 **Screenshot থাকলে পাঠাতে পারেন।**", 
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['text', 'photo'], func=lambda msg: user_states.get(msg.chat.id) == "WAITING_ISSUE")
def submit_issue(msg):
    chat_id = msg.chat.id
    user_states.pop(chat_id, None)

    name = support_data.get(chat_id, {}).get('name', 'N/A')
    phone = support_data.get(chat_id, {}).get('phone', 'N/A')
    email = support_data.get(chat_id, {}).get('email', 'প্রদান করা হয়নি')
    issue = msg.caption if msg.photo else msg.text

    random_num = random.randint(10000, 99999)
    ticket_id = f"#SZ-AJI{random_num}"

    admin_text = (
        f"🎫 **Ticket তৈরি হয়েছে!**\n\n"
        f"🆔 **Ticket ID:** `{ticket_id}`\n"
        f"👤 **গ্রাহক:** {name}\n"
        f"📱 **মোবাইল:** `{phone}`\n"
        f"📧 **জিমেইল:** `{email}`\n\n"
        f"📌 **সমস্যার বিবরণ:**\n{issue or '📷 গ্রাহক স্ক্রিনশট পাঠিয়েছেন'}\n"
        "────────────────────────\n"
        "⏱️ স্ট্যাটাস: **সক্রিয় (১০ মিনিট কাউন্টডাউন)**"
    )

    admin_markup = types.InlineKeyboardMarkup(row_width=2)
    btn_ext = types.InlineKeyboardButton("⏳ ৫ মিনিট বাড়ান", callback_data=f"ext_{chat_id}")
    btn_vote = types.InlineKeyboardButton("🗳️ সমাধানের ভোট পাঠান", callback_data=f"sendvote_{chat_id}")
    btn_quick = types.InlineKeyboardButton("⚡ কুইক রিপ্লাই", callback_data=f"quick_{chat_id}")
    btn_close = types.InlineKeyboardButton("🔒 চ্যাট বন্ধ", callback_data=f"close_{chat_id}")
    btn_transfer = types.InlineKeyboardButton("👔 কর্তৃপক্ষ হস্তান্তর", callback_data=f"trans_{chat_id}")
    
    admin_markup.add(btn_ext, btn_vote)
    admin_markup.add(btn_quick)
    admin_markup.add(btn_close, btn_transfer)

    sent_msg = None
    if msg.photo:
        sent_msg = bot.send_photo(ADMIN_CHAT_ID, msg.photo[-1].file_id, caption=admin_text, reply_markup=admin_markup, parse_mode="Markdown")
    else:
        sent_msg = bot.send_message(ADMIN_CHAT_ID, admin_text, reply_markup=admin_markup, parse_mode="Markdown")

    if sent_msg:
        user_map[sent_msg.message_id] = chat_id

    start_session_timer(chat_id, ticket_id)

def start_session_timer(user_id, ticket_id):
    active_sessions[user_id] = {'remaining': 600, 'active': True, 'ticket': ticket_id}

    cust_markup = types.InlineKeyboardMarkup(row_width=1)
    cust_markup.add(types.InlineKeyboardButton("🛑 চ্যাট বন্ধ করুন", callback_data=f"custclose_{user_id}"))

    initial_text = (
        "🛎️ **Sheikh Zone হেল্পডেস্ক সাপোর্ট**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ **আপনার অনুরোধটি সিস্টেমে নথিভুক্ত হয়েছে।**\n\n"
        f"🎫 **টিকিট রেফারেন্স:** `{ticket_id}`\n"
        "👤 **স্ট্যাটাস:** প্রতিনিধি পর্যালোচনায় রয়েছে\n"
        "⏳ **প্রত্যাশিত সময়:** সর্বোচ্চ ১০ মিনিট\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⏱️ **বাকি সময়:** `১০:০০` মিনিট\n\n"
        "💡 *প্রয়োজনে চ্যাটে সংশ্লিষ্ট ট্রানজেকশন আইডি বা স্ক্রিনশট শেয়ার করুন।*"
    )
    sent_timer = bot.send_message(user_id, initial_text, reply_markup=cust_markup, parse_mode="Markdown")
    active_sessions[user_id]['msg_id'] = sent_timer.message_id

    def countdown_thread():
        while active_sessions.get(user_id, {}).get('active', False) and active_sessions[user_id]['remaining'] > 0:
            time.sleep(5)
            if not active_sessions.get(user_id, {}).get('active', False):
                break

            active_sessions[user_id]['remaining'] -= 5
            rem = active_sessions[user_id]['remaining']
            mins = rem // 60
            secs = rem % 60
            timer_str = f"{mins:02d}:{secs:02d}"

            try:
                bot.edit_message_text(
                    chat_id=user_id,
                    message_id=active_sessions[user_id]['msg_id'],
                    text=(
                        "🛎️ **Sheikh Zone হেল্পডেস্ক সাপোর্ট**\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        "✅ **আপনার অনুরোধটি সিস্টেমে নথিভুক্ত হয়েছে।**\n\n"
                        f"🎫 **টিকিট রেফারেন্স:** `{ticket_id}`\n"
                        "👤 **স্ট্যাটাস:** প্রতিনিধি পর্যালোচনায় রয়েছে\n"
                        "⏳ **প্রত্যাশিত সময়:** সর্বোচ্চ ১০ মিনিট\n"
                        "━━━━━━━━━━━━━━━━━━━━\n"
                        f"⏱️ **বাকি সময়:** `{timer_str}` মিনিট\n\n"
                        "💡 *প্রয়োজনে চ্যাটে সংশ্লিষ্ট ট্রানজেকশন আইডি বা স্ক্রিনশট শেয়ার করুন।*"
                    ),
                    reply_markup=cust_markup,
                    parse_mode="Markdown"
                )
            except Exception:
                pass

        if active_sessions.get(user_id, {}).get('active', False) and active_sessions[user_id]['remaining'] <= 0:
            active_sessions[user_id]['active'] = False
            send_owner_transfer(user_id, is_auto=True)

    threading.Thread(target=countdown_thread).start()

@bot.message_handler(func=lambda msg: str(msg.chat.id) != ADMIN_CHAT_ID and msg.text not in ["🛠️ কাস্টমার সাপোর্ট", "🛠️ আবেদন", "🛠️ সমস্যা রিপোর্ট", "📢 অফিশিয়াল চ্যানেল", "🌐 অফিসিয়াল ফেসবুক পেইজ"], content_types=['text', 'photo'])
def forward_customer_extra(msg):
    if msg.photo:
        bot.send_photo(ADMIN_CHAT_ID, msg.photo[-1].file_id, caption=f"📷 গ্রাহক ({msg.from_user.first_name})-এর পাঠানো অতিরিক্ত স্ক্রিনশট।")
        bot.reply_to(msg, "✅ আপনার স্ক্রিনশটটি টিমের কাছে যুক্ত করা হয়েছে।")
    else:
        bot.send_message(ADMIN_CHAT_ID, f"💬 **গ্রাহক বার্তা:**\n{msg.text}", parse_mode="Markdown")
        bot.reply_to(msg, "✅ আপনার মেসেজটি সংরক্ষিত হয়েছে।")

def send_owner_transfer(user_id, is_auto=False):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("💬 প্রধান কর্তৃপক্ষের সাথে যোগাযোগ করুন", url=f"https://t.me/{OWNER_USERNAME}"))

    if is_auto:
        msg_text = (
            "👨‍💼 **Sheikh Zone Senior Support**\n"
            "────────────────────────\n"
            "প্রিয় গ্রাহক, নির্দিষ্ট সময়ের মধ্যে সাপোর্ট সম্পন্ন না হওয়ায় আপনার বিষয়টি দ্রুত সমাধানের জন্য সরাসরি আমাদের **প্রধান কর্তৃপক্ষ (Senior Authority)**-এর নিকট স্থানান্তর করা হলো।\n\n"
            "নিচের বাটনে চাপ দিয়ে সরাসরি আপনার বিষয়টি জানান:"
        )
        bot.send_message(ADMIN_CHAT_ID, f"⚠️ গ্রাহক (ID: {user_id})-এর ১০ মিনিট পার হওয়ায় স্বয়ংক্রিয়ভাবে প্রধান কর্তৃপক্ষের নিকট স্থানান্তর করা হয়েছে।")
    else:
        msg_text = (
            "👨‍💼 **Sheikh Zone Senior Support**\n"
            "────────────────────────\n"
            "প্রিয় গ্রাহক, আপনার বিষয়টি অধিকতর গুরুত্বের সাথে সমাধানের জন্য আমাদের **প্রধান কর্তৃপক্ষ (Senior Management)**-এর নিকট স্থানান্তর করা হয়েছে।\n\n"
            "নিচের বাটনে চাপ দিয়ে সরাসরি যোগাযোগ করুন:"
        )

    bot.send_message(user_id, msg_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    data = call.data

    if data.startswith("ext_"):
        uid = int(data.split("_")[1])
        if uid in active_sessions and active_sessions[uid]['active']:
            active_sessions[uid]['remaining'] += 300
            bot.send_message(uid, "⏳ আপনার বিষয়টি প্রক্রিয়াধীন রয়েছে, দয়া করে আর কিছুক্ষণ সময় দিয়ে সহযোগিতা করুন। আমাদের টিম সক্রিয়ভাবে কাজ করছে।")
            bot.answer_callback_query(call.id, "✅ ৫ মিনিট সময় বৃদ্ধি করা হয়েছে।")
        else:
            bot.answer_callback_query(call.id, "⚠️ সেশনটি সক্রিয় নেই।")

    elif data.startswith("quick_"):
        uid = int(data.split("_")[1])
        q_markup = types.InlineKeyboardMarkup(row_width=1)
        q_markup.add(
            types.InlineKeyboardButton("💰 টাকা অ্যাড হয়েছে, চেক করুন", callback_data=f"sendq_{uid}_1"),
            types.InlineKeyboardButton("🔢 অনুগ্রহ করে সঠিক TrxID দিন", callback_data=f"sendq_{uid}_2"),
            types.InlineKeyboardButton("⌛ ৫-১০ মিনিটের মধ্যে কাজ সম্পন্ন হবে", callback_data=f"sendq_{uid}_3")
        )
        bot.send_message(ADMIN_CHAT_ID, "⚡ **যে উত্তরটি পাঠাতে চান সিলেক্ট করুন:**", reply_markup=q_markup, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    elif data.startswith("sendq_"):
        parts = data.split("_")
        uid = int(parts[1])
        opt = parts[2]
        
        reply_texts = {
            "1": "আপনার ওয়ালেটে টাকা যুক্ত করে দেওয়া হয়েছে। দয়া করে আপনার একাউন্ট চেক করুন। ধন্যবাদ! ❤️",
            "2": "আপনার পেমেন্টের ট্রানজেকশন আইডি (TrxID) সঠিক নয়। দয়া করে মেসেজ বা হিস্ট্রি চেক করে সঠিক TrxID প্রদান করুন।",
            "3": "আপনার অনুরোধটি প্রক্রিয়াধীন রয়েছে। অনুগ্রহ করে পরবর্তী ৫-১০ মিনিট অপেক্ষা করুন।"
        }
        selected_text = reply_texts.get(opt, "")
        
        bot.send_message(uid, f"💬 **সাপোর্ট টিম বার্তা:**\n\n{selected_text}", parse_mode="Markdown")
        bot.send_message(ADMIN_CHAT_ID, f"✅ দ্রুত উত্তর পাঠানো হয়েছে:\n\"{selected_text}\"")
        bot.answer_callback_query(call.id, "পাঠানো হয়েছে!")

    elif data.startswith("sendvote_"):
        uid = int(data.split("_")[1])
        vote_markup = types.InlineKeyboardMarkup(row_width=2)
        btn_yes = types.InlineKeyboardButton("✅ হ্যাঁ, সমাধান হয়েছে", callback_data=f"vote_yes_{uid}")
        btn_no = types.InlineKeyboardButton("❌ না, এখনো হয়নি", callback_data=f"vote_no_{uid}")
        vote_markup.add(btn_yes, btn_no)

        vote_text = (
            "❓ **আপনার সমস্যাটি কি সম্পূর্ণ সমাধান হয়েছে?**\n\n"
            "অনুগ্রহ করে নিচের বাটনে চাপ দিয়ে আপনার মূল্যবান মতামত নিশ্চিত করুন:"
        )
        bot.send_message(uid, vote_text, reply_markup=vote_markup, parse_mode="Markdown")
        bot.answer_callback_query(call.id, "✅ গ্রাহকের কাছে ভোট পাঠানো হয়েছে।")

    elif data.startswith("close_"):
        uid = int(data.split("_")[1])
        if uid in active_sessions:
            active_sessions[uid]['active'] = False
        bot.send_message(uid, "🔒 এডমিন আপনার সাপোর্ট সেশনটি সমাপ্ত করেছেন। Sheikh Zone-এর সাথে থাকার জন্য ধন্যবাদ!", reply_markup=get_main_keyboard())
        bot.answer_callback_query(call.id, "✅ সেশন বন্ধ করা হয়েছে।")

    elif data.startswith("trans_"):
        uid = int(data.split("_")[1])
        if uid in active_sessions:
            active_sessions[uid]['active'] = False
        send_owner_transfer(uid, is_auto=False)
        bot.answer_callback_query(call.id, "✅ প্রধান কর্তৃপক্ষের নিকট হস্তান্তর সম্পন্ন হয়েছে।")

    elif data.startswith("custclose_"):
        uid = int(data.split("_")[1])
        if uid in active_sessions:
            active_sessions[uid]['active'] = False
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🛑 আপনি সাপোর্ট চ্যাটটি সমাপ্ত করেছেন। ধন্যবাদ সাথে থাকার জন্য!"
        )
        bot.send_message(ADMIN_CHAT_ID, "ℹ️ গ্রাহক নিজে থেকেই সেশন সমাপ্ত করেছেন।")

    elif data.startswith("vote_yes_"):
        uid = int(data.split("_")[2])
        if uid in active_sessions:
            active_sessions[uid]['active'] = False

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="✅ **আলহামদুলিল্লাহ! আপনার সমস্যার সমাধান হওয়ায় আমরা আনন্দিত। সেশনটি সফলভাবে সমাপ্ত হলো।**\n\nSheikh Zone-এর সাথেই থাকুন! ❤️",
            parse_mode="Markdown"
        )
        bot.send_message(ADMIN_CHAT_ID, f"🎉 গ্রাহক নিশ্চিত করেছেন সমাধান হয়েছে। টিকিট সফলভাবে ক্লোজ হয়েছে।")

    elif data.startswith("vote_no_"):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌ **দুঃখিত! বিষয়টি আরও খতিয়ে দেখা হচ্ছে। অনুগ্রহ করে একটু ধৈর্য ধরুন।**",
            parse_mode="Markdown"
        )
        bot.send_message(ADMIN_CHAT_ID, f"⚠️ গ্রাহক জানিয়েছেন এখনও সমাধান হয়নি! দয়া করে বিষয়টি পুনরায় পর্যালোচনা করুন।")

@bot.message_handler(func=lambda msg: str(msg.chat.id) == ADMIN_CHAT_ID and msg.reply_to_message)
def admin_reply_handler(msg):
    replied_id = msg.reply_to_message.message_id
    customer_id = user_map.get(replied_id)

    if customer_id:
        cust_reply = (
            "💬 **সাপোর্ট টিম বার্তা:**\n\n"
            f"{msg.text}"
        )
        bot.send_message(customer_id, cust_reply, parse_mode="Markdown")
        bot.reply_to(msg, "✅ গ্রাহকের কাছে উত্তর পৌঁছে গেছে।")
    else:
        bot.reply_to(msg, "⚠️ গ্রাহকের চ্যাট রেকর্ড পাওয়া যায়নি।")

print("বট সফলভাবে চালু হয়েছে এবং সব বাটন নিচে কীবোর্ডে সেট করা হয়েছে...")
bot.infinity_polling()
