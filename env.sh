export CMAKE_ARGS="-DGGML_HIP=on"
export LD_LIBRARY_PATH=/home/antoine/projects/vllm/.venv/lib/python3.12/site-packages/_rocm_sdk_libraries/lib/:/opt/rocm/lib:$LD_LIBRARY_PATH
export FB_APP_ID=$(secret-tool lookup facebook app-id)
export FB_APP_SECRET=$(secret-tool lookup facebook app-secret)
export FB_TOKEN=$(secret-tool lookup facebook token)
