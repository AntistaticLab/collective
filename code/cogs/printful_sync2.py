import base64
import os
import aiohttp
import discord
from discord.ext import commands

class PrintfulCategorySync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "Ejected-Media")
        self.repo_name = os.getenv("GITHUB_REPO_NAME", "printful-assets")
        
        # Map channel names or keywords to specific Printful repository subfolders
        self.folder_mappings = {
            "deskmats": "products/deskmats",
            "keycaps": "products/keycaps",
            "hoodies": "products/apparel",
            "z-erg": "products/peripherals"
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.attachments:
            return

        # Determine target folder based on channel name or category
        channel_name = message.channel.name.lower()
        category_name = message.channel.category.name.lower() if message.channel.category else ""
        
        target_subfolder = "products/general"
        for key, folder in self.folder_mappings.items():
            if key in channel_name or key in category_name:
                target_subfolder = folder
                break

        async with aiohttp.ClientSession() as session:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp', '.svg']):
                    image_bytes = await attachment.read()
                    encoded_content = base64.b64encode(image_bytes).decode("utf-8")
                    
                    file_path = f"{target_subfolder}/{attachment.filename}"
                    commit_message = f"Sync Printful asset [{attachment.filename}] from #{channel_name} by {message.author}"
                    
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
        
        # Check if file exists to retrieve its sha for updates
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
    await bot.add_cog(PrintfulCategorySync(bot))
