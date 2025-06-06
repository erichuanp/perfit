# -*- coding: utf-8 -*-
"""
Perfit - A lightweight Python performance profiler and visualizer.

Copyright (c) 2025 erichuanp (erichuanp@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Author: erichuanp
Email: erichuanp@gmail.com
Created: 2025-06-06
"""


import time
import tracemalloc
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from functools import wraps
from datetime import datetime


class Perfit:
    """
    Perfit - A lightweight Python performance profiler and visualizer.
    This class provides tools to measure the execution time and memory usage of
    functions, filter outliers, save performance data, and visualize results.
    
    Attributes:
        badDataScaler (float): A multiplier used to filter outliers based on the median.
        results (dict): A dictionary to store performance data for decorated functions.
    """
    def __init__(self, badDataScaler=1000):
        """
        Initialize the Perfit class.

        Args:
            badDataScaler (float): Multiplier for filtering outliers. Default is 1000.
        """
        self.results = {}  # Store performance data for all functions
        self.badDataScaler = badDataScaler  # Global multiplier for outlier filtering

    def __call__(self, func):
        """
        Decorator to wrap a function and record its performance data.

        Args:
            func (callable): The function to be decorated.

        Returns:
            callable: The wrapped function with performance tracking.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Start time and memory tracking
            tracemalloc.start()
            start_time = time.perf_counter()

            # Execute the function
            result = func(*args, **kwargs)

            # Stop time and memory tracking
            end_time = time.perf_counter()
            current, mem_usage = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Record performance data
            if func.__name__ not in self.results:
                self.results[func.__name__] = []
            self.results[func.__name__].append({
                "t": end_time - start_time,  # Execution time in seconds
                "m": mem_usage / 1024  # Memory usage in KB
            })

            return result
        return wrapper

    def _filter_bad_data(self, values):
        """
        Filter outliers from performance data based on the global badDataScaler.

        Args:
            values (list): List of performance metrics (e.g., execution times or memory usage).

        Returns:
            list: Filtered performance data without outliers.
        """
        median_value = np.median(values)  # Calculate the median value
        return [v for v in values if v <= median_value * self.badDataScaler]

    def _to_json(self):
        """
        Save all recorded performance data to JSON files.
        Each function's data is saved in a separate file named with a timestamp.
        """
        # Ensure the "performances" directory exists
        performances_dir = "performances"
        if not os.path.exists(performances_dir):
            os.makedirs(performances_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for func_name, data in self.results.items():
            filename = f"{func_name}_{timestamp}.json"
            filepath = os.path.join(performances_dir, filename)
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Results for {func_name} saved to {filepath}")

    def prints(self, precision=5, showPlot=False):
        """
        Print statistical performance data for all recorded functions.

        Args:
            precision (int): Number of decimal places to display. Default is 5.
            showPlot (bool): Whether to display performance plots. Default is False.
        """
        for func_name, data in self.results.items():
            print(f"Function: {func_name}")
            times = [entry["t"] for entry in data]
            memories = [entry["m"] for entry in data]

            # Filter outliers
            times = self._filter_bad_data(times)

            analysis = {
                "Count": len(times),
                "Total Time": sum(times),
                "Max Time": max(times),
                "Min Time": min(times),
                "Average Time": np.mean(times),
                "Median Time": np.median(times),
                "Time Standard Deviation": np.std(times),
                "Mean Memory (KB)": np.mean(memories)
            }
            print("\nPerformance Results:")
            for key, value in analysis.items():
                if "Memory" in key:
                    print(f"  {key}: {value:.{precision}f} KB")  # Format memory values
                else:
                    print(f"  {key}: {value:.{precision}f}")  # Format time values
            print()
            self._to_json()
            if showPlot:
                self.plots()

    def plots(self, block=True, showMean=False, showMedian=False):
        """
        Plot performance data from the latest 7 JSON files in the "performances" directory.

        Args:
            block (bool): Whether to block the execution until the plot window is closed. Default is True.
            showMean (bool): Whether to display the mean value as a horizontal line. Default is False.
            showMedian (bool): Whether to display the median value as a horizontal line. Default is False.
        """
        # Ensure the "performances" directory exists
        performances_dir = "performances"
        if not os.path.exists(performances_dir):
            print("No performances directory found.")
            return

        # Get all JSON files in the directory
        files = [f for f in os.listdir(performances_dir) if f.endswith(".json")]
        if not files:
            print("No performance files found in the directory.")
            return

        # Sort files by modification time and get the latest 7
        files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(performances_dir, f)), reverse=True)[:7]

        # Read and parse performance data
        colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
        plt.figure(figsize=(15, 12))

        for i, file in enumerate(files):
            filepath = os.path.join(performances_dir, file)
            with open(filepath, "r") as f:
                data = json.load(f)

            # Extract execution time data
            values = [entry["t"] for entry in data]
            func_name = os.path.splitext(file)[0]  # Use the filename as the function name

            # Filter outliers
            values = self._filter_bad_data(values)

            # Plot the performance data
            plt.plot(values, label=func_name, color=colors[i % len(colors)])
            
            # Plot mean and median lines if enabled
            if showMean:
                mean_value = np.mean(values)
                plt.axhline(mean_value, color=colors[i % len(colors)], linestyle='--', label=f"{func_name} Mean: {mean_value:.2f}")
            if showMedian:
                median_value = np.median(values)
                plt.axhline(median_value, color=colors[i % len(colors)], linestyle=':', label=f"{func_name} Median: {median_value:.2f}")

        # Set chart title and labels
        plt.xlabel("Run Index")
        plt.ylabel("Execution Time (s)")
        plt.title("Execution Time Over Runs (Latest 7 Files)")
        plt.legend()
        plt.show(block=block)
