import os
import discord
from discord.ext import commands
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

groq = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# Letzte Nachrichten als Gesprächskontext
conversation = []

MAX_HISTORY = 20


@bot.event
async def on_ready():
    print(f"🤖 Eingeloggt als {bot.user}")
    print(f"📺 KI-Kanal: {CHANNEL_ID}")


@bot.event
async def on_message(message):

    # Eigene Nachrichten ignorieren
    if message.author == bot.user:
        return

    # Nur der KI-Kanal
    if message.channel.id != CHANNEL_ID:
        return

    # Leere Nachrichten ignorieren
    if not message.content.strip():
        return

    # Nachricht speichern
    conversation.append({
        "role": "user",
        "content": f"{message.author.display_name}: {message.content}"
    })

    # Nur die letzten 20 Nachrichten behalten
    if len(conversation) > MAX_HISTORY:
        conversation.pop(0)

    async with message.channel.typing():

        try:

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Du bist ein freundlicher KI-Discord-Bot. "
                        "Du befindest dich auf einem Discord-Server. "
                        "Antworte locker und natürlich. "
                        "Wenn jemand Deutsch schreibt, antworte auf Deutsch. "
                        "Beziehe dich auf vorherige Nachrichten, wenn es sinnvoll ist. "
                        "Sei nicht unnötig lang."
                    )
                }
            ]

            messages.extend(conversation)

            response = groq.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                max_tokens=1000
            )

            answer = response.choices[0].message.content

            # KI-Antwort speichern
            conversation.append({
                "role": "assistant",
                "content": answer
            })

            if len(conversation) > MAX_HISTORY:
                conversation.pop(0)

            # Discord-Limit beachten
            if len(answer) <= 2000:
                await message.reply(answer)

            else:
                for i in range(0, len(answer), 2000):
                    await message.channel.send(
                        answer[i:i + 2000]
                    )

        except Exception as error:

            print("Fehler:", error)

            await message.reply(
                "⚠️ Die KI konnte gerade nicht antworten."
            )


bot.run(DISCORD_TOKEN)
