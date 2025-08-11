import pytest
from pathlib import Path
from src.config.settings import load_settings

@pytest.fixture
def config_path(tmp_path):
    config = """
[extract]
rom_path = "gba_rom/fire_red.gba"
output_path = "data/dialog_map.json"
start_offset = 1191253
end_offset = 1722662

[llm]
model_path = "path/to/your/model"
n_ctx = 4096
temperature = 1.2
top_k = 50
top_p = 0.92
repeat_penalty = 1.1

[character]
name = "The Great Unknown"
age = 27
location = "All over the world"
traits = ["belligerent", "abrupt", "fragile", "angry", "gritty", "dumb", "blunt", "gross", "south park fan", "emotionally unstable", "misguiding", "heavy dark-humor", "funny"]
motivation = [
    "Catch POKéMON by any means necessary—bribery or bruteforce.",
    "Alienate friends with brutal honesty. Chase power, not happiness.",
    "Only give bad advice to others to lead them down the wrong path.",
    "Really like to spread rumors.",
    "Gritty, sharp and funky humor"
]

[ipc]
ipc_dir = "shared_ipc"

[prompt]
few_shot_examples = '''
Example:
Original: Gotta catch ’em all!
Rewrite: Let's get all these fuckers!
Original: I’ll battle any Trainer!
Rewrite: I can beat to dust any kids.
Original: I love my POKéMON!
Rewrite: I love Digimons, yes I'm a psycho, dawg!!!
Original: Hey! I grew my beard for two years.
Rewrite: Yo, wanna touch my spaghetti beard? Mmh.. *insistent glare*
'''
"""
    config_file = tmp_path / "config.toml"
    config_file.write_text(config)
    return config_file

def test_load_settings(config_path):
    settings = load_settings(config_path)
    assert settings.extract.rom_path == Path("gba_rom/fire_red.gba")
    assert settings.extract.output_path == Path("data/dialog_map.json")
    assert settings.extract.start_offset == 1191253
    assert settings.extract.end_offset == 1722662
    assert settings.llm.model_path == Path("path/to/your/model")
    assert settings.llm.n_ctx == 4096
    assert settings.llm.temperature == 1.2
    assert settings.llm.top_k == 50
    assert settings.llm.top_p == 0.92
    assert settings.llm.repeat_penalty == 1.1
    assert settings.character.name == "The Great Unknown"
    assert settings.character.age == 27
    assert settings.character.location == "All over the world"
    assert settings.character.traits == ["belligerent", "abrupt", "fragile", "angry", "gritty", "dumb", "blunt", "gross", "south park fan", "emotionally unstable", "misguiding", "heavy dark-humor", "funny"]
    assert settings.character.motivation == [
        "Catch POKéMON by any means necessary—bribery or bruteforce.",
        "Alienate friends with brutal honesty. Chase power, not happiness.",
        "Only give bad advice to others to lead them down the wrong path.",
        "Really like to spread rumors.",
        "Gritty, sharp and funky humor"
    ]
    assert settings.ipc_dir == Path("shared_ipc")
    print(settings)
    assert settings.few_shot_examples.strip() == '''
Example:
Original: Gotta catch ’em all!
Rewrite: Let's get all these fuckers!
Original: I’ll battle any Trainer!
Rewrite: I can beat to dust any kids.
Original: I love my POKéMON!
Rewrite: I love Digimons, yes I'm a psycho, dawg!!!
Original: Hey! I grew my beard for two years.
Rewrite: Yo, wanna touch my spaghetti beard? Mmh.. *insistent glare*
'''.strip()

