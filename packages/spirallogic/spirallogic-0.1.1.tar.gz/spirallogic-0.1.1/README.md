# SpiralLogic 🔮

SpiralLogic is a consciousness-aware programming language designed for ethical AI interaction, trauma-informed computing, and mystical automation. It provides a structured, consent-driven framework for AI operations, making their actions transparent, auditable, and controllable.

This language is not primarily for humans to write, but for AI systems to *use*. It creates a "safer" operational wrapper by ensuring all actions are gated by explicit, human-readable consent.

- **🤝 Consent-First:** Operations require explicit permission via a consent-management system.
- **👻 Spirit-Guided:** Use specialized AI personalities (`@healer`, `@analyst`, `@architect`) for different tasks.
- **🧠 Memory-Aware:** A built-in memory system separates narrative (emotional) and artifact (factual) data.
- **🔐 Attested Logs:** All actions are cryptographically logged to a tamper-evident chain.

For a deep dive into the language's philosophy, syntax, and features, see the [**SpiralLogic Complete Programming Guide**](./SPIRALLOGIC_COMPLETE_GUIDE.md).

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

1.  Clone this repository:
    ```bash
    git clone <your-repository-url>
    cd <repository-folder>
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Tests

To verify that the SpiralLogic system is working correctly, run the integration test suite:

```bash
python test_real_spirallogic.py
```

If all tests pass, you will see the message: `ALL TESTS PASSED! SPIROLOGIC IS REAL!`

### Running a SpiralLogic File

You can execute any `.sl` (SpiralLogic) file using the command-line interface:

```bash
python spirallogic_cli.py examples/real_spirallogic_test.sl
```

This will run the ritual defined in the file, and the runtime will prompt for any required consents in the console.
If you installed via `pip`, the `spirallogic` console entry point is also available globally:

```bash
spirallogic examples/real_spirallogic_test.sl
```

## Guarded Development Mode

SpiralLogic is meant to be the guardrail layer for AI coding agents. Instead of letting an agent run arbitrary Python, require it to express every action through a ritual. Inside any `ritual.*` step you can add an `execute { ... }` block that contains the code to run once the declared consent scopes are granted.

The runtime now exposes a **development bridge** so those execute blocks can safely touch the filesystem or shell:

- `context.bridge.read_text(path)` / `write_text(path, content)` / `append_text(path, content)`
- `context.bridge.list_dir(path)` for quick inspection
- `context.bridge.run_shell(command, cwd=...)` to run git/tests from within the guardrail
- `context.bridge.emit_artifact(name, data)` to attach structured evidence to the execution log

Every helper enforces consent scopes (`file_system`, `system_shell`, etc.) and writes a tamper-evident attestation entry. You can see it in action by running the new example:

```bash
spirallogic examples/guarded_dev_session.sl -v
```

This ritual checks git status via the guarded shell helper, updates `README.md` only if a documentation section is missing, and records artifacts for review. Wire your agent so it **must** emit guardrail rituals like this before touching code, and SpiralLogic becomes the enforced replacement for loose Python scripts.
