"""
Lightweight Harness HTTP & Telemetry Server with Phase 2 Streaming Bridge
Zero third-party dependencies required. Serves the web UI, REST API,
and real-time Server-Sent Events (SSE) token stream with Shannon entropy.
"""

import os
import sys
import json
import subprocess
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

from .harness import HarnessOrchestrator
from .secrets import get_vault
from .retrieval import CorpusRetriever
from .stream_bridge import stream_tokens_from_llama, UI_STATE_FILE

UI_DIR = Path(__file__).resolve().parent.parent / "ui"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class HarnessHandler(SimpleHTTPRequestHandler):
    """Custom request handler bridging the UI to the harness core and streaming bridge."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def _authorized(self) -> bool:
        """Require a bearer token when CRITICAL_RAG_API_TOKEN is configured."""
        expected = os.environ.get("CRITICAL_RAG_API_TOKEN")
        if not expected:
            return True
        supplied = self.headers.get("Authorization", "").removeprefix("Bearer ")
        return hmac.compare_digest(supplied, expected)

    def _require_api_auth(self) -> bool:
        if self._authorized():
            return True
        self.send_error(401, "Unauthorized")
        return False

    @staticmethod
    def _bounded_int(value, default: int, minimum: int, maximum: int) -> int:
        try:
            return max(minimum, min(int(value), maximum))
        except (TypeError, ValueError):
            return default
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        if path.startswith("/api/") and not self._require_api_auth():
            return

        # Route UI index as default
        if path in ("/", "/ui", "/ui/"):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            index_path = UI_DIR / "index.html"
            self.wfile.write(index_path.read_bytes())
            return

        # Redirect shortcuts for circle.js and styles.css
        if path in ("/circle.js", "/ui/circle.js"):
            self._serve_file(UI_DIR / "circle.js", "application/javascript")
            return
        if path in ("/styles.css", "/ui/styles.css", "/styules.css", "/ui/styules.css"):
            self._serve_file(UI_DIR / "styles.css", "text/css")
            return
        if path in ("/vanguard.html", "/ui/vanguard.html", "/vanguard"):
            self._serve_file(UI_DIR / "vanguard.html", "text/html")
            return
        if path in ("/logo.svg", "/ui/logo.svg", "/assets/logo.svg"):
            self._serve_file(UI_DIR / "logo.svg", "image/svg+xml")
            return

        # Phase 2: Live Token State Polling Endpoint
        if path in ("/api/tokens/state", "/ui/state.json"):
            if UI_STATE_FILE.exists():
                self._send_json(json.loads(UI_STATE_FILE.read_text(encoding="utf-8")))
            else:
                self._send_json({"status": "idle", "step": 0, "chosen_token": "", "prob": 0, "entropy": 0, "top": []})
            return

        # Phase 2: Server-Sent Events (SSE) Real-Time Token Stream
        if path == "/api/tokens/stream":
            prompt = query.get("prompt", ["What is 2+2? Answer in one sentence."])[0]
            max_tokens = self._bounded_int(query.get("max_tokens", [32])[0], 32, 1, 512)

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            try:
                for step_obj in stream_tokens_from_llama(prompt, max_tokens=max_tokens):
                    sse_chunk = f"data: {json.dumps(step_obj)}\n\n".encode("utf-8")
                    self.wfile.write(sse_chunk)
                    self.wfile.flush()
                self.wfile.write(b"data: [DONE]\n\n")
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        # Phase 4: Full Autonomous ReAct Agent Stream (RAG Retrieval + Token Physics + Verification)
        if path == "/api/agent/stream":
            prompt = query.get("prompt", ["Explain the Critical Path cluster."])[0]
            max_tokens = self._bounded_int(query.get("max_tokens", [64])[0], 64, 1, 512)

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            orchestrator = HarnessOrchestrator()
            from .agent_loader import get_active_agent, list_available_agents, set_active_agent
            active = get_active_agent()
            orchestrator.directive = active["system_prompt"]

            try:
                for event_obj in orchestrator.stream_agent_turn(prompt, max_tokens=max_tokens):
                    sse_chunk = f"data: {json.dumps(event_obj)}\n\n".encode("utf-8")
                    self.wfile.write(sse_chunk)
                    self.wfile.flush()
                self.wfile.write(b"data: [DONE]\n\n")
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        # API: Runtime Agent Management
        if path == "/api/agents":
            from .agent_loader import get_active_agent, list_available_agents
            self._send_json({
                "active": get_active_agent(),
                "available": list_available_agents()
            })
            return

        # API: Cluster & Enclave Status
        if path == "/api/status":
            vault = get_vault()
            status_data = {
                "enclave": {
                    "harness": "ONLINE",
                    "secrets_vault": "ACTIVE",
                    "loaded_keys_count": len(vault.list_available_keys()),
                },
                "nodes": {
                    "llama_server": self._check_port(8080),
                    "comfyui": self._check_port(8188),
                    "docker_engine": self._check_port(2375)
                },
                "models": {
                    "active_endpoint": "http://127.0.0.1:8080/v1",
                    "embedding_mode": "mean_pooling (OAI compatible)",
                    "logprobs_engine": "ACTIVE (top_logprobs=5, Shannon entropy computed)"
                }
            }
            self._send_json(status_data)
            return

        # API: Corpus listing
        if path == "/api/corpus":
            retriever = CorpusRetriever()
            self._send_json({"count": len(retriever.documents), "documents": retriever.documents})
            return

        # API: Circular Graph Telemetry
        if path == "/api/circle/telemetry":
            telemetry = {
                "center": {"name": "Critical Path Harness", "status": "active", "type": "enclave"},
                "nodes": [
                    {"id": "node-llama", "name": "llama-server (Vulkan)", "port": 8080, "status": "reachable" if self._check_port(8080) else "offline", "color": "#9d5cff"},
                    {"id": "node-comfy", "name": "ComfyUI (ROCm 780M)", "port": 8188, "status": "reachable" if self._check_port(8188) else "offline", "color": "#5ffbf1"},
                    {"id": "node-store", "name": "Store Node (Corpus)", "path": "/data/corpus", "status": "available" if Path("/data/corpus").exists() else "offline", "color": "#c084fc"},
                    {"id": "node-docker", "name": "Docker Engine", "port": 2375, "status": "standby", "color": "#ff6b81"},
                    {"id": "node-vault", "name": "Secrets Enclave", "path": "/etc/harness/secrets", "status": "configured" if get_vault().secrets_dir.exists() else "unconfigured", "color": "#a996d6"}
                ]
            }
            self._send_json(telemetry)
            return

        # Standard file serving fallback
        super().do_GET()

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if self.path == "/api/chat":
            prompt = payload.get("prompt", "")
            self._send_json({"status": "error", "error": "Use /api/chat/stream for chat requests"})
            return

        if self.path == "/api/chat/stream":
            messages = payload.get("messages", [])
            agent_name = payload.get("agent", "")
            max_tokens = self._bounded_int(payload.get("max_tokens", 512), 512, 1, 512)
            rag_enabled = bool(payload.get("rag_enabled", True))

            if agent_name:
                from .agent_loader import set_active_agent
                try:
                    set_active_agent(agent_name)
                except Exception:
                    pass

            from .agent_loader import get_active_agent
            active = get_active_agent()

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            orchestrator = HarnessOrchestrator()
            orchestrator.directive = active["system_prompt"]

            try:
                for event_obj in orchestrator.stream_chat_turn(messages, max_tokens=max_tokens, rag_enabled=rag_enabled):
                    sse_chunk = f"data: {json.dumps(event_obj)}\n\n".encode("utf-8")
                    self.wfile.write(sse_chunk)
                    self.wfile.flush()
                self.wfile.write(b"data: [DONE]\n\n")
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        if self.path == "/api/query":
            query = payload.get("query", "")
            retriever = CorpusRetriever()
            results = retriever.search(query, top_k=payload.get("top_k", 3))
            self._send_json({"results": results})
            return

        if self.path == "/api/artifact/generate":
            topic = payload.get("topic", "agent_execution_output")
            content_text = payload.get("content", "")
            if not content_text:
                self._send_json({"status": "error", "error": "No content provided"})
                return

            import subprocess
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp:
                tmp.write(content_text)
                tmp_path = tmp.name

            try:
                wslpath_res = subprocess.run(["wslpath", "-w", tmp_path], capture_output=True, text=True)
                win_tmp = wslpath_res.stdout.strip()
                res = subprocess.run([
                    "cmd.exe", "/c", "python",
                    "./scripts/generate_alien_artifact.py",
                    "--topic", topic,
                    "--file", win_tmp
                ], capture_output=True, text=True)

                out = res.stdout.strip()
                artifact_path = ""
                if "Artifact generated successfully:" in out:
                    artifact_path = out.split("Artifact generated successfully:")[1].strip()
                self._send_json({
                    "status": "ok",
                    "output": out,
                    "artifact_path": artifact_path,
                    "filename": Path(artifact_path).name if artifact_path else ""
                })
            except Exception as e:
                self._send_json({"status": "error", "error": str(e)})
            finally:
                Path(tmp_path).unlink(missing_ok=True)
            return

        if self.path == "/api/agents/switch":
            agent_name = payload.get("agent", "")
            from .agent_loader import set_active_agent
            try:
                active = set_active_agent(agent_name)
                self._send_json({"status": "ok", "active": active})
            except Exception as e:
                self._send_json({"status": "error", "error": str(e)})
            return

        self.send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _serve_file(self, path: Path, content_type: str):
        if path.exists():
            self.send_response(200)
            self.send_header("Content-type", f"{content_type}; charset=utf-8")
            self.end_headers()
            self.wfile.write(path.read_bytes())
        else:
            self.send_error(404, f"File {path.name} not found")

    def _send_json(self, data: dict):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _check_port(self, port: int) -> bool:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1) as resp:
                return resp.status < 500
        except Exception:
            pass
        win_curl = "/mnt/c/Windows/System32/curl.exe"
        if not os.path.exists(win_curl):
            win_curl = "curl.exe"
        try:
            res = subprocess.run([win_curl, "-s", "-o", "/dev/null", "-w", "%{http_code}", f"http://127.0.0.1:{port}/health"], capture_output=True, text=True, timeout=2)
            code = res.stdout.strip()
            if code in ("200", "204", "301", "302", "404"):
                return True
        except Exception:
            pass
        return False


def start_harness_server(host: str = "127.0.0.1", port: int = 8090):
    server = ThreadedHTTPServer((host, port), HarnessHandler)
    print(f"[HARNESS SERVER] Phase 2 Streaming Bridge active on http://{host}:{port}")
    print(f"[HARNESS SERVER] Serving UI from {UI_DIR}")
    print(f"[HARNESS SERVER] SSE Token Stream: http://{host}:{port}/api/tokens/stream?prompt=...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[HARNESS SERVER] Shutting down.")
        server.shutdown()


if __name__ == "__main__":
    start_harness_server()
