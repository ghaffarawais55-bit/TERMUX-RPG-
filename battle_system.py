import random
import asyncio
import discord

POKEMON_DATA = {
    "Charmander": {"type": "Fire", "hp": 120, "moves": ["Scratch", "Ember", "Flame Burst"]},
    "Squirtle": {"type": "Water", "hp": 140, "moves": ["Tackle", "Water Gun", "Aqua Tail"]},
    "Bulbasaur": {"type": "Grass", "hp": 130, "moves": ["Tackle", "Vine Whip", "Razor Leaf"]},
    "Sycoizz": {"type": "Supreme", "hp": 250, "moves": ["Quantum Blast", "Overlord Matrix", "SUPREME APOCALYPSE"]}
}

ANIMATIONS = {
    "Scratch": "⚔️ *[━╋━   ]* Swiping claws slicing forward!",
    "Ember": "🔥 *[ ⚡☄️✨  ]* Sparks erupt and cascade outwards!",
    "Flame Burst": "💥 *[ 🔥🔥🔥 ]* An explosive dome of fire engulfs everything!",
    "Tackle": "🏃‍♂️ *[ 💨💥   ]* Ramming forward at high velocity!",
    "Water Gun": "💧 *[ ━━━━🌊 ]* A high pressure stream shoots across!",
    "Aqua Tail": "🐋 *[ 🌊🌀✨ ]* Whirling currents slap down heavily!",
    "Vine Whip": "🌿 *[ ➰➰💥 ]* Thorny emerald extensions lash the area!",
    "Razor Leaf": "🍃 *[ 🗡️🗡️🍃 ]* Razor sharp foliage slices the wind!",
    "Quantum Blast": "🔮 *[ 🌀⚡✨ ]* Distorting reality into a condensed energy vortex!",
    "Overlord Matrix": "👑 *[ 💻☣️🔱 ]* Injecting malicious code protocols into the target!",
    "SUPREME APOCALYPSE": "👁️‍🗨️ *[ 🌌☠️💥☠️🌌 ]* THE SPACE-TIME CONTINUUM COLLAPSES UNDER ULTIMATE POWER!"
}

def get_damage(move: str, p_level: int) -> int:
    base = random.randint(10, 20) + (p_level * 2)
    if move in ["Flame Burst", "Aqua Tail", "Razor Leaf", "Overlord Matrix"]:
        base += random.randint(10, 18)
    elif move == "SUPREME APOCALYPSE":
        base += random.randint(55, 85)
    return base
  
