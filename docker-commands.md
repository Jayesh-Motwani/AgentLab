## Docker model Runner

_From host terminal_
```bash
curl http://localhost:12434/engines/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "ai/gemma3:4b-q4_K_M",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Please write 500 words about fall of Rome"
            }
        ]
    }'
```

_From within a container_
```bash
curl http://model-runner.docker.internal/engines/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "ai/gemma3:4b-q4_K_M",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Please write 500 words about fall of Rome"
            }
        ]
    }'
```

_For Windows Powershell_
```bash
curl.exe --% http://localhost:12434/engines/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"ai/gemma3:4b-q4_K_M\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}"
```