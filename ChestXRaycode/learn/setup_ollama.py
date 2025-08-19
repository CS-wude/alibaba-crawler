#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama安装和设置脚本
帮助用户快速设置Ollama环境并下载所需模型
"""

import os
import sys
import subprocess
import platform
import requests
import json
import time

def check_system():
    """检查系统环境"""
    system = platform.system().lower()
    print(f"🖥️  检测到系统: {platform.system()} {platform.release()}")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"🐍 Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("⚠️  建议使用Python 3.7或更高版本")
    
    return system

def check_ollama_installed():
    """检查Ollama是否已安装"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Ollama已安装: {version}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Ollama未安装")
    return False

def install_ollama():
    """安装Ollama"""
    system = platform.system().lower()
    
    print("📥 正在安装Ollama...")
    
    if system == "linux" or system == "darwin":  # Linux或macOS
        try:
            # 使用官方安装脚本
            install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
            print(f"执行命令: {install_cmd}")
            
            result = subprocess.run(install_cmd, shell=True, check=True)
            if result.returncode == 0:
                print("✅ Ollama安装成功")
                return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 安装失败: {e}")
            
    elif system == "windows":
        print("🪟 Windows系统安装说明:")
        print("1. 访问 https://ollama.ai/download")
        print("2. 下载Windows安装包")
        print("3. 运行安装程序")
        print("4. 重启终端后再运行此脚本")
        
    else:
        print(f"❌ 不支持的系统: {system}")
    
    return False

def check_ollama_service():
    """检查Ollama服务是否运行"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama服务正在运行")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print("❌ Ollama服务未运行")
    return False

def start_ollama_service():
    """启动Ollama服务"""
    print("🚀 正在启动Ollama服务...")
    
    try:
        # 在后台启动Ollama服务
        if platform.system().lower() == "windows":
            subprocess.Popen(['ollama', 'serve'], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        for i in range(30):  # 最多等待30秒
            time.sleep(1)
            if check_ollama_service():
                return True
            print(f"   等待中... ({i+1}/30)")
        
        print("❌ 服务启动超时")
        return False
        
    except FileNotFoundError:
        print("❌ 找不到ollama命令，请确保已正确安装")
        return False

def list_available_models():
    """列出可用的模型"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print(f"📚 已安装的模型 ({len(models)}个):")
                for model in models:
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0)
                    size_gb = size / (1024**3) if size > 0 else 0
                    print(f"   • {name} ({size_gb:.1f}GB)")
            else:
                print("📚 未找到已安装的模型")
            
            return [model.get('name', '') for model in models]
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
    
    return []

def download_model(model_name):
    """下载指定模型"""
    print(f"📥 正在下载模型: {model_name}")
    print("⏳ 这可能需要几分钟到几十分钟，请耐心等待...")
    
    try:
        # 使用ollama pull命令下载模型
        process = subprocess.Popen(['ollama', 'pull', model_name], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT, 
                                 text=True, universal_newlines=True)
        
        # 实时显示下载进度
        for line in process.stdout:
            line = line.strip()
            if line:
                print(f"   {line}")
        
        process.wait()
        
        if process.returncode == 0:
            print(f"✅ 模型 {model_name} 下载完成")
            return True
        else:
            print(f"❌ 模型 {model_name} 下载失败")
            return False
            
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

def test_model(model_name):
    """测试模型是否正常工作"""
    print(f"🧪 测试模型: {model_name}")
    
    test_prompt = "Hello, how are you?"
    
    try:
        data = {
            "model": model_name,
            "prompt": test_prompt,
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", 
                               json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '')
            if answer:
                print(f"✅ 模型响应正常")
                print(f"   测试问题: {test_prompt}")
                print(f"   模型回答: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                return True
        
        print(f"❌ 模型测试失败: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        return False

def install_python_dependencies():
    """安装Python依赖"""
    dependencies = ['ollama', 'requests']
    
    print("📦 安装Python依赖包...")
    
    for package in dependencies:
        try:
            print(f"   安装 {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"   ✅ {package} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ {package} 安装失败: {e}")
            return False
    
    return True

def setup_medical_models():
    """设置医学相关的推荐模型"""
    recommended_models = {
        'llama2': {
            'name': 'llama2',
            'description': '通用大模型，适合医学报告生成',
            'size': '3.8GB',
            'recommended': True
        },
        'mistral': {
            'name': 'mistral',
            'description': '高效模型，响应速度快',
            'size': '4.1GB', 
            'recommended': True
        },
        'codellama': {
            'name': 'codellama',
            'description': '代码生成专用，适合技术文档',
            'size': '3.8GB',
            'recommended': False
        },
        'llama2:13b': {
            'name': 'llama2:13b',
            'description': '更大的模型，质量更高但需要更多资源',
            'size': '7.3GB',
            'recommended': False
        }
    }
    
    print("\n🏥 医学AI推荐模型:")
    for key, model in recommended_models.items():
        status = "🌟 推荐" if model['recommended'] else "🔧 可选"
        print(f"   {status} {model['name']} - {model['description']} ({model['size']})")
    
    installed_models = list_available_models()
    
    # 检查是否有推荐模型已安装
    has_recommended = any(model['name'] in installed_models for model in recommended_models.values() if model['recommended'])
    
    if not has_recommended:
        print("\n📥 建议安装至少一个推荐模型:")
        
        choice = input("是否安装 llama2 模型? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            if download_model('llama2'):
                test_model('llama2')
        
        choice = input("是否安装 mistral 模型? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            if download_model('mistral'):
                test_model('mistral')
    else:
        print("✅ 已有推荐模型安装")

def create_usage_examples():
    """创建使用示例文件"""
    examples_content = """
# Ollama + 胸部X光片分类 使用示例

## 基本使用

### 1. 确保Ollama服务运行
```bash
ollama serve
```

### 2. 基本的多模态分析
```bash
python multimodal_service.py --image ../../data/ChestXRay/test/PNEUMONIA/person1_virus_11.jpeg
```

### 3. 使用不同的LLM模型
```bash
python multimodal_service.py --image path/to/xray.jpg --llm mistral
python multimodal_service.py --image path/to/xray.jpg --llm llama2
```

### 4. 生成简化报告
```bash
python multimodal_service.py --image path/to/xray.jpg --simple
```

### 5. 只显示总结
```bash
python multimodal_service.py --image path/to/xray.jpg --summary-only
```

### 6. 保存完整报告
```bash
python multimodal_service.py --image path/to/xray.jpg --output reports/analysis.json
```

## API使用示例

### Python API调用
```python
from multimodal_service import MedicalMultimodalAI

# 创建AI系统
ai = MedicalMultimodalAI('checkpoints/best_model.pth', 'llama2')

# 分析图像
result = ai.analyze_xray_with_report('path/to/xray.jpg')

# 生成总结
summary = ai.generate_summary_report(result)
print(summary)
```

## 常见问题

### Q: Ollama服务无法启动？
A: 
1. 确保已正确安装Ollama
2. 检查端口11434是否被占用
3. 重启终端后重试

### Q: 模型下载很慢？
A: 
1. 检查网络连接
2. 考虑使用镜像源
3. 可以尝试较小的模型如mistral

### Q: 内存不足？
A: 
1. 关闭其他程序释放内存
2. 使用较小的模型
3. 考虑增加系统内存

### Q: 生成的报告质量不佳？
A: 
1. 尝试使用更大的模型如llama2:13b
2. 调整提示语模板
3. 确保图像分类结果准确
"""
    
    with open('ollama_usage_examples.md', 'w', encoding='utf-8') as f:
        f.write(examples_content)
    
    print(f"📖 使用示例已保存到: ollama_usage_examples.md")

def main():
    """主函数"""
    print("🚀 Ollama + 胸部X光片分类 环境设置")
    print("=" * 50)
    
    # 1. 检查系统
    system = check_system()
    
    # 2. 检查并安装Ollama
    if not check_ollama_installed():
        print("\n📥 需要安装Ollama")
        choice = input("是否现在安装? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            if not install_ollama():
                print("❌ 安装失败，请手动安装Ollama")
                return
        else:
            print("⏭️  跳过安装，请手动安装后重新运行")
            return
    
    # 3. 安装Python依赖
    print("\n📦 检查Python依赖...")
    if not install_python_dependencies():
        print("❌ 依赖安装失败")
        return
    
    # 4. 启动Ollama服务
    print("\n🚀 检查Ollama服务...")
    if not check_ollama_service():
        choice = input("Ollama服务未运行，是否启动? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            if not start_ollama_service():
                print("❌ 服务启动失败")
                print("💡 请手动运行: ollama serve")
                return
        else:
            print("⏭️  跳过服务启动")
            print("💡 使用前请手动运行: ollama serve")
    
    # 5. 设置医学模型
    print("\n🏥 设置医学模型...")
    setup_medical_models()
    
    # 6. 创建使用示例
    print("\n📖 创建使用示例...")
    create_usage_examples()
    
    # 7. 完成设置
    print("\n" + "=" * 50)
    print("✅ 环境设置完成！")
    print("\n🎯 下一步操作:")
    print("1. 确保Ollama服务运行: ollama serve")
    print("2. 测试多模态分析:")
    print("   python multimodal_service.py --image path/to/xray.jpg")
    print("3. 查看详细使用方法: ollama_usage_examples.md")
    
    # 最终测试
    print("\n🧪 运行快速测试...")
    if check_ollama_service():
        models = list_available_models()
        if models:
            test_model_name = models[0].split(':')[0]
            print(f"测试模型: {test_model_name}")
            test_model(test_model_name)
    
    print("\n🎉 设置完成！开始使用你的多模态医学AI系统吧！")

if __name__ == "__main__":
    main() 