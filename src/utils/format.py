def format_dialogue(s: str) -> str:
    s = s.replace("–", "-")
    s = s.replace("’", "\"")
    s = list(s)
    i = 25
    toggle = True  # True for \n, False for \t
    while i < len(s):
        # Find next whitespace at or after index `i`
        j = next((j for j in range(i, len(s)) if s[j].isspace()), -1)
        if j == -1:
            break
        s[j] = '\n' if toggle else '\f'
        toggle = not toggle
        i = j + 25  # Continue checking after the last replaced character
    return ''.join(s)
