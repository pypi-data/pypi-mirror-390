# Resuming Population-Based Training (FSP)

This guide explains how to resume training with Fictitious Self-Play (FSP) and restore the population pool.

## Overview

When resuming FSP training, you need to:
1. Load the training state (optimizer, LoRA weights, etc.)
2. Restore the FSP population pool (historical checkpoints)

The system **automatically infers** which historical checkpoints should be in the pool based on:
- The resume step (extracted from `load_checkpoint_path`)
- FSP configuration (`fsp_start_from`, `fsp_update_interval`, `fsp_pool_size`)

**No `checkpoints.jsonl` file needed!** Everything is computed from the configuration.

## How to Resume

```bash
python train_spiral_tinker.py \
    ... \
    load_checkpoint_path="tinker://6dff3612-07f8-4c7a-a3ac-8b37a9b74972/weights/000180" \
    fsp_resume_checkpoint_base="tinker://6dff3612-07f8-4c7a-a3ac-8b37a9b74972/sampler_weights/" \
    fsp_enabled=True \
    fsp_pool_size=10 \
    fsp_start_from=0 \
    fsp_update_interval=5
```

## Parameters Explained

### Resume Parameters

- **`load_checkpoint_path`**: Path to training checkpoint
  - Format: `tinker://<uuid>/weights/000180`
  - This loads the training state (optimizer, LoRA adapters)
  - Step number is automatically extracted from the path

- **`fsp_resume_checkpoint_base`**: Base path for FSP sampler checkpoints
  - Format: `tinker://<uuid>/sampler_weights/`
  - System will append step numbers (e.g., `000130`, `000135`, etc.)

### FSP Configuration

- **`fsp_enabled`**: Enable fictitious self-play (must be `True`)
- **`fsp_pool_size`**: Maximum number of historical checkpoints in pool
- **`fsp_start_from`**: Step when FSP started originally
- **`fsp_update_interval`**: How often checkpoints were added to pool
- **`fsp_include_current`**: Whether current model is available for sampling

## How It Works

### 1. Step Detection

The system automatically extracts the step number from `load_checkpoint_path`:
- Path: `tinker://.../weights/000180` → Step: 180

### 2. Checkpoint Inference

Based on your FSP configuration, the system **calculates** which checkpoints should be in the pool:

```python
# Example: Resume from step 180 with:
# - fsp_start_from = 0
# - fsp_update_interval = 5
# - fsp_pool_size = 10

# Algorithm:
# 1. Generate all valid FSP steps: 0, 5, 10, 15, ..., 170, 175
#    (from fsp_start_from to resume_step-1, at fsp_update_interval)
# 2. Keep last pool_size steps: [130, 135, 140, 145, 150, 155, 160, 165, 170, 175]
```

### 3. Path Construction

For each inferred checkpoint step, it constructs the full path:
```
tinker://6dff3612-07f8-4c7a-a3ac-8b37a9b74972/sampler_weights/000130
tinker://6dff3612-07f8-4c7a-a3ac-8b37a9b74972/sampler_weights/000135
...
tinker://6dff3612-07f8-4c7a-a3ac-8b37a9b74972/sampler_weights/000175
```

### 4. Client Creation

Creates sampling clients from each checkpoint and adds them to the population pool.

**Key insight**: No file parsing or checkpoint discovery needed - everything is computed from the configuration!

## Example: Your Scenario

Given:
- Training state: `tinker://6dff3612-07f8-4c7a-a3ac-8b37a9b74972/weights/000180`
- Sampler weights: `tinker://6dff3612-07f8-4c7a-a3ac-8b37a9b74972/sampler_weights/000180`

Resume command:

```bash
python train_spiral_tinker.py \
    model_name="Qwen/Qwen3-8B-Base" \
    ... \
    load_checkpoint_path="tinker://6dff3612-07f8-4c7a-a3ac-8b37a9b74972/weights/000180" \
    fsp_resume_checkpoint_base="tinker://6dff3612-07f8-4c7a-a3ac-8b37a9b74972/sampler_weights/" \
    fsp_enabled=True \
    fsp_pool_size=10 \
    fsp_start_from=0 \
    fsp_update_interval=5 \
    fsp_include_current=True
```

This will:
1. Extract resume step: 180
2. Calculate pool steps: [130, 135, 140, 145, 150, 155, 160, 165, 170, 175] (last 10 at interval 5)
3. Load training state from `weights/000180`
4. Load sampling clients from `sampler_weights/000130`, `000135`, ..., `000175`
5. Continue training from step 181

## Verification

Check the logs for confirmation:

```
[FSP] Restoring population from base path: tinker://.../sampler_weights/
[FSP] Loading 10 checkpoints: [130, 135, 140, 145, 150, 155, 160, 165, 170, 175]
[FSP] Restored checkpoint from step 130: tinker://.../sampler_weights/000130
[FSP] Restored checkpoint from step 135: tinker://.../sampler_weights/000135
...
[FSP] Population restoration complete. Pool size: 10/10
[FSP] Population steps: [130, 135, 140, 145, 150, 155, 160, 165, 170, 175]
[FSP] Restored population with 10 agents
```

## Troubleshooting

### Missing Checkpoints

If some checkpoints are missing, the system will log errors but continue:

```
[FSP] Failed to load checkpoint from step 130 at tinker://.../000130: Not found
```

The pool will have fewer agents than `fsp_pool_size`, but training will continue.

### Wrong Step Detection

If the step number cannot be extracted from `load_checkpoint_path`, the system will fail. Ensure your path ends with `/000180` format (6 digits).

## See Also

- Example script: [cmd/tinker/qwen3_8b/resume_fsp.sh](cmd/tinker/qwen3_8b/resume_fsp.sh)
- Population manager: [spiral/tinker/training/population.py](spiral/tinker/training/population.py)
- Training loop: [spiral/tinker/training/train.py](spiral/tinker/training/train.py)
