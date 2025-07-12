# Locomo Benchmark for Various Memory Backends

>  This project is originally forked from [mem0-evaluation](https://github.com/mem0ai/mem0/tree/main/evaluation) in commit `393a4fd5a6cfeb754857a2229726f567a9fadf36` 

This project contains the code of running benchmark results on [Locomo dataset](https://github.com/snap-research/locomo/tree/main) with different memory methods:

- langmem
- mem0
- zep
- basic rag
- naive LLM
- Memobase

## Result

- We ran Memobase results and pasted the other methods' result from [Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory](https://arxiv.org/pdf/2504.19413). 

- We mainly report the LLM Judge Sorce (higher is better).

| Method                 | Single-Hop(%) | Multi-Hop(%) | Open Domain(%) | Temporal(%) | Overall(%) |
| ---------------------- | ------------- | ------------ | -------------- | ----------- | ---------- |
| Mem0                   | **67.13**     | 51.15        | 72.93          | 55.51       | 66.88      |
| Mem0-Graph             | 65.71         | 47.19        | 75.71          | 58.13       | 68.44      |
| LangMem                | 62.23         | 47.92        | 71.12          | 23.43       | 58.10      |
| Zep                    | 61.70         | 41.35        | 76.60      | 49.31       | 65.99      |
| OpenAI                 | 63.79         | 42.92        | 62.29          | 21.71       | 52.90      |
| Memobase(*v0.0.32*) | 63.83         | **52.08**    | 71.82          | 80.37   | 70.91  |
| Memobase(*v0.0.37*) | **70.92** | 46.88 | **77.17**   | **85.05** | **75.78** |

> **What is LLM Judge Score?**
>
> Basically, Locomo benchmark offers some long conversations and prepare some questions. LLM Judge Score is to use LLM(*e.g.* OpenAI `gpt-4o`) to judge if the answer generated from memory method is the same as the ground truth, score is 1 if it is, else 0.

We attached the artifacts of Memobase under `fixture/memobase/`:

- v0.0.32
  - `fixture/memobase/results_0503_3000.json`: predicted answers from Memobase Memory
  - `fixture/memobase/memobase_eval_0503_3000.json`: LLM Judge results of predicted answers

- v0.0.37
  - `fixture/memobase/results_0710_3000.json`: predicted answers from Memobase Memory
  - `fixture/memobase/memobase_eval_0710_3000.json`: LLM Judge results of predicted answers

To generate the latest scorings, run:

```bash
python generate_scores.py --input_path="fixture/memobase/memobase_eval_0710_3000.json"
```

Output:

```
Mean Scores Per Category:
          bleu_score  f1_score  llm_score  count         type
category
1             0.3516    0.4629     0.7092    282   single_hop
2             0.4758    0.6423     0.8505    321     temporal
3             0.1758    0.2293     0.4688     96    multi_hop
4             0.4089    0.5155     0.7717    841  open_domain

Overall Mean Scores:
bleu_score    0.3978
f1_score      0.5145
llm_score     0.7578
dtype: float64
```


> ❕ We update the results from Zep team (Zep*). See this [issue](https://github.com/memodb-io/memobase/issues/101) for detail reports and artifacts.
> | Method     | Single-Hop(%) | Multi-Hop(%) | Open Domain(%) | Temporal(%) | Overall(%) |
> | ---------- | ------------- | ------------ | -------------- | ----------- | ---------- |
> | Zep*       | 74.11         | 66.04        | 67.71          | 79.79       | 75.14      |



## 🔍 Dataset

[Download](https://github.com/snap-research/locomo/tree/main/data) the `locomo10.json` file and place it under `dataset/`



## 🚀 Getting Started

### Prerequisites

Create a `.env` file with your API keys and configurations. You must have beflow envs:

```bash
# OpenAI API key for GPT models and embeddings
OPENAI_API_KEY="your-openai-api-key"
```

Below is the detailed requirements

### Memobase

**Deps**

```bash
pip install memobase
```

**Env**

You can find free API key in [Memobase Cloud](https://memobase.io), or [deploy](../../../readme.md) one in your local

```bash
MEMOBASE_API_KEY=XXXXX
MEMOBASE_PROJECT_URL=http://localhost:8019 # OPTIONAL
```

**Command**

```bash
# memorize the data
make run-memobase-add 
# answer the benchmark
make run-memobase-search 
# evaluate the results
py evals.py --input_file results.json --output_file evals.json 
# print the final scores
py generate_scores.py --input_path="evals.json"
```



### Run Mem0

**Deps**

```bash
pip install mem0
```

**Env**

```bash
# Mem0 API keys (for Mem0 and Mem0+ techniques)
MEM0_API_KEY="your-mem0-api-key"
MEM0_PROJECT_ID="your-mem0-project-id"
MEM0_ORGANIZATION_ID="your-mem0-organization-id"
```

**Command**

> Just like the commands of Memobase, but replace `memobase` with `mem0`. See [all commands](#Memory Techniques)



### Run Zep

**Deps**

```bash
pip install zep_cloud
```

**Env**

```bash
ZEP_API_KEY="api-key-from-zep"
```

**Command**

> Just like the commands of Memobase, but replace `memobase` with `zep`. See [all commands](#Memory Techniques)



### Run langmem

**Deps**

```bash
pip install langgraph langmem
```

**Env**

```bash
EMBEDDING_MODEL="text-embedding-3-small"  # or your preferred embedding model
```

**Command**
> Just like the commands of Memobase, but replace `memobase` with `zep`. See [all commands](#Memory Techniques)


### Other methods

The rest methods don't require extra deps/envs.



## Memory Techniques

```bash
# Run Mem0 experiments
make run-memobase-add         # Add memories using Memobase
make run-memobase-search      # Search memories using Memobase

# Run Mem0 experiments
make run-mem0-add         # Add memories using Mem0
make run-mem0-search      # Search memories using Mem0

# Run Mem0+ experiments (with graph-based search)
make run-mem0-plus-add    # Add memories using Mem0+
make run-mem0-plus-search # Search memories using Mem0+

# Run RAG experiments
make run-rag              # Run RAG with chunk size 500
make run-full-context     # Run RAG with full context

# Run LangMem experiments
make run-langmem          # Run LangMem

# Run Zep experiments
make run-zep-add          # Add memories using Zep
make run-zep-search       # Search memories using Zep

# Run OpenAI experiments
make run-openai           # Run OpenAI experiments
```



### 📊 Evaluation

To evaluate results, run:

```bash
python evals.py --input_file [path_to_results] --output_file [output_path]
```

This script:
1. Processes each question-answer pair
2. Calculates BLEU and F1 scores automatically
3. Uses an LLM judge to evaluate answer correctness
4. Saves the combined results to the output file

### 📈 Generating Scores

Generate final scores with:

```bash
python generate_scores.py
```

This script:
1. Loads the evaluation metrics data
2. Calculates mean scores for each category (BLEU, F1, LLM)
3. Reports the number of questions per category
4. Calculates overall mean scores across all categories

Example output:
```
Mean Scores Per Category:
         bleu_score  f1_score  llm_score  count
category                                       
1           0.xxxx    0.xxxx     0.xxxx     xx
2           0.xxxx    0.xxxx     0.xxxx     xx
3           0.xxxx    0.xxxx     0.xxxx     xx

Overall Mean Scores:
bleu_score    0.xxxx
f1_score      0.xxxx
llm_score     0.xxxx
```



## 📁 Project Structure

```
.
├── src/                  # Source code for different memory techniques
│   ├── memobase_client/  # Implementation of the Memobase
│   ├── memzero/          # Implementation of the Mem0 technique
│   ├── openai/           # Implementation of the OpenAI memory
│   ├── zep/              # Implementation of the Zep memory
│   ├── rag.py            # Implementation of the RAG technique
│   └── langmem.py        # Implementation of the Language-based memory
├── metrics/              # Code for evaluation metrics
├── results/              # Results of experiments
├── dataset/              # Dataset files
├── evals.py              # Evaluation script
├── run_experiments.py    # Script to run experiments
├── generate_scores.py    # Script to generate scores from results
└── prompts.py            # Prompts used for the models
```
