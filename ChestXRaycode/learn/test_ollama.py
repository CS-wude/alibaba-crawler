#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama连接测试脚本
诊断和修复Ollama连接问题
"""

import sys
import json
import traceback
import subprocess

def test_ollama_import():
    """测试ollama包导入"""
    print("🔍 测试ollama包导入...")
    try:
        import ollama
        print("✅ ollama包导入成功")
        print(f"   版本信息: {getattr(ollama, '__version__', '未知')}")
        return True, ollama
    except ImportError as e:
        print(f"❌ ollama包导入失败: {e}")
        print("💡 解决方案: pip install ollama")
        return False, None

def test_ollama_service():
    """测试Ollama服务连接"""
    print("\n🔍 测试Ollama服务连接...")
    try:
        import ollama
        # 尝试列出模型
        models_response = ollama.list()
        print("✅ Ollama服务连接成功")
        
        if 'models' in models_response:
            models_list = models_response['models']
            available_models = []
            
            for model in models_list:
                # 兼容不同版本的Ollama响应格式
                if hasattr(model, 'model'):
                    available_models.append(model.model)
                elif hasattr(model, 'name'):
                    available_models.append(model.name)
                elif isinstance(model, dict):
                    if 'model' in model:
                        available_models.append(model['model'])
                    elif 'name' in model:
                        available_models.append(model['name'])
                else:
                    # 打印模型对象结构用于调试
                    print(f"   模型对象结构: {dir(model)}")
                    available_models.append(str(model))
            
            if available_models:
                print(f"   可用模型: {available_models}")
                return True, available_models
            else:
                print("   ⚠️  没有找到已安装的模型")
                print(f"   响应中的模型数量: {len(models_list)}")
                if models_list:
                    print(f"   第一个模型对象: {models_list[0]}")
                return True, []  # 服务正常，但没有模型
        else:
            print("⚠️  响应格式异常")
            print(f"   原始响应: {models_response}")
            return False, []
            
    except Exception as e:
        print(f"❌ Ollama服务连接失败: {e}")
        print("   错误详情:")
        traceback.print_exc()
        return False, []

def test_model_generation():
    """测试模型生成功能"""
    print("\n🔍 测试模型生成功能...")
    try:
        import ollama
        
        # 获取可用模型 - 使用之前修复的逻辑
        models_response = ollama.list()
        if not models_response.get('models'):
            print("❌ 没有可用的模型")
            return False
        
        # 获取模型名称（使用兼容的方式）
        models_list = models_response['models']
        model_name = None
        
        for model in models_list:
            if hasattr(model, 'model'):
                model_name = model.model
                break
            elif hasattr(model, 'name'):
                model_name = model.name
                break
            elif isinstance(model, dict):
                if 'model' in model:
                    model_name = model['model']
                    break
                elif 'name' in model:
                    model_name = model['name']
                    break
        
        if not model_name:
            print("❌ 无法确定模型名称")
            print(f"   第一个模型对象: {models_list[0]}")
            return False
        
        print(f"   使用模型: {model_name}")
        
        test_prompt = "Hello, this is a simple test. Please respond briefly."
        print(f"   测试提示: {test_prompt}")
        
        try:
            response = ollama.generate(
                model=model_name,
                prompt=test_prompt
            )
            
            if 'response' in response:
                print("✅ 模型生成测试成功")
                print(f"   响应: {response['response'][:100]}...")
                return True
            else:
                print("❌ 生成响应格式异常")
                print(f"   原始响应: {response}")
                return False
        except Exception as gen_error:
            print(f"❌ 生成请求失败: {gen_error}")
            return False
            
    except Exception as e:
        print(f"❌ 模型生成测试失败: {e}")
        traceback.print_exc()
        return False

def check_ollama_process():
    """检查Ollama进程状态"""
    print("\n🔍 检查Ollama进程状态...")
    try:
        if sys.platform.startswith('win'):
            # Windows
            result = subprocess.run(['tasklist', '/fi', 'imagename eq ollama.exe'], 
                                  capture_output=True, text=True)
            if 'ollama.exe' in result.stdout:
                print("✅ Ollama进程正在运行")
                return True
            else:
                print("❌ Ollama进程未运行")
                return False
        else:
            # Linux/Mac
            result = subprocess.run(['pgrep', 'ollama'], capture_output=True)
            if result.returncode == 0:
                print("✅ Ollama进程正在运行")
                return True
            else:
                print("❌ Ollama进程未运行")
                return False
    except Exception as e:
        print(f"⚠️  无法检查进程状态: {e}")
        return None

def auto_install_recommended_model():
    """自动安装推荐的医学模型"""
    print("\n🔄 自动安装推荐模型...")
    
    # 推荐的模型列表（按优先级排序）
    recommended_models = [
        ('llama3.1:8b', '高质量通用模型，适合医学分析'),
        ('llama2:7b', '稳定的中型模型'),
        ('llama2:13b', '更大的模型，更好的性能（需要更多内存）'),
    ]
    
    try:
        import ollama
        
        for model_name, description in recommended_models:
            try:
                print(f"   正在下载 {model_name} ({description})...")
                print("   这可能需要几分钟时间，请耐心等待...")
                
                # 开始下载模型
                ollama.pull(model_name)
                print(f"   ✅ {model_name} 下载成功！")
                return True
                
            except Exception as e:
                print(f"   ❌ {model_name} 下载失败: {e}")
                continue
        
        print("   ❌ 所有推荐模型下载都失败了")
        return False
        
    except Exception as e:
        print(f"   ❌ 模型安装过程出错: {e}")
        return False

def suggest_solutions(issues):
    """根据发现的问题提供解决方案"""
    print("\n" + "="*60)
    print("🔧 解决方案建议")
    print("="*60)
    
    if not issues:
        print("✅ Ollama配置正常，可以正常使用医学报告功能！")
        return
    
    print("发现的问题:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
    
    print("\n💡 解决步骤:")
    
    if "ollama包" in str(issues):
        print("\n1. 安装ollama包:")
        print("   pip install ollama")
    
    if "进程未运行" in str(issues):
        print("\n2. 启动Ollama服务:")
        print("   ollama serve")
        print("   (在另一个终端窗口中运行，保持运行状态)")
    
    if "没有可用的模型" in str(issues) or "没有找到已安装的模型" in str(issues):
        print("\n3. 下载推荐的医学模型:")
        print("   手动下载:")
        print("   ollama pull llama3.1:8b")
        print("   # 或者")
        print("   ollama pull llama2:7b")
        
        # 提供自动安装选项
        choice = input("\n是否现在自动下载推荐模型？这可能需要几分钟 (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            success = auto_install_recommended_model()
            if success:
                print("\n🎉 模型安装成功！现在可以重启Web应用享受完整的医学报告功能了。")
            else:
                print("\n❌ 自动安装失败，请尝试手动安装。")
    
    if "连接失败" in str(issues):
        print("\n4. 检查网络和防火墙:")
        print("   - 确保端口11434未被占用")
        print("   - 检查防火墙设置")
        print("   - 尝试重启Ollama服务")
        print("   - 检查Ollama版本兼容性")

def main():
    """主测试函数"""
    print("🦙 Ollama连接诊断工具")
    print("="*60)
    
    issues = []
    
    # 1. 测试包导入
    import_ok, ollama_module = test_ollama_import()
    if not import_ok:
        issues.append("ollama包导入失败")
        suggest_solutions(issues)
        return
    
    # 2. 检查进程状态
    process_running = check_ollama_process()
    if process_running is False:
        issues.append("Ollama进程未运行")
    
    # 3. 测试服务连接
    service_ok, models = test_ollama_service()
    if not service_ok:
        issues.append("Ollama服务连接失败")
    elif not models:
        issues.append("没有找到已安装的模型")
    
    # 4. 测试生成功能（仅在有模型时测试）
    if service_ok and models:
        generation_ok = test_model_generation()
        if not generation_ok:
            issues.append("模型生成功能异常")
    
    # 提供解决方案
    suggest_solutions(issues)
    
    print("\n" + "="*60)
    if not issues:
        print("🎉 诊断完成: Ollama配置正常!")
        print("现在可以重启Web应用以使用完整的医学报告功能。")
    else:
        print(f"🔧 诊断完成: 发现 {len(issues)} 个问题需要修复")
    print("="*60)

if __name__ == "__main__":
    main() 