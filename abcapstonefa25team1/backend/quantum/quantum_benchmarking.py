# Project: PSU Abington Fall 2025 Capstone
# Purpose Details: Shor's Algorithm Performance Benchmark Suite + CPU vs GPU Comparison
# Course: CMPSC 488
# Author: Avik Bhuiyan
# Date Developed: 11/05/25
# Last Date Changed: 11/13/25
# Revision: 0.1.0

import time
import logging
import os
import sys
import math
from datetime import datetime
import pandas as pd

# Add the parent directory to the path to import quantum_shors
from quantum_shors import Quantum_Shors

try:
    import platform
    import psutil
except ImportError:
    print("Please install psutil: pip install psutil")
    sys.exit(1)

# 🎨 Color setup
from colorama import Fore, Style, init
init(autoreset=True)

try:
    import GPUtil
except ImportError:
    GPUtil = None


class ShorsBenchmark:
    def __init__(self):
        self.system_info = self._get_system_info()
        self.benchmarks = []
        
        # Logger setup
        self.logger = logging.getLogger("ShorsBenchmark")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

    def _get_system_info(self):
        """Collect system information for benchmark context"""
        try:
            info = {
                "platform": f"{platform.system()} {platform.release()}",
                "processor": platform.processor(),
                "cpu_cores_physical": psutil.cpu_count(logical=False),
                "cpu_cores_logical": psutil.cpu_count(logical=True),
                "ram_gb": round(psutil.virtual_memory().total / (1024**3), 1)
            }

            if GPUtil:
                gpus = GPUtil.getGPUs()
                info["gpus"] = [{"name": g.name, "memory_mb": g.memoryTotal} for g in gpus] if gpus else []
            else:
                info["gpus"] = "GPU info unavailable (install GPUtil)"

            return info
        except Exception as e:
            return {"error": str(e)}

    def benchmark_single_run(self, N, use_gpu=False, max_attempts=5):
        """Run a single benchmark and measure detailed resource metrics"""
        shor = Quantum_Shors()
        shor.enable_gpu(use_gpu)
        shor.logger.setLevel(logging.WARNING)

        process = psutil.Process(os.getpid())
        cpu_before = psutil.cpu_percent(interval=None)
        mem_before = process.memory_info().rss / (1024 ** 2)
        gpu_before = GPUtil.getGPUs()[0].memoryUsed if (GPUtil and GPUtil.getGPUs()) else 0

        start_time = time.time()
        result = shor.run_shors_algorithm(N, max_attempts=max_attempts)
        end_time = time.time()

        cpu_after = psutil.cpu_percent(interval=None)
        mem_after = process.memory_info().rss / (1024 ** 2)
        gpu_after = GPUtil.getGPUs()[0].memoryUsed if (GPUtil and GPUtil.getGPUs()) else 0

        execution_time = end_time - start_time
        success = result is not None

        # Get circuit metrics
        try:
            n_count = max(8, 2 * math.ceil(math.log2(N)))
            test_circuit = shor.create_shor_circuit(N, 2, n_count)
            circuit_qubits = test_circuit.num_qubits
            circuit_gates = test_circuit.size()
            circuit_depth = test_circuit.depth()
        except Exception:
            circuit_qubits = circuit_gates = circuit_depth = 0

        return {
            "N": N,
            "use_gpu": use_gpu,
            "execution_time": execution_time,
            "success": success,
            "factors": result if success else None,
            "cpu_usage_delta": round(cpu_after - cpu_before, 2),
            "mem_usage_mb": round(mem_after - mem_before, 2),
            "gpu_mem_used_mb": round(gpu_after - gpu_before, 2),
            "circuit_qubits": circuit_qubits,
            "circuit_gates": circuit_gates,
            "circuit_depth": circuit_depth,
        }

    def run_comparison_benchmark(self, test_numbers, runs_per_test=3, max_attempts=5):
        """Run CPU vs GPU comparisons across multiple test numbers"""
        self.logger.info(Fore.CYAN + "=" * 80)
        self.logger.info(Fore.CYAN + Style.BRIGHT + "SHOR'S ALGORITHM PERFORMANCE BENCHMARK")
        self.logger.info(Fore.CYAN + "=" * 80)
        self.logger.info(Fore.YELLOW + f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(Fore.YELLOW + f"System: {self.system_info['platform']}")
        self.logger.info(Fore.YELLOW + f"CPU: {self.system_info['processor']}")
        self.logger.info(Fore.YELLOW + f"RAM: {self.system_info['ram_gb']} GB")
        if isinstance(self.system_info["gpus"], list):
            for gpu in self.system_info["gpus"]:
                self.logger.info(Fore.MAGENTA + f"GPU: {gpu['name']} ({gpu['memory_mb']} MB)")
        self.logger.info(Fore.CYAN + "=" * 80)

        all_runs = []

        for N in test_numbers:
            self.logger.info(Fore.CYAN + f"\nBenchmarking N = {N}")
            self.logger.info(Fore.CYAN + "-" * 50)

            for mode, color in [("CPU", Fore.YELLOW), ("GPU", Fore.MAGENTA)]:
                use_gpu = mode == "GPU"
                self.logger.info(color + f"Running {mode} tests...")
                times = []

                for run in range(runs_per_test):
                    print(color + f"  {mode} Run {run + 1}/{runs_per_test}...", end=" ")
                    try:
                        metrics = self.benchmark_single_run(N, use_gpu, max_attempts)
                        all_runs.append(metrics)
                        times.append(metrics["execution_time"])
                        if metrics["success"]:
                            print(Fore.GREEN + f"✓ {metrics['execution_time']:.2f}s (factors: {metrics['factors']})")
                        else:
                            print(Fore.RED + f"✗ {metrics['execution_time']:.2f}s")
                    except Exception as e:
                        print(Fore.RED + f"✗ Error: {e}")
                        times.append(0)

            cpu_avg = sum(r["execution_time"] for r in all_runs if not r["use_gpu"]) / max(1, runs_per_test)
            gpu_avg = sum(r["execution_time"] for r in all_runs if r["use_gpu"]) / max(1, runs_per_test)
            speedup = cpu_avg / gpu_avg if gpu_avg > 0 else 0

            winner = "GPU" if speedup > 1.1 else "CPU" if speedup < 0.9 else "Tie"
            # Pull one representative run for circuit details (any CPU run should have them)
            circuit_data = next((r for r in all_runs if r["N"] == N and not r["use_gpu"]), None)
            if circuit_data:
                qubits = circuit_data["circuit_qubits"]
                gates = circuit_data["circuit_gates"]
                depth = circuit_data["circuit_depth"]
            else:
                qubits = gates = depth = 0

            self.logger.info(Fore.CYAN + f"\nSUMMARY for N = {N}:")
            self.logger.info(Fore.WHITE + f"  Circuit: {qubits} qubits, {gates} gates, depth {depth}")
            self.logger.info(
                Fore.WHITE
                + f"  CPU Avg: {cpu_avg:.2f}s | GPU Avg: {gpu_avg:.2f}s | "
                + f"Speedup: {speedup:.2f}x | Winner: "
                + (Fore.GREEN + winner if winner == "GPU" else Fore.YELLOW + winner)
)

        # self.save_results(all_runs)

        self.logger.info(Fore.CYAN + "\n" + "=" * 80)
        self.logger.info(Fore.CYAN + Style.BRIGHT + "RECOMMENDATION")
        self.logger.info(Fore.CYAN + "=" * 80)
        self.logger.info(Fore.CYAN + "💡 For small N, CPU is typically faster due to GPU overhead.")
        self.logger.info(Fore.CYAN + "💡 Use GPU only for large circuits (N > 35).")

    # def save_results(self, data, filename="benchmark_results.csv"):
    #     """Save all benchmark results to a CSV file"""
    #     df = pd.DataFrame(data)
    #     df.to_csv(filename, index=False)
    #     self.logger.info(Fore.GREEN + f"\nSaved detailed results to {filename}")


def main():
    """Main benchmark execution - Console output only"""
    print(Fore.CYAN + Style.BRIGHT + "Starting Shor's Algorithm Benchmark...")
    print(Fore.YELLOW + "This will test both CPU and GPU performance.")
    print(Fore.CYAN + "Each test runs 2 times for statistical accuracy.\n")

    benchmark = ShorsBenchmark()
    benchmark.run_comparison_benchmark(test_numbers=[15, 21, 35], runs_per_test=2, max_attempts=3)


if __name__ == "__main__":
    main()