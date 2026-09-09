import os
import datetime
from werkzeug.utils import secure_filename
from sqlalchemy import text
from sqlalchemy.event import listens_for
from PIL import Image
from models.user import User

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
