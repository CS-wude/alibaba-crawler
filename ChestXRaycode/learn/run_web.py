#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
胸部X光片分析Web应用启动脚本
简化启动过程并提供配置选项
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def check_requirements():
    """检查必要的依赖和文件"""
    print("🔍 检查运行环境...")
    
    issues = []
    
    # 检查Python包
    required_packages = [
        'flask', 'torch', 'torchvision', 'PIL', 'numpy'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            issues.append(f"缺少Python包: {package}")
            print(f"   ❌ {package}")
    
    # 检查模型文件
    model_path = 'checkpoints/best_model.pth'
    if os.path.exists(model_path):
        print(f"   ✅ 模型文件: {model_path}")
    else:
        issues.append(f"模型文件不存在: {model_path}")
        print(f"   ❌ 模型文件: {model_path}")
    
    # 检查必要目录
    required_dirs = ['templates', 'static']
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✅ 目录: {directory}")
        else:
            print(f"   ⚠️  目录不存在，将自动创建: {directory}")
    
    # 检查Ollama（可选）
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"   ✅ Ollama已安装")
        else:
            print(f"   ⚠️  Ollama未正确安装")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print(f"   ⚠️  Ollama未安装（多模态功能不可用）")
    
    if issues:
        print(f"\n❌ 发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    
    print("✅ 环境检查通过！")
    return True

def install_missing_packages():
    """安装缺失的包"""
    print("📦 正在安装缺失的Python包...")
    
    required_packages = [
        'flask', 'werkzeug', 'jinja2', 'pillow', 'requests'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"   安装 {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package])

def create_directories():
    """创建必要的目录"""
    dirs = [
        'templates', 'static', 'static/uploads', 'static/reports', 
        'static/css', 'static/js', 'static/images', 'checkpoints'
    ]
    
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)

def setup_environment():
    """设置环境"""
    print("🔧 设置运行环境...")
    
    # 创建目录
    create_directories()
    
    # 设置环境变量
    os.environ['FLASK_APP'] = 'web_app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    print("✅ 环境设置完成")

def start_web_app(host='0.0.0.0', port=5000, debug=True):
    """启动Web应用"""
    print("🚀 启动Web应用...")
    print(f"   主机: {host}")
    print(f"   端口: {port}")
    print(f"   调试模式: {debug}")
    print(f"   访问地址: http://localhost:{port}")
    print("\n" + "="*50)
    print("Web应用已启动！")
    print("="*50)
    
    try:
        from web_app import app
        app.run(host=host, port=port, debug=debug)
    except ImportError as e:
        print(f"❌ 无法导入Web应用: {e}")
        return False
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='胸部X光片分析Web应用启动器')
    parser.add_argument('--host', type=str, default='0.0.0.0', 
                       help='服务器主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, 
                       help='服务器端口 (默认: 5000)')
    parser.add_argument('--no-debug', action='store_true', 
                       help='禁用调试模式')
    parser.add_argument('--skip-check', action='store_true', 
                       help='跳过环境检查')
    parser.add_argument('--install-deps', action='store_true', 
                       help='自动安装缺失的依赖')
    
    args = parser.parse_args()
    
    print("🏥 胸部X光片AI分析系统 - Web应用启动器")
    print("=" * 60)
    
    # 环境检查
    if not args.skip_check:
        if not check_requirements():
            if args.install_deps:
                install_missing_packages()
            else:
                print("\n💡 解决建议:")
                print("   1. 安装缺失的包: pip install flask torch torchvision pillow")
                print("   2. 确保模型文件存在: checkpoints/best_model.pth")
                print("   3. 或使用 --install-deps 自动安装依赖")
                return
    
    # 设置环境
    setup_environment()
    
    # 启动应用
    if not start_web_app(
        host=args.host, 
        port=args.port, 
        debug=not args.no_debug
    ):
        print("❌ 启动失败")
        return
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Web应用已停止")
    except Exception as e:
        print(f"\n❌ 运行时错误: {e}")
        import traceback
        traceback.print_exc() 