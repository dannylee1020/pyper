# Pyper
Pyper is a knowledge-driven data generation framework for building unbiased, high quality synthetic dataset.

## Overview
Pyper is built upon [Stanford Alpaca](https://github.com/tatsu-lab/stanford_alpaca/tree/main), with some changes in data generation logics. It is capable of supplying domain knowledge to the data generation process, overcoming inherent bias in LLM's knowledge base.

Set OpenAI API Key first.

```
    export OPENAI_API_KEY=<your-api-key>
```

To run with default arguments:

```
    python generate_instructions.py
```

To supply example domain knowledge:

```
    python generate_instructions.py -k ./source/knowledge.txt
```

For the list of all arguments, run:

```
    python generate_instructions.py --help
```

## Citation
```
@misc{alpaca,
  author = {Rohan Taori and Ishaan Gulrajani and Tianyi Zhang and Yann Dubois and Xuechen Li and Carlos Guestrin and Percy Liang and Tatsunori B. Hashimoto },
  title = {Stanford Alpaca: An Instruction-following LLaMA model},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/tatsu-lab/stanford_alpaca}},
}
```