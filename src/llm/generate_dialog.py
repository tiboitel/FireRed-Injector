from llama_cpp import Llama
from random import uniform
import llama_cpp.llama_cpp as cpp

print("Built with CUDA:", cpp.llama_supports_gpu_offload())

llm = Llama(
    model_path="/mnt/sda1/text-generation-webui/models/llama2-13b-tiefighter.Q4_K_M.gguf",
    n_gpu_layers=30,
    n_ctx=2048,
    backend='cuda',
    use_mmap=True,
    use_mlock=True,
    streaming=False
)

# Few-shot examples in Game Boy style
few_shot = """
Example:
  “Gotta catch ’em all!” → “My net’s ready — bugs, show your might!”
  “I’ll battle any Trainer!” → “Challengers, step up — Bug mastery awaits!”
"""

character_card = {
    "name": "Bug Catcher Timmy",
    "age": 10,
    "location": "Viridian Forest Entrance",
    "traits": ["enthusiastic", "naive", "excitable"],
    "motivation": "prove Bug-types are the best"
}

def build_prompt(card, original):
    return (
        f"{few_shot}"
        "\nNow rewrite the line below in the same style:\n"
        f"Character: {card['name']} ({card['age']} y.o.), at {card['location']}. "
        f"Traits: {', '.join(card['traits'])}. Goal: {card['motivation']}.\n\n"
        f"Original: “{original}”\n"
        "Rewrite:"
    )

def generate_dialogue(original_line):
    prompt = build_prompt(character_card, original_line)
    resp = llm(
        prompt,
        max_tokens=60,
        temperature=0.9,
        top_k=50,
        top_p=0.92,
        repeat_penalty=1.2,
        stop=["\n"]
    )
    text = resp["choices"][0]["text"].strip().strip("“”")
    return text

if __name__ == "__main__":
    lines = [
        "I came here with some friends to catch us some BUG POKéMON!",
        "They’re all itching to get into some POKéMON battles!"
    ]
    for line in lines:
        out = generate_dialogue(line)
        print(f"\n→ {out}")

