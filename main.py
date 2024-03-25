import discord
from discord.ext import commands
import pyttsx3
from recuperation_lien_yt import download_video
from recuperation_lien_yt import download_and_split_video


from token_id import *

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Bot pret à etre utiliser')

# # Evenement qui permet au bot d'envoyer bonjour si on écrit bonjour dans un channel du serveur discord
# @bot.event
# async def on_message(message : discord.Message):
#     if message.author.bot == True:
#         return
    
#     if "bonjour" in message.content:
#         await message.channel.send("bonjour")
    
# # Commande qui permet au bot d'envoyer Hello World si on écrit !hello
# @bot.command()
# async def hello(ctx : commands.Context):
#     return await ctx.send("Hello World !")

# Commande pour supprimer des messages 
@bot.command()
async def delete_message(ctx : commands.Context, amount : int = 1) -> discord.Message:

    is_in_private_message = ctx.guild is None and isinstance(ctx.author, discord.User)
    if is_in_private_message == True:
        return await ctx.send("Vous ne pouvez pas utiliser cette en commande en MP")
    
    has_permission = ctx.author.guild_permissions.manage_messages
    if not has_permission:
        return await ctx.send("Vous n'avez pas les permissions pour cette commande")
    
    is_limit_reached = amount > 100
    if is_limit_reached == True:
        return await ctx.send("Vous ne pouvez pas supprimer + de 100 messages")
    
    is_text_channel = isinstance(ctx.channel, discord.TextChannel)
    if not is_text_channel:
        return await ctx.send("Vous devez appeler cette commande depuis un salon textuel")
    
    await ctx.channel.purge(limit=amount+1)

    return await ctx.send(f"{amount} messages ont été supprimés")

# Commande pour ban un membre avec 2 paramètres : le nom du membre à bannir et la raison 
@bot.command()
async def ban(ctx : commands.Context, membre : discord.Member, *, reason: str = ""):
    is_in_private_message = ctx.guild is None and isinstance(ctx.author, discord.User)
    if is_in_private_message:
        return await ctx.send("Cette commande ne peut être utiliser en MP")

    has_permission = ctx.author.guild_permissions.ban_members
    if not has_permission:
        return await ctx.send("Vous n'avez pas les permissions pour bannir un membre")
    
    is_bannable = ctx.author.top_role > membre.top_role
    if not is_bannable:
        return await ctx.send("Vous ne pouvez pas bannir ce membre")
    
    if reason == "":
        reason = "Aucune raison définie"
    
    await membre.ban(reason=reason)

    return await ctx.send(f"{membre.name} a été banni pour {reason}")

# Commande pour kick un membre avec 2 paramètres : le nom du membre à bannir et la raison 
@bot.command()
async def kick(ctx : commands.Context, membre : discord.Member, *, reason: str = ""):
    is_in_private_message = ctx.guild is None and isinstance(ctx.author, discord.User)
    if is_in_private_message:
        return await ctx.send("Cette commande ne peut être utiliser en MP")

    has_permission = ctx.author.guild_permissions.ban_members
    if not has_permission:
        return await ctx.send("Vous n'avez pas les permissions pour cette commande")
    
    is_bannable = ctx.author.top_role > membre.top_role
    if not is_bannable:
        return await ctx.send("Vous ne pouvez pas kick ce membre")
    
    if reason == "":
        reason = "Aucune raison définie"
    
    await membre.kick(reason=reason)

    return await ctx.send(f"{membre.name} a été kick pour {reason}")

# Commande pour unban un membre
@bot.command()
async def unban(ctx : commands.Context, membre : discord.Member, *, reason: str = ""):
    is_in_private_message = ctx.guild is None and isinstance(ctx.author, discord.User)
    if is_in_private_message:
        return await ctx.send("Cette commande ne peut être utiliser en MP")
    
    has_permission = ctx.author.guild_permissions.ban_members
    if not has_permission:
        return await ctx.send("Vous n'avez pas les permissions pour cette commande")
    
    banned_users = [ban_entry async for ban_entry in ctx.guild.bans()]
    member_name, member_discriminater = membre.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminater):
            await ctx.guild.unban(user, reason=reason)
            return await ctx.send(f"{user.name} a été débanni")
        
        return await ctx.send(f"{user.name} n'a pas été trouvé")
    
# Commande pour changer le pseudo d'un utilisateur
@bot.command()
async def nick(ctx : commands.Context, membre : discord.Member, *, nickname: str = None) -> discord.Message:
    is_in_private_message = ctx.guild is None and isinstance(ctx.author, discord.User)
    if is_in_private_message:
        return await ctx.send("Cette commande ne peut être utiliser en MP")
    
    has_permission = ctx.author.guild_permissions.manage_nicknames
    if not has_permission:
        return await ctx.send("Vous n'avez pas les permissions pour cette commande")
    
    is_member_nickable = ctx.author.top_role > membre.top_role
    if not is_member_nickable:
        return await ctx.send("Vous ne pouvez pas nick ce membre")
    
    await membre.edit(nick=nickname)

    if nickname is None:
        return await ctx.send(f"Le pseudo de {membre.name} a été retiré")
    
    return await ctx.send(f"Le pseudo de {membre.name} a été défini sur {nickname}")

# Commande pour faire rejoindre le bot dans un salon vocal
@bot.command()
async def join(ctx : commands.Context):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Vous devez être dans un canal vocal pour que je puisse vous rejoindre !")

# Commande pour faire sortir le bot d'un salon vocal
@bot.command()
async def leave(ctx : commands.Context):
    voice_client = ctx.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("J'ai quitté le canal vocal.")
    else:
        await ctx.send("Je ne suis pas connecté à un canal vocal.")


engine = pyttsx3.init()

# Commande pour faire parler le bot avec le texte entré
@bot.command()
async def dis(ctx : commands.Context, *, text_a_dire):
    engine.say(text_a_dire)
    engine.runAndWait()

# Commande pour télécharger une vidéo youtube 
@bot.command()
async def download_youtube_video(ctx, video_url: str):
    output_path = "video_youtube" # Dossier où sera stocké la vidéo
    success, message = await download_video(video_url, output_path)
    await ctx.send(message)

# Commande qui télécharge une vidéo youtube en plusieurs les extraits vidéo de 1min
@bot.command()
async def split_youtube_video(ctx, video_url: str):
    output_folder = "video_youtube"  # Dossier où seront stockés les extraits vidéo
    success, message = await download_and_split_video(video_url, output_folder)
    await ctx.send(message)

if __name__ == "__main__":
    bot.run(token_id)