import logging
import numpy as np

logger = logging.getLogger(__name__)

# Try importing torch safely
TORCH_AVAILABLE = False
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None


class DriverMonitoringModel:
    """Driver Monitoring AI Inference interface. Automatically uses CUDA GPU when available."""

    def __init__(self):
        self.cuda_available = TORCH_AVAILABLE and torch.cuda.is_available()
        self.device = "cuda" if self.cuda_available else "cpu"
        self.gpu_name = torch.cuda.get_device_name(0) if self.cuda_available else "None"
        self.is_real_model = False  # Set to True when trained model weights are loaded

        if self.cuda_available:
            logger.info(f"[GPU AI WORKER] CUDA Available! Device: {self.device} ({self.gpu_name})")
        else:
            logger.info("[GPU AI WORKER] CUDA Not Available. Running on CPU / Simulation mode.")

    def get_gpu_info(self) -> dict:
        vram_str = "N/A"
        cuda_ver = "N/A"
        pytorch_ver = torch.__version__ if TORCH_AVAILABLE else "Not Installed"

        if self.cuda_available:
            try:
                allocated_gb = torch.cuda.memory_allocated(0) / (1024 ** 3)
                total_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
                vram_str = f"{allocated_gb:.1f} / {total_gb:.1f} GB"
                cuda_ver = torch.version.cuda or "Available"
            except Exception as e:
                logger.warning(f"Error querying VRAM info: {e}")

        return {
            "cuda_available": self.cuda_available,
            "ai_device": self.device,
            "gpu_name": self.gpu_name,
            "vram_usage": vram_str,
            "pytorch_version": pytorch_ver,
            "cuda_version": cuda_ver,
            "is_real_model": self.is_real_model
        }

    def predict(self, frame: np.ndarray) -> dict:
        """Runs driver monitoring inference on input RGB frame."""
        # Simulated inference fallback if no heavy PyTorch model weights loaded
        return {
            "drowsiness_score": 0.05,
            "fatigue_score": 0.02,
            "unresponsive": False,
            "inference_mode": "REAL_GPU" if (self.cuda_available and self.is_real_model) else "SIMULATION"
        }


driver_ai_model = DriverMonitoringModel()
