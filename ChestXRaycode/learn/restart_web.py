#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用重启脚本
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def kill_existing_processes():
    """终止现有的Web应用进程"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                          capture_output=True, check=False)
        else:  # Linux/Mac
            subprocess.run(['pkill', '-f', 'web_app.py'], 
                          capture_output=True, check=False)
        print("🔄 已终止现有进程")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️  终止进程时出错: {e}")

def check_environment():
    """检查环境状态"""
    print("🔍 检查环境...")
    
    # 检查模型文件
    model_path = 'checkpoints/best_model.pth'
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024*1024)
        print(f"✅ 模型文件: {model_path} ({size_mb:.1f}MB)")
    else:
        print(f"❌ 模型文件不存在: {model_path}")
        return False
    
    # 检查关键文件
    key_files = ['web_app.py', 'deploy_simple.py', 'model.py', 'dataset.py']
    for file in key_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ 缺少文件: {file}")
            return False
    
    return True

def restart_web_app():
    """重启Web应用"""
    print("🚀 重启胸部X光片AI Web应用")
    print("=" * 50)
    
    # 终止现有进程
    kill_existing_processes()
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败")
        return
    
    # 启动Web应用
    print("🌟 启动Web应用...")
    try:
        # 使用当前Python解释器启动
        subprocess.run([sys.executable, 'web_app.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 用户终止应用")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    restart_web_app() 