import os
import re
import time
import asyncio
from pyrogram.enums import ChatAction
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Version du bot
BOT_VERSION = "1.6"

# Identifiants Telegram (à personnaliser)
API_ID = 23992653
API_HASH = "ef7ad3a6a3e88b487108cd5242851ed4"
BOT_TOKEN = "7634028476:AAHDjeRCagDKlxtVmRV3SoBBRgAG4nG0tbw"

app = Client("rename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

SEQUENCE_MODE = False
RECEIVED_FILES = []
CURRENT_THUMB = None
RENAME_MODE = False
RENAME_INFO = {}
PENDING_FILE = None
SEND_AS_VIDEO = None  # None = auto
AUTO_MODE = False
FILES_SENT = 0

THUMBNAIL_DIR = "thumbnail"
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

def extract_episode_number(text):
    match = re.search(r'(?:EP|Ep|ep|e)[\s._-]*(\d{1,3})', text)
    return int(match.group(1)) if match else None

async def progress_bar(current, total, message, status="Uploading"):
    now = time.time()
    percentage = current * 100 / total
    progress = round(20 * current / total)
    bar = "█" * progress + "░" * (20 - progress)
    speed = current / (now - message.date.timestamp() + 1)
    eta = (total - current) / (speed + 1)
    text = f"""╭━━━━❰ ᴘʀᴏɢʀᴇss ʙᴀʀ ❱━➣
┣⪼ {status}
┣⪼ 🗃️ Sɪᴢᴇ: {round(current / 1024 / 1024, 2)} MB | {round(total / 1024 / 1024, 2)} MB
┣⪼ ⏳️ Dᴏɴᴇ : {round(percentage, 1)}%
┣⪼ 🚀 Sᴩᴇᴇᴅ: {round(speed / 1024 / 1024, 2)} MB/s
┣⪼ ⏰️ Eᴛᴀ: {int(eta)}s
╰━━━━━━━━━━━━━━━➣
{bar}"""
    try:
        await message.edit(text)
    except:
        pass

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        f"👋 Bienvenue sur le Bot de renommage !\n\n📦 Version : {BOT_VERSION}\n\nCommandes disponibles :\n/start\n/seq_start\n/seq_stop\n/stop\n/set_mode [video|doc]\n/auto_mode [on|off]\n/stats\n/info (en réponse à un fichier)\n/show_thumb"
    )

@app.on_message(filters.command("stats"))
async def stats(client, message):
    mode = "Vidéo" if SEND_AS_VIDEO else "Document" if SEND_AS_VIDEO is False else "Automatique"
    thumb = "Oui" if CURRENT_THUMB else "Non"
    auto = "Activé" if AUTO_MODE else "Désactivé"
    await message.reply(
        f"📊 **Statistiques :**\n\n"
        f"📁 Fichiers envoyés : `{FILES_SENT}`\n"
        f"🎬 Mode d'envoi : `{mode}`\n"
        f"🖼 Miniature : `{thumb}`\n"
        f"⚙️ Mode auto : `{auto}`"
    )

@app.on_message(filters.command("auto_mode"))
async def toggle_auto_mode(client, message):
    global AUTO_MODE
    if len(message.command) < 2:
        await message.reply("❌ Utilisez `/auto_mode on` ou `/auto_mode off`.")
        return
    mode = message.command[1].lower()
    AUTO_MODE = mode == "on"
    await message.reply(f"✅ Mode auto {'activé' if AUTO_MODE else 'désactivé'}.")

@app.on_message(filters.command("set_mode"))
async def set_mode(client, message):
    global SEND_AS_VIDEO
    if len(message.command) < 2:
        await message.reply("❌ Utilisez `/set_mode video` ou `/set_mode doc`", quote=True)
        return
    mode = message.command[1].lower()
    if mode == "video":
        SEND_AS_VIDEO = True
        await message.reply("✅ Mode d'envoi : Vidéo")
    elif mode == "doc":
        SEND_AS_VIDEO = False
        await message.reply("✅ Mode d'envoi : Document")
    else:
        await message.reply("❌ Mode inconnu.")

@app.on_message(filters.command("seq_start"))
async def start_sequence(client, message):
    global SEQUENCE_MODE, RECEIVED_FILES, RENAME_MODE
    SEQUENCE_MODE = True
    RENAME_MODE = False
    RECEIVED_FILES = []
    await message.reply("✅ Séquence démarrée. Envoyez vos fichiers maintenant.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Stop", callback_data="stop_seq")]]))

@app.on_message(filters.command("seq_stop"))
async def stop_sequence(client, message):
    global SEQUENCE_MODE, RENAME_MODE
    SEQUENCE_MODE = False
    if RECEIVED_FILES:
        RENAME_MODE = True
        await message.reply("🛑 Séquence arrêtée. Envoyez le nom souhaité. Exemple :\nExemple : baby {1} VF")
    else:
        await message.reply("❌ Aucun fichier reçu pendant la séquence.")

@app.on_message(filters.command("stop"))
async def stop_copy(client, message):
    global SEQUENCE_MODE, RECEIVED_FILES, RENAME_MODE
    SEQUENCE_MODE = False
    RECEIVED_FILES = []
    RENAME_MODE = False
    await message.reply("🛑 Copie interrompue.")

@app.on_message(filters.command("info"))
async def info_file(client, message):
    target = message.reply_to_message
    if target and (target.document or target.video):
        media = target.document or target.video
        file_name = media.file_name or "Inconnu"
        text = (
            f"📄 **Nom :** `{file_name}`\n"
            f"📦 **Taille :** {round(media.file_size / 1024 / 1024, 2)} MB\n"
            f"🎬 **Type :** {'Vidéo' if target.video else 'Document'}"
        )
        await message.reply(text)
    else:
        await message.reply("❌ Répondez à un fichier vidéo/document.")

@app.on_message(filters.command("show_thumb"))
async def show_thumb(client, message):
    path = os.path.join(THUMBNAIL_DIR, "thumbnail.jpg")
    if os.path.exists(path):
        await message.reply_photo(photo=path, caption="🖼️ Miniature actuelle")
    else:
        await message.reply("❌ Aucune miniature définie.")

@app.on_message(filters.photo)
async def set_thumbnail(client, message):
    global CURRENT_THUMB
    path = os.path.join(THUMBNAIL_DIR, "thumbnail.jpg")
    CURRENT_THUMB = await message.download(file_name=path)
    await message.reply("✅ Miniature définie.")

@app.on_callback_query()
async def handle_buttons(client, callback_query):
    global PENDING_FILE
    data = callback_query.data

    if data == "stop_seq":
        global SEQUENCE_MODE, RENAME_MODE
        SEQUENCE_MODE = False
        RENAME_MODE = True
        await callback_query.message.edit_text("🛑 Séquence arrêtée. Envoyez le nom souhaité. Exemple :\nExemple : baby {1} VF")
        return

    if not PENDING_FILE:
        await callback_query.message.edit_text("❌ Aucun fichier à traiter.")
        return

    if data == "confirm_send":
        await send_with_progress(client, PENDING_FILE, PENDING_FILE.new_name)
        await callback_query.message.edit_text("✅ Fichier envoyé.")
        PENDING_FILE = None
    elif data == "cancel_send":
        await callback_query.message.edit_text("❌ Envoi annulé.")
        PENDING_FILE = None

@app.on_message(filters.document | filters.video)
async def receive_files(client, message):
    global SEQUENCE_MODE, RECEIVED_FILES, PENDING_FILE

    if SEQUENCE_MODE:
        RECEIVED_FILES.append(message)
        await message.reply("📥 Fichier reçu.")
        return

    if AUTO_MODE:
        file_name = message.document.file_name if message.document else message.video.file_name
        ep = extract_episode_number(file_name)
        template = f"AutoFile {ep or 'X'}"
        new_name = template + os.path.splitext(file_name or "")[1]
        await send_with_progress(client, message, new_name)
        return

    PENDING_FILE = message
    file_name = message.document.file_name if message.document else message.video.file_name
    ep = extract_episode_number(file_name) or 1
    ext = os.path.splitext(file_name or "")[1]
    suggested_name = f"video {ep}{ext}"
    PENDING_FILE.new_name = suggested_name

    preview = f"✏️ Nom prévu : `{suggested_name}`\nSouhaitez-vous l'envoyer ?"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Envoyer", callback_data="confirm_send"),
         InlineKeyboardButton("❌ Annuler", callback_data="cancel_send")]
    ])
    await message.reply(preview, reply_markup=buttons)

async def send_with_progress(client, msg, filename=None):
    global FILES_SENT
    media = msg.document or msg.video
    name = filename or media.file_name or "file.bin"
    ext = os.path.splitext(name)[1]
    if not ext:
        ext = ".mp4" if msg.video else ".bin"
        name += ext

    progress_msg = await msg.reply("⬇️ Téléchargement...")

    async def download_progress(current, total):
        await progress_bar(current, total, progress_msg, status="Downloading")

    path = await msg.download(progress=download_progress)
    if not path or not os.path.exists(path):
        await progress_msg.edit_text("❌ Téléchargement échoué.")
        return

    await client.send_chat_action(msg.chat.id, ChatAction.UPLOAD_DOCUMENT)

    async def upload_progress(current, total):
        await progress_bar(current, total, progress_msg, status="Uploading")

    is_video = SEND_AS_VIDEO if SEND_AS_VIDEO is not None else bool(msg.video)

    kwargs = {
        "chat_id": msg.chat.id,
        "file_name": name,
        "progress": upload_progress
    }
    if CURRENT_THUMB and os.path.exists(CURRENT_THUMB):
        kwargs["thumb"] = CURRENT_THUMB

    try:
        if is_video and msg.video:
            await client.send_video(video=path, **kwargs)
        else:
            await client.send_document(document=path, **kwargs)
    finally:
        if os.path.exists(path):
            os.remove(path)

    FILES_SENT += 1
    await progress_msg.edit_text("✅ Fichier envoyé.")

async def process_files(client, message):
    global RECEIVED_FILES, RENAME_INFO
    for msg in RECEIVED_FILES:
        file_name = RENAME_INFO['template'].replace("{1}", str(RENAME_INFO["ep"]))
        await send_with_progress(client, msg, file_name)
        RENAME_INFO["ep"] += 1
    RECEIVED_FILES = []

if __name__ == "__main__":
    app.run()
