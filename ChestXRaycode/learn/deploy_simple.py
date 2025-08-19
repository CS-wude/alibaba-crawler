#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的模型部署脚本
用于将训练好的胸部X光片分类模型部署为可用的预测工具
"""

import os
import sys
import torch
import torch.nn.functional as F
from PIL import Image
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

from model import create_model
from dataset import get_data_transforms

class ChestXRayPredictor:
    """胸部X光片分类预测器"""
    
    def __init__(self, model_path, device=None):
        """
        初始化预测器
        
        Args:
            model_path: 模型权重文件路径
            device: 计算设备
        """
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.class_names = ['NORMAL', 'PNEUMONIA']
        
        # 加载模型
        self.model = self._load_model()
        
        # 获取数据变换
        _, self.transform = get_data_transforms()
        
        print(f"✅ 模型已加载到设备: {self.device}")
        print(f"✅ 模型路径: {model_path}")
    
    def _load_model(self):
        """加载训练好的模型"""
        try:
            # 创建模型
            model = create_model(num_classes=2, model_name='resnet50').to(self.device)
            
            # 加载权重
            checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=False)
            model.load_state_dict(checkpoint['model_state_dict'])
            
            # 设置为评估模式
            model.eval()
            
            # 打印模型信息
            if 'best_acc' in checkpoint:
                print(f"📊 模型训练时最佳精度: {checkpoint['best_acc']:.4f}")
            
            return model
            
        except Exception as e:
            raise RuntimeError(f"加载模型失败: {e}")
    
    def predict_single_image(self, image_path, return_probabilities=True):
        """
        预测单张图片
        
        Args:
            image_path: 图片路径
            return_probabilities: 是否返回概率
            
        Returns:
            dict: 预测结果
        """
        try:
            # 加载图片
            image = Image.open(image_path).convert('RGB')
            original_size = image.size
            
            # 预处理
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # 预测
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = F.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            # 构建结果
            result = {
                'image_path': str(image_path),
                'image_size': original_size,
                'predicted_class': self.class_names[predicted.item()],
                'confidence': confidence.item(),
                'prediction_time': datetime.now().isoformat()
            }
            
            if return_probabilities:
                result['probabilities'] = {
                    self.class_names[i]: probabilities[0][i].item() 
                    for i in range(len(self.class_names))
                }
            
            return result
            
        except Exception as e:
            return {
                'error': f"预测失败: {e}",
                'image_path': str(image_path)
            }
    
    def predict_batch(self, image_paths, batch_size=8):
        """
        批量预测多张图片
        
        Args:
            image_paths: 图片路径列表
            batch_size: 批处理大小
            
        Returns:
            list: 预测结果列表
        """
        results = []
        
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i + batch_size]
            batch_tensors = []
            valid_paths = []
            
            # 加载和预处理批次图片
            for path in batch_paths:
                try:
                    image = Image.open(path).convert('RGB')
                    tensor = self.transform(image)
                    batch_tensors.append(tensor)
                    valid_paths.append(path)
                except Exception as e:
                    results.append({
                        'image_path': str(path),
                        'error': f"加载图片失败: {e}"
                    })
            
            if not batch_tensors:
                continue
            
            # 批量预测
            try:
                batch_input = torch.stack(batch_tensors).to(self.device)
                
                with torch.no_grad():
                    outputs = self.model(batch_input)
                    probabilities = F.softmax(outputs, dim=1)
                    confidences, predictions = torch.max(probabilities, 1)
                
                # 处理结果
                for j, path in enumerate(valid_paths):
                    result = {
                        'image_path': str(path),
                        'predicted_class': self.class_names[predictions[j].item()],
                        'confidence': confidences[j].item(),
                        'probabilities': {
                            self.class_names[k]: probabilities[j][k].item() 
                            for k in range(len(self.class_names))
                        }
                    }
                    results.append(result)
                    
            except Exception as e:
                for path in valid_paths:
                    results.append({
                        'image_path': str(path),
                        'error': f"批量预测失败: {e}"
                    })
        
        return results
    
    def get_medical_recommendation(self, prediction_result, threshold=0.5):
        """
        根据预测结果给出医学建议
        
        Args:
            prediction_result: 预测结果字典
            threshold: 分类阈值
            
        Returns:
            dict: 医学建议
        """
        if 'error' in prediction_result:
            return {'recommendation': '无法生成建议，预测失败'}
        
        predicted_class = prediction_result['predicted_class']
        confidence = prediction_result['confidence']
        pneumonia_prob = prediction_result.get('probabilities', {}).get('PNEUMONIA', 0)
        
        # 生成建议
        if predicted_class == 'PNEUMONIA':
            if confidence >= 0.9:
                risk_level = '高风险'
                recommendation = '强烈建议立即就医，进行进一步检查和治疗'
                urgency = 'urgent'
            elif confidence >= 0.7:
                risk_level = '中风险'
                recommendation = '建议尽快就医，咨询专业医生意见'
                urgency = 'moderate'
            else:
                risk_level = '低风险'
                recommendation = '建议医疗机构复查，结合临床症状判断'
                urgency = 'low'
        else:  # NORMAL
            if confidence >= 0.9:
                risk_level = '正常'
                recommendation = '影像显示正常，如有症状请咨询医生'
                urgency = 'none'
            elif confidence >= 0.7:
                risk_level = '基本正常'
                recommendation = '影像基本正常，如有不适建议观察或复查'
                urgency = 'low'
            else:
                risk_level = '不确定'
                recommendation = '结果不确定，建议专业医生进一步评估'
                urgency = 'moderate'
        
        return {
            'risk_level': risk_level,
            'recommendation': recommendation,
            'urgency': urgency,
            'confidence_interpretation': self._interpret_confidence(confidence),
            'disclaimers': [
                '本结果仅供参考，不能替代专业医生诊断',
                '如有症状或担忧，请及时就医',
                '最终诊断需要结合临床表现和其他检查'
            ]
        }
    
    def _interpret_confidence(self, confidence):
        """解释置信度含义"""
        if confidence >= 0.95:
            return '模型对此预测非常确信'
        elif confidence >= 0.85:
            return '模型对此预测比较确信'
        elif confidence >= 0.7:
            return '模型对此预测有一定把握'
        elif confidence >= 0.6:
            return '模型对此预测把握较小'
        else:
            return '模型对此预测不确定'

def create_prediction_report(predictor, image_path, save_path=None):
    """
    创建完整的预测报告
    
    Args:
        predictor: 预测器实例
        image_path: 图片路径
        save_path: 报告保存路径
        
    Returns:
        dict: 完整报告
    """
    # 获取预测结果
    prediction = predictor.predict_single_image(image_path)
    
    if 'error' not in prediction:
        # 获取医学建议
        medical_advice = predictor.get_medical_recommendation(prediction)
        
        # 构建完整报告
        report = {
            'report_info': {
                'generated_time': datetime.now().isoformat(),
                'model_version': 'ChestXRay-v1.0',
                'patient_id': f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
            },
            'image_analysis': prediction,
            'medical_assessment': medical_advice,
            'technical_details': {
                'model_architecture': 'ResNet50',
                'input_size': '224x224',
                'preprocessing': 'ImageNet normalization'
            }
        }
    else:
        report = {
            'error': prediction['error'],
            'generated_time': datetime.now().isoformat()
        }
    
    # 保存报告
    if save_path:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"📄 报告已保存至: {save_path}")
    
    return report

def batch_process_directory(predictor, input_dir, output_dir=None, file_pattern="*.jpeg"):
    """
    批量处理目录中的图片
    
    Args:
        predictor: 预测器实例
        input_dir: 输入目录
        output_dir: 输出目录
        file_pattern: 文件匹配模式
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return
    
    # 查找图片文件
    image_files = list(input_path.glob(file_pattern))
    if not image_files:
        print(f"❌ 在目录 {input_dir} 中未找到匹配的图片文件")
        return
    
    print(f"🔍 找到 {len(image_files)} 个图片文件")
    
    # 创建输出目录
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    
    # 批量预测
    results = predictor.predict_batch(image_files)
    
    # 生成汇总报告
    summary = {
        'total_images': len(image_files),
        'successful_predictions': len([r for r in results if 'error' not in r]),
        'failed_predictions': len([r for r in results if 'error' in r]),
        'class_distribution': {},
        'confidence_statistics': {},
        'processed_time': datetime.now().isoformat()
    }
    
    # 统计分析
    successful_results = [r for r in results if 'error' not in r]
    if successful_results:
        # 类别分布
        for class_name in predictor.class_names:
            count = len([r for r in successful_results if r['predicted_class'] == class_name])
            summary['class_distribution'][class_name] = count
        
        # 置信度统计
        confidences = [r['confidence'] for r in successful_results]
        summary['confidence_statistics'] = {
            'mean': np.mean(confidences),
            'std': np.std(confidences),
            'min': np.min(confidences),
            'max': np.max(confidences)
        }
    
    # 保存结果
    if output_dir:
        # 保存详细结果
        with open(output_path / 'detailed_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 保存汇总报告
        with open(output_path / 'summary_report.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"📊 结果已保存至: {output_dir}")
    
    # 打印汇总
    print(f"\n📋 批量处理汇总:")
    print(f"   总计图片: {summary['total_images']}")
    print(f"   成功预测: {summary['successful_predictions']}")
    print(f"   失败预测: {summary['failed_predictions']}")
    
    if summary['class_distribution']:
        print(f"   类别分布:")
        for class_name, count in summary['class_distribution'].items():
            percentage = count / summary['successful_predictions'] * 100
            print(f"     {class_name}: {count} ({percentage:.1f}%)")
    
    return results, summary

def main():
    """主函数 - 演示预测器的使用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='胸部X光片分类预测工具')
    parser.add_argument('--model', type=str, default='checkpoints/best_model.pth',
                       help='模型权重文件路径')
    parser.add_argument('--image', type=str, help='单张图片路径')
    parser.add_argument('--batch', type=str, help='批量处理目录路径') 
    parser.add_argument('--output', type=str, help='输出目录路径')
    parser.add_argument('--report', action='store_true', help='生成详细报告')
    
    args = parser.parse_args()
    
    # 检查模型文件
    if not os.path.exists(args.model):
        print(f"❌ 模型文件不存在: {args.model}")
        print("请先训练模型或检查文件路径")
        return
    
    # 创建预测器
    try:
        predictor = ChestXRayPredictor(args.model)
    except Exception as e:
        print(f"❌ 创建预测器失败: {e}")
        return
    
    # 单张图片预测
    if args.image:
        if not os.path.exists(args.image):
            print(f"❌ 图片文件不存在: {args.image}")
            return
        
        print(f"\n🔍 正在分析图片: {args.image}")
        
        if args.report:
            # 生成详细报告
            report_path = args.output or f"prediction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report = create_prediction_report(predictor, args.image, report_path)
            
            print(f"\n📋 预测报告:")
            if 'error' not in report:
                print(f"   预测类别: {report['image_analysis']['predicted_class']}")
                print(f"   置信度: {report['image_analysis']['confidence']:.4f}")
                print(f"   风险等级: {report['medical_assessment']['risk_level']}")
                print(f"   医学建议: {report['medical_assessment']['recommendation']}")
            else:
                print(f"   错误: {report['error']}")
        else:
            # 简单预测
            result = predictor.predict_single_image(args.image)
            
            print(f"\n📋 预测结果:")
            if 'error' not in result:
                print(f"   预测类别: {result['predicted_class']}")
                print(f"   置信度: {result['confidence']:.4f}")
                print(f"   概率分布:")
                for class_name, prob in result['probabilities'].items():
                    print(f"     {class_name}: {prob:.4f}")
            else:
                print(f"   错误: {result['error']}")
    
    # 批量处理
    elif args.batch:
        print(f"\n🔍 批量处理目录: {args.batch}")
        batch_process_directory(predictor, args.batch, args.output)
    
    else:
        print("请指定 --image 或 --batch 参数")
        print("\n使用示例:")
        print("  单张图片: python deploy_simple.py --image path/to/image.jpg")
        print("  详细报告: python deploy_simple.py --image path/to/image.jpg --report")
        print("  批量处理: python deploy_simple.py --batch path/to/images/ --output results/")

if __name__ == "__main__":
    main() 