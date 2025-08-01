class PromptBuilder:
    def __init__(self, few_shot: str):
        self.few_shot = few_shot

    def build(self, card, original: str) -> str:
        return (
            f"{self.few_shot}\nNow rewrite the line below in the same style:\n"
            f"Character: {card.name} ({card.age} y.o.), at {card.location}. "
            f"Traits: {', '.join(card.traits)}. Goal: {card.motivation}.\n\n"
            f"Original: “{original}”\nRewrite:"
        )

