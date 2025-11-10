def bread(text: str) -> str:
    """Wrap text with bread emojis."""
    return f"🍞 {text} 🍞"

def toast(text: str) -> str:
    """Make text uppercase with flame."""
    return text.upper() + " 🔥"

def repeat(text: str, n=3) -> str:
    """Repeat bread pattern n times."""
    return ("🥖" * n) + f" {text} " + ("🥖" * n)

def donut(text: str) -> str:
    """Replace vowels with donuts."""
    vowels = "aeiouAEIOU"
    return "".join("🍩" if ch in vowels else ch for ch in text)

def random_fact():
    """Return a random bread fact."""
    import random
    facts = [
        "Bread was invented at least 12,000 years ago.",
        "The most expensive bread costs over $1,500.",
        "Bread goes stale faster in the fridge.",
        "Sourdough contains friendly bacteria.",
        "In France, a law controls how baguettes are baked."
    ]
    return random.choice(facts)

def easter():
    """Easter egg."""
    return "🥷 You unlocked the Bread Ninja secret."

def breadify(text: str) -> str:
    """
    Wraps the given text between tasty bread emojis.
    Special Easter Egg:
    - If text is "developer", it prints the developer's name instead.
    """
    
    # Easter egg
    if text.lower() == "developer":
        return "🍞 Venkat 🍞"
    
    return f"🍞 {text} 🍞"
