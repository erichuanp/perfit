import time
import tracemalloc
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from functools import wraps
from datetime import datetime


class Perfit:
    def __init__(self, badDataScaler=1000):
        """
        初始化 Perfit 类。
        :param precision: 打印小数点后几位，默认为 5 位。
        :param badDataScaler: 异常值过滤倍数，默认为 1000 倍中位数。
        """
        self.results = {}  # 存储所有函数的性能数据
        self.badDataScaler = badDataScaler  # 全局异常值过滤倍数

    def __call__(self, func):
        """
        装饰器，用于包装函数，记录性能数据。
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 开始计时和内存跟踪
            tracemalloc.start()
            start_time = time.perf_counter()

            # 执行函数
            result = func(*args, **kwargs)

            # 停止计时和内存跟踪
            end_time = time.perf_counter()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # 记录性能数据
            if func.__name__ not in self.results:
                self.results[func.__name__] = []
            self.results[func.__name__].append({
                "t": end_time - start_time,
                "m": peak / 1024  # 转为 KB
            })

            return result
        return wrapper

    def _filter_bad_data(self, values):
        """
        根据全局 badDataScaler 过滤异常值。
        :param values: 性能数据列表。
        :return: 过滤后的性能数据列表。
        """
        median_value = np.median(values)  # 计算中位数
        return [v for v in values if v <= median_value * self.badDataScaler]

    def _to_json(self):
        """
        保存所有函数的测试结果为 JSON 文件。
        """
        # 确保 performances 文件夹存在
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
        打印所有函数的统计信息，包括平均内存使用。
        """
        for func_name, data in self.results.items():
            print(f"Function: {func_name}")
            times = [entry["t"] for entry in data]
            memories = [entry["m"] for entry in data]

            # 过滤异常值
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
                    print(f"  {key}: {value:.{precision}f} KB")  # 格式化内存为用户定义的小数位数
                else:
                    print(f"  {key}: {value:.{precision}f}")  # 格式化时间为用户定义的小数位数
            print()
            self._to_json()
            if showPlot:
                self.plots()

    def plots(self, block=True, showMean=False, showMedian=False):
        """
        绘制 `performances` 文件夹中最新 7 个文件的性能变化图。
        """
        # 确保 performances 文件夹存在
        performances_dir = "performances"
        if not os.path.exists(performances_dir):
            print("No performances directory found.")
            return

        # 获取文件夹中的所有 JSON 文件
        files = [f for f in os.listdir(performances_dir) if f.endswith(".json")]
        if not files:
            print("No performance files found in the directory.")
            return

        # 按修改时间排序，获取最新的 7 个文件
        files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(performances_dir, f)), reverse=True)[:7]

        # 读取文件内容并解析性能数据
        colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
        plt.figure(figsize=(15, 12))

        for i, file in enumerate(files):
            filepath = os.path.join(performances_dir, file)
            with open(filepath, "r") as f:
                data = json.load(f)

            # 提取执行时间数据
            values = [entry["t"] for entry in data]
            func_name = os.path.splitext(file)[0]  # 使用文件名作为函数名称

            # 过滤异常值
            values = self._filter_bad_data(values)

            # 绘制曲线
            plt.plot(values, label=func_name, color=colors[i % len(colors)])
            
            # 绘制平均值和中位值的横线
            if showMean:
                mean_value = np.mean(values)
                plt.axhline(mean_value, color=colors[i % len(colors)], linestyle='--', label=f"{func_name} Mean: {mean_value:.{self.precision}f}")
            if showMedian:
                median_value = np.median(values)
                plt.axhline(median_value, color=colors[i % len(colors)], linestyle=':', label=f"{func_name} Median: {median_value:.{self.precision}f}")

        # 设置图表标题和标签
        plt.xlabel("Run Index")
        plt.ylabel("Execution Time (s)")
        plt.title("Execution Time Over Runs (Latest 7 Files)")
        plt.legend()
        plt.show(block=block)
