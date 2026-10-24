import time
import logging
import threading
from ai_worker.inference.driver_model import driver_ai_model

logger = logging.getLogger(__name__)


class AIWorker:
    """Background GPU Worker for computer vision and driver monitoring inference."""

    def __init__(self):
        self.is_running = False
        self.worker_thread = None
        self.inference_fps = 0.0

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._run_loop, daemon=True)
            self.worker_thread.start()
            logger.info(f"AI Worker background process started on device: {driver_ai_model.device}")

    def stop(self):
        self.is_running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)
            logger.info("AI Worker stopped.")

    def _run_loop(self):
        frame_count = 0
        start_time = time.time()
        while self.is_running:
            # Simulate or execute GPU inference tick
            time.sleep(0.05)  # ~20 FPS inference loop
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                self.inference_fps = round(frame_count / elapsed, 1)
                frame_count = 0
                start_time = time.time()

    def get_status(self) -> dict:
        info = driver_ai_model.get_gpu_info()
        info["inference_fps"] = self.inference_fps
        info["status"] = "ONLINE" if self.is_running else "OFFLINE"
        return info


ai_worker = AIWorker()
