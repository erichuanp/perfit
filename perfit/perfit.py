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
            func = globals()[func_name]
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            print(f"[Perfit] {func_name} Time: {end - start:.3f}s")
            return result
        return wrapper

    def __call__(self, func, *args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        func_name = getattr(func, '__name__', str(func))
        print(f"[Perfit] {func_name} Time: {end - start:.3f}s")
        return result

perfit = Perfit()

# result = perfit.print("Test")
# result = perfit(pop, 5)
# perfit(pop, 5)
