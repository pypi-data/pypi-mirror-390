# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SPIRAL is a self-play reinforcement learning framework for training language models on competitive two-player zero-sum games. This repository supports **two backends**:

1. **OAT backend** (`train_spiral.py`) - Original implementation using OAT framework with vLLM
2. **Tinker backend** (`train_spiral_tinker.py`) - New implementation using Tinker's distributed training infrastructure

The system trains models to play competitive games (TicTacToe, Kuhn Poker, Liars Dice, Simple Negotiation) through continuous self-improvement, developing reasoning and strategic capabilities.

## Installation

```bash
# Clone and setup environment
conda create -y -n spiral-tinker python=3.10
conda activate spiral-tinker

# Install with Tinker backend
pip install -e .

# Install with OAT backend (for train_spiral.py)
pip install vllm==0.8.4 && pip install oat-llm==0.2.1
pip install -e .
```

## API Keys Setup

Training scripts require API keys to be set as environment variables. **The `.env` file is already created with your keys and is excluded from git.**

Before running any training script, source the `.env` file:

```bash
# Source the .env file to load API keys
source .env

# Then run your training script
bash cmd/tinker/qwen3_8b/train.sh
```

**Important**:
- The `.env` file contains your actual API keys and is in `.gitignore` (won't be committed to git)
- If you need to share the repository, others should create their own `.env` file using `.env.example` as a template

Required API keys:
- **TINKER_API_KEY**: For Tinker backend training
- **WANDB_API_KEY**: For Weights & Biases experiment tracking
- **OPENROUTER_API_KEY**: For evaluation against external models (e.g., Gemini)

All training scripts in `cmd/tinker/` will check for these environment variables and exit with an error if they're not set.

## Common Commands

### Training

**Tinker backend** (recommended):
```bash
# Basic training
python train_spiral_tinker.py \
    model_name="Qwen/Qwen3-8B-Base" \
    renderer_name=qwen3 \
    env_ids='TicTacToe-v0,KuhnPoker-v1' \
    batch_size=128 \
    learning_rate=4e-5

# Population-based self-play (FSP)
python train_spiral_tinker.py \
    model_name="Qwen/Qwen3-8B-Base" \
    fsp_enabled=True \
    fsp_pool_size=25 \
    fsp_update_interval=5

# Using training scripts
bash cmd/tinker/qwen3_8b/train.sh
bash cmd/tinker/qwen3_8b/train_fsp_pool_25.sh

# Resume FSP training
python train_spiral_tinker.py \
    load_checkpoint_path="tinker://xxx/weights/000180" \
    fsp_resume_checkpoint_base="tinker://xxx/sampler_weights/" \
    fsp_enabled=True \
    fsp_pool_size=25
```

**OAT backend**:
```bash
# Using training scripts in cmd/oat/
bash cmd/oat/qwen3_8b/run_multi.sh
bash cmd/oat/qwen3_4b/run_multi.sh
```

### Testing

```bash
# Run tests (configured in pyproject.toml)
pytest tests/

# Run specific test
pytest spiral/core/envs/test/test_simple_negotiation.py
```

### Code Quality

```bash
# Format code
black spiral/
isort spiral/

# Type checking
mypy spiral/
```

## Architecture

### Package Structure

The codebase uses a **modular three-tier architecture**:

```
spiral/
├── core/           # Shared components (used by both backends)
│   ├── envs/      # Custom TextArena game implementations
│   ├── agents/    # Agent implementations (RandomAgent, utils)
│   ├── template.py # Prompt templates for different model types
│   └── utils.py   # Basic utilities (EMA, GameState, extract_boxed_answer)
├── oat/           # OAT-specific implementation (vLLM-based)
│   ├── components.py # SelfPlayCollector, MATHOracle
│   └── metrics.py    # EvaluationMetrics
└── tinker/        # Tinker-specific implementation (imports from spiral.core)
    ├── dataset.py        # SpiralRLDatasetBuilder
    ├── renderer.py       # Prompt rendering with template selection
    ├── utils.py          # Tinker-specific utils (setup_logging, compute_trajectory_metrics)
    ├── training/         # Training loops and environment management
    │   ├── env.py           # SpiralTwoPlayerEnv, TwoPlayerCoordinator
    │   ├── rollouts.py      # Trajectory collection with draw retry
    │   ├── train.py         # Main training loop factory
    │   ├── train_step.py    # Single training step logic
    │   ├── population.py    # PopulationManager for FSP
    │   └── async_actor_learner/ # Async architecture with replay buffer
    └── eval/          # Evaluation framework
        ├── evaluator.py  # GameEvaluator for game-based evaluation
        └── math_test.py  # Math benchmark evaluation
```

### Two Training Scripts

- **`train_spiral.py`**: OAT backend with vLLM, multi-GPU support, original SPIRAL implementation
- **`train_spiral_tinker.py`**: Tinker backend with distributed training, LoRA, FSP support

**Key Architecture Points**:
- `spiral/core` contains **all shared components**: game environments, agents, templates, and basic utilities
- `spiral/tinker` and `spiral/oat` import from `spiral.core` (no code duplication)
- `spiral/tinker/utils.py` contains **Tinker-specific** utilities (logging, trajectory metrics, JSON serialization)

### Key Training Concepts

**Role-conditioned Advantage Estimation (RAE)**:
In self-play, both players use the same policy but different roles. RAE computes separate advantages for each role to prevent conflating perspectives and improve stability.

**Population-based Self-Play (FSP)**:
Instead of pure self-play, FSP trains against a pool of historical checkpoints for more diverse training signal and robustness. Managed by `PopulationManager` in `spiral/tinker/training/population.py`.

**Draw Retry Mechanism**:
When `filter_draw=True`, the system retries games that end in draws (up to `max_draw_retries`) to ensure training signal from decisive outcomes. Implemented in `do_group_rollout_with_draw_retry()`.

**Async Actor-Learner**:
Optional architecture (`use_async_actor_learner=True`) that decouples trajectory collection from policy updates using a replay buffer for improved throughput.

### Training Pipeline (Tinker Backend)

1. **Environment Setup**: `SpiralTwoPlayerEnv` wraps TextArena games with observation formatters
2. **Self-Play Collection**: `do_group_rollout()` generates trajectories with both players using current policy
3. **Dataset Building**: `SpiralRLDatasetBuilder` processes trajectories into training data
4. **Advantage Estimation**: RAE computes separate advantages for each role using role-specific baselines
5. **Policy Updates**: Tinker's PPO learner updates policy using collected trajectories
6. **Evaluation**: `GameEvaluator` tracks win rates against opponents, optional math test evaluation

## Configuration

Key parameters in `train_spiral_tinker.py`:

**Model Settings**:
- `model_name`: Base model (e.g., "Qwen/Qwen3-8B-Base")
- `renderer_name`: Prompt renderer ("qwen3", "llama3", "deepseek")
- `lora_rank`: LoRA rank for efficient fine-tuning

**Training**:
- `batch_size`: Batch size (default: 128)
- `learning_rate`: Learning rate (default: 1e-4)
- `max_tokens`: Maximum token length
- `loss_fn`: "importance_sampling" or "ppo"

**SPIRAL-Specific**:
- `use_role_baseline`: Enable role-conditioned baselines (recommended: True)
- `role_baseline_ema_gamma`: EMA decay for baseline (default: 0.95)
- `filter_draw`: Filter out draw games (default: False)
- `max_draw_retries`: Max retries when filtering draws (default: 5)

**FSP (Population-based)**:
- `fsp_enabled`: Enable fictitious self-play
- `fsp_pool_size`: Number of historical checkpoints (e.g., 25)
- `fsp_start_from`: Step to start FSP
- `fsp_update_interval`: Steps between pool updates
- `fsp_resume_checkpoint_base`: Base path for resuming FSP (see [RESUME_FSP.md](docs/RESUME_FSP.md))

**Async Actor-Learner**:
- `use_async_actor_learner`: Enable async architecture
- `replay_buffer_max_staleness`: Max staleness for replay buffer

## Resuming FSP Training

When resuming FSP training, the system automatically infers which historical checkpoints should be in the pool based on the resume step and FSP configuration. See [RESUME_FSP.md](docs/RESUME_FSP.md) for detailed instructions.

The system computes checkpoint steps from configuration (no `checkpoints.jsonl` file needed):
```bash
python train_spiral_tinker.py \
    load_checkpoint_path="tinker://xxx/weights/000180" \
    fsp_resume_checkpoint_base="tinker://xxx/sampler_weights/" \
    fsp_enabled=True \
    fsp_pool_size=10 \
    fsp_update_interval=5
```

## Supported Environments

From [TextArena](https://github.com/LeonGuertler/TextArena):
- `TicTacToe-v0` - Classic tic-tac-toe
- `KuhnPoker-v1` - Simplified poker variant
- `LiarsDice-v1` - Bluffing dice game
- `SimpleNegotiation-v2` - Resource negotiation
- `ConnectFour-v0` - Connect 4 game

## Dependencies

Managed via `pyproject.toml`:

**Core** (backend-agnostic):
- `textarena==0.6.4` - Game environments
- `numpy`, `tqdm`, `textblob`, `latex2sympy2`

**Optional extras**:
- `spiral[oat]` - OAT backend: `oat-llm==0.2.1`, `vllm==0.8.4`
- `spiral[tinker]` - Tinker backend: `tinker`, `tinker-cookbook`, `chz>=0.1.0`
- `spiral[dev]` - Development: `pytest`, `black`, `isort`, `mypy`, `pylint`
- `spiral[all]` - All backends
- `spiral[full]` - All backends + dev tools

## Development Notes

- Python 3.10 required
- Code formatting: Black (line length 100), isort (black profile)
- Type checking: mypy configured in `pyproject.toml`
- Test configuration: pytest configured in `pyproject.toml`, testpaths = ["tests"]
- Training scripts organized by backend: `cmd/oat/` and `cmd/tinker/`
- Tinker uses LoRA for efficient fine-tuning, OAT uses full model training
- Both backends support Weights & Biases experiment tracking
- API keys needed for evaluation: `OPENROUTER_API_KEY` for opponent models, `WANDB_API_KEY` for logging

## Releasing to PyPI and GitHub Packages

The package is published as `spiral-rl` on PyPI. To release a new version:

### 1. Update Version Number

Edit `pyproject.toml` and update the version:
```toml
[project]
name = "spiral-rl"
version = "0.2.1"  # Update this
```

### 2. Build the Package

```bash
# Build the distribution files
bash scripts/build_package.sh
```

This creates `dist/spiral_rl-*.whl` and `dist/spiral_rl-*.tar.gz` files.

### 3. Test Locally (Optional)

```bash
# Install the built package in a test environment
pip install dist/spiral_rl-*.whl
```

### 4. Release to PyPI

```bash
# Set your PyPI token (get from https://pypi.org/manage/account/token/)
export PYPI_TOKEN=your_pypi_token

# Upload to PyPI
bash scripts/release_pypi.sh
```

### 5. Release to GitHub Packages

```bash
# Set your GitHub token (get from https://github.com/settings/tokens with 'write:packages' scope)
export GITHUB_TOKEN=your_github_token

# Upload to GitHub Packages
bash scripts/release_github.sh
```

### 6. Create GitHub Release

After publishing to PyPI, create a GitHub release:
1. Go to https://github.com/spiral-rl/spiral-on-tinker/releases
2. Click "Draft a new release"
3. Create a tag (e.g., `v0.2.1`)
4. Add release notes
5. Attach the `dist/` files
6. Publish release

### Installation from Published Package

Users can install from PyPI:
```bash
pip install spiral-rl[tinker]  # Tinker backend
pip install spiral-rl[oat]     # OAT backend
pip install spiral-rl[all]     # Both backends
```

Or from GitHub Packages:
```bash
pip install spiral-rl --extra-index-url https://pypi.pkg.github.com/spiral-rl/
```
