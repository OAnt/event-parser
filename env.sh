export CMAKE_ARGS="-DGGML_HIP=on"
export MODEL=data/models/bartowski/mistralai_Ministral-3-3B-Instruct-2512-Q8_0.gguf
export MMPROJ=data/models/bartowski/mmproj-mistralai_Ministral-3-3B-Instruct-2512-bf16.gguf
export INSTA_ID=$(secret-tool lookup instagram app-id)
export FB_APP_ID=$(secret-tool lookup facebook app-id)
export FB_APP_SECRET=$(secret-tool lookup facebook app-secret)
export FB_TOKEN=$(secret-tool lookup facebook token)
export MONGO_INITDB_ROOT_USERNAME=$(secret-tool lookup id MONGO_USERNAME)
export MONGO_INITDB_ROOT_PASSWORD=$(secret-tool lookup id MONGO_PASSWORD)
export MONGO_PORT=27017
export MONGO_HOST=localhost
