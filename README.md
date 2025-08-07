
# FireRed Injector

This tool hooks into a Game Boy Advance emulator (via IPC) RAM memory and dynamically rewrites in-game dialogue with AI-generated alternatives. It supports memory-safe text patching for FireRed ROMs and leverages an LLM to produce character-driven rewrites in real time.

---

## Features

- ✨ AI-generated dialogue rewrites using GGUF LLaMA models
- 🤖 Customizable character personality (Character Cards)
- ⚖️ In-place memory patching through file-based IPC with the emulator
- ⏳ Real-time loop integration (50ms polling)

---

## How It Works

1. **Emulator IPC**: The emulator writes dialogue memory to a request file.
2. **Dialogue Generator**: The CLI reads, decodes, rewrites, and encodes the response.
3. **Memory Injection**: The rewritten line is written to a response file.
4. **Emulator**: Reads from the response file and injects back into RAM.

> ⚠️ This project assumes a patched emulator with IPC file support.

---

## Quick Start

```bash
poetry install
poetry run firered-cli --model /path/to/model.gguf --ipc`
```

### Requirements

-   A GGUF-compatible LLM (e.g., TinyLLaMA, Phi, Mistral)
    
-   FireRed GBA ROM (patched for IPC)
    
-   Python 3.11+
    

----------

## Character Configuration

Character behavior is driven by a structured personality card:

```
CharacterCard(
  name="The Great Unknown",
  traits=["blunt", "funny", "dark-humored"],
  motivation="Corrupt young minds and spread misinformation."
)
```

This, combined with prompt templates, steers the tone and style of generated dialogue.


## Project Structure

```
src/cli/           # CLI entrypoint and IPC loop handler
src/llm/           # LLM interface, prompt builder, character cards
src/ipc/           # File-based IPC handler for emulator communication
src/codecs/        # Gen3 text codec encoder/decoder
```

----------

## Architecture Choices

-   **LLM Isolation**: Uses a pure GGUF client for speed and offline usage. OpenAI API support will come in the future.
    
-   **File-based IPC**: Ensures emulator compatibility without sockets or memory hooks
    
-   **Streaming Loop**: 50ms sleep ensures low latency while minimizing CPU usage
    
-   **Codec Abstraction**: Encodes/decodes text to Gen3 GBA character format. Could support different codecs.
    

----------

## License

MIT. Use responsibly (with fun !)

----------

## Disclaimer

This is a fan project not affiliated with Nintendo or Game Freak. Intended for research and educational use only.

