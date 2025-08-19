#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模态医学AI服务
结合图像分类和大语言模型，提供智能医学报告生成
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  未安装ollama包，请运行: pip install ollama")

from deploy_simple import ChestXRayPredictor

class MedicalMultimodalAI:
    """多模态医学AI系统"""
    
    def __init__(self, model_path, llm_model="llama2"):
        """
        初始化多模态AI系统
        
        Args:
            model_path: 图像分类模型路径
            llm_model: Ollama LLM模型名称
        """
        # 初始化图像分类器
        print("🔧 正在初始化图像分类器...")
        self.predictor = ChestXRayPredictor(model_path)
        
        # 设置LLM模型
        self.llm_model = llm_model
        self.llm_available = False  # 默认为False，在成功连接后设置为True
        
        # 检查Ollama连接
        if OLLAMA_AVAILABLE:
            try:
                models_response = ollama.list()
                
                # 兼容不同版本的Ollama响应格式
                available_models = []
                if 'models' in models_response:
                    models_list = models_response['models']
                    
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
                            # 作为字符串处理
                            available_models.append(str(model))
                
                print(f"✅ Ollama连接成功，可用模型: {available_models}")
                
                # 检查指定的模型是否可用
                if available_models:
                    # 尝试匹配模型名称（支持部分匹配）
                    matching_model = None
                    for model in available_models:
                        if llm_model in model or model.split(':')[0] == llm_model:
                            matching_model = model
                            break
                    
                    if matching_model:
                        self.llm_model = matching_model
                        print(f"✅ 使用模型: {self.llm_model}")
                        self.llm_available = True
                        
                        # 测试模型连接
                        try:
                            test_response = ollama.generate(
                                model=self.llm_model,
                                prompt="Hello"
                            )
                            print("✅ LLM模型连接测试成功")
                        except Exception as test_error:
                            print(f"⚠️  模型测试失败，但连接正常: {test_error}")
                    else:
                        print(f"⚠️  模型 {llm_model} 未找到，将尝试下载...")
                        self._download_model(llm_model)
                else:
                    print("❌ 没有找到可用的模型")
                    self.llm_available = False
                    
            except Exception as e:
                print(f"❌ Ollama连接失败: {e}")
                print("请确保Ollama服务正在运行: ollama serve")
                self.llm_available = False
        else:
            print("❌ Ollama不可用，只能进行图像分类")
            self.llm_available = False
    
    def _download_model(self, model_name):
        """下载指定的LLM模型"""
        try:
            print(f"📥 正在下载模型 {model_name}...")
            ollama.pull(model_name)
            print(f"✅ 模型 {model_name} 下载完成")
            self.llm_available = True
        except Exception as e:
            print(f"❌ 模型下载失败: {e}")
            self.llm_available = False
    
    def create_medical_prompt(self, classification_result):
        """创建医学报告生成提示"""
        if 'error' in classification_result:
            return f"图像分析失败：{classification_result['error']}"
        
        # 根据分类结果调整提示语
        if classification_result['predicted_class'] == 'PNEUMONIA':
            diagnosis_context = "AI系统检测到可能的肺炎征象"
        else:
            diagnosis_context = "AI系统未检测到明显异常"
        
        prompt = f"""
你是一名经验丰富的放射科医生。请根据AI辅助诊断系统的分析结果，生成一份专业的胸部X光片诊断报告。

AI分析结果：
- 预测类别：{classification_result['predicted_class']}
- 置信度：{classification_result['confidence']:.1%}
- {diagnosis_context}
- 各类别概率：
  * 正常 (NORMAL): {classification_result['probabilities']['NORMAL']:.1%}
  * 肺炎 (PNEUMONIA): {classification_result['probabilities']['PNEUMONIA']:.1%}

请按以下格式生成报告：

## 胸部X光片诊断报告

**检查日期**: {classification_result['prediction_time'][:10]}
**检查方式**: 胸部X光片（AI辅助分析）

**影像学描述**:
[请基于AI分析结果，用专业术语描述可能的影像学表现]

**AI分析结果**:
- 分类结果: {classification_result['predicted_class']}
- 系统置信度: {classification_result['confidence']:.1%}

**诊断意见**:
[基于AI分析结果和临床经验，给出专业的诊断意见]

**建议**:
[根据诊断结果提供具体的医学建议，包括：]
- 是否需要进一步检查
- 治疗建议
- 随访计划

**备注**:
- 本报告基于AI辅助分析系统，仅供临床参考
- 最终诊断需结合患者临床表现、实验室检查等综合判断
- 如有疑问请咨询相关专科医生

请确保报告专业、准确、符合医学标准，使用规范的医学术语。
"""
        return prompt
    
    def create_simple_prompt(self, classification_result):
        """创建简化的提示（适用于非医学专业的LLM）"""
        if 'error' in classification_result:
            return f"图像分析失败：{classification_result['error']}"
        
        prompt = f"""
请根据以下胸部X光片AI分析结果，生成一份易懂的健康报告：

分析结果：
- 检测结果：{classification_result['predicted_class']}
- AI可信度：{classification_result['confidence']:.1%}
- 正常概率：{classification_result['probabilities']['NORMAL']:.1%}
- 异常概率：{classification_result['probabilities']['PNEUMONIA']:.1%}

请生成包含以下内容的报告：
1. 简单解释这个结果意味着什么
2. 基于结果的一般性健康建议
3. 是否需要寻求医疗帮助
4. 重要的免责声明

请使用简单易懂的语言，避免过于专业的医学术语。
"""
        return prompt
    
    def analyze_xray_with_report(self, image_path, use_simple_prompt=False):
        """完整的X光片分析和报告生成"""
        print(f"🔍 正在分析X光片: {image_path}")
        
        # 1. 图像分类
        classification = self.predictor.predict_single_image(image_path)
        
        if 'error' in classification:
            return {
                'error': classification['error'],
                'image_path': image_path,
                'timestamp': datetime.now().isoformat()
            }
        
        print(f"📊 分类完成: {classification['predicted_class']} (置信度: {classification['confidence']:.1%})")
        
        # 2. 生成医学报告（如果Ollama可用）
        medical_report = None
        if OLLAMA_AVAILABLE and hasattr(self, 'llm_available') and self.llm_available:
            try:
                print("📝 正在生成医学报告...")
                
                # 选择提示类型
                if use_simple_prompt:
                    prompt = self.create_simple_prompt(classification)
                else:
                    prompt = self.create_medical_prompt(classification)
                
                response = ollama.generate(
                    model=self.llm_model,
                    prompt=prompt
                )
                medical_report = response['response']
                print("✅ 报告生成完成")
                
            except Exception as e:
                medical_report = f"报告生成失败: {e}"
                print(f"❌ 报告生成失败: {e}")
        else:
            medical_report = "LLM服务不可用，无法生成详细报告"
            print("⚠️  跳过报告生成（LLM不可用）")
        
        # 3. 生成综合评估
        assessment = self._create_comprehensive_assessment(classification)
        
        return {
            'image_analysis': classification,
            'medical_report': medical_report,
            'comprehensive_assessment': assessment,
            'system_info': {
                'image_model': 'ResNet50-ChestXRay',
                'llm_model': self.llm_model if medical_report else 'N/A',
                'analysis_time': datetime.now().isoformat(),
                'image_path': str(image_path)
            }
        }
    
    def _create_comprehensive_assessment(self, classification):
        """创建综合评估"""
        predicted_class = classification['predicted_class']
        confidence = classification['confidence']
        pneumonia_prob = classification['probabilities']['PNEUMONIA']
        
        # 风险等级评估
        if predicted_class == 'PNEUMONIA':
            if confidence >= 0.9:
                risk_level = "高风险"
                risk_description = "AI系统高度怀疑存在肺炎征象"
                urgency = "urgent"
                action = "强烈建议立即就医进行专业诊断"
            elif confidence >= 0.7:
                risk_level = "中风险"
                risk_description = "AI系统检测到可能的肺炎征象"
                urgency = "moderate"
                action = "建议尽快就医咨询专业医生"
            else:
                risk_level = "低风险"
                risk_description = "AI系统检测到轻微异常征象"
                urgency = "low"
                action = "建议医疗机构复查，结合临床症状判断"
        else:  # NORMAL
            if confidence >= 0.9:
                risk_level = "正常范围"
                risk_description = "AI系统未检测到明显异常"
                urgency = "none"
                action = "影像显示正常，如有症状请咨询医生"
            elif confidence >= 0.7:
                risk_level = "基本正常"
                risk_description = "AI系统显示基本正常"
                urgency = "low"
                action = "影像基本正常，如有不适建议观察或复查"
            else:
                risk_level = "不确定"
                risk_description = "AI系统分析结果不确定"
                urgency = "moderate"
                action = "结果不确定，建议专业医生进一步评估"
        
        # 置信度解释
        confidence_interpretation = self._interpret_confidence(confidence)
        
        # 生成具体建议
        recommendations = self._generate_detailed_recommendations(classification)
        
        # 医学警告和免责声明
        disclaimers = [
            "🚨 重要提醒：本分析结果仅供参考，不能替代专业医生诊断",
            "💊 如有任何症状或健康担忧，请及时就医",
            "🏥 最终诊断需要结合临床表现、实验室检查等综合判断",
            "👨‍⚕️ 请将此报告提供给专业医生作为参考"
        ]
        
        return {
            'risk_assessment': {
                'level': risk_level,
                'description': risk_description,
                'urgency': urgency,
                'recommended_action': action
            },
            'confidence_analysis': {
                'score': confidence,
                'interpretation': confidence_interpretation,
                'reliability': self._assess_reliability(confidence)
            },
            'probability_breakdown': {
                'normal_probability': classification['probabilities']['NORMAL'],
                'pneumonia_probability': pneumonia_prob,
                'dominant_class': predicted_class
            },
            'recommendations': recommendations,
            'disclaimers': disclaimers
        }
    
    def _interpret_confidence(self, confidence):
        """解释置信度含义"""
        if confidence >= 0.95:
            return "AI模型对此诊断非常确信，结果可靠性很高"
        elif confidence >= 0.85:
            return "AI模型对此诊断比较确信，结果可靠性较高"
        elif confidence >= 0.7:
            return "AI模型对此诊断有一定把握，建议结合临床判断"
        elif confidence >= 0.6:
            return "AI模型对此诊断把握较小，需要专业医生评估"
        else:
            return "AI模型对此诊断不够确定，强烈建议人工复查"
    
    def _assess_reliability(self, confidence):
        """评估结果可靠性"""
        if confidence >= 0.9:
            return "高可靠性"
        elif confidence >= 0.7:
            return "中等可靠性"
        elif confidence >= 0.6:
            return "较低可靠性"
        else:
            return "低可靠性"
    
    def _generate_detailed_recommendations(self, classification):
        """生成详细建议"""
        predicted_class = classification['predicted_class']
        confidence = classification['confidence']
        
        recommendations = {
            'immediate_actions': [],
            'follow_up': [],
            'lifestyle': [],
            'when_to_seek_help': []
        }
        
        if predicted_class == 'PNEUMONIA':
            if confidence >= 0.8:
                recommendations['immediate_actions'] = [
                    "立即预约呼吸科或内科医生",
                    "准备详细的症状描述（发热、咳嗽、呼吸困难等）",
                    "考虑进行血常规检查"
                ]
                recommendations['follow_up'] = [
                    "可能需要痰培养检查",
                    "必要时进行胸部CT扫描",
                    "根据医生建议进行抗生素治疗"
                ]
            else:
                recommendations['immediate_actions'] = [
                    "建议在1-2天内就医咨询",
                    "密切观察症状变化"
                ]
                recommendations['follow_up'] = [
                    "如症状加重请立即就医",
                    "考虑1周内复查胸片"
                ]
            
            recommendations['lifestyle'] = [
                "保持充足休息",
                "多饮水，保持室内空气流通",
                "避免吸烟和二手烟",
                "注意保暖，避免受凉"
            ]
            
            recommendations['when_to_seek_help'] = [
                "出现高热（>38.5°C）",
                "呼吸困难或胸痛加重",
                "咳嗽痰液增多或呈脓性",
                "精神状态明显下降"
            ]
        else:  # NORMAL
            recommendations['immediate_actions'] = [
                "如有症状仍建议咨询医生",
                "保持定期健康检查"
            ]
            
            recommendations['follow_up'] = [
                "建议每年进行胸部体检",
                "如有呼吸系统症状及时就医"
            ]
            
            recommendations['lifestyle'] = [
                "保持健康的生活方式",
                "戒烟限酒，适量运动",
                "保持室内空气质量",
                "注意防护避免呼吸道感染"
            ]
            
            if confidence < 0.8:
                recommendations['when_to_seek_help'] = [
                    "如出现持续咳嗽、胸痛等症状",
                    "如有发热、呼吸困难等异常",
                    "建议3-6个月后复查"
                ]
        
        return recommendations
    
    def generate_summary_report(self, result):
        """生成简洁的总结报告"""
        if 'error' in result:
            return f"分析失败：{result['error']}"
        
        assessment = result['comprehensive_assessment']
        analysis = result['image_analysis']
        
        summary = f"""
🏥 胸部X光片AI分析总结

📊 分析结果：{analysis['predicted_class']}
🎯 置信度：{analysis['confidence']:.1%} ({assessment['confidence_analysis']['reliability']})
⚠️  风险等级：{assessment['risk_assessment']['level']}

💡 主要建议：{assessment['risk_assessment']['recommended_action']}

🔍 详细概率分布：
   • 正常：{analysis['probabilities']['NORMAL']:.1%}
   • 肺炎征象：{analysis['probabilities']['PNEUMONIA']:.1%}

⏰ 分析时间：{result['system_info']['analysis_time'][:19]}
"""
        return summary

def main():
    """演示多模态医学AI系统"""
    import argparse
    
    parser = argparse.ArgumentParser(description='多模态医学AI诊断系统')
    parser.add_argument('--model', type=str, default='checkpoints/best_model.pth',
                       help='图像分类模型路径')
    parser.add_argument('--image', type=str, required=True,
                       help='X光片图像路径')
    parser.add_argument('--llm', type=str, default='llama2',
                       help='Ollama LLM模型名称 (llama2, mistral, codellama等)')
    parser.add_argument('--output', type=str,
                       help='报告输出文件路径')
    parser.add_argument('--simple', action='store_true',
                       help='使用简化的提示语（适合非医学专业LLM）')
    parser.add_argument('--summary-only', action='store_true',
                       help='只显示总结报告')
    
    args = parser.parse_args()
    
    # 检查文件
    if not os.path.exists(args.model):
        print(f"❌ 模型文件不存在: {args.model}")
        print("请确保已训练模型并检查路径")
        return
    
    if not os.path.exists(args.image):
        print(f"❌ 图像文件不存在: {args.image}")
        return
    
    # 创建多模态AI系统
    try:
        print("🚀 正在初始化多模态医学AI系统...")
        ai_system = MedicalMultimodalAI(args.model, args.llm)
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")
        return
    
    # 分析图像并生成报告
    print(f"\n📋 开始分析...")
    result = ai_system.analyze_xray_with_report(args.image, use_simple_prompt=args.simple)
    
    if 'error' in result:
        print(f"❌ 分析失败: {result['error']}")
        return
    
    # 显示结果
    print("\n" + "="*80)
    print("🏥 多模态医学AI诊断系统报告")
    print("="*80)
    
    if args.summary_only:
        # 只显示总结
        print(ai_system.generate_summary_report(result))
    else:
        # 显示详细结果
        analysis = result['image_analysis']
        assessment = result['comprehensive_assessment']
        
        print(f"\n📊 图像分析结果:")
        print(f"   文件: {analysis['image_path']}")
        print(f"   预测类别: {analysis['predicted_class']}")
        print(f"   置信度: {analysis['confidence']:.1%}")
        print(f"   图像尺寸: {analysis['image_size']}")
        
        print(f"\n🎯 风险评估:")
        print(f"   等级: {assessment['risk_assessment']['level']}")
        print(f"   描述: {assessment['risk_assessment']['description']}")
        print(f"   建议行动: {assessment['risk_assessment']['recommended_action']}")
        
        print(f"\n🔍 置信度分析:")
        print(f"   分数: {assessment['confidence_analysis']['score']:.1%}")
        print(f"   可靠性: {assessment['confidence_analysis']['reliability']}")
        print(f"   解释: {assessment['confidence_analysis']['interpretation']}")
        
        print(f"\n📈 概率分布:")
        for class_name, prob in analysis['probabilities'].items():
            print(f"   {class_name}: {prob:.1%}")
        
        if result['medical_report'] and "失败" not in result['medical_report']:
            print(f"\n📝 AI生成的医学报告:")
            print("-" * 60)
            print(result['medical_report'])
            print("-" * 60)
        
        print(f"\n💡 详细建议:")
        recs = assessment['recommendations']
        if recs['immediate_actions']:
            print(f"   立即行动:")
            for action in recs['immediate_actions']:
                print(f"     • {action}")
        
        if recs['follow_up']:
            print(f"   后续跟进:")
            for action in recs['follow_up']:
                print(f"     • {action}")
        
        if recs['when_to_seek_help']:
            print(f"   何时寻求医疗帮助:")
            for condition in recs['when_to_seek_help']:
                print(f"     • {condition}")
        
        print(f"\n⚠️  重要提醒:")
        for disclaimer in assessment['disclaimers']:
            print(f"   {disclaimer}")
    
    # 保存完整报告
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📄 完整报告已保存至: {args.output}")
        
        # 同时保存总结报告
        summary_path = output_path.parent / (output_path.stem + "_summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(ai_system.generate_summary_report(result))
        print(f"📄 总结报告已保存至: {summary_path}")
    
    print(f"\n✅ 分析完成！")

if __name__ == "__main__":
    main() 