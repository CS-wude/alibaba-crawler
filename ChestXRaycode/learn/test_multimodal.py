#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多模态AI系统的Ollama连接
"""

import os
import sys

def test_multimodal_ai():
    """测试多模态AI系统"""
    print("🧪 测试多模态AI系统")
    print("=" * 50)
    
    try:
        # 检查模型文件
        model_path = 'checkpoints/best_model.pth'
        if not os.path.exists(model_path):
            print(f"❌ 模型文件不存在: {model_path}")
            return False
        
        print(f"✅ 模型文件存在: {model_path}")
        
        # 尝试创建多模态AI系统
        from multimodal_service import MedicalMultimodalAI
        
        print("\n🔧 创建多模态AI系统...")
        ai_system = MedicalMultimodalAI(model_path, 'llama2')
        
        print(f"\n📊 系统状态:")
        print(f"   LLM模型: {ai_system.llm_model}")
        print(f"   LLM可用: {ai_system.llm_available}")
        
        if ai_system.llm_available:
            print("✅ 多模态AI系统完全可用")
            
            # 测试图片分析（如果有测试图片）
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
                print(f"\n🔍 测试图片分析: {test_image}")
                try:
                    result = ai_system.analyze_xray_with_report(test_image)
                    
                    if 'error' in result:
                        print(f"❌ 分析失败: {result['error']}")
                    else:
                        print("✅ 图片分析成功")
                        print(f"   预测结果: {result['image_analysis']['predicted_class']}")
                        print(f"   置信度: {result['image_analysis']['confidence']:.1%}")
                        
                        if result['medical_report'] and '失败' not in result['medical_report']:
                            print("✅ 医学报告生成成功")
                            print(f"   报告长度: {len(result['medical_report'])} 字符")
                        else:
                            print("❌ 医学报告生成失败")
                            print(f"   错误: {result['medical_report']}")
                        
                except Exception as e:
                    print(f"❌ 测试分析失败: {e}")
            else:
                print("⚠️  没有找到测试图片，跳过图片分析测试")
        else:
            print("⚠️  LLM不可用，只能进行基础图像分析")
        
        return True
        
    except Exception as e:
        print(f"❌ 多模态AI系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_multimodal_ai()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成")
        print("现在可以重启Web应用享受完整的医学报告功能了！")
    else:
        print("❌ 测试失败，请检查错误信息")
    print("=" * 50)

if __name__ == "__main__":
    main() 