import os
import datetime

from alembic.util import not_none
from werkzeug.utils import secure_filename
from sqlalchemy import text
from sqlalchemy.event import listens_for
from PIL import Image
from models.user import User
import requests
import config
import html
import re
import time
import threading
from flask import has_request_context, request


# Directory for profile uploads
UPLOAD_DIR = os.path.join("static", "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}

# Function to check allowed file extension
def allowed(name):
    return "." in name and name.rsplit(".", 1)[-1].lower() in ALLOWED_EXT

# Generate custom image filename: createddate_module_action_username.ext
def generate_image_filename(original_filename, module, action, username):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_username = secure_filename(username or 'user').replace(' ', '_') or 'user'
    ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'png'
    return f"{timestamp}_{module}_{action}_{clean_username}.{ext}"

# Process user profile image: saves 100% quality original and -80% reduced thumbnail (20% quality, max 150x150)
def process_user_profile_image(file, user_id, username):
    # Enforce 5MB limit
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > 5 * 1024 * 1024:
        return None, "File size exceeds 5MB limit."

    clean_username = secure_filename(username or 'user').replace(' ', '_') or 'user'
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'png'

    org_filename = f"{user_id}_org_{clean_username}.{ext}"
    thum_filename = f"{user_id}_thum_{clean_username}.jpg"

    org_path = os.path.join(UPLOAD_DIR, org_filename)
    thum_path = os.path.join(UPLOAD_DIR, thum_filename)

    # Version 1: Save Original (100% Quality)
    file.save(org_path)

    # Version 2: Save Thumbnail (-80% quality reduction / 20% quality & 150x150 max dimensions)
    try:
        with Image.open(org_path) as img:
            img.thumbnail((150, 150))
            if img.mode in ("RGBA", "P"):
                rgb_img = img.convert("RGB")
            else:
                rgb_img = img
            rgb_img.save(thum_path, format="JPEG", quality=20)
    except Exception as e:
        print(f"Error processing thumbnail image: {e}")

    return org_filename, None

# Delete all profile photos belonging to a user
def delete_user_photos(user):
    if not user:
        return

    protected_files = {
        'default.png', 'profile.png', 'image.png',
        'image copy.png', 'photo_2026-07-12_21-39-04.jpg', 'seteccc.jpg'
    }

    user_id = str(user.id)
    raw_username = user.username or ''
    clean_username = secure_filename(raw_username).replace(' ', '_').lower()

    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            filename_lower = filename.lower()

            # Skip protected system files
            if filename_lower in protected_files or filename_lower.startswith('default'):
                continue

            should_delete = False

            # 1. Match profile filename stored in DB
            if user.profile:
                profile_basename = os.path.basename(user.profile).lower()
                if filename_lower == profile_basename:
                    should_delete = True

            # 2. Match ID prefix pattern (e.g. 17_org_..., 17_thum_..., 17_...)
            if filename_lower.startswith(f"{user_id}_org_") or \
               filename_lower.startswith(f"{user_id}_thum_") or \
               filename_lower.startswith(f"{user_id}_"):
                should_delete = True

            # 3. Match username pattern if valid clean username
            if clean_username and clean_username != 'user':
                if f"_{clean_username}." in filename_lower or filename_lower.endswith(f"_{clean_username}"):
                    should_delete = True

            if should_delete:
                file_path = os.path.join(UPLOAD_DIR, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Deleted user photo: {file_path}")
                except Exception as e:
                    print(f"Error deleting user photo {file_path}: {e}")

@listens_for(User, 'before_delete')
def delete_user_photos_event(mapper, connection, target):
    delete_user_photos(target)


# Register fallback handler for shorthand url_for endpoints across blueprints
def register_url_fallbacks(app):
    from flask import url_for

    def url_fallback(error, endpoint, values):
        if '.' in endpoint:
            raise error
        for bp_name in ['front_bp', 'admin_bp', 'api_bp']:
            full_endpoint = f"{bp_name}.{endpoint}"
            if full_endpoint in app.view_functions:
                return url_for(full_endpoint, **values)
        raise error

    app.url_build_error_handlers.append(url_fallback)



# Message Send to Telegram
def _dispatch_telegram_message(token, chat_id, payload):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json=payload, timeout=8)
        if not resp.ok:
            print(f"Telegram alert error ({resp.status_code}): {resp.text}")
    except Exception as ex:
        print(f"Failed to send Telegram alert: {ex}")


def _extract_concise_error_info(tb_str: str):
    """Extracts only the critical error type, user application file/line, and failing code."""
    lines = (tb_str or "").strip().splitlines()
    if not lines:
        return "Unknown Error", None, None

    error_line = lines[-1].strip()

    relevant_frame = None
    relevant_code = None

    # Find the most relevant user project frame (exclude library boilerplate)
    for idx, line in enumerate(lines):
        clean = line.strip()
        if clean.startswith("File ") and "site-packages" not in clean and ".venv" not in clean:
            relevant_frame = clean
            if idx + 1 < len(lines):
                next_l = lines[idx + 1].strip()
                if not next_l.startswith("File ") and not next_l.startswith("Traceback"):
                    relevant_code = next_l

    # Fallback to last frame if none matched
    if not relevant_frame:
        for idx in range(len(lines) - 2, -1, -1):
            if lines[idx].strip().startswith("File "):
                relevant_frame = lines[idx].strip()
                if idx + 1 < len(lines):
                    relevant_code = lines[idx + 1].strip()
                break

    # Clean file path to relative path
    if relevant_frame:
        match = re.search(r'File ".*?[\\/]([^\\/]+[\\/][^\\/]+)", line (\d+), in (.*)', relevant_frame)
        if match:
            relevant_frame = f"{match.group(1)}:{match.group(2)} ({match.group(3)})"
        else:
            match_single = re.search(r'File ".*?[\\/]([^\\/]+)", line (\d+), in (.*)', relevant_frame)
            if match_single:
                relevant_frame = f"{match_single.group(1)}:{match_single.group(2)} ({match_single.group(3)})"
        relevant_frame = relevant_frame.replace('\\', '/')

    return error_line, relevant_frame, relevant_code


# Anti-Spam Alert Deduplication Cache
_ALERT_CACHE = {}
_ALERT_LOCK = threading.Lock()

def _should_send_alert(dedup_key: str, cooldown_seconds: int = 300) -> bool:
    """Returns True if the alert should be sent (1st time or cooldown expired), False if it should be throttled."""
    now = time.time()
    with _ALERT_LOCK:
        # Periodic cleanup if cache grows
        if len(_ALERT_CACHE) > 200:
            expired = [k for k, t in _ALERT_CACHE.items() if (now - t) > (cooldown_seconds * 2)]
            for k in expired:
                _ALERT_CACHE.pop(k, None)

        last_time = _ALERT_CACHE.get(dedup_key)
        if last_time is None or (now - last_time) >= cooldown_seconds:
            _ALERT_CACHE[dedup_key] = now
            return True
        return False


def send_telegram_alert(content: str, status_code: int = 500, async_send: bool = True):
    bot_token = getattr(config, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(config, 'TELEGRAM_CHAT_ID', '')
    cooldown = getattr(config, 'TELEGRAM_ALERT_COOLDOWN', 300)

    if not bot_token or not chat_id:
        print("Telegram bot token or chat ID not configured.")
        return

    # Auto-ensure leading @ for public group usernames if not starting with - or @
    if isinstance(chat_id, str) and not chat_id.startswith('@') and not chat_id.startswith('-'):
        chat_id = f"@{chat_id}"

    # Extract request information if available
    method = "N/A"
    path = "N/A"
    remote_addr = "N/A"
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if has_request_context():
        method = request.method
        path = request.path
        remote_addr = request.headers.get('X-Forwarded-For', request.remote_addr)

    content_str = str(content or "").strip()
    safe_content = html.escape(content_str)

    if status_code == 500:
        err_name, err_file, err_line = _extract_concise_error_info(content_str)
        dedup_key = f"500:{remote_addr}:{method}:{path}:{err_name}:{err_file}"

        # Check anti-spam cooldown (1 time only per cooldown window)
        if not _should_send_alert(dedup_key, cooldown):
            print(f"[Anti-Spam] Suppressed duplicate 500 alert for {dedup_key}")
            return

        text_parts = [
            "🚨 <b>[HTTP 500] Internal Server Error</b>",
            f"<b>Error:</b> <code>{html.escape(err_name)}</code>",
        ]
        if err_file:
            text_parts.append(f"<b>File:</b> <code>{html.escape(err_file)}</code>")
        if err_line:
            text_parts.append(f"<b>Line:</b> <code>{html.escape(err_line)}</code>")
        text_parts.append(f"<b>Endpoint:</b> <code>{method} {path}</code>")
        text_parts.append(f"<b>Client IP:</b> <code>{remote_addr}</code> | <b>Time:</b> <code>{time_str}</code>")
        text = "\n".join(text_parts)

    elif status_code == 429:
        dedup_key = f"429:{remote_addr}:{method}:{path}"

        # Check anti-spam cooldown (1 time only per cooldown window)
        if not _should_send_alert(dedup_key, cooldown):
            print(f"[Anti-Spam] Suppressed duplicate 429 alert for {dedup_key}")
            return

        text = (
            f"⚠️ <b>[HTTP 429] Too Many Requests</b>\n"
            f"<b>Reason:</b> <code>{safe_content[:300]}</code>\n"
            f"<b>Endpoint:</b> <code>{method} {path}</code>\n"
            f"<b>Client IP:</b> <code>{remote_addr}</code> | <b>Time:</b> <code>{time_str}</code>"
        )
    else:
        dedup_key = f"{status_code}:{remote_addr}:{method}:{path}"

        if not _should_send_alert(dedup_key, cooldown):
            return

        text = (
            f"⚠️ <b>[HTTP {status_code}] Application Alert</b>\n"
            f"<b>Message:</b> <code>{safe_content[:300]}</code>\n"
            f"<b>Endpoint:</b> <code>{method} {path}</code>\n"
            f"<b>Client IP:</b> <code>{remote_addr}</code> | <b>Time:</b> <code>{time_str}</code>"
        )

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if async_send:
        worker = threading.Thread(
            target=_dispatch_telegram_message,
            args=(bot_token, chat_id, payload),
            daemon=True
        )
        worker.start()
    else:
        _dispatch_telegram_message(bot_token, chat_id, payload)

