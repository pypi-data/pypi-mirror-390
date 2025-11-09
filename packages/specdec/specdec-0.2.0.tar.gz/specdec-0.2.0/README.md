# SpecDec: A Speculative Decoding Benchmarking Tool

## Overview

SpecDec is a Python-based command-line tool designed for benchmarking the performance of speculative decoding against conventional autoregressive generation. Speculative decoding is an optimization technique that utilizes a smaller, faster model to generate draft tokens, which are then verified by a larger, more powerful model. This can result in significant latency improvements for text generation tasks.

This tool provides a standardized interface for evaluating the speedup achieved with different model configurations and hyperparameters.

## Installation

To install the latest stable version from the Python Package Index (PyPI):

```bash
pip install specdec
```

## Usage

The `specdec` command-line tool is the primary entry point for running benchmarks.

### Command Structure

```bash
specdec --num_sample_tok <value> [OPTIONS]
```

### Example

Here is an example of how to run a benchmark using `gpt2` as the small model and `gpt2-xl` as the large model:

```bash
specdec \
    --small_model "gpt2" \
    --big_model "gpt2-xl" \
    --prompt "Quantum computing is a field that" \
    --max_new_tok 100 \
    --num_sample_tok 5 \
    --device "cuda" \
    --seed 42
```

The tool will output the time taken for both autoregressive and speculative generation, the generated text from both methods, and the calculated speedup.

## Command-Line Arguments

The following arguments are available to configure the benchmark:

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--small_model` | `string` | No | `"gpt2"` | The identifier for the smaller draft model from Hugging Face. |
| `--big_model` | `string` | No | `"gpt2-xl"`| The identifier for the larger verification model. |
| `--prompt` | `string` | No | `"Artificial intelligence is"` | The input prompt for text generation. |
| `--max_new_tok` | `integer` | No | `50` | The maximum number of new tokens to generate. |
| `--num_sample_tok`| `integer` | Yes | - | The number of tokens to sample from the small model at each step. |
| `--device` | `string` | No | `"cuda"` | The device to run the models on (`"cuda"` or `"cpu"`). |
| `--[no-]sample` | `flag` | No | `True` | Toggles sampling for the autoregressive generation baseline. |
| `--seed` | `integer` | No | `None` | A random seed for ensuring reproducibility. |


To view all available options, run:

```bash
specdec --help
```
