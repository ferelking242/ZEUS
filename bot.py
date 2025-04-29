from pyrogram import Client, filters

# ⚠️ Remplace ces valeurs par les tiennes
API_ID = "23992653"
API_HASH = "ef7ad3a6a3e88b487108cd5242851ed4"
BOT_TOKEN = "7634028476:AAHDjeRCagDKlxtVmRV3SoBBRgAG4nG0tbw"

app = Client(
    "simple_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.private & filters.text)
async def reply_hello(client, message):
    await message.reply("Bonjour !")

app.run()
