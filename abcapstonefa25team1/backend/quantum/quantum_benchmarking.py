"""
Shor's Algorithm Performance Benchmark Suite
Compares CPU vs GPU performance with detailed metrics - Console output only
"""

import time
import logging
import os
import sys
from datetime import datetime

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


class ShorsBenchmark:
    def __init__(self):
        self.system_info = self._get_system_info()
        self.benchmarks = []
        
        # Set up clean logging for benchmarks
        self.logger = logging.getLogger("ShorsBenchmark")
        self.logger.setLevel(logging.INFO)
        
        # Create console handler with clean format
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

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
            
            # Try to get GPU info
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    info["gpus"] = [{"name": gpu.name, "memory_mb": gpu.memoryTotal} for gpu in gpus]
                else:
                    info["gpus"] = []
            except ImportError:
                info["gpus"] = "GPU info unavailable (install GPUtil)"
                
            return info
        except Exception as e:
            return {"error": str(e)}

    def benchmark_single_run(self, N, use_gpu=False, max_attempts=5):
        """Benchmark a single factorization run"""
        shor = Quantum_Shors()
        shor.enable_gpu(use_gpu)
        
        # Suppress detailed logging for clean benchmark output
        shor.logger.setLevel(logging.WARNING)
        
        start_time = time.time()
        result = shor.run_shors_algorithm(N, max_attempts=max_attempts)
        end_time = time.time()
        
        execution_time = end_time - start_time
        success = result is not None
        
        # Get circuit information by creating a test circuit
        try:
            import math
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
            "circuit_qubits": circuit_qubits,
            "circuit_gates": circuit_gates,
            "circuit_depth": circuit_depth,
            "attempts_made": max_attempts if not success else "unknown"
        }

    def run_comparison_benchmark(self, test_numbers, runs_per_test=3, max_attempts=5):
        """Run comprehensive CPU vs GPU comparison"""
        self.logger.info(Fore.CYAN + "=" * 80)
        self.logger.info(Fore.CYAN + Style.BRIGHT + "SHOR'S ALGORITHM PERFORMANCE BENCHMARK")
        self.logger.info(Fore.CYAN + "=" * 80)
        self.logger.info(Fore.YELLOW + f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(Fore.YELLOW + f"System: {self.system_info['platform']}")
        self.logger.info(Fore.YELLOW + f"CPU: {self.system_info['processor']}")
        self.logger.info(Fore.YELLOW + f"RAM: {self.system_info['ram_gb']} GB")
        self.logger.info(Fore.YELLOW + f"CPU Cores: {self.system_info['cpu_cores_physical']} physical, {self.system_info['cpu_cores_logical']} logical")
        
        if 'gpus' in self.system_info and isinstance(self.system_info['gpus'], list):
            if self.system_info['gpus']:
                self.logger.info(Fore.MAGENTA + "GPUs:")
                for gpu in self.system_info['gpus']:
                    self.logger.info(Fore.MAGENTA + f"  - {gpu['name']} ({gpu['memory_mb']} MB)")
            else:
                self.logger.info(Fore.RED + "GPUs: None detected")
        
        self.logger.info(Fore.CYAN + "=" * 80)
        
        for N in test_numbers:
            self.logger.info(Fore.CYAN + f"\nBenchmarking N = {N}")
            self.logger.info(Fore.CYAN + "-" * 50)
            
            benchmark_data = {"N": N, "cpu_runs": [], "gpu_runs": [], "summary": {}}
            
            # CPU Tests
            self.logger.info(Fore.YELLOW + "Running CPU tests...")
            cpu_times, cpu_successes = [], 0
            
            for run in range(runs_per_test):
                print(Fore.YELLOW + f"  CPU Run {run + 1}/{runs_per_test}...", end=" ")
                try:
                    metrics = self.benchmark_single_run(N, use_gpu=False, max_attempts=max_attempts)
                    benchmark_data["cpu_runs"].append(metrics)
                    cpu_times.append(metrics["execution_time"])
                    if metrics["success"]:
                        cpu_successes += 1
                        print(Fore.GREEN + f"✓ {metrics['execution_time']:.2f}s (factors: {metrics['factors']})")
                    else:
                        print(Fore.RED + f"✗ {metrics['execution_time']:.2f}s")
                except Exception as e:
                    print(Fore.RED + f"✗ CPU Error: {str(e)}")
                    cpu_times.append(0)
            
            # GPU Tests
            self.logger.info(Fore.MAGENTA + "Running GPU tests...")
            gpu_times, gpu_successes = [], 0
            
            for run in range(runs_per_test):
                print(Fore.MAGENTA + f"  GPU Run {run + 1}/{runs_per_test}...", end=" ")
                try:
                    metrics = self.benchmark_single_run(N, use_gpu=True, max_attempts=max_attempts)
                    benchmark_data["gpu_runs"].append(metrics)
                    gpu_times.append(metrics["execution_time"])
                    if metrics["success"]:
                        gpu_successes += 1
                        print(Fore.GREEN + f"✓ {metrics['execution_time']:.2f}s (factors: {metrics['factors']})")
                    else:
                        print(Fore.RED + f"✗ {metrics['execution_time']:.2f}s")
                except Exception as e:
                    print(Fore.RED + f"✗ GPU Error: {str(e)}")
                    gpu_times.append(0)
            
            # Summary Stats
            def avg(lst): return sum(lst)/len([x for x in lst if x > 0]) if any(lst) else 0
            cpu_avg, gpu_avg = avg(cpu_times), avg(gpu_times)
            
            speedup = cpu_avg / gpu_avg if gpu_avg > 0 else 0
            winner = "GPU" if speedup > 1.1 else "CPU" if speedup < 0.9 else "Tie"
            
            self.logger.info(Fore.CYAN + f"\nSUMMARY for N = {N}:")
            self.logger.info(Fore.WHITE + f"  CPU Avg: {cpu_avg:.2f}s | GPU Avg: {gpu_avg:.2f}s | Winner: " +
                             (Fore.GREEN + winner if winner == "GPU" else Fore.YELLOW + winner))
        
        self.logger.info(Fore.CYAN + "\n" + "=" * 80)
        self.logger.info(Fore.CYAN + Style.BRIGHT + "RECOMMENDATION")
        self.logger.info(Fore.CYAN + "=" * 80)
        self.logger.info(Fore.CYAN + "💡 For small N, CPU is typically faster due to GPU overhead.")
        self.logger.info(Fore.CYAN + "💡 Use GPU only for large circuits (N > 35).")


def main():
    """Main benchmark execution - Console output only"""
    print(Fore.CYAN + Style.BRIGHT + "Starting Shor's Algorithm Benchmark...")
    print(Fore.YELLOW + "This will test both CPU and GPU performance.")
    print(Fore.CYAN + "Each test runs 2 times for statistical accuracy.\n")
    
    benchmark = ShorsBenchmark()
    benchmark.run_comparison_benchmark(test_numbers=[15, 21], runs_per_test=2, max_attempts=3)


if __name__ == "__main__":
    main()