export CMAKE_ARGS="-DGGML_HIP=on"
export LD_LIBRARY_PATH=/home/antoine/projects/vllm/.venv/lib/python3.12/site-packages/_rocm_sdk_libraries/lib/:/opt/rocm/lib:$LD_LIBRARY_PATH
export MODEL=data/models/bartowski/mistralai_Ministral-3-3B-Instruct-2512-Q8_0.gguf
export MMPROJ=data/models/bartowski/mmproj-mistralai_Ministral-3-3B-Instruct-2512-bf16.gguf
export INSTA_ID=17841421840340416
export FB_APP_ID=$(secret-tool lookup facebook app-id)
export FB_APP_SECRET=$(secret-tool lookup facebook app-secret)
export FB_TOKEN=$(secret-tool lookup facebook token)
