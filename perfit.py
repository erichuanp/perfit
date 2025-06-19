# -*- coding: utf-8 -*-
"""
Perfit - A lightweight Python timer.

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
Created: 2025-02-07
"""


import time

class Perfit:
    def __getattr__(self, func_name):
        def wrapper(*args, **kwargs):
            # 支持全局作用域查找
            func = globals()[func_name]
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            print(f"[Perfit] {func_name} 耗时：{end - start:.3f} 秒")
            return result
        return wrapper

    def __call__(self, func, *args, **kwargs):
        # 直接传入可调用对象
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        # 尝试获取函数名，如果不可用则用str表示
        func_name = getattr(func, '__name__', str(func))
        print(f"[Perfit] {func_name} 耗时：{end - start:.3f} 秒")
        return result

# 实例化
perfit = Perfit()

# 用法一：像属性一样
# result = perfit.transcriber("/home/sniper/whisper_test/1.wav")

# 用法二：直接传对象
# result = perfit(transcriber, "/home/sniper/whisper_test/1.wav")
