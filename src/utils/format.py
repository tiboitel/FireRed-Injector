def format_dialogue(text: str) -> str:
    # Normalize punctuation
    t = text.replace("–", "-").replace("’", "\"")
    # Break into chars for inserting control codes
    chars = list(t)
    i = 25
    toggle = True  # True = newline, False = formfeed
    while i < len(chars):
        # Find next whitespace at or after index i
        j = next((k for k in range(i, len(chars)) if chars[k].isspace()), -1)
        if j == -1:
            break
        chars[j] = "\n" if toggle else "\f"
        toggle = not toggle
        i = j + 25
    return "".join(chars)

