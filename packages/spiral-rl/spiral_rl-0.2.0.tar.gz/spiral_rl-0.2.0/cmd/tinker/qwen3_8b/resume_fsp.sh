#!/bin/bash
# Example: Resume FSP training from step 180
# This demonstrates how to resume both training state and FSP population pool
#
# The system automatically infers which checkpoints should be in the pool:
# - Given: resume_step=180, fsp_start_from=50, fsp_update_interval=5, fsp_pool_size=25
# - Valid FSP steps: 50, 55, 60, ..., 170, 175 (all steps ≥50 at interval 5)
# - Inferred pool: last 25 = [55, 60, 65, ..., 170, 175]
#
# No checkpoints.jsonl needed!


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

export WEAVE_PRINT_CALL_LINK=false
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY is not set"
    echo "Please set it with: export OPENROUTER_API_KEY=your_api_key"
    exit 1
fi


python train_spiral_tinker.py \
    model_name="Qwen/Qwen3-8B-Base" \
    renderer_name=qwen3 \
    lora_rank=64 \
    env_ids='TicTacToe-v0,KuhnPoker-v1,SimpleNegotiation-v2' \
    use_llm_obs_wrappers='False,True,True' \
    batch_size=128 \
    num_train_datapoints=51200 \
    num_test_datapoints=128 \
    learning_rate=4e-5 \
    max_tokens=16384 \
    num_substeps=1 \
    use_role_baseline=True \
    role_baseline_ema_gamma=0.95 \
    eval_env_ids='TicTacToe-v0,KuhnPoker-v1,SimpleNegotiation-v2' \
    eval_use_llm_obs_wrappers='False,True,True' \
    eval_opponent_names='google/gemini-2.0-flash-001' \
    eval_every=16 \
    enable_math_test_eval=True \
    math_test_data_paths="data/aime,data/amc,data/olympiad_bench,data/math,data/minerva" \
    save_every=20 \
    loss_fn=importance_sampling \
    wandb_project=spiral \
    wandb_name=qwen3-8b-fsp-resume \
    use_streaming=false \
    fsp_enabled=True \
    fsp_pool_size=25 \
    fsp_start_from=50 \
    fsp_update_interval=5 \
    fsp_include_current=true \
    load_checkpoint_path="tinker://6dff3612-07f8-4c7a-a3ac-8b37a9b74972/weights/000180" \
    fsp_resume_checkpoint_base="tinker://6dff3612-07f8-4c7a-a3ac-8b37a9b74972/sampler_weights/"
