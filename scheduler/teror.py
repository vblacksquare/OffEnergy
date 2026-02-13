
from bot import bot
import random


async def update_teror():
    msg = random.choice(architect_teasing)
    for i in [8509826947, 667632489]:
        await bot.send_message(
            text=msg,
            chat_id=i
        )


architect_teasing =[
    "Опять вставила в рендер 2D-людей из нулевых? Твой скилл застрял в текстурах 2004 года 🤣💀",
]