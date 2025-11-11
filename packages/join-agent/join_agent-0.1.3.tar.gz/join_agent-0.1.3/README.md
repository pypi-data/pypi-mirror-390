# Join Agent

LLM-driven intelligent data joining and relationship analysis agent. The JoinAgent uses large language models (LLMs) to analyze table structures, suggest optimal join strategies, and validate the quality of joins between datasets.

## 🌟 Features

Analyze table structures and sample data to identify potential join keys.
Suggest optimal join strategies with reasoning and confidence scores.
Validate join schema compatibility and data overlap.
Supports multiple operations:
    golden_dataset – Identify join keys and build join order across multiple tables to create a golden dataset.
    manual_data_prep – Determine join keys and join type between two tables for manual data preparation.
Integrates with SFN Blueprint’s AI handler for LLM-powered reasoning.
Returns structured join plans including validated join types and overlap percentages.

## 📦 Installation

### Prerequisites
- Python 3.11+
- Git
- [**uv**](https://docs.astral.sh/uv/getting-started/installation/) – A fast Python package and environment manager.
    -   For a quick setup on macOS/Linux, you can use:
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/stepfnAI/join_agent.git
   cd join_agent/
   git checkout review
   ```

2. **Set up the virtual environment and install dependencies**
   This command creates a `.venv` folder in the current directory and installs all required packages.
    ```bash
    uv sync --extra dev
    source .venv/bin/activate
    ```

3. **Clone and install the `sfn_blueprint` dependency:**
    The agent requires the `sfn_blueprint` library. The following commands clone it into a sibling directory and install it in editable mode.
    
   ```bash
   cd ..
   git clone https://github.com/stepfnAI/sfn_blueprint.git
   cd sfn_blueprint
   git switch dev
   uv pip install -e .
   cd ../join_agent
   ```

4. **Set up environment variables**
   ```bash   
   # Optional: Configure LLM provider (default: openai)
   export LLM_PROVIDER="your_llm_provider"
   
   # Optional: Configure LLM model (default: gpt-4.1-mini)
   export LLM_MODEL="your_llm_model"
   
   # Required: Your LLM API key (Note: If LLM provider is opeani then 'export OPENAI_API_KEY', if it antropic 'export ANTROPIC_API_KEY', use this accordingly as per LLM provider )
   export OPENAI_API_KEY="your_llm_api_key"
   ```

## 🚀 Quick Start

### Basic Usage
This will support for detection of join keys from 2 to mutliple datsets
for operation = "golden_dataset" it support for multiple table join
for operation = "manual_data_prep" it will support for only 2 table join

from root directory -
```bash
python examples/goldendataset_usage.py
python examples/manualdataprep_usage.py
```


## 🧪 Testing

```bash
pytest -s tests/test_joinagent.py
```


## 📝 Prompt Management

All LLM prompts used by the JoinAgent are centralized in `src/join_agent/constants.py` for easy review and maintenance.

### Prompt Types
Based upon operations there are 2 kinds of prompts:

- **Golden_dataset_op_prompt**: Template for analyzing join potential between multiple datasets purely based on column metadata
- **Manual_data_prep_prompt**: Template for analyzing join potential between multiple datasets considering column metadata, groupby fields, primary table

### Benefits

- **Easy Review**: All prompts in one location for prompt engineering
- **Version Control**: Track prompt changes alongside code changes
- **Maintainability**: Update prompts without touching business logic
- **Consistency**: Standardized prompt formatting across the agent

## 🏗️ Architecture

The Target Synthesis Agent is built with a modular architecture:

- **Core Components**:
  - `agent.py`: Base agent implementation
  - `models.py`: Data models and schemas
  - `constants.py`: prompts
  - `config.py`: model configurations


- **Dependencies**:
  - `sfn-blueprint`: Core framework and utilities
  - `pydantic`: Data validation

## 📚 Documentation

For detailed documentation, visit: [https://join-agent.readthedocs.io](https://join-agent.readthedocs.io)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

- **Email**: team@stepfunction.ai
- **GitHub**: [https://github.com/stepfnAI/join_agent](https://github.com/stepfnAI/join_agent)
