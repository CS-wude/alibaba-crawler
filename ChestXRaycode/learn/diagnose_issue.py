#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI系统初始化诊断脚本
帮助诊断Web应用AI系统初始化失败的原因
"""

import os
import sys
import traceback
from pathlib import Path

def check_basic_environment():
    """检查基础环境"""
    print("🔍 检查基础环境...")
    
    issues = []
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"   Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        issues.append("Python版本过低，建议使用Python 3.7+")
    
    # 检查当前工作目录
    current_dir = os.getcwd()
    print(f"   当前目录: {current_dir}")
    
    # 检查项目结构
    expected_files = [
        'web_app.py',
        'deploy_simple.py', 
        'multimodal_service.py',
        'model.py',
        'dataset.py'
    ]
    
    for file in expected_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            issues.append(f"缺少关键文件: {file}")
            print(f"   ❌ {file}")
    
    return issues

def check_python_packages():
    """检查Python包"""
    print("\n📦 检查Python包...")
    
    required_packages = {
        'torch': 'PyTorch深度学习框架',
        'torchvision': 'PyTorch视觉库',
        'PIL': 'Python图像库',
        'numpy': '数值计算库',
        'flask': 'Web框架',
        'requests': 'HTTP库'
    }
    
    issues = []
    
    for package, description in required_packages.items():
        try:
            if package == 'PIL':
                import PIL
                print(f"   ✅ {package} (Pillow) - {description}")
            else:
                __import__(package)
                print(f"   ✅ {package} - {description}")
        except ImportError as e:
            issues.append(f"缺少包: {package} - {description}")
            print(f"   ❌ {package} - {e}")
    
    return issues

def check_model_files():
    """检查模型文件"""
    print("\n🤖 检查模型文件...")
    
    issues = []
    
    # 检查模型文件
    model_path = 'checkpoints/best_model.pth'
    if os.path.exists(model_path):
        file_size = os.path.getsize(model_path) / (1024*1024)  # MB
        print(f"   ✅ 模型文件: {model_path} ({file_size:.1f}MB)")
        
        # 尝试加载模型
        try:
            import torch
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
            print(f"   ✅ 模型可以正常加载")
            
            if 'model_state_dict' in checkpoint:
                print(f"   ✅ 模型包含状态字典")
            else:
                issues.append("模型文件格式不正确，缺少model_state_dict")
                
        except Exception as e:
            issues.append(f"模型加载失败: {e}")
            print(f"   ❌ 模型加载失败: {e}")
    else:
        issues.append(f"模型文件不存在: {model_path}")
        print(f"   ❌ 模型文件不存在: {model_path}")
    
    return issues

def check_ai_modules():
    """检查AI模块导入"""
    print("\n🧠 检查AI模块导入...")
    
    issues = []
    
    # 检查基础预测器
    try:
        sys.path.append('.')
        from deploy_simple import ChestXRayPredictor
        print("   ✅ deploy_simple.ChestXRayPredictor 导入成功")
    except Exception as e:
        issues.append(f"基础预测器导入失败: {e}")
        print(f"   ❌ deploy_simple 导入失败: {e}")
        traceback.print_exc()
    
    # 检查多模态服务
    try:
        from multimodal_service import MedicalMultimodalAI
        print("   ✅ multimodal_service.MedicalMultimodalAI 导入成功")
    except Exception as e:
        issues.append(f"多模态服务导入失败: {e}")
        print(f"   ❌ multimodal_service 导入失败: {e}")
        # 不打印traceback，因为这可能是Ollama不可用导致的
    
    # 检查核心模型模块
    try:
        from model import create_model, ChestXRayClassifier
        print("   ✅ model 模块导入成功")
    except Exception as e:
        issues.append(f"模型模块导入失败: {e}")
        print(f"   ❌ model 模块导入失败: {e}")
        traceback.print_exc()
    
    # 检查数据集模块
    try:
        from dataset import get_data_transforms, ChestXRayDataset
        print("   ✅ dataset 模块导入成功")
    except Exception as e:
        issues.append(f"数据集模块导入失败: {e}")
        print(f"   ❌ dataset 模块导入失败: {e}")
        traceback.print_exc()
    
    return issues

def test_basic_prediction():
    """测试基础预测功能"""
    print("\n🧪 测试基础预测功能...")
    
    issues = []
    
    try:
        # 检查是否可以创建预测器
        from deploy_simple import ChestXRayPredictor
        model_path = 'checkpoints/best_model.pth'
        
        if not os.path.exists(model_path):
            issues.append("无法测试：模型文件不存在")
            return issues
        
        print("   正在创建预测器...")
        predictor = ChestXRayPredictor(model_path)
        print("   ✅ 基础预测器创建成功")
        
        # 测试是否有测试图片
        test_images = [
            '../../data/ChestXRay/test/NORMAL/IM-0001-0001.jpeg',
            '../../data/ChestXRay/test/PNEUMONIA/person1_virus_11.jpeg'
        ]
        
        test_image = None
        for img_path in test_images:
            if os.path.exists(img_path):
                test_image = img_path
                break
        
        if test_image:
            print(f"   正在测试图片: {test_image}")
            result = predictor.predict_single_image(test_image)
            
            if 'error' in result:
                issues.append(f"预测测试失败: {result['error']}")
                print(f"   ❌ 预测失败: {result['error']}")
            else:
                print(f"   ✅ 预测成功: {result['predicted_class']} (置信度: {result['confidence']:.3f})")
        else:
            print("   ⚠️  没有找到测试图片，跳过预测测试")
            
    except Exception as e:
        issues.append(f"基础预测测试失败: {e}")
        print(f"   ❌ 测试失败: {e}")
        traceback.print_exc()
    
    return issues

def check_ollama_status():
    """检查Ollama状态"""
    print("\n🦙 检查Ollama状态...")
    
    issues = []
    
    # 检查ollama包
    try:
        import ollama
        print("   ✅ ollama 包已安装")
        
        # 检查服务连接
        try:
            models = ollama.list()
            available_models = [model['name'] for model in models['models']]
            print(f"   ✅ Ollama服务运行中，可用模型: {available_models}")
        except Exception as e:
            issues.append("Ollama服务未运行或不可访问")
            print(f"   ❌ Ollama服务不可用: {e}")
            
    except ImportError:
        issues.append("ollama包未安装")
        print("   ❌ ollama 包未安装")
    
    return issues

def generate_fix_suggestions(all_issues):
    """生成修复建议"""
    print("\n" + "="*60)
    print("🔧 修复建议")
    print("="*60)
    
    if not all_issues:
        print("✅ 没有发现问题！AI系统应该可以正常初始化。")
        return
    
    print(f"发现 {len(all_issues)} 个问题：")
    
    for i, issue in enumerate(all_issues, 1):
        print(f"{i}. {issue}")
    
    print("\n💡 解决方案：")
    
    # 根据问题类型给出建议
    if any("缺少包" in issue for issue in all_issues):
        print("\n📦 安装缺失的Python包：")
        print("pip install torch torchvision pillow numpy flask requests")
        
    if any("模型文件" in issue for issue in all_issues):
        print("\n🤖 模型文件问题：")
        print("1. 请确保已完成模型训练: python main.py train")
        print("2. 检查模型文件路径: checkpoints/best_model.pth")
        print("3. 如果模型文件损坏，请重新训练")
    
    if any("导入失败" in issue for issue in all_issues):
        print("\n🔄 代码模块问题：")
        print("1. 确保所有Python文件都存在且无语法错误")
        print("2. 检查当前工作目录是否正确")
        print("3. 重新下载或检查项目文件")
    
    if any("ollama" in issue.lower() for issue in all_issues):
        print("\n🦙 Ollama问题（可选功能）：")
        print("1. 安装Ollama: pip install ollama")
        print("2. 启动Ollama服务: ollama serve")
        print("3. 下载模型: ollama pull llama2")
        print("注意：Ollama是可选的，没有它也能使用基础功能")

def main():
    """主函数"""
    print("🏥 胸部X光片AI系统诊断工具")
    print("="*60)
    print("正在检查AI系统初始化失败的原因...\n")
    
    all_issues = []
    
    # 依次检查各个方面
    all_issues.extend(check_basic_environment())
    all_issues.extend(check_python_packages())
    all_issues.extend(check_model_files())
    all_issues.extend(check_ai_modules())
    all_issues.extend(test_basic_prediction())
    all_issues.extend(check_ollama_status())
    
    # 生成修复建议
    generate_fix_suggestions(all_issues)
    
    print(f"\n{'='*60}")
    if all_issues:
        print("❌ 诊断完成，发现问题需要修复")
    else:
        print("✅ 诊断完成，系统状态正常")
    print("="*60)

if __name__ == "__main__":
    main() 