import time
import argparse
import torch
import numpy as np
from .decoder import SpecDecoder

def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def benchmark_methods(decoder, prompt, max_new_tok, num_sample_tok=None, do_sample=True):
    start_time = time.time()
    normal_output = decoder.autoregressive_gen(prompt, max_new_tok, do_sample=do_sample)
    normal_time = time.time() - start_time
    
    if num_sample_tok is not None:
        start_time = time.time()
        spec_output = decoder.spec_gen(prompt, max_new_tok, num_sample_tok)
        spec_time = time.time() - start_time
        return normal_output, normal_time, spec_output, spec_time
    
    return normal_output, normal_time, None, None

def main():
    parser = argparse.ArgumentParser(description="Benchmark speculative decoding.")
    parser.add_argument("--small_model", type=str, default="gpt2", help="Small model for speculative decoding.")
    parser.add_argument("--big_model", type=str, default="gpt2-xl", help="Big model for speculative decoding.")
    parser.add_argument("--prompt", type=str, default="Artificial intelligence is", help="Prompt for text generation.")
    parser.add_argument("--max_new_tok", type=int, default=50, help="Maximum number of new tokens to generate.")
    parser.add_argument("--num_sample_tok", type=int, required=True, help="Number of tokens to sample from the small model.")
    parser.add_argument("--device", type=str, default="cuda", help="Device to run models on (e.g., 'cuda', 'cpu').")
    parser.add_argument("--sample", action=argparse.BooleanOptionalAction, default=True, help="Enable/disable sampling for autoregressive generation.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    args = parser.parse_args()

    if args.seed is not None:
        set_seed(args.seed)

    print("=" * 50)
    print("Speculative Decoding Benchmark")
    print(f"Small model: {args.small_model}")
    print(f"Big model: {args.big_model}")
    print(f"Prompt: '{args.prompt}'")
    print(f"Max new tokens: {args.max_new_tok}")
    print(f"Num sample tokens: {args.num_sample_tok}")
    print(f"Device: {args.device}")
    print(f"Sampling: {args.sample}")
    print(f"Seed: {args.seed}")
    print("=" * 50)

    decoder = SpecDecoder(args.small_model, args.big_model, device=args.device)
    
    normal_output, normal_time, spec_output, spec_time = benchmark_methods(
        decoder, args.prompt, args.max_new_tok, args.num_sample_tok, do_sample=args.sample
    )

    print("\n--- Autoregressive Generation ---")
    print(f"Time: {normal_time:.3f}s")
    print(f"Output: {normal_output}")

    print("\n--- Speculative Decoding ---")
    print(f"Time: {spec_time:.3f}s")
    print(f"Output: {spec_output}")

    if spec_time > 0:
        speedup = normal_time / spec_time
        print(f"\nSpeedup: {speedup:.2f}x")
    
    print("=" * 50)


if __name__ == "__main__":
    main()