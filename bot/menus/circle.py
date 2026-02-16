
import asyncio
from aiogram.utils.i18n import gettext as _
from aiogram import Router, F
from aiogram import types
from tempfile import NamedTemporaryFile


circle_router = Router()


@circle_router.message(F.video)
async def handle_start(message: types.Message):
    bot_message = await message.reply(
        text=_("processing_msg"),
        parse_mode="html"
    )

    video = message.video

    file = await message.bot.get_file(video.file_id)

    with (
        NamedTemporaryFile(suffix=".mp4") as input_file,
        NamedTemporaryFile(suffix=".mp4") as output_file
    ):

        await message.bot.download_file(file.file_path, input_file.name)

        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-y",
            "-i", input_file.name,
            "-vf", "crop=min(in_w\\,in_h):min(in_w\\,in_h),scale=640:640",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            output_file.name
        )
        await process.communicate()

        await message.reply_video_note(
            video_note=types.FSInputFile(output_file.name),
            duration=min(video.duration, 60),
            length=640
        )
        await bot_message.delete()
