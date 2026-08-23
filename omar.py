import discord
from discord import app_commands
from discord.ext import commands
import os
import re
import math
from typing import Optional

# --- CONFIGURATION ---
TOKEN = os.getenv("TOKEN")            
TARGET_USER_ID = 1241496820455313533 
PROBOT_ID = 282859044593598464       

# --- PERMISSIONS & ROOMS CONFIG ---
ALLOWED_ADMIN_IDS = [1488072348107014244, 1241496820455313533, 1242950158052884511] 
STOCK_CHANNEL_ID = 1539813725865775224  
BUY_CHANNEL_ID = 1539796754428465183    
REFUND_CHANNEL_ID = 1539813213158506566 

# --- CUSTOM EMOJIS ---
EMOJIS = {
    "cart": "<:Shoppingcart:1539798150167142490>",       
    "pin": "<a:ping:1539797253567418489>",        
    "price": "<a:MoneySoaring:1539798937345589308>",      
    "stock": "📦",      
    "info": "<a:dev:1539799868782940231>",        
    "card": "<a:BlackMoneyCard:1323318279955152956>",       
    "gift": "<a:Oc_Giveway:1539800809691283546>",       
    "success": "<:yes:1539801006899204116>",    
    "error": "<:No:1539801163736686622>",      
    "warning": "<a:aha:1539423195374026798>",    
    "reason": "<:emoji_164:1539801927955648552>"      
}

# Zdt hna "tutorial" f kulla منتج باش تحط فيه lien dyal l-video dyalo
PRODUCTS = {
    "autobuy": {"name": "Project Auto Buy", "price": 37500000, "type": "Source Code", "file": "Auto Buy.txt", "stock": 3, "tutorial": "https://youtu.be/h4qCmWpSMZ8"},
    "shop": {"name": "Project Systeme Shop", "price": 27500000, "type": "Source Code", "file": "Systeme Shop.txt", "stock": 3, "tutorial": "https://youtu.be/XobMtzyP8jE"},
    "broadcast": {"name": "Project Broadcast", "price": 25000000, "type": "Source Code", "file": "Broadcast.txt", "stock": 3, "tutorial": "https://youtu.be/Jhw6q8OcivE"},
    "giveaway": {"name": "Project Giveaway", "price": 20000000, "type": "Source Code", "file": "Giveaway.txt", "stock": 3, "tutorial": "https://youtu.be/5SWUG9360kM"},
    "invites": {"name": "Project Invites", "price": 17500000, "type": "Source Code", "file": "Invites.txt", "stock": 3, "tutorial": "https://youtu.be/RN6Has9NKp4"},
    "Tax": {"name": "Project Tax", "price": 15000000, "type": "Source Code", "file": "Tax.txt", "stock": 3, "tutorial": "https://youtu.be/usveduNlrm4"},
    "Coins": {"name": "Project Coins", "price": 12500000, "type": "Source Code", "file": "Coins.txt", "stock": 3, "tutorial": "https://youtu.be/Nk10PIzlfbU"}
}

pending_orders = {}

def get_probot_price(net_price):
    return math.ceil(net_price / 0.95)

class ShopBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        await self.tree.sync()
        activity = discord.Streaming(
            name="Discord.gg/Octopus-s",
            url="https://www.twitch.tv/discord"
        )
        await self.change_presence(status=discord.Status.online, activity=activity)
        print(f"{EMOJIS['success']} Bot Online as: {self.user}")

bot = ShopBot()

def is_product_available(file_path):
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

# --- HELPER FUNCTION: UPDATE STOCK CHANNEL AUTOMATICALLY ---
async def update_stock_display():
    if STOCK_CHANNEL_ID == 0:
        return
    channel = bot.get_channel(STOCK_CHANNEL_ID)
    if not channel:
        try:
            channel = await bot.fetch_channel(STOCK_CHANNEL_ID)
        except Exception:
            return

    try:
        await channel.purge(limit=10)
    except Exception:
        pass

    embed = discord.Embed(title=f"{EMOJIS['cart']} Shop Stock", color=discord.Color.blue())
    for key, info in PRODUCTS.items():
        file_ok = is_product_available(info["file"])
        if file_ok and info["stock"] > 0:
            stock_display = str(info["stock"])
        else:
            stock_display = "0 (Hors stock)"
        
        embed.add_field(
            name=f"{EMOJIS['pin']} {info['name']} (`{key}`)",
            value=f"{EMOJIS['price']} **Price:** ${info['price']}\n{EMOJIS['stock']} **Stock:** {stock_display}\n{EMOJIS['info']} **Type:** {info['type']}",
            inline=False
        )
    
    await channel.send(embed=embed)

# --- COMMAND /STOCK ---
@bot.tree.command(name="stock", description="Voir les produits disponibles en stock")
async def stock(interaction: discord.Interaction):
    if STOCK_CHANNEL_ID != 0 and interaction.channel_id != STOCK_CHANNEL_ID:
        await interaction.response.send_message(
            f"{EMOJIS['error']} Cette commande ne peut être utilisée que dans le salon <#{STOCK_CHANNEL_ID}>.", 
            ephemeral=True
        )
        return

    embed = discord.Embed(title=f"{EMOJIS['cart']} Shop Stock", color=discord.Color.blue())
    for key, info in PRODUCTS.items():
        file_ok = is_product_available(info["file"])
        if file_ok and info["stock"] > 0:
            stock_display = str(info["stock"])
        else:
            stock_display = "0 (Hors stock)"
        
        embed.add_field(
            name=f"{EMOJIS['pin']} {info['name']} (`{key}`)",
            value=f"{EMOJIS['price']} **Price:** ${info['price']}\n{EMOJIS['stock']} **Stock:** {stock_display}\n{EMOJIS['info']} **Type:** {info['type']}",
            inline=False
        )
    await interaction.response.send_message(embed=embed)

# --- COMMAND /BUY ---
@bot.tree.command(name="buy", description="Acheter un produit")
@app_commands.choices(product=[
    app_commands.Choice(name="Project Auto Buy", value="autobuy"),
    app_commands.Choice(name="Project Systeme Shop", value="shop"),
    app_commands.Choice(name="Project Broadcast", value="broadcast"),
    app_commands.Choice(name="Project Giveaway", value="giveaway"),
    app_commands.Choice(name="Project Invites", value="invites"),
    app_commands.Choice(name="Project Tax", value="Tax"),
    app_commands.Choice(name="Project Coins", value="Coins")
])
async def buy(interaction: discord.Interaction, product: str, quantity: int = 1):
    if BUY_CHANNEL_ID != 0 and interaction.channel_id != BUY_CHANNEL_ID:
        await interaction.response.send_message(
            f"{EMOJIS['error']} Cette commande ne peut être utilisée que dans le salon <#{BUY_CHANNEL_ID}>.", 
            ephemeral=True
        )
        return

    if quantity <= 0:
        await interaction.response.send_message(f"{EMOJIS['error']} La quantité doit être supérieure à 0.", ephemeral=True)
        return
        
    prod_info = PRODUCTS.get(product)
    if not prod_info or not is_product_available(prod_info["file"]):
        await interaction.response.send_message(f"{EMOJIS['error']} Produit actuellement indisponible en stock !", ephemeral=True)
        return

    if prod_info["stock"] < quantity:
        await interaction.response.send_message(
            f"{EMOJIS['error']} Stock insuffisant ! Stock disponible: **{prod_info['stock']}**", 
            ephemeral=True
        )
        return

    total_price = prod_info["price"] * quantity
    amount_to_send = get_probot_price(total_price)
    user_id = interaction.user.id
    
    pending_orders[user_id] = {
        "product": product,
        "quantity": quantity,
        "total_price": total_price,
        "amount_to_send": amount_to_send
    }

    embed = discord.Embed(title=f"{EMOJIS['card']} Transfert Requis", color=discord.Color.gold())
    embed.description = (
        f"Produit: **{quantity}x {prod_info['name']}**\n"
        f"Prix Net: **${total_price:.2f}**\n"
        f"Montant à envoyer (avec taxe ProBot 5%): **${amount_to_send}**\n\n"
        f"Pour payer, tapez la commande ou utilisez `/credits`:\n"
        f"`c <@{TARGET_USER_ID}> {amount_to_send}`"
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- COMMAND /GIVE (TA3WID / REPLACEMENT) ---
@bot.tree.command(name="give", description="Donner manuellement un produit à un utilisateur (Ta3wid)")
@app_commands.choices(product=[
    app_commands.Choice(name="Project Auto Buy", value="autobuy"),
    app_commands.Choice(name="Project Systeme Shop", value="shop"),
    app_commands.Choice(name="Project Broadcast", value="broadcast"),
    app_commands.Choice(name="Project Giveaway", value="giveaway"),
    app_commands.Choice(name="Project Invites", value="invites"),
    app_commands.Choice(name="Project Tax", value="Tax"),
    app_commands.Choice(name="Project Coins", value="Coins")
])
async def give(
    interaction: discord.Interaction, 
    user: discord.User, 
    product: str, 
    quantity: int = 1, 
    reason: Optional[str] = None
):
    if REFUND_CHANNEL_ID != 0 and interaction.channel_id != REFUND_CHANNEL_ID:
        await interaction.response.send_message(
            f"{EMOJIS['error']} Cette commande ne peut être utilisée que dans le salon <#{REFUND_CHANNEL_ID}>.", 
            ephemeral=True
        )
        return

    if interaction.user.id not in ALLOWED_ADMIN_IDS:
        await interaction.response.send_message(
            f"{EMOJIS['error']} Vous n'avez pas la permission d'utiliser cette commande.", 
            ephemeral=True
        )
        return

    prod_info = PRODUCTS.get(product)
    if not prod_info or not is_product_available(prod_info["file"]):
        await interaction.response.send_message(f"{EMOJIS['error']} Fichier produit introuvable ou vide !", ephemeral=True)
        return

    if prod_info["stock"] < quantity:
        await interaction.response.send_message(
            f"{EMOJIS['error']} Stock insuffisant ! Stock disponible: **{prod_info['stock']}**", 
            ephemeral=True
        )
        return

    reason_str = f"\n{EMOJIS['reason']} **Raison:** {reason}" if reason else ""
    tutorial_link = prod_info.get("tutorial", "")
    tutorial_str = f"\n\n🎥 **Tutoriel Video:** {tutorial_link}" if tutorial_link else ""

    dm_embed = discord.Embed(title=f"{EMOJIS['gift']} Livraison Manuelle / Ta3wid", color=discord.Color.green())
    dm_embed.description = f"Un administrateur vous a envoyé **{quantity}x {prod_info['name']}**.{reason_str}{tutorial_str}\n\n📁 **Le fichier source est joint ci-dessous.**"

    try:
        file_attachment = discord.File(prod_info["file"], filename=f"{prod_info['name']}.py")
        await user.send(embed=dm_embed, file=file_attachment)
        
        prod_info["stock"] -= quantity

        await interaction.response.send_message(
            f"{EMOJIS['success']} **{quantity}x {prod_info['name']}** envoyé(s) avec succès à {user.mention} en MP ! (Stock restant: {prod_info['stock']})"
        )
        
        # Auto refresh stock channel
        await update_stock_display()
    except Exception as e:
        await interaction.response.send_message(
            f"{EMOJIS['warning']} Impossible d'envoyer le MP à {user.mention} (DMs fermés). Error: `{e}`",
            ephemeral=True
        )

# --- DETECTION PROBOT ---
@bot.event
async def on_message(message: discord.Message):
    if message.author.id == PROBOT_ID:
        clean_text = re.sub(r'[*\_~`]', '', message.content or "")

        if "has transferred" in clean_text.lower():
            match_amount = re.search(r"transferred\s*\$?(\d+(?:\.\d+)?)", clean_text, re.IGNORECASE)

            if match_amount:
                amount = float(match_amount.group(1))

                is_target = False
                if str(TARGET_USER_ID) in message.content or any(u.id == TARGET_USER_ID for u in message.mentions):
                    is_target = True

                if not is_target:
                    return

                matched_user_id = None
                for uid, order in list(pending_orders.items()):
                    if abs(order["total_price"] - amount) < 0.6 or abs(order["amount_to_send"] - amount) < 0.6:
                        matched_user_id = uid
                        break

                if matched_user_id:
                    order = pending_orders.pop(matched_user_id)
                    prod_info = PRODUCTS[order["product"]]

                    try:
                        user = await bot.fetch_user(matched_user_id)
                        if is_product_available(prod_info["file"]) and user and prod_info["stock"] >= order["quantity"]:
                            file_attachment = discord.File(prod_info["file"], filename=f"{prod_info['name']}.py")
                            
                            tutorial_link = prod_info.get("tutorial", "")
                            tutorial_msg = f"\n🎥 **Tutoriel Video:** {tutorial_link}" if tutorial_link else ""

                            await user.send(
                                content=f"{EMOJIS['success']} **Paiement Reçu avec succès!**\nVoici votre fichier source pour **{prod_info['name']}**:{tutorial_msg}",
                                file=file_attachment
                            )
                            
                            prod_info["stock"] -= order["quantity"]

                            await message.channel.send(f"{EMOJIS['success']} Merci <@{matched_user_id}> ! Vos fichiers ont été envoyés en MP.")
                            
                            # Auto refresh stock channel
                            await update_stock_display()
                        else:
                            await message.channel.send(f"{EMOJIS['warning']} Erreur lors de la récupération du fichier ou stock épuisé pour <@{matched_user_id}>.")
                    except Exception as e:
                        await message.channel.send(f"{EMOJIS['warning']} Impossible d'envoyer les fichiers en MP à <@{matched_user_id}> (DMs fermés).")

    await bot.process_commands(message)

bot.run(TOKEN)
