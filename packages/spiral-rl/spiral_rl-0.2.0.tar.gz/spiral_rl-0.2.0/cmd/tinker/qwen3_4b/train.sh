#!/bin/bash
# Copyright 2025 SPIRAL Team. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Check for required API keys
if [ -z "$TINKER_API_KEY" ]; then
    echo "Error: TINKER_API_KEY is not set"
    echo "Please set it with: export TINKER_API_KEY=your_api_key"
    exit 1
fi

if [ -z "$WANDB_API_KEY" ]; then
    echo "Error: WANDB_API_KEY is not set"
    echo "Please set it with: export WANDB_API_KEY=your_api_key"
    exit 1
fi

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY is not set"
    echo "Please set it with: export OPENROUTER_API_KEY=your_api_key"
    exit 1
fi

export WEAVE_PRINT_CALL_LINK=false

python train_spiral_tinker.py \
    model_name="Qwen/Qwen3-4B-Instruct-2507" \
    renderer_name=qwen3 \
    lora_rank=32 \
    env_ids='TicTacToe-v0,KuhnPoker-v1,SimpleNegotiation-v2' \
    use_llm_obs_wrappers='False,True,True' \
    batch_size=128 \
    num_train_datapoints=51200 \
    num_test_datapoints=128 \
    learning_rate=4e-5 \
    max_tokens=8192 \
    num_substeps=1 \
    use_role_baseline=True \
    role_baseline_ema_gamma=0.95 \
    eval_env_ids='TicTacToe-v0,KuhnPoker-v1,SimpleNegotiation-v2' \
    eval_use_llm_obs_wrappers='False,True,True' \
    eval_opponent_names='google/gemini-2.0-flash-001' \
    eval_every=16 \
    save_every=20 \
    loss_fn=importance_sampling \
    wandb_project=spiral \
    wandb_name=qwen3-4b-instruct-2507-train \
    use_streaming=false
