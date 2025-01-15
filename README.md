# Pyper

Pyper is a framework for generating high-quality synthetic data specifically designed for LLM finetuning. It combines several research approaches to create diverse and high-quality training datasets.

## Features

- **General Seed Generation**: Generate seed data across various academic disciplines using an approach inspired by GLAN
- **Knowledge-Driven Generation**: Create datasets based on specific domain knowledge by supplying ground truth information
- **Data Fission**: Expand small seed datasets through iterative generation using LLM, inspired by self-instruct and evol-instruct methodologies

## Installation

Pyper uses Poetry for dependency management. To install:

```bash
# Install poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clone the repository
git clone https://github.com/yourusername/pyper.git
cd pyper

# Install dependencies
poetry install
```

## Project Structure

```
pyper/
├── fission/           # Data fission implementation
├── gen/              # Core generation modules
│   ├── batch/        # Batch processing utilities
│   ├── prompt/       # Prompt templates
│   └── src/          # Source generators
└── source/           # Source data and examples
```

## Usage

### Environment Setup

First, set your OpenAI API key:

```bash
export OPENAI_API_KEY=your-openai-api-key
```

### General Seed Generation

Generate seed data for a specific academic discipline:

```bash
poetry run python main.py generate --discipline mathematics --num-tasks 50
```

Example disciplines include mathematics, physics, chemistry, etc. Use `--help` to see all options.

### Knowledge-Driven Generation

Generate data using specific domain knowledge:

```bash
poetry run python main.py generate_with_knowledge \
    --name project_name \
    --knowledge-path ./path/to/knowledge.txt \
    --num-tasks 50
```

The knowledge file should contain the ground truth information in plain text format.

### Data Fission

Expand an existing seed dataset:

```bash
poetry run python main.py generate \
    --name dataset_name \
    --num-tasks 50 \
    --output-dir ./output
```

To see all available options, use `--help` flag

## Research & Citations

Pyper's implementation is based on several key research papers:

```bibtex
@misc{selfinstruct,
  title={Self-Instruct: Aligning Language Model with Self Generated Instructions},
  author={Wang, Yizhong and Kordi, Yeganeh and Mishra, Swaroop and Liu, Alisa and Smith, Noah A. and Khashabi, Daniel and Hajishirzi, Hannaneh},
  journal={arXiv preprint arXiv:2212.10560},
  year={2022}
}

@misc{alpaca,
  author = {Rohan Taori and Ishaan Gulrajani and Tianyi Zhang and Yann Dubois and Xuechen Li and Carlos Guestrin and Percy Liang and Tatsunori B. Hashimoto },
  title = {Stanford Alpaca: An Instruction-following LLaMA model},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/tatsu-lab/stanford_alpaca}},
}

@article{luo2023wizardmath,
  title={WizardMath: Empowering Mathematical Reasoning for Large Language Models via Reinforced Evol-Instruct},
  author={Luo, Haipeng and Sun, Qingfeng and Xu, Can and Zhao, Pu and Lou, Jianguang and Tao, Chongyang and Geng, Xiubo and Lin, Qingwei and Chen, Shifeng and Zhang, Dongmei},
  journal={arXiv preprint arXiv:2308.09583},
  year={2023}
}
```

Additional research:
- [Generalized Instruction Tuning (GLAN)](https://arxiv.org/abs/2402.13064)
