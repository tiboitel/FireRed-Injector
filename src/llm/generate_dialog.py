from llama_cpp import Llama
from .character_card import CharacterCard
from .prompt_builder import PromptBuilder
from random import uniform

llm = Llama(
    model_path="/mnt/sda1/text-generation-webui/models/llama2-13b-tiefighter.Q4_K_M.gguf",
    n_gpu_layers=30,
    n_ctx=2048,
    backend='cuda',
    use_mmap=True,
    use_mlock=True,
    streaming=False
)

card = CharacterCard(
    name="Bug Catcher Timmy",
    age=10,
    location="Viridian Forest Entrance",
    traits=["enthusiastic", "naive", "excitable"],
    motivation="prove Bug-types are the best"
)


builder = PromptBuilder(few_shot="""
Example:
  “Gotta catch ’em all!” → “My net’s ready — bugs, show your might!”
  “I’ll battle any Trainer!” → “Challengers, step up — Bug mastery awaits!”
""")

def generate_dialogue(original_line):
    prompt = builder.build(card, original_line)
    result = llm(
        prompt,
        max_tokens=60,
        temperature=0.9,
        top_k=50,
        top_p=0.92,
        repeat_penalty=1.2,
        stop=["\n"]
    )
    return result["choices"][0]["text"].strip().strip("“”")
