#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强医学报告生成器
不依赖Ollama，基于规则生成详细医学报告
"""

from datetime import datetime
import json

class EnhancedMedicalReportGenerator:
    """增强医学报告生成器"""
    
    def __init__(self):
        self.report_templates = {
            'header': {
                'title': '胸部X线片AI辅助分析报告',
                'system': 'ChestXRay AI 分析系统 v1.0',
                'disclaimer': '本报告由AI系统生成，仅供临床参考，不能替代专业医生诊断'
            },
            'pneumonia_findings': {
                'high_confidence': {
                    'interpretation': '影像学表现提示肺炎可能性较高',
                    'findings': [
                        '肺野可能存在炎症浸润征象',
                        'AI模型检测到与细菌性或病毒性肺炎相关的影像特征',
                        '建议结合患者临床症状进行综合评估'
                    ],
                    'differential': [
                        '细菌性肺炎',
                        '病毒性肺炎',
                        '支原体肺炎',
                        '其他感染性疾病'
                    ]
                },
                'medium_confidence': {
                    'interpretation': '影像学表现存在肺炎可能',
                    'findings': [
                        '检测到可能的肺部异常征象',
                        'AI模型识别出与肺炎相关的特征，但需进一步确认',
                        '建议临床医生结合病史和体格检查综合判断'
                    ],
                    'differential': [
                        '早期肺炎',
                        '肺部感染',
                        '炎症性病变',
                        '需排除其他肺部疾病'
                    ]
                },
                'low_confidence': {
                    'interpretation': '影像学征象不典型，需要进一步评估',
                    'findings': [
                        '检测到轻微异常征象',
                        'AI模型检测结果不确定，可能存在技术限制',
                        '强烈建议专业放射科医生重新评估'
                    ],
                    'differential': [
                        '炎症性改变',
                        '正常变异',
                        '技术因素影响',
                        '需要其他影像学检查'
                    ]
                }
            },
            'normal_findings': {
                'high_confidence': {
                    'interpretation': '胸部X线片未见明显异常',
                    'findings': [
                        '双肺野透亮度正常',
                        '心影大小形态正常',
                        '肋膈角锐利',
                        '纵隔轮廓清晰'
                    ],
                    'note': '影像学表现基本正常，但不能完全排除早期或细微病变'
                },
                'medium_confidence': {
                    'interpretation': '胸部X线片基本正常',
                    'findings': [
                        '主要解剖结构显示正常',
                        '未发现明显病理征象',
                        'AI分析结果倾向于正常'
                    ],
                    'note': '如有临床症状，建议进一步检查或动态观察'
                },
                'low_confidence': {
                    'interpretation': 'X线片质量或AI分析存在不确定性',
                    'findings': [
                        '影像质量可能影响判断',
                        'AI模型分析结果不确定',
                        '需要专业医生重新评估'
                    ],
                    'note': '建议重新拍摄或进行其他影像学检查'
                }
            }
        }
        
    def get_confidence_level(self, confidence):
        """根据置信度确定级别"""
        if confidence >= 0.8:
            return 'high_confidence'
        elif confidence >= 0.6:
            return 'medium_confidence'
        else:
            return 'low_confidence'
    
    def generate_clinical_recommendations(self, predicted_class, confidence):
        """生成临床建议"""
        recommendations = []
        
        if predicted_class == 'PNEUMONIA':
            if confidence >= 0.9:
                recommendations = [
                    '立即进行临床评估，包括详细病史询问和体格检查',
                    '建议检查血常规、CRP、PCT等炎症指标',
                    '考虑痰液培养和药敏试验',
                    '根据临床表现考虑抗感染治疗',
                    '密切观察病情变化，必要时复查胸片'
                ]
            elif confidence >= 0.7:
                recommendations = [
                    '建议临床医生详细评估患者症状',
                    '考虑实验室检查以明确感染指标',
                    '如有发热、咳嗽等症状，建议及时治疗',
                    '1-2天内复查或进一步影像学检查',
                    '注意观察病情进展'
                ]
            else:
                recommendations = [
                    'AI分析结果不确定，请专业医生重新评估',
                    '建议结合患者临床表现综合判断',
                    '如有呼吸道症状，建议密切观察',
                    '考虑其他影像学检查方法（如CT）',
                    '必要时请呼吸科会诊'
                ]
        else:  # NORMAL
            if confidence >= 0.8:
                recommendations = [
                    '影像学未见明显异常，但需结合临床症状',
                    '如患者无症状，建议定期健康体检',
                    '如有呼吸道症状，建议临床评估',
                    '保持良好的生活方式和肺部健康',
                    '有症状变化时及时就医'
                ]
            else:
                recommendations = [
                    'AI分析倾向于正常，但建议专业医生确认',
                    '如有任何呼吸道症状，请及时就医',
                    '建议定期复查或进一步检查',
                    '保持对呼吸系统健康的关注',
                    '必要时进行其他影像学检查'
                ]
        
        return recommendations
    
    def generate_follow_up_plan(self, predicted_class, confidence):
        """生成随访计划"""
        if predicted_class == 'PNEUMONIA':
            if confidence >= 0.8:
                return {
                    'immediate': '24-48小时内临床随访',
                    'short_term': '3-5天后复查胸片或临床评估',
                    'medium_term': '1-2周后评估治疗效果',
                    'long_term': '治疗完成后1个月复查'
                }
            else:
                return {
                    'immediate': '48-72小时内专科评估',
                    'short_term': '1周内明确诊断',
                    'medium_term': '根据确诊结果制定治疗计划',
                    'long_term': '按治疗方案定期随访'
                }
        else:
            return {
                'immediate': '如有症状出现立即就医',
                'short_term': '3-6个月常规体检',
                'medium_term': '年度胸部影像学检查',
                'long_term': '维持健康生活方式'
            }
    
    def generate_comprehensive_report(self, image_analysis):
        """生成综合医学报告"""
        predicted_class = image_analysis.get('predicted_class')
        confidence = image_analysis.get('confidence', 0)
        confidence_level = self.get_confidence_level(confidence)
        
        # 获取对应的模板
        if predicted_class == 'PNEUMONIA':
            findings_template = self.report_templates['pneumonia_findings'][confidence_level]
        else:
            findings_template = self.report_templates['normal_findings'][confidence_level]
        
        # 生成报告
        report = {
            'report_header': {
                'title': self.report_templates['header']['title'],
                'generated_time': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'),
                'report_id': f"RPT{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'ai_system': self.report_templates['header']['system'],
                'disclaimer': self.report_templates['header']['disclaimer']
            },
            
            'imaging_analysis': {
                'ai_prediction': predicted_class,
                'confidence_score': f"{confidence:.1%}",
                'confidence_interpretation': self._get_confidence_interpretation(confidence),
                'risk_stratification': self._get_risk_level(predicted_class, confidence)
            },
            
            'clinical_findings': {
                'primary_interpretation': findings_template['interpretation'],
                'detailed_findings': findings_template['findings'],
                'differential_diagnosis': findings_template.get('differential', []),
                'additional_notes': findings_template.get('note', '')
            },
            
            'clinical_recommendations': {
                'immediate_actions': self.generate_clinical_recommendations(predicted_class, confidence),
                'follow_up_plan': self.generate_follow_up_plan(predicted_class, confidence),
                'additional_testing': self._suggest_additional_tests(predicted_class, confidence)
            },
            
            'quality_metrics': {
                'model_performance': '训练准确率: 84.6%',
                'validation_notes': 'AI模型基于大量胸部X线片训练',
                'limitations': [
                    'AI分析不能替代专业医生判断',
                    '对于早期或不典型病变可能存在漏诊',
                    '影像质量会影响分析准确性',
                    '需要结合临床症状综合判断'
                ]
            },
            
            'medical_disclaimer': {
                'important_notes': [
                    '本AI分析结果仅供临床参考',
                    '最终诊断需由执业医师作出',
                    '如有症状或疑虑请及时就医',
                    '本系统不承担任何医疗责任'
                ],
                'emergency_guidance': '如出现呼吸困难、胸痛、高热等急症症状，请立即就近急诊科就医'
            }
        }
        
        return report
    
    def _get_confidence_interpretation(self, confidence):
        """置信度解释"""
        if confidence >= 0.9:
            return "AI模型对此分析结果非常确信"
        elif confidence >= 0.8:
            return "AI模型对此分析结果比较确信"
        elif confidence >= 0.7:
            return "AI模型对此分析结果有一定把握"
        elif confidence >= 0.6:
            return "AI模型对此分析结果把握一般"
        else:
            return "AI模型对此分析结果不确定，建议专业医生评估"
    
    def _get_risk_level(self, predicted_class, confidence):
        """风险分层"""
        if predicted_class == 'PNEUMONIA':
            if confidence >= 0.9:
                return "高风险 - 建议立即就医"
            elif confidence >= 0.7:
                return "中等风险 - 建议尽快就医"
            else:
                return "低风险 - 建议专业评估"
        else:
            if confidence >= 0.8:
                return "低风险 - 影像学正常"
            else:
                return "待评估 - 需专业医生确认"
    
    def _suggest_additional_tests(self, predicted_class, confidence):
        """建议额外检查"""
        tests = []
        
        if predicted_class == 'PNEUMONIA':
            if confidence >= 0.8:
                tests = [
                    '血常规+CRP',
                    '痰液培养（如有咳痰）',
                    '血氧饱和度监测',
                    '必要时胸部CT检查'
                ]
            else:
                tests = [
                    '胸部CT增强扫描',
                    '炎症标志物检测',
                    '病原学检查',
                    '肺功能评估（如适用）'
                ]
        else:
            if confidence < 0.8:
                tests = [
                    '胸部CT平扫',
                    '动态观察',
                    '必要时专科会诊',
                    '其他针对性检查（根据症状）'
                ]
        
        return tests

def create_enhanced_report(image_analysis):
    """创建增强医学报告的便利函数"""
    generator = EnhancedMedicalReportGenerator()
    return generator.generate_comprehensive_report(image_analysis)

# 测试函数
def test_report_generation():
    """测试报告生成功能"""
    # 测试肺炎高置信度
    test_analysis_1 = {
        'predicted_class': 'PNEUMONIA',
        'confidence': 0.92,
        'probabilities': {'NORMAL': 0.08, 'PNEUMONIA': 0.92}
    }
    
    # 测试正常低置信度
    test_analysis_2 = {
        'predicted_class': 'NORMAL',
        'confidence': 0.65,
        'probabilities': {'NORMAL': 0.65, 'PNEUMONIA': 0.35}
    }
    
    generator = EnhancedMedicalReportGenerator()
    
    print("测试报告1 - 高置信度肺炎:")
    report1 = generator.generate_comprehensive_report(test_analysis_1)
    print(json.dumps(report1, ensure_ascii=False, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    print("测试报告2 - 低置信度正常:")
    report2 = generator.generate_comprehensive_report(test_analysis_2)
    print(json.dumps(report2, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_report_generation() 