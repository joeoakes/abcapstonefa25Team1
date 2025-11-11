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
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'quantum'))
from quantum_shors import Quantum_Shors

try:
    import platform
    import psutil
except ImportError:
    print("Please install psutil: pip install psutil")
    sys.exit(1)


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
        except Exception as e:
            # Fallback values if circuit creation fails
            circuit_qubits = 0
            circuit_gates = 0
            circuit_depth = 0
        
        metrics = {
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
        
        return metrics

    def run_comparison_benchmark(self, test_numbers, runs_per_test=3, max_attempts=5):
        """Run comprehensive CPU vs GPU comparison"""
        
        self.logger.info("=" * 80)
        self.logger.info("SHOR'S ALGORITHM PERFORMANCE BENCHMARK")
        self.logger.info("=" * 80)
        self.logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"System: {self.system_info['platform']}")
        self.logger.info(f"CPU: {self.system_info['processor']}")
        self.logger.info(f"RAM: {self.system_info['ram_gb']} GB")
        self.logger.info(f"CPU Cores: {self.system_info['cpu_cores_physical']} physical, {self.system_info['cpu_cores_logical']} logical")
        
        if 'gpus' in self.system_info and isinstance(self.system_info['gpus'], list):
            if self.system_info['gpus']:
                self.logger.info("GPUs:")
                for gpu in self.system_info['gpus']:
                    self.logger.info(f"  - {gpu['name']} ({gpu['memory_mb']} MB)")
            else:
                self.logger.info("GPUs: None detected")
        
        self.logger.info("=" * 80)
        
        for N in test_numbers:
            self.logger.info(f"\nBenchmarking N = {N}")
            self.logger.info("-" * 50)
            
            benchmark_data = {
                "N": N,
                "cpu_runs": [],
                "gpu_runs": [],
                "summary": {}
            }
            
            # CPU Benchmarks
            self.logger.info("Running CPU tests...")
            cpu_times = []
            cpu_successes = 0
            
            for run in range(runs_per_test):
                print(f"  CPU Run {run + 1}/{runs_per_test}...", end=" ")
                
                try:
                    metrics = self.benchmark_single_run(N, use_gpu=False, max_attempts=max_attempts)
                    benchmark_data["cpu_runs"].append(metrics)
                    
                    cpu_times.append(metrics["execution_time"])
                    if metrics["success"]:
                        cpu_successes += 1
                        print(f"✓ {metrics['execution_time']:.2f}s (factors: {metrics['factors']})")
                    else:
                        print(f"✗ {metrics['execution_time']:.2f}s")
                except Exception as e:
                    print(f"✗ CPU Error: {str(e)}")
                    cpu_times.append(0)
            
            # GPU Benchmarks
            self.logger.info("Running GPU tests...")
            gpu_times = []
            gpu_successes = 0
            
            for run in range(runs_per_test):
                print(f"  GPU Run {run + 1}/{runs_per_test}...", end=" ")
                
                try:
                    metrics = self.benchmark_single_run(N, use_gpu=True, max_attempts=max_attempts)
                    benchmark_data["gpu_runs"].append(metrics)
                    
                    gpu_times.append(metrics["execution_time"])
                    if metrics["success"]:
                        gpu_successes += 1
                        print(f"✓ {metrics['execution_time']:.2f}s (factors: {metrics['factors']})")
                    else:
                        print(f"✗ {metrics['execution_time']:.2f}s")
                        
                except Exception as e:
                    print(f"✗ GPU Error: {str(e)}")
                    benchmark_data["gpu_runs"].append({
                        "N": N, "use_gpu": True, "execution_time": 0, 
                        "success": False, "error": str(e)
                    })
                    gpu_times.append(0)
            
            # Calculate summary statistics
            if cpu_times and any(t > 0 for t in cpu_times):
                valid_cpu_times = [t for t in cpu_times if t > 0]
                cpu_avg = sum(valid_cpu_times) / len(valid_cpu_times) if valid_cpu_times else 0
                cpu_min = min(valid_cpu_times) if valid_cpu_times else 0
                cpu_max = max(valid_cpu_times) if valid_cpu_times else 0
            else:
                cpu_avg = cpu_min = cpu_max = 0
                
            if gpu_times and any(t > 0 for t in gpu_times):
                valid_gpu_times = [t for t in gpu_times if t > 0]
                gpu_avg = sum(valid_gpu_times) / len(valid_gpu_times) if valid_gpu_times else 0
                gpu_min = min(valid_gpu_times) if valid_gpu_times else 0
                gpu_max = max(valid_gpu_times) if valid_gpu_times else 0
            else:
                gpu_avg = gpu_min = gpu_max = 0
            
            # Get circuit info from successful runs
            circuit_info = {"qubits": 0, "gates": 0, "depth": 0}
            for run in benchmark_data["cpu_runs"] + benchmark_data["gpu_runs"]:
                if run.get("circuit_qubits", 0) > 0:
                    circuit_info = {
                        "qubits": run["circuit_qubits"],
                        "gates": run["circuit_gates"], 
                        "depth": run["circuit_depth"]
                    }
                    break
            
            benchmark_data["summary"] = {
                "cpu_avg_time": cpu_avg,
                "cpu_min_time": cpu_min,
                "cpu_max_time": cpu_max,
                "cpu_success_rate": (cpu_successes / runs_per_test) * 100,
                "gpu_avg_time": gpu_avg,
                "gpu_min_time": gpu_min,
                "gpu_max_time": gpu_max,
                "gpu_success_rate": (gpu_successes / runs_per_test) * 100,
                "speedup": cpu_avg / gpu_avg if gpu_avg > 0 else 0,
                "circuit_qubits": circuit_info["qubits"],
                "circuit_gates": circuit_info["gates"],
                "circuit_depth": circuit_info["depth"]
            }
            
            self.benchmarks.append(benchmark_data)
            
            # Print summary for this N
            self._print_summary_for_n(benchmark_data)
        
        # Print overall summary
        self._print_overall_summary()

    def _print_summary_for_n(self, data):
        """Print summary for a single N value"""
        summary = data["summary"]
        
        self.logger.info(f"\nSUMMARY for N = {data['N']}:")
        self.logger.info(f"Circuit: {summary['circuit_qubits']} qubits, {summary['circuit_gates']} gates, depth {summary['circuit_depth']}")
        self.logger.info(f"CPU:     Avg {summary['cpu_avg_time']:.2f}s, Min {summary['cpu_min_time']:.2f}s, Max {summary['cpu_max_time']:.2f}s, Success {summary['cpu_success_rate']:.0f}%")
        self.logger.info(f"GPU:     Avg {summary['gpu_avg_time']:.2f}s, Min {summary['gpu_min_time']:.2f}s, Max {summary['gpu_max_time']:.2f}s, Success {summary['gpu_success_rate']:.0f}%")
        
        if summary['speedup'] > 0:
            if summary['speedup'] > 1:
                self.logger.info(f"Result:  GPU is {summary['speedup']:.2f}x FASTER")
            else:
                self.logger.info(f"Result:  CPU is {1/summary['speedup']:.2f}x FASTER")
        else:
            self.logger.info("Result:  Unable to calculate speedup")

    def _print_overall_summary(self):
        """Print overall benchmark summary"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("OVERALL PERFORMANCE SUMMARY")
        self.logger.info("=" * 80)
        
        # Create summary table
        self.logger.info(f"{'N':<6} {'Qubits':<8} {'Gates':<8} {'Depth':<8} {'CPU Avg':<10} {'GPU Avg':<10} {'Speedup':<12} {'Winner':<10}")
        self.logger.info("-" * 80)
        
        total_cpu_time = 0
        total_gpu_time = 0
        
        for benchmark in self.benchmarks:
            summary = benchmark["summary"]
            N = benchmark["N"]
            
            total_cpu_time += summary["cpu_avg_time"]
            total_gpu_time += summary["gpu_avg_time"]
            
            if summary["speedup"] > 1.1:
                winner = "GPU"
                speedup_str = f"{summary['speedup']:.2f}x"
            elif summary["speedup"] < 0.9 and summary["speedup"] > 0:
                winner = "CPU"
                speedup_str = f"{1/summary['speedup']:.2f}x"
            else:
                winner = "Tie"
                speedup_str = "~1.0x"
            
            self.logger.info(f"{N:<6} {summary['circuit_qubits']:<8} {summary['circuit_gates']:<8} {summary['circuit_depth']:<8} "
                           f"{summary['cpu_avg_time']:<10.2f} {summary['gpu_avg_time']:<10.2f} {speedup_str:<12} {winner:<10}")
        
        # Overall recommendation
        self.logger.info("\n" + "=" * 80)
        self.logger.info("RECOMMENDATIONS")
        self.logger.info("=" * 80)
        
        if total_gpu_time > 0 and total_cpu_time > 0:
            overall_speedup = total_cpu_time / total_gpu_time
            
            if overall_speedup > 1.2:
                self.logger.info("✓ GPU acceleration is beneficial for this workload")
                self.logger.info(f"  Overall speedup: {overall_speedup:.2f}x faster with GPU")
                self.logger.info("  Recommendation: Use GPU mode for better performance")
            elif overall_speedup < 0.8:
                self.logger.info("⚠ CPU performs better than GPU for this workload")
                self.logger.info(f"  CPU is {1/overall_speedup:.2f}x faster than GPU")
                self.logger.info("  Recommendation: Use CPU mode for better performance")
                self.logger.info("  Note: GPU overhead may exceed benefits for small circuits")
            else:
                self.logger.info("≈ CPU and GPU performance are similar")
                self.logger.info("  Recommendation: Either mode is acceptable")
        
        self.logger.info("\nPerformance Notes:")
        self.logger.info("- N ≤ 21: Fast (seconds)")
        self.logger.info("- N ≤ 35: Moderate (10-60 seconds)")
        self.logger.info("- N ≤ 77: Slow (minutes)")
        self.logger.info("- N > 100: Very slow (may require hours or fail due to memory)")
        self.logger.info("\nGPU Performance Notes:")
        self.logger.info("- GPU acceleration is most beneficial for larger circuits")
        self.logger.info("- Small circuits may show GPU overhead instead of speedup")
        self.logger.info("- Results depend heavily on your specific GPU hardware")
        self.logger.info("- Memory bandwidth often more important than compute power for quantum simulation")


def main():
    """Main benchmark execution - Console output only"""
    benchmark = ShorsBenchmark()
    
    # Test with different problem sizes - start very small for testing
    test_numbers = [15, 21]  # Start small for testing
    
    print("Starting Shor's Algorithm Benchmark...")
    print("This will test both CPU and GPU performance.")
    print(f"Testing with N = {test_numbers}")
    print("Each test runs 2 times for statistical accuracy.")
    
    benchmark.run_comparison_benchmark(
        test_numbers=test_numbers,
        runs_per_test=2,
        max_attempts=3
    )


if __name__ == "__main__":
    main()