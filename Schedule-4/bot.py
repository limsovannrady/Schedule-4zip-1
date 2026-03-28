import os
import json
import asyncio
from datetime import datetime, timezone, timedelta
from telegram import (
    Update, constants,
    InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo,
    ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
)

from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    ChatMemberHandler, MessageHandler, filters
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CAMBODIA_TZ = timezone(timedelta(hours=7))
WEBAPP_URL = os.environ.get("WEBAPP_URL", "")
ADMIN_ID = 5002402843

GROUPS_FILE = "groups.json"
USER_GROUPS_FILE = "user_groups.json"
PENDING_FILE = "pending_schedules.json"
SCHEDULED_FILE = "scheduled_messages.json"


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def register_user_in_group(user_id: str, chat_id: str, chat_title: str):
    user_groups = load_json(USER_GROUPS_FILE, {})
    if user_id not in user_groups:
        user_groups[user_id] = {}
    if chat_id not in user_groups[user_id]:
        user_groups[user_id][chat_id] = chat_title
        save_json(USER_GROUPS_FILE, user_groups)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type in ("group", "supergroup"):
        groups = load_json(GROUPS_FILE, {})
        if str(chat.id) in groups:
            register_user_in_group(str(user.id), str(chat.id), chat.title)
        return

    await context.bot.send_chat_action(chat.id, constants.ChatAction.TYPING)
    name = user.first_name or "អ្នក"

    if user.id == ADMIN_ID and WEBAPP_URL:
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("📱 Mini App", web_app=WebAppInfo(url=WEBAPP_URL))
        ]])
        await update.message.reply_text(
            f"សួស្តី {name} 👋",
            reply_markup=reply_markup,
            do_quote=True
        )
    else:
        await update.message.reply_text(
            f"សួស្តី {name} 👋",
            do_quote=True
        )


async def track_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if not user or chat.type not in ("group", "supergroup"):
        return
    groups = load_json(GROUPS_FILE, {})
    chat_id = str(chat.id)
    if chat_id not in groups:
        return
    register_user_in_group(str(user.id), chat_id, groups[chat_id]["title"])


async def track_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if result is None:
        return

    chat = result.chat
    new_status = result.new_chat_member.status
    groups = load_json(GROUPS_FILE, {})

    if new_status in ("member", "administrator") and chat.type in ("group", "supergroup"):
        groups[str(chat.id)] = {
            "title": chat.title,
            "type": chat.type
        }
        save_json(GROUPS_FILE, groups)
    elif new_status in ("left", "kicked"):
        chat_id = str(chat.id)
        groups.pop(chat_id, None)
        save_json(GROUPS_FILE, groups)
        user_groups = load_json(USER_GROUPS_FILE, {})
        changed = False
        for uid in user_groups:
            if chat_id in user_groups[uid]:
                del user_groups[uid][chat_id]
                changed = True
        if changed:
            save_json(USER_GROUPS_FILE, user_groups)


async def send_any_message(bot, chat_id: int, item: dict, reply_to_message_id: int = None):
    msg_type = item.get("msg_type", "text")
    content = item.get("content") or item.get("message", "")
    caption = item.get("caption")
    reply_kwargs = {"reply_to_message_id": reply_to_message_id} if reply_to_message_id else {}
    if msg_type == "forward":
        # caption stores from_chat_id, content stores message_id
        await bot.forward_message(
            chat_id=chat_id,
            from_chat_id=int(caption),
            message_id=int(content)
        )
    elif msg_type == "photo":
        await bot.send_photo(chat_id=chat_id, photo=content, caption=caption, **reply_kwargs)
    elif msg_type == "video":
        await bot.send_video(chat_id=chat_id, video=content, caption=caption, **reply_kwargs)
    elif msg_type == "document":
        await bot.send_document(chat_id=chat_id, document=content, caption=caption, **reply_kwargs)
    elif msg_type == "sticker":
        await bot.send_sticker(chat_id=chat_id, sticker=content, **reply_kwargs)
    elif msg_type == "voice":
        await bot.send_voice(chat_id=chat_id, voice=content, caption=caption, **reply_kwargs)
    elif msg_type == "audio":
        await bot.send_audio(chat_id=chat_id, audio=content, caption=caption, **reply_kwargs)
    elif msg_type == "animation":
        await bot.send_animation(chat_id=chat_id, animation=content, caption=caption, **reply_kwargs)
    elif msg_type == "video_note":
        await bot.send_video_note(chat_id=chat_id, video_note=content, **reply_kwargs)
    elif msg_type == "contact":
        data = json.loads(content)
        await bot.send_contact(chat_id=chat_id, phone_number=data["phone_number"], first_name=data["first_name"], last_name=data.get("last_name"), vcard=data.get("vcard"), **reply_kwargs)
    elif msg_type == "location":
        data = json.loads(content)
        await bot.send_location(chat_id=chat_id, latitude=data["latitude"], longitude=data["longitude"], **reply_kwargs)
    elif msg_type == "venue":
        data = json.loads(content)
        await bot.send_venue(chat_id=chat_id, latitude=data["latitude"], longitude=data["longitude"], title=data["title"], address=data["address"], **reply_kwargs)
    elif msg_type == "poll":
        data = json.loads(content)
        await bot.send_poll(chat_id=chat_id, question=data["question"], options=data["options"], is_anonymous=data.get("is_anonymous", True), type=data.get("type", "regular"), allows_multiple_answers=data.get("allows_multiple_answers", False), **reply_kwargs)
    elif msg_type == "dice":
        await bot.send_dice(chat_id=chat_id, emoji=content, **reply_kwargs)
    else:
        await bot.send_message(chat_id=chat_id, text=content, **reply_kwargs)


async def check_scheduled_messages(context: ContextTypes.DEFAULT_TYPE):
    scheduled = load_json(SCHEDULED_FILE, [])
    if not scheduled:
        return

    now = datetime.now(timezone.utc)
    remaining = []

    for idx, item in enumerate(scheduled, 1):
        try:
            send_time_str = item["scheduled_time"]
            if send_time_str.endswith("Z"):
                send_time_str = send_time_str.replace("Z", "+00:00")
            send_time = datetime.fromisoformat(send_time_str)
            if send_time.tzinfo is None:
                send_time = send_time.replace(tzinfo=CAMBODIA_TZ)

            if now >= send_time:
                try:
                    reply_id = item.get("reply_to_message_id")
                    await send_any_message(context.bot, int(item["group_id"]), item, reply_to_message_id=int(reply_id) if reply_id else None)
                except Exception as send_err:
                    print(f"[Scheduler] Error sending: {send_err}")
                    remaining.append(item)
            else:
                remaining.append(item)
        except Exception as e:
            print(f"[Scheduler] Parse error: {e}")
            remaining.append(item)

    save_json(SCHEDULED_FILE, remaining)


def extract_message_content(msg):
    # Forwarded message — store message_id + from_chat_id for forward_message API
    if msg.forward_origin is not None:
        return "forward", str(msg.message_id), str(msg.chat.id)
    if msg.text:
        return "text", msg.text, None
    elif msg.photo:
        return "photo", msg.photo[-1].file_id, msg.caption
    elif msg.video:
        return "video", msg.video.file_id, msg.caption
    elif msg.document:
        return "document", msg.document.file_id, msg.caption
    elif msg.sticker:
        return "sticker", msg.sticker.file_id, None
    elif msg.voice:
        return "voice", msg.voice.file_id, msg.caption
    elif msg.audio:
        return "audio", msg.audio.file_id, msg.caption
    elif msg.animation:
        return "animation", msg.animation.file_id, msg.caption
    elif msg.video_note:
        return "video_note", msg.video_note.file_id, None
    elif msg.contact:
        c = msg.contact
        return "contact", json.dumps({"phone_number": c.phone_number, "first_name": c.first_name, "last_name": c.last_name, "vcard": c.vcard}), None
    elif msg.location and not msg.venue:
        loc = msg.location
        return "location", json.dumps({"latitude": loc.latitude, "longitude": loc.longitude}), None
    elif msg.venue:
        v = msg.venue
        return "venue", json.dumps({"latitude": v.location.latitude, "longitude": v.location.longitude, "title": v.title, "address": v.address}), None
    elif msg.poll:
        p = msg.poll
        return "poll", json.dumps({"question": p.question, "options": [o.text for o in p.options], "is_anonymous": p.is_anonymous, "type": p.type, "allows_multiple_answers": p.allows_multiple_answers}), None
    elif msg.dice:
        return "dice", msg.dice.emoji, None
    return None, None, None


def schedule_keyboard(count: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton("បោះបង់ ❌"), KeyboardButton(f"រួចរាល់ ✅ ({count})")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def format_display_time(scheduled_time_raw: str) -> tuple:
    try:
        st = scheduled_time_raw
        if st.endswith("Z"):
            st = st.replace("Z", "+00:00")
        send_time = datetime.fromisoformat(st)
        if send_time.tzinfo is None:
            send_time = send_time.replace(tzinfo=CAMBODIA_TZ)
        display_str = send_time.astimezone(CAMBODIA_TZ).strftime("%d-%m-%Y %H:%M")
        return send_time, display_str
    except Exception:
        return None, scheduled_time_raw


async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    pending = load_json(PENDING_FILE, {})
    text = update.message.text or ""

    # Handle keyboard button: cancel
    if text == "បោះបង់ ❌":
        if user_id in pending:
            del pending[user_id]
            save_json(PENDING_FILE, pending)
        await update.message.reply_text(
            "❌ បានបោះបង់ការ schedule!",
            reply_markup=ReplyKeyboardRemove(),
            do_quote=True
        )
        return

    # Handle keyboard button: confirm (any "រួចរាល់ ✅" variant)
    if text.startswith("រួចរាល់ ✅"):
        if user_id not in pending:
            await update.message.reply_text(
                "❌ គ្មានការ schedule ដែលត្រូវបញ្ជាក់!",
                reply_markup=ReplyKeyboardRemove(),
                do_quote=True
            )
            return

        schedule = pending[user_id]
        messages = schedule.get("messages", [])

        if not messages:
            await update.message.reply_text(
                "❌ សូមបញ្ចូលសារជាមុនសិន!",
                reply_markup=schedule_keyboard(0),
                do_quote=True
            )
            return

        del pending[user_id]
        save_json(PENDING_FILE, pending)

        group_id = schedule["group_id"]
        group_title = schedule["group_title"]
        scheduled_time_raw = schedule["scheduled_time"]
        reply_to_message_id = schedule.get("reply_to_message_id")
        if reply_to_message_id:
            reply_to_message_id = int(reply_to_message_id)
        send_time, display_str = format_display_time(scheduled_time_raw)
        now = datetime.now(timezone.utc)

        chat_id = update.effective_chat.id
        prompt_msg_ids = schedule.get("prompt_msg_ids", [])

        if send_time and now >= send_time:
            try:
                for msg_item in messages:
                    await send_any_message(context.bot, int(group_id), msg_item, reply_to_message_id=reply_to_message_id)
                await update.message.reply_text(
                    f"✅ សារត្រូវបានផ្ញើទៅក្រុម *{group_title}* រួចរាល់",
                    parse_mode="Markdown",
                    reply_markup=ReplyKeyboardRemove(),
                    do_quote=True
                )
            except Exception as e:
                await update.message.reply_text(
                    f"❌ មានបញ្ហា: {e}",
                    reply_markup=ReplyKeyboardRemove(),
                    do_quote=True
                )
        else:
            scheduled = load_json(SCHEDULED_FILE, [])
            existing_keys = set()
            for s in scheduled:
                key = str(s.get("group_id") or s.get("group_title", "")) + "|" + str(s.get("scheduled_time", ""))
                existing_keys.add(key)
            schedule_number = len(existing_keys) + 1
            for msg_item in messages:
                scheduled.append({
                    "group_id": str(group_id),
                    "group_title": group_title,
                    "msg_type": msg_item["msg_type"],
                    "content": msg_item["content"],
                    "caption": msg_item["caption"],
                    "scheduled_time": scheduled_time_raw,
                    "scheduled_time_display": display_str,
                    "user_chat_id": str(update.effective_chat.id),
                    "reply_to_message_id": reply_to_message_id,
                    "schedule_number": schedule_number
                })
            save_json(SCHEDULED_FILE, scheduled)

            confirm_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton("📱 Mini App", web_app=WebAppInfo(url=WEBAPP_URL))
            ]]) if WEBAPP_URL else ReplyKeyboardRemove()
            await update.message.reply_text(
                f"✅ Schedule រួចរាល់ #{schedule_number}\n\n"
                f"🔸 ក្រុម: *{group_title}*\n"
                f"🔸 ម៉ោងផ្ញើ: {display_str}",
                parse_mode="Markdown",
                reply_markup=confirm_markup,
                do_quote=True
            )

        for msg_id in prompt_msg_ids:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception:
                pass
        return

    # Otherwise: accumulate message
    if user_id not in pending:
        return

    schedule = pending[user_id]
    msg_type, content, caption = extract_message_content(update.message)

    if msg_type is None:
        await update.message.reply_text("❌ ប្រភេទសារនេះមិនអាច schedule បានទេ!", do_quote=True)
        return

    if "messages" not in schedule:
        schedule["messages"] = []
    schedule["messages"].append({"msg_type": msg_type, "content": content, "caption": caption})
    pending[user_id] = schedule
    save_json(PENDING_FILE, pending)

    group_title = schedule["group_title"]
    _, display_str = format_display_time(schedule["scheduled_time"])
    count = len(schedule["messages"])

    prompt_msg = await update.message.reply_text(
        f"សូមបញ្ចូលសារ៖\n\n"
        f"🔸 ក្រុម: *{group_title}*\n"
        f"🔸 ម៉ោងផ្ញើ: {display_str}",
        parse_mode="Markdown",
        reply_markup=schedule_keyboard(count),
        do_quote=True
    )
    if "prompt_msg_ids" not in schedule:
        schedule["prompt_msg_ids"] = []
    schedule["prompt_msg_ids"].append(prompt_msg.message_id)
    pending[user_id] = schedule
    save_json(PENDING_FILE, pending)


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(ChatMemberHandler(track_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
    track_group_message
))
app.add_handler(MessageHandler(
    ~filters.COMMAND & filters.ChatType.PRIVATE,
    handle_private_message
))
app.job_queue.run_repeating(check_scheduled_messages, interval=1, first=1)
app.run_polling()
