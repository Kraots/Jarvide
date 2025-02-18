import disnake
import io
import aiohttp

from disnake.ext import commands
from typing import TypeVar


def add_lines(content: str) -> None:
    enumerated = list(enumerate(content.split("\n")))
    lines = []
    for number, line in enumerated:
        number = ("0" * (len(str(enumerated[-1][0])) - len(str(number)))) + str(number)
        line = f"\n{number} | {line}"
        lines.append(line)

    return "".join(lines)

Self = TypeVar("Self")


class IncorrectInstance(Exception):
    """User passed incorrect instance"""

    def __init__(self, argument: str) -> None:
        super().__init__(f"{argument}")


class File:
    def __init__(self, *, filename, content, bot) -> None:
        self.filename = filename
        self.bot = bot
        self.content = content

        self.setup()

    def setup(self) -> None:
        if hasattr(self.filename, "content"):
            self.filename = self.filename.content
        if hasattr(self.content, "content"):
            self.content = self.content.content
        if hasattr(self.content, "decode"):
            self.content = self.content.decode("utf-8")
        self.content = self.content.replace("```", "`\u200b`\u200b`\u200b")

    async def get_message(self) -> disnake.Message:
        f = io.StringIO(self.content)

        message = await self.bot.channel.send(file=disnake.File(fp=f, filename=self.filename))  # type: ignore
        return message

    @classmethod
    async def from_url(
        cls: Self,
        *,
        bot: commands.Bot,
        url,
    ) -> Self:

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.read()
                filename = url.split("?")[0].split("/")[-1]
        return cls(
            filename=filename,
            content=content,
            bot=bot,
        )

    async def to_url(self) -> str:
        return (await self.get_message()).attachments[0].url

    async def to_real(self) -> disnake.Attachment:
        return (await self.get_message()).attachments[0]


class EmbedFactory:
    @staticmethod
    def ide_embed(
        ctx: commands.Context, description: str, format_: str = "yaml"
    ) -> disnake.Embed:
        return (
            disnake.Embed(
                title="Jarvide Text Editor",
                description=f"```{format_}\n{description}```",
                timestamp=ctx.message.created_at,
            )
            .set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            .set_footer(
                text="The official jarvide text editor and ide. Expires in 5min"
            )
        )

    @staticmethod
    def code_embed(ctx: commands.Context, code: str, path: str, format_: str = "py"):
        return (
            disnake.Embed(
                title="Jarvide Text Editor",
                description=f"**{path}**\n```{format_}\n{code}```",
                timestamp=ctx.message.created_at,
            )
            .set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            .set_footer(text="The official jarvide text editor and ide")
        )


async def get_info(file_: File) -> str:
    real_file = await file_.to_real()

    return (
        f"Opened file: {real_file.filename}"
        f"\nType: {real_file.content_type}"
        f"\nSize: {real_file.size // 1000} KB ({real_file.size:,} bytes)"
    )
