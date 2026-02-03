"""
model_manager.py — Load / unload models with triple backend support.

Backends (in priority order):
  OLLAMA → HTTP API to local Ollama server (FAST, zero-install)
  GGUF   → llama-cpp-python (optional, if installed)
  HF     → HuggingFace transformers (slowest fallback)

Ollama handles model loading/unloading automatically.
Just call generate() — it pulls the model if needed.
"""

import gc
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ── GGUF backend (optional) ────────────────────────────────

_HAS_LLAMA_CPP = False
try:
    from llama_cpp import Llama
    _HAS_LLAMA_CPP = True
except ImportError:
    pass

# ── HF backend (optional) ──────────────────────────────────

_HAS_HF = False
try:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        GenerationConfig,
    )
    _HAS_HF = True
except ImportError:
    pass


# ── Ollama helpers ──────────────────────────────────────────

OLLAMA_BASE = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def _ollama_request(endpoint: str, payload: dict,
                    timeout: float = 600) -> dict:
    """Make a JSON POST request to Ollama API."""
    url = f"{OLLAMA_BASE}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ollama_request_stream(endpoint: str, payload: dict,
                           timeout: float = 600) -> str:
    """Make a streaming POST request, collect full response text."""
    url = f"{OLLAMA_BASE}{endpoint}"
    payload["stream"] = False  # we want single JSON response
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result


def _ollama_is_running() -> bool:
    """Check if Ollama server is reachable."""
    try:
        url = f"{OLLAMA_BASE}/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _ollama_has_model(model_name: str) -> bool:
    """Check if a model is already pulled in Ollama."""
    try:
        url = f"{OLLAMA_BASE}/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m["name"] for m in data.get("models", [])]
            # Ollama names can have :latest suffix
            for m in models:
                base = m.split(":")[0]
                if model_name == m or model_name == base:
                    return True
                if model_name.split(":")[0] == base:
                    return True
            return False
    except Exception:
        return False


def _ollama_pull(model_name: str) -> None:
    """Pull a model into Ollama (downloads if needed)."""
    print(f"[ModelManager] Pulling {model_name} in Ollama "
          f"(this may download several GB) ...")
    # Use stream=False for simpler handling
    url = f"{OLLAMA_BASE}/api/pull"
    payload = {"name": model_name, "stream": True}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=3600) as resp:
        # Stream progress
        for line in resp:
            try:
                chunk = json.loads(line.decode("utf-8"))
                status = chunk.get("status", "")
                if "pulling" in status:
                    total = chunk.get("total", 0)
                    completed = chunk.get("completed", 0)
                    if total > 0:
                        pct = completed / total * 100
                        print(f"\r  [{status}] {pct:.0f}%    ",
                              end="", flush=True)
                elif status:
                    print(f"\r  [{status}]              ",
                          end="", flush=True)
            except Exception:
                pass
    print()  # newline after progress


# ── GGUF download helper ───────────────────────────────────

CACHE_DIR = Path.home() / ".cache" / "cot-synth" / "gguf"


def _download_gguf(repo: str, filename: str) -> str:
    """Download a GGUF file from HuggingFace Hub if not cached."""
    local_path = CACHE_DIR / repo.replace("/", "--") / filename
    if local_path.exists():
        return str(local_path)

    print(f"[ModelManager] Downloading {repo}/{filename} ...")
    local_path.parent.mkdir(parents=True, exist_ok=True)

    from huggingface_hub import hf_hub_download
    downloaded = hf_hub_download(
        repo_id=repo,
        filename=filename,
        local_dir=str(local_path.parent),
        local_dir_use_symlinks=False,
    )
    return downloaded


# ================================================================
# ModelManager
# ================================================================

class ModelManager:
    """Loads one model at a time. Supports Ollama, GGUF, and HF."""

    def __init__(self):
        self._model = None       # for GGUF/HF
        self._tokenizer = None   # for HF only
        self._current_id: str | None = None
        self._backend: str | None = None
        self._ollama_checked = False
        self._ollama_available = False

    # ── Public API ──────────────────────────────────────────

    def load(self, model_cfg: dict) -> None:
        """Load a model from config. Unloads previous if different."""
        mid = model_cfg["id"]
        if mid == self._current_id:
            return

        self._unload()
        backend = model_cfg.get("backend", "ollama")

        if backend == "ollama":
            self._load_ollama(model_cfg)
        elif backend == "gguf":
            self._load_gguf(model_cfg)
        elif backend == "hf":
            self._load_hf(model_cfg)
        else:
            raise ValueError(f"Unknown backend: {backend}")

        self._current_id = mid
        self._backend = backend

    def generate(
        self,
        messages: list[dict],
        max_new_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 1.1,
    ) -> str:
        """Generate from chat-style messages. Routes to correct backend."""
        if self._backend == "ollama":
            return self._generate_ollama(
                messages, max_new_tokens, temperature, top_p, top_k,
                repetition_penalty,
            )
        elif self._backend == "gguf":
            assert self._model is not None, "No model loaded."
            return self._generate_gguf(
                messages, max_new_tokens, temperature, top_p, top_k,
                repetition_penalty,
            )
        else:
            assert self._model is not None, "No model loaded."
            return self._generate_hf(
                messages, max_new_tokens, temperature, top_p, top_k,
                repetition_penalty,
            )

    def current_model_id(self) -> str | None:
        return self._current_id

    def current_backend(self) -> str | None:
        return self._backend

    # ── Ollama backend ──────────────────────────────────────

    def _load_ollama(self, cfg: dict) -> None:
        if not self._ollama_checked:
            self._ollama_available = _ollama_is_running()
            self._ollama_checked = True

        if not self._ollama_available:
            raise ConnectionError(
                "Ollama is not running!\n"
                "  1. Install from https://ollama.com\n"
                "  2. Start it: just run 'ollama serve' in a terminal\n"
                "  3. Then re-run this pipeline"
            )

        model_name = cfg["ollama_model"]
        print(f"[ModelManager] Using Ollama: {cfg['id']} "
              f"(model={model_name}) ...")

        # Auto-pull if not already downloaded
        if not _ollama_has_model(model_name):
            _ollama_pull(model_name)

        # Warm up — load model into VRAM by sending a tiny request
        print(f"[ModelManager] Warming up {model_name} ...")
        try:
            _ollama_request_stream("/api/chat", {
                "model": model_name,
                "messages": [{"role": "user", "content": "hi"}],
                "options": {"num_predict": 1},
            }, timeout=120)
        except Exception as e:
            print(f"[ModelManager] Warmup note: {e}")

        self._model = model_name  # just store the name
        print(f"[ModelManager] {cfg['id']} ready (Ollama).")

    def _generate_ollama(
        self, messages, max_new_tokens, temperature, top_p, top_k,
        repetition_penalty,
    ) -> str:
        model_name = self._model  # stored as string for Ollama
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": max_new_tokens,
                "temperature": max(temperature, 0.01),
                "top_p": top_p,
                "top_k": top_k,
                "repeat_penalty": repetition_penalty,
            },
        }

        result = _ollama_request_stream("/api/chat", payload, timeout=600)
        content = result.get("message", {}).get("content", "")
        return content.strip()

    # ── GGUF backend ────────────────────────────────────────

    def _load_gguf(self, cfg: dict) -> None:
        if not _HAS_LLAMA_CPP:
            raise ImportError(
                "llama-cpp-python not installed. "
                "Use --backend ollama instead (recommended), or install with:\n"
                "  CMAKE_ARGS=\"-DGGML_CUDA=ON\" "
                "pip install llama-cpp-python"
            )

        repo = cfg["gguf_repo"]
        fname = cfg["gguf_file"]
        model_path = _download_gguf(repo, fname)

        n_ctx = min(cfg.get("ctx", 32768), 32768)
        n_gpu_layers = cfg.get("gpu_layers", -1)

        print(f"[ModelManager] Loading GGUF: {cfg['id']} "
              f"(n_ctx={n_ctx}, gpu_layers={n_gpu_layers}) ...")

        self._model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            n_threads=os.cpu_count() or 4,
            verbose=False,
            flash_attn=True,
        )
        print(f"[ModelManager] {cfg['id']} ready (GGUF).")

    def _generate_gguf(
        self, messages, max_new_tokens, temperature, top_p, top_k,
        repetition_penalty,
    ) -> str:
        response = self._model.create_chat_completion(
            messages=messages,
            max_tokens=max_new_tokens,
            temperature=max(temperature, 0.01),
            top_p=top_p,
            top_k=top_k,
            repeat_penalty=repetition_penalty,
        )
        content = response["choices"][0]["message"]["content"]
        return content.strip() if content else ""

    # ── HF backend ──────────────────────────────────────────

    def _load_hf(self, cfg: dict) -> None:
        if not _HAS_HF:
            raise ImportError("transformers / torch not installed.")

        repo = cfg["hf_repo"]
        quant = cfg.get("quant", "none")

        print(f"[ModelManager] Loading HF: {cfg['id']} ({repo}) ...")

        tok_kwargs = {"trust_remote_code": True}
        mod_kwargs = {
            "trust_remote_code": True,
            "device_map": "auto",
            "torch_dtype": torch.float16,
        }

        if quant == "4bit":
            bnb_cfg = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            mod_kwargs["quantization_config"] = bnb_cfg

        self._tokenizer = AutoTokenizer.from_pretrained(repo, **tok_kwargs)
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

        self._model = AutoModelForCausalLM.from_pretrained(repo, **mod_kwargs)
        self._model.eval()
        print(f"[ModelManager] {cfg['id']} ready (HF).")

    def _generate_hf(
        self, messages, max_new_tokens, temperature, top_p, top_k,
        repetition_penalty,
    ) -> str:
        if hasattr(self._tokenizer, "apply_chat_template"):
            prompt = self._tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            prompt = ""
            for m in messages:
                role, content = m["role"], m["content"]
                if role == "system":
                    prompt += f"System: {content}\n\n"
                elif role == "user":
                    prompt += f"User: {content}\n\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n\n"
            prompt += "Assistant: "

        inputs = self._tokenizer(prompt, return_tensors="pt").to(
            self._model.device
        )

        gen_cfg = GenerationConfig(
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            do_sample=True,
            pad_token_id=self._tokenizer.pad_token_id,
        )

        with torch.no_grad():
            out = self._model.generate(**inputs, generation_config=gen_cfg)

        new_tokens = out[0][inputs["input_ids"].shape[1]:]
        text = self._tokenizer.decode(new_tokens, skip_special_tokens=True)
        return text.strip()

    # ── Cleanup ─────────────────────────────────────────────

    def _unload(self):
        if self._current_id is None:
            return

        print(f"[ModelManager] Unloading {self._current_id} ...")

        if self._backend == "ollama":
            # Ollama manages its own memory — nothing to free
            self._model = None
        elif self._backend == "gguf":
            del self._model
            self._model = None
        else:
            del self._model
            del self._tokenizer
            self._model = None
            self._tokenizer = None

        self._current_id = None
        self._backend = None

        gc.collect()
        try:
            import torch as _torch
            if _torch.cuda.is_available():
                _torch.cuda.empty_cache()
                _torch.cuda.synchronize()
        except ImportError:
            pass
