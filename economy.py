import random
import discord
import asyncio
from discord.ext import commands
from database import get_player, save_player

class EconomyGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cf")
    async def coin_flip(self, ctx, amount: str):
        p = get_player(ctx.author.id)
        if p["has_starter"] == 0:
            await ctx.send("❌ | Get a companion first via `s start`."); return
        bet = p["balance"] if amount.lower() == "all" else int(amount)
        if bet <= 0 or bet > p["balance"]:
            await ctx.send("❌ | Check your funds or bet amount."); return

        if random.choice(["heads", "tails"]) == "heads":
            p["balance"] += bet
            color = 0x4caf50
            desc = f"🪙 landed on **HEADS**! You won **`+{bet:,}`**"
        else:
            p["balance"] -= bet
            color = 0xf44336
            desc = f"🪙 landed on **TAILS**... You lost **`-{bet:,}`**"
            
        save_player(ctx.author.id, p)
        emb = discord.Embed(title="🪙 COINFLIP MATCH", description=desc, color=color)
        emb.add_field(name="Balance", value=f"`{p['balance']:,}` sycoizz")
        await ctx.send(embed=emb)

    @commands.command(name="slots", aliases=["slot"])
    async def slots_game(self, ctx, bet: int):
        p = get_player(ctx.author.id)
        if bet <= 0 or p["balance"] < bet:
            await ctx.send("❌ | Invalid bet."); return
        emojis = ["🍒", "🍋", "💎", "👑"]
        r1, r2, r3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
        grid = f"🎰 **[ {r1} | {r2} | {r3} ]**"
        
        if r1 == r2 == r3:
            payout = bet * 5
            p["balance"] += payout
            emb = discord.Embed(title="🎰 SLOTS JACKPOT", description=f"{grid}\n🎉 Match 3! `+{payout:,}`", color=0x4caf50)
        elif r1 == r2 or r2 == r3 or r1 == r3:
            payout = int(bet * 1.5)
            p["balance"] += payout
            emb = discord.Embed(title="🎰 SLOTS WIN", description=f"{grid}\n✨ Match 2! `+{payout:,}`", color=0x8bc34a)
        else:
            p["balance"] -= bet
            emb = discord.Embed(title="🎰 SLOTS BLANK", description=f"{grid}\n❌ No match! `-{bet:,}`", color=0xf44336)
            
        save_player(ctx.author.id, p)
        emb.add_field(name="Wallet", value=f"`{p['balance']:,}`")
        await ctx.send(embed=emb)

    @commands.command(name="bj", aliases=["blackjack"])
    async def blackjack_game(self, ctx, bet: int):
        p = get_player(ctx.author.id)
        if bet <= 0 or p["balance"] < bet:
            await ctx.send("❌ | Invalid bet resources."); return

        def calc(hand):
            v, aces = 0, 0
            for card in hand:
                if card in ["J", "Q", "K"]: v += 10
                elif card == "A": aces += 1; v += 11
                else: v += int(card)
            while v > 21 and aces: v -= 10; aces -= 1
            return v

        deck = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"] * 4
        p_hand, d_hand = [random.choice(deck), random.choice(deck)], [random.choice(deck), random.choice(deck)]
        msg = await ctx.send(f"🃏 **BJ** | Hand: {p_hand} (`{calc(p_hand)}`) vs Dealer: [{d_hand[0]}, ❓]\nType `hit` or `stand`.")

        def check(m): return m.author.id == ctx.author.id and m.content.lower() in ["hit", "stand"] and m.channel.id == ctx.channel.id

        while calc(p_hand) < 21:
            try:
                choice = await self.bot.wait_for("message", check=check, timeout=20.0)
                if choice.content.lower() == "hit":
                    p_hand.append(random.choice(deck))
                    if calc(p_hand) > 21: break
                    await msg.edit(content=f"🃏 **BJ** | Hand: {p_hand} (`{calc(p_hand)}`) vs Dealer: [{d_hand[0]}, ❓]\nType `hit` or `stand`.")
                else: break
            except asyncio.TimeoutError: break

        p_score, d_score = calc(p_hand), calc(d_hand)
        if p_score > 21:
            p["balance"] -= bet
            await ctx.send(f"💥 BUSTED! Score: `{p_score}`. Loss: `-{bet:,}`.")
        else:
            while calc(d_hand) < 17: d_hand.append(random.choice(deck))
            d_score = calc(d_hand)
            if d_score > 21 or p_score > d_score:
                p["balance"] += bet
                await ctx.send(f"🎉 WIN! `{p_score}` vs `{d_score}`. Gain: `+{bet:,}`!")
            elif d_score > p_score:
                p["balance"] -= bet
                await ctx.send(f"❌ LOSS! `{p_score}` vs `{d_score}`. Loss: `-{bet:,}`.")
            else:
                await ctx.send(f"🤝 PUSH! Tied stance at `{p_score}`.")
        save_player(ctx.author.id, p)

    @commands.command(name="crash")
    async def crash_game(self, ctx, bet: int):
        p = get_player(ctx.author.id)
        if bet <= 0 or p["balance"] < bet:
            await ctx.send("❌ | Check wager inputs."); return
        p["balance"] -= bet
        save_player(ctx.author.id, p)

        multiplier, crash_point = 1.0, round(random.uniform(1.1, 4.5), 2)
        if random.random() < 0.15: crash_point = 1.0
        
        msg = await ctx.send(f"📈 Rocket rising... Multiplier: `1.0x`\nType `cashout` to claim win!")
        cashed_out = False

        for _ in range(30):
            await asyncio.sleep(1.2)
            if multiplier >= crash_point: break
            multiplier = round(multiplier + random.uniform(0.1, 0.4), 2)
            if multiplier >= crash_point: multiplier = crash_point; break
            
            try:
                def chk(m): return m.author.id == ctx.author.id and m.content.lower() == "cashout" and m.channel.id == ctx.channel.id
                await self.bot.wait_for("message", check=chk, timeout=0.2)
                cashed_out = True; break
            except asyncio.TimeoutError:
                try: await msg.edit(content=f"📈 Rocket rising... Multiplier: `{multiplier}x`\nType `cashout` now!")
                except: pass

        if cashed_out:
            win = int(bet * multiplier)
            p = get_player(ctx.author.id)
            p["balance"] += win
            save_player(ctx.author.id, p)
            await ctx.send(f"💰 CASHOUT! Pulled at `{multiplier}x`. Won: `+{win:,}` sycoizz!")
        else:
            await ctx.send(f"💥 CRASHED at `{crash_point}x`! You lost your bet of `{bet:,}`.")

    @commands.command(name="roulette", aliases=["rl"])
    async def roulette_game(self, ctx, choice: str, bet: int):
        p = get_player(ctx.author.id)
        choice = choice.lower()
        if choice not in ["red", "black", "green"] or bet <= 0 or p["balance"] < bet:
            await ctx.send("❌ | Setup format error. Use: `s rl [red/black/green] [bet]`"); return
        spin = random.randint(0, 36)
        res_color = "green" if spin == 0 else ("red" if spin % 2 == 0 else "black")
        if choice == res_color:
            payout = bet * (35 if res_color == "green" else 2)
            p["balance"] += payout
            await ctx.send(f"🎡 Settled on **{spin} ({res_color.upper()})**! Win: `+{payout:,}` sycoizz!")
        else:
            p["balance"] -= bet
            await ctx.send(f"🎡 Settled on **{spin} ({res_color.upper()})**... Lost: `-{bet:,}` sycoizz.")
        save_player(ctx.author.id, p)

    @commands.command(name="dice")
    async def dice_game(self, ctx, bet: int):
        p = get_player(ctx.author.id)
        if bet <= 0 or p["balance"] < bet:
            await ctx.send("❌ | Invalid dice wager asset."); return
        p_roll, b_roll = random.randint(2, 12), random.randint(2, 12)
        if p_roll > b_roll:
            p["balance"] += bet
            await ctx.send(f"🎲 Your Roll: `{p_roll}` vs Sycoizz Roll: `{b_roll}`. Won `+{bet:,}`!")
        elif b_roll > p_roll:
            p["balance"] -= bet
            await ctx.send(f"🎲 Your Roll: `{p_roll}` vs Sycoizz Roll: `{b_roll}`. Lost `-{bet:,}`.")
        else:
            await ctx.send(f"🎲 Tied roll at `{p_roll}`. Pushed stance.")
        save_player(ctx.author.id, p)

    @commands.command(name="give")
    async def transfer_coins(self, ctx, target: discord.User, amount: int):
        p = get_player(ctx.author.id)
        if amount <= 0 or p["balance"] < amount:
            await ctx.send("❌ | Insufficient liquid core balance."); return
        t = get_player(target.id)
        if t["has_starter"] == 0:
            await ctx.send("❌ | Recipient profile unregistered."); return
        p["balance"] -= amount
        t["balance"] += amount
        save_player(ctx.author.id, p)
        save_player(target.id, t)
        await ctx.send(f"🤝 Wired `{amount:,}` sycoizz cleanly to **{target.name}**!")

async def setup(bot):
    await bot.add_cog(EconomyGames(bot))
      
