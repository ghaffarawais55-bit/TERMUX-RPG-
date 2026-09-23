import sys
import types
import os
import random
import asyncio
import discord
from discord.ext import commands
from database import init_db, get_player, save_player
from battle_system import POKEMON_DATA, ANIMATIONS, get_damage

# Structural compatibility support override layer
sys.modules['audioop'] = types.ModuleType('audioop')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=["s ", "S ", "s", "S"], intents=intents, help_command=None)

@bot.event
async def on_ready():
    init_db()
    try:
        await bot.load_extension("economy")
        print("📦 Modular OwO Economy Node Linked Successfully.")
    except Exception as e:
        print(f"⚠️ Extension mapping failure: {e}")
    print("==================================================")
    print("🚀 SYCOIZZ FULL RPG TERMUX ENGINE ONLINE AND READY")
    print("==================================================")

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    content = message.content
    if content.lower().startswith("s "):
        message.content = "s" + content[1:]
    await bot.process_commands(message)

@bot.command(name="help")
async def help_menu(ctx):
    emb = discord.Embed(title="📜 SYCOIZZ RPG SYSTEM UTILITIES", color=0x00abc9)
    emb.add_field(name="🎒 Pokémon Battling", value="• `s start` ─ Pick companion.\n• `s battle` ─ Wild match loop.\n• `s challenge @user` ─ PvP match loop.\n• `s hint` ─ Dynamic luck node.", inline=False)
    emb.add_field(name="🛒 Shop & Currency", value="• `s bal` ─ Data metrics.\n• `s shop` ─ Purchase blueprints.\n• `s buy [item]` ─ Buy items/gems.", inline=False)
    emb.add_field(name="🎲 OwO Casino Core", value="• `s cf [amt]` • `s slots [amt]` • `s bj [amt]`\n• `s crash [amt]` • `s rl [color] [amt]` • `s dice [amt]`", inline=False)
    await ctx.send(embed=emb)

@bot.command(name="balance", aliases=["bal", "profile"])
async def show_profile(ctx, target: discord.User = None):
    u = target or ctx.author
    p = get_player(u.id)
    if p["has_starter"] == 0:
        await ctx.send("❌ | Unregistered user profile configuration."); return
    emb = discord.Embed(title=f"📊 {u.name}'s Ledger Matrix", color=0x00e676)
    emb.add_field(name="💰 Cash Wallet", value=f"`{p['balance']:,}` sycoizz", inline=False)
    emb.add_field(name="💎 Luck Gems", value=f"`{p['gems']}` active nodes", inline=True)
    active_pet = p["active_team"] if p["active_team"] else "None"
    emb.add_field(name="⚔️ Loaded Pet", value=f"`{active_pet}` (Lvl {p['level']})", inline=True)
    await ctx.send(embed=emb)

@bot.command(name="start")
async def choose_starter(ctx):
    p = get_player(ctx.author.id)
    if p["has_starter"] == 1:
        await ctx.send("❌ | Starter companion already bounds onto asset rows."); return
    emb = discord.Embed(title="🌿 PICK YOUR STARTER COMPANION 🌿", description="Type selection name below:", color=0x4caf50)
    emb.add_field(name="🔥 Charmander", value="Type: Fire", inline=True)
    emb.add_field(name="💧 Squirtle", value="Type: Water", inline=True)
    emb.add_field(name="🍃 Bulbasaur", value="Type: Grass", inline=True)
    await ctx.send(embed=emb)

    def chk(m): return m.author.id == ctx.author.id and m.content.lower() in ["charmander", "squirtle", "bulbasaur"] and m.channel.id == ctx.channel.id
    try:
        m = await bot.wait_for("message", check=chk, timeout=30.0)
        sel = m.content.lower().capitalize()
        p["pets"].append(sel); p["active_team"] = [sel]; p["has_starter"] = 1
        save_player(ctx.author.id, p)
        await ctx.send(f"🎉 | Adventure online! Linked companion path: **{sel}**!")
    except asyncio.TimeoutError: await ctx.send("⏱️ | System context selection frame expired.")

@bot.command(name="shop")
async def shop_marketplace(ctx):
    emb = discord.Embed(title="🛒 MATRIX RPG SHOP", color=0xff9800)
    emb.add_field(name="💎 Core Luck Gems (`s buy gem`)", value="Cost: `50,000` sycoizz\n*Increases the probability parameters of getting premium solutions via s hint commands.*", inline=False)
    emb.add_field(name="🦖 Supreme Sycoizz Token (`s buy sycoizz`)", value="Cost: `5,000,000` sycoizz\n*Unlocks the legendary ultimate entity equipped with SUPREME APOCALYPSE actions.*", inline=False)
    await ctx.send(embed=emb)

@bot.command(name="buy")
async def purchase_node(ctx, *, item: str):
    p = get_player(ctx.author.id)
    item = item.lower()
    if "gem" in item:
        if p["balance"] < 50000: await ctx.send("❌ | Insufficient balance."); return
        p["balance"] -= 50000; p["gems"] += 1
        await ctx.send("💎 | Luck Gem bound successfully! Checked onto internal stats profile rows.")
    elif "sycoizz" in item:
        if p["balance"] < 5000000: await ctx.send("❌ | Requires 5,000,000 coins."); return
        p["balance"] -= 5000000; p["pets"].append("Sycoizz"); p["active_team"] = ["Sycoizz"]
        await ctx.send("🦖 | UNLOCKED SUPREME SYCOIZZ PET ENEMY BLUEPRINT MATRIX!")
    else: await ctx.send("❌ | Unknown shop stock item designation target.")
    save_player(ctx.author.id, p)

@bot.command(name="hint")
async def lucky_hint_engine(ctx):
    p = get_player(ctx.author.id)
    if p["has_starter"] == 0: return
    base_luck = 30 + (p["gems"] * 12)
    roll = random.randint(1, 100)
    if roll <= base_luck:
        loot = random.randint(10000, 35000)
        p["balance"] += loot
        await ctx.send(f"🔮 **HINT SEARCH SUCCESSFUL!** Your gem footprint modified algorithms. Found hidden cache: `+{loot:,}` sycoizz!")
    else:
        await ctx.send("💨 | Hint lookup failed. Try socketing more luck gems into character core fields.")
    save_player(ctx.author.id, p)

# ========================================================
# ⚔️ ADVANCED TURN BATTLE SUB-ROUTINE ENGINE
# ========================================================
async def execute_battle_loop(ctx, p1_id, p1_pet, p2_id, p2_pet, is_pvp=False):
    d1, d2 = POKEMON_DATA[p1_pet], POKEMON_DATA[p2_pet]
    hp1, hp2 = d1["hp"], d2["hp"]
    pa1, pa2 = get_player(p1_id), get_player(p2_id)
    
    await ctx.send(f"⚔️ **MATCH START:** `{p1_pet}` (HP: {hp1}) vs `{p2_pet}` (HP: {hp2})")
    
    while hp1 > 0 and hp2 > 0:
        # Turn 1 Action
        await ctx.send(f"🎭 **{p1_pet}** moves array: `{d1['moves']}`. Type move target:")
        def chk1(m): return m.author.id == p1_id and m.content.strip() in d1["moves"] and m.channel.id == ctx.channel.id
        try:
            m1 = await bot.wait_for("message", check=chk1, timeout=30.0)
            mv1 = m1.content.strip()
            dmg1 = get_damage(mv1, pa1["level"])
            
            # Formatted split-line block sequence
            hp2 -= dmg1
            if hp2 < 0:
                hp2 = 0
                
            await ctx.send(f"{ANIMATIONS.get(mv1, '💥')} -> Dealt `{dmg1}` damage!")
        except asyncio.TimeoutError: 
            await ctx.send("⏱️ | Inactivity default swipe.")
            hp1 = 0
            break
        
        if hp2 <= 0: break
        await asyncio.sleep(1.0)
        
        # Turn 2 Action
        if is_pvp:
            await ctx.send(f"🎭 **{p2_pet}** moves array: `{d2['moves']}`. Type move target:")
            def chk2(m): return m.author.id == p2_id and m.content.strip() in d2["moves"] and m.channel.id == ctx.channel.id
            try:
                m2 = await bot.wait_for("message", check=chk2, timeout=30.0)
                mv2 = m2.content.strip()
                dmg2 = get_damage(mv2, pa2["level"])
            except asyncio.TimeoutError: 
                hp2 = 0
                break
        else:
            mv2 = random.choice(d2["moves"])
            dmg2 = get_damage(mv2, 1)
            
        # Formatted split-line block sequence
        hp1 -= dmg2
        if hp1 < 0:
            hp1 = 0
            
        await ctx.send(f"{ANIMATIONS.get(mv2, '💥')} -> Target counter structural attack dealt `{dmg2}` damage!")
        await ctx.send(f"📊 **STATUS MATRIX:** `{p1_pet}`: `{hp1}` HP | `{p2_pet}`: `{hp2}` HP")
        await asyncio.sleep(1.0)

    return hp1, hp2

@bot.command(name="battle")
async def wild_pokemon_fight(ctx):
    p = get_player(ctx.author.id)
    if not p["active_team"]: await ctx.send("❌ | Set starter pet companion active."); return
    p_pet = p["active_team"]
    wild_options = ["Charmander", "Squirtle", "Bulbasaur"]
    w_pet = random.choice(wild_options)
    
    hp1, hp2 = await execute_battle_loop(ctx, ctx.author.id, p_pet, bot.user.id, w_pet, is_pvp=False)
    
    if hp1 > 0:
        prize = random.randint(5000, 15000)
        p["balance"] += prize; p["xp"] += 35
        if p["xp"] >= (p["level"] * 100): p["level"] += 1; await ctx.send("🌟 **LEVEL UP COG TRIGGERED!** Metrics advanced.")
        await ctx.send(f"🏆 **VICTORY!** Decimated wild `{w_pet}` loop. Loot wired: `+{prize:,}` sycoizz!")
    else: await ctx.send("💀 | Your pet was crushed. Rest up profile metrics components.")
    save_player(ctx.author.id, p)

@bot.command(name="challenge")
async def pvp_battle_challenge(ctx, target: discord.User):
    if target.id == ctx.author.id: return
    p1, p2 = get_player(ctx.author.id), get_player(target.id)
    if p1["has_starter"] == 0 or p2["has_starter"] == 0: await ctx.send("❌ | Both users must have profiles."); return
    
    await ctx.send(f"⚔️ **PvP Wager Event:** **{target.name}**, type `accept` to enter match vectors!")
    def chk(m): return m.author.id == target.id and m.content.lower() == "accept" and m.channel.id == ctx.channel.id
    try: await bot.wait_for("message", check=chk, timeout=25.0)
    except asyncio.TimeoutError: await ctx.send("⏱️ | Invitation timed out."); return
    
    hp1, hp2 = await execute_battle_loop(ctx, ctx.author.id, p1["active_team"], target.id, p2["active_team"], is_pvp=True)
    if hp1 > 0: await ctx.send(f"🏆 **PRO-MATCH CONCLUDED:** **{ctx.author.name}** won the prestige arena fight!")
  
