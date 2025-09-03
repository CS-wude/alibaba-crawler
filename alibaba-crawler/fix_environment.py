#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys

def run_command(cmd):
    """运行命令并打印输出"""
    print(f"执行: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"输出: {result.stdout}")
        if result.stderr:
            print(f"错误: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"命令执行失败: {e}")
        return False

def fix_environment():
    """修复Python环境"""
    print("开始修复Python环境...")
    
    # 卸载有问题的包
    commands = [
        "pip uninstall urllib3 requests selenium -y",
        "pip install requests==2.28.2",
        "pip install urllib3==1.26.18", 
        "pip install selenium==4.15.0",
        "pip install six",
        "pip install tqdm",
        "pip install xlsxwriter"
    ]
    
    for cmd in commands:
        success = run_command(cmd)
        if not success:
            print(f"命令失败: {cmd}")
            return False
    
    print("环境修复完成！")
    return True

if __name__ == "__main__":
    fix_environment()
