import importlib
import sys
import time
import random
import platform
from typing import Optional

try:
    import cpuinfo
except ImportError:
    cpuinfo = None

class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"

def typewriter(text, delay=0.02, color=Color.RESET):
    for char in text:
        sys.stdout.write(color + char + Color.RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def detect_cpu_info():
    if cpuinfo:
        try:
            return cpuinfo.get_cpu_info().get("brand_raw", "").strip()
        except Exception:
            pass

    cpu_name = platform.processor()
    if cpu_name:
        return cpu_name.strip()

    uname_info = platform.uname()
    if uname_info.processor:
        return uname_info.processor.strip()

    return "Unknown CPU"

def test(torch_module: Optional[object] = None) -> bool:
    typewriter("🔥 Starting PyTorch Environment Test 🔥", 0.03, Color.MAGENTA)
    time.sleep(0.3)

    try:
        torch = torch_module or importlib.import_module("torch")
    except ModuleNotFoundError:
        typewriter("❌ PyTorch is not installed yet.", 0.02, Color.RED)
        typewriter("💡 Install using:", 0.02, Color.YELLOW)
        print(Color.CYAN + "   pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121" + Color.RESET)
        return False

    version = torch.__version__
    cuda_available = torch.cuda.is_available()
    cuda_version = getattr(torch.version, "cuda", None)

    typewriter(f"🧩 PyTorch version: {version}", 0.02, Color.CYAN)

    if not cuda_available:
        cpu_name = detect_cpu_info()
        typewriter("⚙️  CUDA support: Not available", 0.02, Color.YELLOW)
        typewriter(f"🧠 Running on CPU: {cpu_name}", 0.02, Color.GREEN)

        if "+cpu" in version:
            typewriter("\n💡 Your PyTorch is the CPU-only version.", 0.02, Color.RED)
            typewriter("   To use the GPU (e.g. RTX 3050), install the version with CUDA:", 0.02, Color.YELLOW)
            print(Color.CYAN + "   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121" + Color.RESET)
        else:
            typewriter("\n⚠️  “CUDA is not active. Make sure the NVIDIA driver and toolkit are properly installed.", 0.02, Color.RED)
            print(Color.CYAN + "   pip install nvidia-cuda-runtime-cu12" + Color.RESET)

        x = torch.rand(3, 3)
        typewriter("\n📊 Random tensor on CPU:", 0.02, Color.MAGENTA)
        print(Color.CYAN + str(x) + Color.RESET)

    else:
        gpu_name = torch.cuda.get_device_name(0)
        gpu_count = torch.cuda.device_count()
        typewriter(f"⚙️  CUDA version: {cuda_version}", 0.02, Color.CYAN)
        typewriter(f"💻 GPU detected: {gpu_name} (x{gpu_count})", 0.02, Color.GREEN)

        x = torch.rand(3, 3).cuda()
        typewriter("📊 Random tensor on GPU:", 0.02, Color.MAGENTA)
        print(Color.CYAN + str(x) + Color.RESET)

    typewriter("\n🧠 Running quick compute benchmark...", 0.02, Color.YELLOW)
    start = time.time()
    for _ in range(1000):
        _ = x @ x
    end = time.time()

    duration = end - start
    color = Color.GREEN if duration < 0.05 else Color.YELLOW
    typewriter(f"⚡ Compute speed: {duration:.5f}s", 0.02, color)

    mood = random.choice(["🔥 Solid setup!", "🚀 Ready for training!", "🧘 Smooth setup!", "💪 Tensor Power!"])
    typewriter(f"\n✅ Test completed successfully - {mood}", 0.02, Color.BOLD)
    return True
