# Fine Tunning Summary (LLAMA 3 8B base model, A100 4×GPU, took 39.56 min to fine tune.)

## Core Metrics (see Fine-Tuning.png)

- Loss: 0.9456 → 0.9146 (steady decrease; target ~0.5–0.8 for strong convergence)
- Grad norm: 0.508 → 0.527 (stable; healthy range 0.5–0.6)
- Learning rate: 6.07e-05 → 5.30e-05 (scheduled decay, cosine)
- Epoch progress: 1.27 → 1.33 (run configured for 2 epochs; nearing completion)

## Memory (per device, stable)

- max_mem_active_gib: 24.73
- max_mem_allocated_gib: 24.73
- device_mem_reserved_gib: 28.42

## Interpretation

- Loss decreasing: model learning as expected
- Grad norm stable: no exploding / vanishing gradients
- Memory flat: no leaks or fragmentation issues
- Scheduler working: LR decaying smoothly
- Training close to completion

## LoRA Overview

- Concept: Insert low‑rank adapter matrices; freeze original weights
- Advantages: Lower memory, faster iteration, small adapter checkpoints, mergable into base

## QLoRA Overview

- Concept: 4‑bit quantization of base weights + LoRA adapters trained in higher precision
- Advantages: Further memory reduction; enables larger models on limited GPUs

## Current QLoRA Configuration

```
adapter: qlora
lora_r: 64 # Adapter rank
lora_alpha: 32 # Scaling factor
lora_dropout: 0.05 # Regularization
load_in_4bit: true # 4-bit base weight quantization
```

## Why This Setup Works

- Efficient parameter adaptation (QLoRA)
- Low memory footprint with stable usage
- Smooth optimization dynamics
- Near-complete training with no instability flags

## Resulting Artifacts

- Adapter weights only (roughly 100–500 MB)
- Can later merge adapters into original model or keep as plug-in
- Base model remains unchanged

## Next Suggestions

1. After epoch 2 completes, evaluate on held-out validation set.
2. Optionally run perplexity and a small domain-specific benchmark.
3. If loss plateaus above target, consider:
   - +1 epoch with 10–20% lower max LR
   - Reduce lora_dropout to 0.03 if underfitting
4. For deployment, test merged vs. adapter form for latency.

## Current Process:

1. ✅ Pre-trained model: Llama-3.1 (knows language)
2. ✅ Fine-tuning: Teaching it pirate speak (what you're doing now)
3. ⬜ Merge: Combining changes into single model (next step)
4. ⬜ Deploy: Using your pirate model in Ollama

## Training vs Fine-Tuning

### Pre-training (What i am NOT doing)

- Like: Teaching a baby human language from scratch
- What: Training a model from random weights on massive text data
- Time: Weeks/months, needs huge GPU clusters
- Cost: \$\$\$\$\$ (thousands of dollars)
- Result: Base models like "Llama-3.1-8B"

### Fine-Tuning (What i am doing) ✅

- Like: Teaching a college graduate a specific skill (e.g., medical terminology)
- What: Taking a pre-trained model and adapting it for specific tasks
- Time: Hours/days, needs modest GPU
- Cost: \$ (much cheaper)
- Result: Your pirate-speaking model! 🏴‍☠️

You are FINE-TUNING - taking Llama-3.1 and making it talk like a pirate!

## Pre-training vs Post-training

### Pre-training

- When: Before any specific task
- Goal: Learn general language understanding
- Data: Massive internet text (books, websites, code)
- Example: Llama-3.1 understands English grammar, facts, reasoning

### Post-training (what i am doing)

- When: After pre-training
- Goal: Specialize for specific tasks/styles
- Data: Small, targeted datasets (your pirate chats)
- Example: Making Llama talk like a pirate instead of a professor

## What `axolotl merge-lora Train.yml` Does

This command merges the LoRA adapters with the base model:

### Before Merging:

```
Base Model (8GB) + LoRA Adapters (100MB) = Working Pirate Model
```

### After Merging:

```
Single Unified Model (8.1GB) = Standalone Pirate Model
```

### Why Merge?

1. Faster inference (no extra computation)
2. Easier deployment (single file)
3. Better compatibility (works with more tools)
4. Permanent changes (adapter baked into model)

### When to Run Merge:

```bash
# AFTER training completes
axolotl merge-lora ./train.yml

# This creates a merged model in your output directory
```

### What You Get:

- Merged model that works without separate adapter files
- Can use with Ollama directly
- Better performance for inference

## Current Process:

1. ✅ Pre-trained model: Llama-3.1 (knows language)
2. ✅ Fine-tuning: Teaching it pirate speak (what i am doing now)
3. ✅ Merge: Combining changes into single model (next step)
4. ⬜ Deploy: Using your pirate model in Ollama
