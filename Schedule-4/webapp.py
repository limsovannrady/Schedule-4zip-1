import os
import json
import requests
from flask import Flask, send_from_directory, jsonify, request

app = Flask(__name__, static_folder="static")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_ID = "5002402843"
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


def send_telegram_message(chat_id, text, parse_mode="Markdown", reply_markup=None):
    if not TOKEN:
        return None
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json=payload,
            timeout=10
        )
        data = resp.json()
        if data.get("ok"):
            return data["result"]["message_id"]
    except Exception:
        pass
    return None


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


def is_user_in_group(user_id: str, chat_id: str) -> bool:
    if not TOKEN:
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/getChatMember",
            json={"chat_id": int(chat_id), "user_id": int(user_id)},
            timeout=5
        )
        data = resp.json()
        if data.get("ok"):
            status = data.get("result", {}).get("status", "left")
            return status not in ("left", "kicked")
    except Exception:
        pass
    return False


@app.route("/api/groups")
def get_groups():
    user_id = request.args.get("user_id", "")
    if not user_id or not TOKEN:
        return jsonify({})
    if str(user_id) != ADMIN_ID:
        return jsonify({"error": "unauthorized"}), 403
    all_groups = load_json(GROUPS_FILE, {})
    result = {}
    for chat_id, group_info in all_groups.items():
        if is_user_in_group(user_id, chat_id):
            result[chat_id] = group_info
    return jsonify(result)


@app.route("/api/schedule", methods=["POST"])
def set_schedule():
    data = request.get_json()
    user_id = str(data.get("user_id", ""))
    group_id = data.get("group_id")
    group_title = data.get("group_title")
    scheduled_time = data.get("scheduled_time")
    reply_to_message_id = data.get("reply_to_message_id")

    if not all([user_id, group_id, group_title, scheduled_time]):
        return jsonify({"success": False, "error": "Missing fields"}), 400

    if user_id != ADMIN_ID:
        return jsonify({"success": False, "error": "unauthorized"}), 403

    from datetime import datetime, timezone, timedelta
    CAMBODIA_TZ = timezone(timedelta(hours=7))
    try:
        st = scheduled_time
        if st.endswith("Z"):
            st = st.replace("Z", "+00:00")
        dt = datetime.fromisoformat(st)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=CAMBODIA_TZ)
        if dt <= datetime.now(timezone.utc):
            return jsonify({"success": False, "error": "សូមជ្រើសរើសម៉ោងអនាគតកាល!"}), 400
    except Exception:
        return jsonify({"success": False, "error": "ម៉ោងមិនត្រឹមត្រូវ"}), 400

    pending = load_json(PENDING_FILE, {})
    pending[user_id] = {
        "group_id": group_id,
        "group_title": group_title,
        "scheduled_time": scheduled_time,
        "reply_to_message_id": reply_to_message_id,
        "messages": [],
        "prompt_msg_ids": []
    }
    save_json(PENDING_FILE, pending)

    try:
        dt_str = dt.astimezone(CAMBODIA_TZ).strftime("%d-%m-%Y %H:%M")
    except Exception:
        dt_str = scheduled_time

    keyboard = {
        "keyboard": [[
            {"text": "បោះបង់ ❌"},
            {"text": "រួចរាល់ ✅ (0)"}
        ]],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    msg_id = send_telegram_message(
        user_id,
        f"សូមបញ្ចូលសារ៖\n\n"
        f"🔸 ក្រុម: *{group_title}*\n"
        f"🔸 ម៉ោងផ្ញើ: {dt_str}",
        reply_markup=keyboard
    )
    if msg_id:
        pending = load_json(PENDING_FILE, {})
        if user_id in pending:
            pending[user_id].setdefault("prompt_msg_ids", []).append(msg_id)
            save_json(PENDING_FILE, pending)

    return jsonify({"success": True})


@app.route("/api/scheduled")
def get_scheduled():
    user_id = request.args.get("user_id", "")
    if str(user_id) != ADMIN_ID:
        return jsonify({"error": "unauthorized"}), 403
    from datetime import datetime, timezone, timedelta
    CAMBODIA_TZ = timezone(timedelta(hours=7))
    scheduled = load_json(SCHEDULED_FILE, [])
    for item in scheduled:
        try:
            st = item.get("scheduled_time", "")
            if st.endswith("Z"):
                st = st.replace("Z", "+00:00")
            dt = datetime.fromisoformat(st)
            item["scheduled_time_display"] = dt.astimezone(CAMBODIA_TZ).strftime("%d-%m-%Y %H:%M")
        except Exception:
            item["scheduled_time_display"] = item.get("scheduled_time", "")
    return jsonify(scheduled)


@app.route("/api/scheduled/<int:index>", methods=["DELETE"])
def delete_scheduled(index):
    data = request.get_json() or {}
    user_id = str(data.get("user_id", ""))
    if user_id != ADMIN_ID:
        return jsonify({"success": False, "error": "unauthorized"}), 403
    scheduled = load_json(SCHEDULED_FILE, [])
    if 0 <= index < len(scheduled):
        scheduled.pop(index)
        save_json(SCHEDULED_FILE, scheduled)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Not found"}), 404


@app.route("/api/all-groups")
def get_all_groups():
    user_id = request.args.get("user_id", "")
    if str(user_id) != ADMIN_ID:
        return jsonify({"error": "unauthorized"}), 403
    groups = load_json(GROUPS_FILE, {})
    return jsonify(groups)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
