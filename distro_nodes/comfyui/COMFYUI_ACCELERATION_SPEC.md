# ComfyUI GPU Acceleration Node Specification
**Node Identifier:** `comfyui`  
**Distribution:** Ubuntu 26.04 Minimal  
**Runtime:** ROCm 7.1 + TheRock PyTorch Nightly (`gfx1103` AMD Radeon 780M)  
**Port:** `8188` (`comfyui.service` via systemd)  
**Storage VHDX:** `C:\WSL\distros\comfyui\ext4.vhdx`  

---

## 1. Architectural Role
- Provides GPU-accelerated latent diffusion and image synthesis for multimodal artifact assets without host Windows GPU driver contamination.
- Runs inside isolated WSL2 environment accessing the AMD Radeon 780M iGPU via `/dev/dxg` direct kernel hypervisor bridge.

## 2. Hardware Memory Guardrails
- **VRAM Reserve:** Bound with strict `--reserve-vram 2.0` parameter to guarantee 2.0 GB headroom for host desktop compositing and Vulkan LLM inference.
- **Process Lifecycle:** Managed as a systemd service (`systemctl status comfyui`). Automatically suspended or restarted during high-load LLM reasoning.
