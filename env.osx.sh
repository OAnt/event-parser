export CMAKE_ARGS="-DGGML_HIP=on"
export MODEL=data/models/bartowski/mistralai_Ministral-3-3B-Instruct-2512-Q8_0.gguf
export MMPROJ=data/models/bartowski/mmproj-mistralai_Ministral-3-3B-Instruct-2512-bf16.gguf
export INSTA_ID=$(security find-generic-password -s instagram -a app-id -w)
export FB_APP_ID=$(security find-generic-password -s facebook -a app-id -w)
export FB_APP_SECRET=$(security find-generic-password -s facebook -a app-secret -w)
export FB_TOKEN=$(security find-generic-password -s facebook -a token -w)
export MONGO_INITDB_ROOT_USERNAME=$(security find-generic-password -s mongo -a username -w)
export MONGO_INITDB_ROOT_PASSWORD=$(security find-generic-password -s mongo -a password -w)
export MONGO_PORT=27017
export MONGO_HOST=localhost
