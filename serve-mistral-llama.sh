#! /bin/bash
python3 -m llama_cpp.server --model data/models/bartowski/mistralai_Ministral-3-3B-Instruct-2512-Q8_0.gguf  --clip_model_path data/models/bartowski/mmproj-mistralai_Ministral-3-3B-Instruct-2512-bf16.gguf --chat_format mtmd --n_ctx 4096
