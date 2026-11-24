@echo off
REM Start vLLM Server with Mistral-7B LoRA Adapter (Windows)
REM Usage: scripts\start_vllm_server.bat

echo Starting vLLM Server with LoRA Adapter...

REM Configuration
set BASE_MODEL=mistralai/Mistral-7B-Instruct-v0.3
set LORA_PATH=.\nl2sql-json-v2-adapter-manual
set HOST=0.0.0.0
set PORT=8080
set MAX_MODEL_LEN=4096

REM Check if LoRA adapter exists
if not exist "%LORA_PATH%" (
    echo Error: LoRA adapter not found at %LORA_PATH%
    echo Please ensure your fine-tuned adapter is in the correct directory.
    exit /b 1
)

echo Base Model: %BASE_MODEL%
echo LoRA Adapter: %LORA_PATH%
echo Server: http://%HOST%:%PORT%

REM Start vLLM server
python -m vllm.entrypoints.openai.api_server ^
    --model %BASE_MODEL% ^
    --enable-lora ^
    --lora-modules nl2sql=%LORA_PATH% ^
    --host %HOST% ^
    --port %PORT% ^
    --dtype auto ^
    --max-model-len %MAX_MODEL_LEN% ^
    --gpu-memory-utilization 0.9 ^
    --trust-remote-code

echo Server started successfully!
