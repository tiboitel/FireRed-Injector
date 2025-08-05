from src.llm.character_card import CharacterCard

class PromptBuilder:
    def __init__(self, few_shot: str):
        self.few_shot = few_shot

    def build(self, card: CharacterCard, original: str) -> str:
        return (
            f"As an assistant, you receive an original dialogue line from Pokemon FireRed (US) game.\n"
            f"- You have to rewrite the dialogue as a new original dialogue.\n"
            f"- Use same tone and lexical field of classic 90s POKEMON dialogue.\n"
            f"- You are the following character.\nCharacter: {card.name} ({card.age} y.o.), at {card.location}. "
            f"Traits: {', '.join(card.traits)}. Goal: {card.motivation}.\n\n"
            f"{self.few_shot}\nNow rewrite the line below with the same tone:\n"
            f"Original: “{original}”\nRewrite: ”"
        )

