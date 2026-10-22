"""Device resolution and detection for TabPFN execution.

Supports:
  - cpu           : Always available, slower on large data.
  - cuda          : NVIDIA GPU via CUDA (PyTorch CUDA build).
  - rocm / cuda   : AMD GPU via ROCm – PyTorch treats ROCm as `cuda`, so we
                    detect the vendor separately and still pass `cuda` to TabPFN.
  - mps           : Apple Silicon GPU (Metal Performance Shaders).

Auto-detection order:  NVIDIA CUDA  →  AMD ROCm  →  Apple MPS  →  CPU
"""

import logging
from typing import Dict, List, Optional
from backend.app.config import settings

logger = logging.getLogger(__name__)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _torch_cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def _torch_mps_available() -> bool:
    try:
        import torch
        return hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    except Exception:
        return False


def _get_cuda_gpu_info() -> List[Dict]:
    """Return list of dicts with `name`, `vendor`, `vram_gb` for each CUDA device."""
    info: List[Dict] = []
    try:
        import torch
        if not torch.cuda.is_available():
            return info
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            name: str = props.name
            vram_gb = round(props.total_memory / (1024 ** 3), 1)
            # AMD ROCm GPUs expose themselves via CUDA interface but their names
            # contain "Radeon" / "gfx" / "Instinct" / "RX" / "AMD".
            name_lower = name.lower()
            is_amd = any(k in name_lower for k in ("radeon", "gfx", "instinct", "rx ", "amd"))
            vendor = "amd" if is_amd else "nvidia"
            info.append({"index": i, "name": name, "vendor": vendor, "vram_gb": vram_gb})
    except Exception as exc:
        logger.debug(f"Could not enumerate CUDA devices: {exc}")
    return info


def _get_mps_info() -> Optional[Dict]:
    """Return basic MPS device info dict or None."""
    try:
        import torch
        if not (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()):
            return None
        # MPS does not expose detailed memory stats in all PyTorch versions
        return {"name": "Apple Silicon GPU (MPS)", "vendor": "apple"}
    except Exception:
        return None


# ── Public API ────────────────────────────────────────────────────────────────

def get_available_device() -> str:
    """Auto-detect the best available device unless config overrides it.

    Priority: NVIDIA CUDA → AMD ROCm (also 'cuda') → Apple MPS → CPU.
    Returns a string that PyTorch / TabPFN accepts: 'cuda', 'mps', or 'cpu'.
    """
    target = settings.TABPFN_DEVICE.lower().strip()

    # Explicit override from .env / environment
    if target in {"cpu", "cuda", "mps", "rocm"}:
        # ROCm is accessed through the 'cuda' PyTorch interface
        resolved = "cuda" if target == "rocm" else target
        logger.info(f"Device explicitly set to '{target}' → resolved as '{resolved}'.")
        return resolved

    # Auto-detect
    if _torch_cuda_available():
        gpus = _get_cuda_gpu_info()
        if gpus:
            vendor = gpus[0]["vendor"]
            tag = "AMD ROCm" if vendor == "amd" else "NVIDIA CUDA"
            logger.info(f"{tag} GPU detected ({gpus[0]['name']}). Using cuda device.")
        else:
            logger.info("CUDA available (no device enumeration). Using cuda device.")
        return "cuda"

    if _torch_mps_available():
        logger.info("Apple Silicon MPS detected. Using mps device.")
        return "mps"

    logger.info("No GPU detected. Using cpu device.")
    return "cpu"


def get_device_catalog() -> Dict:
    """Return full catalog of available compute devices for the health/status API."""
    cuda_gpus = _get_cuda_gpu_info()
    mps_info  = _get_mps_info()

    available: List[Dict] = [
        {
            "id": "cpu",
            "label": "CPU",
            "vendor": "cpu",
            "available": True,
            "recommended": False,
        }
    ]

    if cuda_gpus:
        for gpu in cuda_gpus:
            vendor_label = "AMD ROCm" if gpu["vendor"] == "amd" else "NVIDIA CUDA"
            available.append({
                "id": "cuda",
                "label": f"{gpu['name']} ({vendor_label})",
                "vendor": gpu["vendor"],          # "nvidia" | "amd"
                "vram_gb": gpu["vram_gb"],
                "available": True,
                "recommended": True,              # GPU preferred
            })
    else:
        # Still advertise the options so UI can show them as unavailable
        for vendor_id, vendor_label in [("nvidia", "NVIDIA CUDA"), ("amd", "AMD ROCm")]:
            available.append({
                "id": "cuda",
                "label": vendor_label,
                "vendor": vendor_id,
                "available": False,
                "recommended": False,
            })

    if mps_info:
        available.append({
            "id": "mps",
            "label": mps_info["name"],
            "vendor": "apple",
            "available": True,
            "recommended": True,
        })
    else:
        available.append({
            "id": "mps",
            "label": "Apple MPS (Apple Silicon only)",
            "vendor": "apple",
            "available": False,
            "recommended": False,
        })

    return {"devices": available}


# ── Legacy helpers used by health router ─────────────────────────────────────

def is_cuda_available() -> bool:
    """Check if any CUDA-capable device (NVIDIA or AMD ROCm) is available."""
    return _torch_cuda_available()


def is_mps_available() -> bool:
    """Check if Apple MPS is available."""
    return _torch_mps_available()
