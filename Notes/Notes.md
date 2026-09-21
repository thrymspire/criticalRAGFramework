harness-enclave acts as your Command & Control Tower. From inside harness-enclave, you can orchestrate tasks across
  all your micro-distros:

    # 1. Trigger isolated execution inside the Harness Enclave
    wsl.exe -d criticalpath-harness-v1.0 -u root python3 /workspace/project/react_loop.py

    # 2. Inspect the persistent Knowledge Store
    wsl.exe -d criticalpath-store-v1.0 -u root ls -la /data/corpus/

    # 3. Check container status on the Docker Node
    wsl.exe -d docker-engine -u root docker ps

    # 4. Check GPU ComfyUI Daemon
    wsl.exe -d comfyui -u root systemctl status comfyui --no-pager
  You can open VS Code directly into the project from harness-enclave:
    code ~/Critical-RAG
