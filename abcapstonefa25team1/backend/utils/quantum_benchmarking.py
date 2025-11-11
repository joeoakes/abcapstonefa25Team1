"""
Benchmark Results Analysis Tool
Analyzes saved benchmark data and generates reports
"""

import json
import sys
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


class BenchmarkAnalyzer:
    def __init__(self, results_file):
        with open(results_file, 'r') as f:
            self.data = json.load(f)
    
    def generate_performance_plots(self):
        """Generate performance comparison plots"""
        # Extract data for plotting
        n_values = []
        cpu_times = []
        gpu_times = []
        qubits = []
        gates = []
        
        for benchmark in self.data["benchmarks"]:
            n_values.append(benchmark["N"])
            cpu_times.append(benchmark["summary"]["cpu_avg_time"])
            gpu_times.append(benchmark["summary"]["gpu_avg_time"])
            qubits.append(benchmark["summary"]["circuit_qubits"])
            gates.append(benchmark["summary"]["circuit_gates"])
        
        # Create subplot figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot 1: Execution Time Comparison
        ax1.plot(n_values, cpu_times, 'bo-', label='CPU', linewidth=2, markersize=8)
        ax1.plot(n_values, gpu_times, 'ro-', label='GPU', linewidth=2, markersize=8)
        ax1.set_xlabel('N (Number to Factor)')
        ax1.set_ylabel('Execution Time (seconds)')
        ax1.set_title('CPU vs GPU Execution Time')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Speedup Factor
        speedups = [cpu/gpu if gpu > 0 else 0 for cpu, gpu in zip(cpu_times, gpu_times)]
        colors = ['green' if s > 1 else 'red' for s in speedups]
        ax2.bar(n_values, speedups, color=colors, alpha=0.7)
        ax2.axhline(y=1, color='black', linestyle='--', alpha=0.5)
        ax2.set_xlabel('N (Number to Factor)')
        ax2.set_ylabel('Speedup Factor (CPU time / GPU time)')
        ax2.set_title('GPU Speedup Factor')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Circuit Complexity
        ax3.plot(n_values, qubits, 'go-', label='Qubits', linewidth=2, markersize=8)
        ax3_twin = ax3.twinx()
        ax3_twin.plot(n_values, gates, 'mo-', label='Gates', linewidth=2, markersize=8)
        ax3.set_xlabel('N (Number to Factor)')
        ax3.set_ylabel('Number of Qubits', color='green')
        ax3_twin.set_ylabel('Number of Gates', color='magenta')
        ax3.set_title('Circuit Complexity vs Problem Size')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Success Rates
        cpu_success = [b["summary"]["cpu_success_rate"] for b in self.data["benchmarks"]]
        gpu_success = [b["summary"]["gpu_success_rate"] for b in self.data["benchmarks"]]
        
        x_pos = range(len(n_values))
        width = 0.35
        
        ax4.bar([x - width/2 for x in x_pos], cpu_success, width, label='CPU', alpha=0.7)
        ax4.bar([x + width/2 for x in x_pos], gpu_success, width, label='GPU', alpha=0.7)
        ax4.set_xlabel('N (Number to Factor)')
        ax4.set_ylabel('Success Rate (%)')
        ax4.set_title('Success Rate Comparison')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(n_values)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('shor_benchmark_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self):
        """Generate detailed text report"""
        report = []
        report.append("=" * 80)
        report.append("SHOR'S ALGORITHM BENCHMARK ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Data from: {self.data['timestamp']}")
        report.append("")
        
        # System info
        info = self.data['system_info']
        report.append("SYSTEM INFORMATION:")
        report.append("-" * 40)
        report.append(f"Platform: {info['platform']}")
        report.append(f"Processor: {info['processor']}")
        report.append(f"RAM: {info['ram_gb']} GB")
        report.append(f"CPU Cores: {info['cpu_cores_physical']} physical, {info['cpu_cores_logical']} logical")
        if 'gpus' in info and isinstance(info['gpus'], list):
            if info['gpus']:
                report.append("GPUs:")
                for gpu in info['gpus']:
                    report.append(f"  - {gpu['name']} ({gpu['memory_mb']} MB)")
            else:
                report.append("GPUs: None detected")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("-" * 40)
        
        for benchmark in self.data["benchmarks"]:
            N = benchmark["N"]
            summary = benchmark["summary"]
            
            report.append(f"\nN = {N}:")
            report.append(f"  Circuit: {summary['circuit_qubits']} qubits, {summary['circuit_gates']} gates, depth {summary['circuit_depth']}")
            report.append(f"  CPU: {summary['cpu_avg_time']:.3f}s avg ({summary['cpu_success_rate']:.0f}% success)")
            report.append(f"  GPU: {summary['gpu_avg_time']:.3f}s avg ({summary['gpu_success_rate']:.0f}% success)")
            
            if summary['speedup'] > 0:
                if summary['speedup'] > 1:
                    report.append(f"  GPU is {summary['speedup']:.2f}x faster")
                else:
                    report.append(f"  CPU is {1/summary['speedup']:.2f}x faster")
        
        # Save report
        with open('benchmark_report.txt', 'w') as f:
            f.write('\n'.join(report))
        
        print('\n'.join(report))
        print(f"\nReport saved to: benchmark_report.txt")
        print(f"Plots saved to: shor_benchmark_analysis.png")


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_benchmark.py <results_file.json>")
        sys.exit(1)
    
    analyzer = BenchmarkAnalyzer(sys.argv[1])
    analyzer.generate_report()
    
    # Generate plots if matplotlib is available
    try:
        analyzer.generate_performance_plots()
    except ImportError:
        print("Install matplotlib and pandas for plot generation: pip install matplotlib pandas")


if __name__ == "__main__":
    main()