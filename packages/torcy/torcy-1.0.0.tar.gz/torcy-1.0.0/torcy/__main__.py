import torch
import platform
import time
import subprocess
import sys
import cpuinfo
from rich.console import Console
from rich.progress import track
from rich.text import Text

console = Console()

def typewriter(text, delay=0.03, color="bold magenta"):
    for ch in text:
        console.print(ch, style=color, end="")
        sys.stdout.flush()
        time.sleep(delay)
    console.print("")  


def get_cpu_name():
    try:
        return cpuinfo.get_cpu_info()["brand_raw"]
    except Exception:
        return platform.processor() or "Unknown CPU"

def run_test():
    typewriter("🔥 Starting PyTorch Environment Test 🔥", 0.03, "bold magenta")
    time.sleep(0.3)

    torch_ver = torch.__version__
    console.print(f"🧩 PyTorch version: [bold cyan]{torch_ver}[/bold cyan]")

    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_cap = torch.cuda.get_device_capability(0)
        console.print(f"⚙️  GPU detected: [bold green]{gpu_name}[/bold green] (CUDA {gpu_cap[0]}.{gpu_cap[1]})")
        device = "cuda"
    else:
        cpu_name = get_cpu_name()
        console.print(f"⚙️  Using CPU: [bold yellow]{cpu_name}[/bold yellow]")
        console.print("💡 You can install the GPU version with: [green]torcy --install-gpu[/green]")
        device = "cpu"

    console.print(f"\n📊 Random tensor on {device.upper()}:")
    tensor = torch.rand((3, 3), device=device)
    console.print(tensor)

    console.print("\n🧠 Running quick compute benchmark...")
    start = time.time()
    for _ in track(range(100000), description="🚀 Benchmarking..."):
        x = torch.rand(100, 100, device=device)
        y = torch.matmul(x, x)
    end = time.time()
    console.print(f"⚡ Compute speed: [bold]{end - start:.5f}s[/bold]")

    console.print(Text("✅ Test completed successfully - 🧘 Smooth setup!", style="bold green"))

def install_gpu_torch():
    console.print("🔍 Checking latest GPU-compatible PyTorch build...", style="bold cyan")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade",
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cu121"
        ], check=True)
        console.print("✅ PyTorch GPU version successfully installed!", style="bold green")
    except Exception as e:
        console.print(f"❌ Failed to install PyTorch GPU: {e}", style="bold red")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--install-gpu":
        install_gpu_torch()
    else:
        run_test()

if __name__ == "__main__":
    main()
