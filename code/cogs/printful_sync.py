import base64
import os
import aiohttp
import discord
from discord.ext import commands

class PrintfulSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "Ejected-Media")
        self.repo_name = os.getenv("GITHUB_REPO_NAME", "printful-assets")
        self.target_channel_id = int(os.getenv("PRINTFUL_CHANNEL_ID", "0"))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        # Check if message is in the designated community center channel and has attachments
        if message.channel.id == self.target_channel_id and message.attachments:
            async with aiohttp.ClientSession() as session:
                for attachment in message.attachments:
                    if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                        # Download image bytes
                        image_bytes = await attachment.read()
                        encoded_content = base64.b64encode(image_bytes).decode("utf-8")
                        
                        file_path = f"products/{attachment.filename}"
                        commit_message = f"Add Printful asset {attachment.filename} via Discord by {message.author}"
                        
                        success = await self.push_to_github(session, file_path, encoded_content, commit_message)
                        if success:
                            await message.add_reaction("✅")
                        else:
                            await message.add_reaction("❌")

    async def push_to_github(self, session: aiohttp.ClientSession, path: str, content: str, message: str) -> bool:
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Check if file already exists to get its sha (required for updates)
        async with session.get(url, headers=headers) as resp:
            sha = None
            if resp.status == 200:
                data = await resp.json()
                sha = data.get("sha")

        payload = {
            "message": message,
            "content": content
        }
        if sha:
            payload["sha"] = sha

        async with session.put(url, headers=headers, json=payload) as resp:
            return resp.status in (201, 200)

async def setup(bot):
    await bot.add_cog(PrintfulSync(bot))
