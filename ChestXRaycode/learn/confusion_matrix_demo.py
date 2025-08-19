#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混淆矩阵详细解释和可视化演示
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.font_manager as fm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def explain_confusion_matrix():
    """详细解释混淆矩阵"""
    
    print("=" * 70)
    print("🏥 胸部X光片分类 - 混淆矩阵详解")
    print("=" * 70)
    
    # 模拟真实的预测结果
    np.random.seed(42)
    
    # 假设测试集有624个样本
    n_normal_true = 234      # 真实正常病例
    n_pneumonia_true = 390   # 真实肺炎病例
    
    # 模拟预测结果 (基于一个表现良好的模型)
    # 正常病例的预测 (大部分正确，少部分误诊为肺炎)
    normal_pred = ['NORMAL'] * 180 + ['PNEUMONIA'] * 54
    
    # 肺炎病例的预测 (大部分正确，少部分漏诊)
    pneumonia_pred = ['NORMAL'] * 12 + ['PNEUMONIA'] * 378
    
    # 合并所有预测
    y_true = ['NORMAL'] * n_normal_true + ['PNEUMONIA'] * n_pneumonia_true
    y_pred = normal_pred + pneumonia_pred
    
    # 生成混淆矩阵
    cm = confusion_matrix(y_true, y_pred, labels=['NORMAL', 'PNEUMONIA'])
    
    print("\n📊 混淆矩阵结果:")
    print("-" * 50)
    
    # 漂亮的打印格式
    print(f"{'':>12} {'预测结果':>20}")
    print(f"{'':>12} {'NORMAL':>10} {'PNEUMONIA':>10}")
    print(f"真实标签 {'NORMAL':>8} {cm[0,0]:>10} {cm[0,1]:>10}")
    print(f"{'':>8} {'PNEUMONIA':>8} {cm[1,0]:>10} {cm[1,1]:>10}")
    
    # 提取各种情况
    TN, FP = cm[0, 0], cm[0, 1]  # 第一行：真正常，假肺炎
    FN, TP = cm[1, 0], cm[1, 1]  # 第二行：假正常，真肺炎
    
    print(f"\n🔍 详细解读:")
    print("-" * 50)
    print(f"✅ TN (真负例): {TN:>3} - 正确识别的正常病例")
    print(f"❌ FP (假正例): {FP:>3} - 误诊为肺炎的正常病例 (虚惊一场)")  
    print(f"🚨 FN (假负例): {FN:>3} - 漏诊的肺炎病例 (危险！)")
    print(f"✅ TP (真正例): {TP:>3} - 正确识别的肺炎病例")
    
    # 计算各种指标
    accuracy = (TP + TN) / (TP + TN + FP + FN)
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\n📈 关键指标:")
    print("-" * 50)
    print(f"🎯 准确率 (Accuracy):     {accuracy:.3f} ({accuracy*100:.1f}%)")
    print(f"🔬 精确率 (Precision):    {precision:.3f} ({precision*100:.1f}%)")
    print(f"🎣 召回率 (Recall):       {recall:.3f} ({recall*100:.1f}%)")
    print(f"🛡️  特异性 (Specificity):  {specificity:.3f} ({specificity*100:.1f}%)")
    print(f"⚖️  F1分数:              {f1_score:.3f} ({f1_score*100:.1f}%)")
    
    print(f"\n💡 指标解释:")
    print("-" * 50)
    print(f"• 准确率: 总体分类正确的比例")
    print(f"• 精确率: 预测为肺炎中真正是肺炎的比例")
    print(f"• 召回率: 真实肺炎中被正确识别的比例")
    print(f"• 特异性: 真实正常中被正确识别的比例")
    print(f"• F1分数: 精确率和召回率的调和平均")
    
    # 医学角度分析
    print(f"\n🏥 医学角度分析:")
    print("-" * 50)
    
    if FN > 0:
        print(f"🚨 警告: 有 {FN} 个肺炎病例被漏诊!")
        print(f"   这在医学上是很危险的，可能延误治疗")
        print(f"   建议: 调整模型阈值，提高召回率")
    
    if FP > 0:
        print(f"⚠️  注意: 有 {FP} 个正常病例被误诊为肺炎")
        print(f"   这会造成不必要的恐慌和医疗资源浪费")
        print(f"   但相比漏诊，这是可以接受的")
    
    if recall < 0.95:
        print(f"📋 建议: 召回率 {recall:.1%} 偏低，应该提高到95%以上")
    else:
        print(f"✅ 召回率 {recall:.1%} 表现良好")
    
    # 可视化
    plot_confusion_matrix(cm, ['NORMAL', 'PNEUMONIA'])
    
    return cm, accuracy, precision, recall, specificity

def plot_confusion_matrix(cm, class_names):
    """绘制美观的混淆矩阵"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 绝对数量的混淆矩阵
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names,
                ax=ax1, cbar_kws={'label': '样本数量'})
    ax1.set_title('混淆矩阵 (绝对数量)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('预测标签', fontsize=12)
    ax1.set_ylabel('真实标签', fontsize=12)
    
    # 添加数量标注
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            text = ax1.text(j+0.5, i+0.5, str(cm[i, j]),
                           ha="center", va="center", fontsize=16, fontweight='bold')
    
    # 百分比的混淆矩阵
    cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    sns.heatmap(cm_percent, annot=True, fmt='.1%', cmap='Oranges',
                xticklabels=class_names, yticklabels=class_names,
                ax=ax2, cbar_kws={'label': '百分比'})
    ax2.set_title('混淆矩阵 (百分比)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('预测标签', fontsize=12)
    ax2.set_ylabel('真实标签', fontsize=12)
    
    plt.tight_layout()
    plt.show()
    
    # 分析每个象限
    print(f"\n🎨 混淆矩阵可视化解读:")
    print("-" * 50)
    print(f"🔵 深蓝色 (左上): 正确识别的正常病例 - 越深越好")
    print(f"🔵 深蓝色 (右下): 正确识别的肺炎病例 - 越深越好") 
    print(f"🔷 浅蓝色 (右上): 误诊的正常病例 - 越浅越好")
    print(f"🔷 浅蓝色 (左下): 漏诊的肺炎病例 - 越浅越好 (最重要!)")

def model_improvement_suggestions(cm):
    """基于混淆矩阵给出模型改进建议"""
    
    TN, FP, FN, TP = cm.ravel()
    total = TN + FP + FN + TP
    
    print(f"\n🔧 模型改进建议:")
    print("=" * 50)
    
    # 假阴性过多
    if FN / (TP + FN) > 0.05:  # 假阴性率 > 5%
        print(f"🚨 问题: 假阴性率过高 ({FN/(TP+FN):.1%})")
        print(f"   解决方案:")
        print(f"   1. 降低分类阈值 (从0.5降到0.3)")
        print(f"   2. 调整class_weight，增加肺炎类别权重")
        print(f"   3. 使用Focal Loss处理类别不平衡")
        print(f"   4. 收集更多肺炎样本数据")
    
    # 假阳性过多  
    if FP / (TN + FP) > 0.3:  # 假阳性率 > 30%
        print(f"⚠️  问题: 假阳性率较高 ({FP/(TN+FP):.1%})")
        print(f"   解决方案:")
        print(f"   1. 增加模型复杂度")
        print(f"   2. 添加更多数据增强")
        print(f"   3. 使用集成学习方法")
    
    # 总体准确率不够
    accuracy = (TP + TN) / total
    if accuracy < 0.9:
        print(f"📊 问题: 总体准确率偏低 ({accuracy:.1%})")
        print(f"   解决方案:")
        print(f"   1. 尝试更大的模型 (ResNet101)")
        print(f"   2. 增加训练轮数")
        print(f"   3. 调整学习率")
        print(f"   4. 使用预训练权重")
    
    print(f"\n✅ 当前模型表现总结:")
    print(f"   • 在医学诊断中，宁可误诊也不要漏诊")
    print(f"   • 你的模型假阴性率: {FN/(TP+FN):.1%}")
    print(f"   • 目标: 假阴性率 < 3%")

if __name__ == "__main__":
    # 运行演示
    cm, acc, prec, rec, spec = explain_confusion_matrix()
    model_improvement_suggestions(cm)
    
    print(f"\n🎓 学习要点:")
    print("=" * 50)
    print(f"1. 混淆矩阵是评估分类模型的最重要工具")
    print(f"2. 在医学诊断中，假阴性(漏诊)比假阳性(误诊)更危险")
    print(f"3. 要根据具体应用场景选择关注的指标")
    print(f"4. 可以通过调整阈值来平衡精确率和召回率")
    print(f"5. 混淆矩阵能直观显示模型的错误模式")
    
    print(f"\n💡 下一步建议:")
    print(f"   运行: python main.py eval --checkpoint checkpoints/best_model.pth")
    print(f"   查看你的真实模型的混淆矩阵表现!") 