#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROC曲线详细演示和可视化
配合ROC曲线详解.md文档使用
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc, precision_recall_curve
from sklearn.metrics import confusion_matrix, classification_report
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def generate_sample_data():
    """生成示例数据来演示ROC曲线"""
    np.random.seed(42)
    
    # 模拟三种不同性能的模型
    n_samples = 1000
    
    # 真实标签：30%肺炎，70%正常
    y_true = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
    
    # 模型1：优秀模型 (AUC ≈ 0.92)
    y_scores_good = np.random.beta(2, 8, n_samples)  # 基础分数
    y_scores_good[y_true == 1] += 0.4  # 肺炎患者得分更高
    y_scores_good = np.clip(y_scores_good, 0, 1)
    
    # 模型2：一般模型 (AUC ≈ 0.75)
    y_scores_avg = np.random.beta(3, 5, n_samples)
    y_scores_avg[y_true == 1] += 0.2  # 较小的区分度
    y_scores_avg = np.clip(y_scores_avg, 0, 1)
    
    # 模型3：较差模型 (AUC ≈ 0.60)
    y_scores_poor = np.random.beta(5, 5, n_samples)  # 几乎随机
    y_scores_poor[y_true == 1] += 0.1
    y_scores_poor = np.clip(y_scores_poor, 0, 1)
    
    return y_true, {
        '优秀模型': y_scores_good,
        '一般模型': y_scores_avg,
        '较差模型': y_scores_poor
    }

def plot_roc_basics():
    """演示ROC曲线基础概念"""
    print("="*60)
    print("🎯 ROC曲线基础概念演示")
    print("="*60)
    
    y_true, models_scores = generate_sample_data()
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('ROC曲线基础概念', fontsize=16, fontweight='bold')
    
    colors = ['darkgreen', 'orange', 'red']
    
    # 1. 基础ROC曲线对比
    ax1 = axes[0, 0]
    for i, (model_name, scores) in enumerate(models_scores.items()):
        fpr, tpr, _ = roc_curve(y_true, scores)
        auc_score = auc(fpr, tpr)
        ax1.plot(fpr, tpr, color=colors[i], lw=2, 
                label=f'{model_name} (AUC={auc_score:.3f})')
    
    # 添加参考线
    ax1.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5, label='随机分类器 (AUC=0.5)')
    ax1.plot([0, 0, 1], [0, 1, 1], 'b:', lw=1, alpha=0.5, label='理想分类器 (AUC=1.0)')
    
    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([0.0, 1.05])
    ax1.set_xlabel('假正率 (FPR)')
    ax1.set_ylabel('真正率 (TPR)')
    ax1.set_title('ROC曲线对比')
    ax1.legend(loc="lower right")
    ax1.grid(True, alpha=0.3)
    
    # 2. 概率分布可视化
    ax2 = axes[0, 1]
    scores = models_scores['优秀模型']
    
    # 正常和肺炎的概率分布
    normal_scores = scores[y_true == 0]
    pneumonia_scores = scores[y_true == 1]
    
    ax2.hist(normal_scores, alpha=0.7, bins=30, label='正常 (NORMAL)', color='blue', density=True)
    ax2.hist(pneumonia_scores, alpha=0.7, bins=30, label='肺炎 (PNEUMONIA)', color='red', density=True)
    ax2.axvline(0.5, color='black', linestyle='--', alpha=0.7, label='默认阈值=0.5')
    ax2.set_xlabel('预测概率')
    ax2.set_ylabel('密度')
    ax2.set_title('优秀模型的概率分布')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 阈值影响演示
    ax3 = axes[1, 0]
    fpr, tpr, thresholds = roc_curve(y_true, models_scores['优秀模型'])
    
    # 选择几个代表性阈值
    threshold_indices = [10, 20, 30, 40, 50]
    for i, idx in enumerate(threshold_indices):
        if idx < len(thresholds):
            ax3.plot(fpr[idx], tpr[idx], 'o', markersize=8, 
                    label=f'阈值={thresholds[idx]:.2f}')
    
    ax3.plot(fpr, tpr, 'g-', lw=2, alpha=0.7)
    ax3.set_xlabel('假正率 (FPR)')
    ax3.set_ylabel('真正率 (TPR)')
    ax3.set_title('不同阈值对应的工作点')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. TPR vs FPR vs 阈值
    ax4 = axes[1, 1]
    ax4.plot(thresholds, tpr[:-1], 'b-', label='TPR (敏感性)', linewidth=2)
    ax4.plot(thresholds, 1-fpr[:-1], 'r-', label='TNR (特异性)', linewidth=2)
    ax4.axhline(0.95, color='blue', linestyle=':', alpha=0.7, label='目标TPR=95%')
    ax4.set_xlabel('分类阈值')
    ax4.set_ylabel('指标值')
    ax4.set_title('阈值 vs 性能指标')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 打印解释
    print("\n📊 图表解读:")
    print("1. 左上图：不同模型的ROC曲线对比")
    print("   - 曲线越向左上角凸起，模型性能越好")
    print("   - AUC值越接近1.0，判别能力越强")
    print("\n2. 右上图：预测概率分布")
    print("   - 蓝色：正常病例的概率分布")
    print("   - 红色：肺炎病例的概率分布")
    print("   - 分离度越大，模型区分能力越强")
    print("\n3. 左下图：不同阈值的工作点")
    print("   - 每个点代表一个(FPR, TPR)组合")
    print("   - 阈值越低，TPR和FPR都越高")
    print("\n4. 右下图：阈值对性能的影响")
    print("   - 蓝线：真正率(召回率)")
    print("   - 红线：真负率(特异性)")
    print("   - 医学应用要求TPR≥95%")

def demonstrate_medical_optimization():
    """演示医学场景下的ROC优化"""
    print("\n" + "="*60)
    print("🏥 医学场景ROC优化演示")
    print("="*60)
    
    y_true, models_scores = generate_sample_data()
    y_scores = models_scores['优秀模型']
    
    # 计算不同方法的最佳阈值
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    
    # 1. 约登指数最佳点
    youden_index = tpr - fpr
    youden_optimal = np.argmax(youden_index)
    youden_threshold = thresholds[youden_optimal]
    youden_tpr = tpr[youden_optimal]
    youden_fpr = fpr[youden_optimal]
    
    # 2. 医学最佳点（TPR≥95%下FPR最小）
    high_tpr_indices = np.where(tpr >= 0.95)[0]
    if len(high_tpr_indices) > 0:
        medical_optimal = high_tpr_indices[np.argmin(fpr[high_tpr_indices])]
        medical_threshold = thresholds[medical_optimal]
        medical_tpr = tpr[medical_optimal]
        medical_fpr = fpr[medical_optimal]
    else:
        medical_optimal = np.argmax(tpr)
        medical_threshold = thresholds[medical_optimal]
        medical_tpr = tpr[medical_optimal]
        medical_fpr = fpr[medical_optimal]
    
    # 可视化
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # ROC曲线与最佳点
    auc_score = auc(fpr, tpr)
    ax1.plot(fpr, tpr, color='darkgreen', lw=3, label=f'ROC曲线 (AUC={auc_score:.3f})')
    ax1.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5, label='随机分类器')
    
    # 标记最佳点
    ax1.plot(youden_fpr, youden_tpr, 'ro', markersize=12, 
             label=f'约登最佳点\n阈值={youden_threshold:.3f}')
    ax1.plot(medical_fpr, medical_tpr, 'go', markersize=12,
             label=f'医学最佳点\n阈值={medical_threshold:.3f}')
    
    # 添加95%TPR线
    ax1.axhline(0.95, color='blue', linestyle=':', alpha=0.7, label='目标TPR=95%')
    
    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([0.0, 1.05])
    ax1.set_xlabel('假正率 (FPR)', fontsize=12)
    ax1.set_ylabel('真正率 (TPR)', fontsize=12)
    ax1.set_title('医学优化的ROC分析', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 混淆矩阵对比
    # 使用医学最佳阈值
    y_pred_medical = (y_scores >= medical_threshold).astype(int)
    cm_medical = confusion_matrix(y_true, y_pred_medical)
    
    # 使用约登最佳阈值
    y_pred_youden = (y_scores >= youden_threshold).astype(int)
    cm_youden = confusion_matrix(y_true, y_pred_youden)
    
    # 绘制混淆矩阵对比
    ax2.axis('off')
    
    # 创建子图
    ax2_1 = plt.subplot2grid((1, 4), (0, 2))
    ax2_2 = plt.subplot2grid((1, 4), (0, 3))
    
    # 医学最佳阈值的混淆矩阵
    sns.heatmap(cm_medical, annot=True, fmt='d', cmap='Blues', ax=ax2_1,
                xticklabels=['NORMAL', 'PNEUMONIA'], yticklabels=['NORMAL', 'PNEUMONIA'])
    ax2_1.set_title(f'医学最佳阈值\n({medical_threshold:.3f})', fontweight='bold')
    
    # 约登最佳阈值的混淆矩阵  
    sns.heatmap(cm_youden, annot=True, fmt='d', cmap='Oranges', ax=ax2_2,
                xticklabels=['NORMAL', 'PNEUMONIA'], yticklabels=['NORMAL', 'PNEUMONIA'])
    ax2_2.set_title(f'约登最佳阈值\n({youden_threshold:.3f})', fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    # 详细分析报告
    print(f"\n📋 阈值优化分析报告:")
    print("-" * 40)
    
    print(f"🎯 约登指数最佳阈值: {youden_threshold:.4f}")
    tn, fp, fn, tp = cm_youden.ravel()
    print(f"   TPR (召回率): {youden_tpr:.3f} ({youden_tpr*100:.1f}%)")
    print(f"   FPR (假警报率): {youden_fpr:.3f} ({youden_fpr*100:.1f}%)")
    print(f"   漏诊患者: {fn} 个")
    print(f"   误诊健康人: {fp} 个")
    
    print(f"\n🏥 医学最佳阈值: {medical_threshold:.4f}")
    tn, fp, fn, tp = cm_medical.ravel()
    print(f"   TPR (召回率): {medical_tpr:.3f} ({medical_tpr*100:.1f}%)")
    print(f"   FPR (假警报率): {medical_fpr:.3f} ({medical_fpr*100:.1f}%)")
    print(f"   漏诊患者: {fn} 个")
    print(f"   误诊健康人: {fp} 个")
    
    # 医学建议
    print(f"\n💡 医学建议:")
    if medical_tpr >= 0.95:
        print(f"✅ 推荐使用医学最佳阈值 {medical_threshold:.3f}")
        print(f"   理由：召回率达到 {medical_tpr:.1%}，符合医学安全标准")
        if medical_fpr > 0.3:
            print(f"   注意：假警报率较高 ({medical_fpr:.1%})，需要后续人工复查")
    else:
        print(f"⚠️  当前模型性能不足以满足医学要求")
        print(f"   最高召回率仅 {medical_tpr:.1%}，建议重新训练模型")
        print(f"   临时方案：使用阈值 {medical_threshold:.3f}，加强人工复查")
    
    return medical_threshold, youden_threshold

def demonstrate_cost_sensitive_analysis():
    """演示成本敏感分析"""
    print("\n" + "="*60)
    print("💰 成本敏感分析演示")
    print("="*60)
    
    y_true, models_scores = generate_sample_data()
    y_scores = models_scores['优秀模型']
    
    # 不同成本比例下的最佳阈值
    cost_ratios = [1, 5, 10, 20]  # 漏诊成本/误诊成本
    optimal_thresholds = []
    
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    colors = ['blue', 'green', 'orange', 'red']
    
    for i, cost_ratio in enumerate(cost_ratios):
        # 计算总成本 (标准化)
        costs = cost_ratio * (1 - tpr) + fpr  # 漏诊成本 + 误诊成本
        optimal_idx = np.argmin(costs)
        optimal_threshold = thresholds[optimal_idx]
        optimal_thresholds.append(optimal_threshold)
        
        # 在ROC曲线上标记最佳点
        ax1.plot(fpr[optimal_idx], tpr[optimal_idx], 'o', color=colors[i], 
                markersize=10, label=f'成本比例 {cost_ratio}:1\n阈值={optimal_threshold:.3f}')
    
    # 绘制ROC曲线
    auc_score = auc(fpr, tpr)
    ax1.plot(fpr, tpr, color='gray', lw=2, alpha=0.7, label=f'ROC曲线 (AUC={auc_score:.3f})')
    ax1.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5)
    
    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([0.0, 1.05])
    ax1.set_xlabel('假正率 (FPR)')
    ax1.set_ylabel('真正率 (TPR)')
    ax1.set_title('成本敏感的最佳工作点')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 成本比例 vs 最佳阈值
    ax2.plot(cost_ratios, optimal_thresholds, 'bo-', linewidth=2, markersize=8)
    ax2.set_xlabel('成本比例 (漏诊成本/误诊成本)')
    ax2.set_ylabel('最佳阈值')
    ax2.set_title('成本比例对最佳阈值的影响')
    ax2.grid(True, alpha=0.3)
    
    # 添加医学建议区域
    ax2.axhspan(0.2, 0.4, alpha=0.3, color='green', label='医学推荐区域')
    ax2.legend()
    
    plt.tight_layout()
    plt.show()
    
    # 打印分析
    print(f"\n📊 成本敏感分析结果:")
    print("-" * 40)
    for i, cost_ratio in enumerate(cost_ratios):
        threshold = optimal_thresholds[i]
        # 找到对应的TPR和FPR
        threshold_idx = np.argmin(np.abs(thresholds - threshold))
        corresponding_tpr = tpr[threshold_idx]
        corresponding_fpr = fpr[threshold_idx]
        
        print(f"成本比例 {cost_ratio:2d}:1 → 最佳阈值: {threshold:.3f}")
        print(f"   TPR: {corresponding_tpr:.3f}, FPR: {corresponding_fpr:.3f}")
        print(f"   含义: 漏诊成本是误诊成本的{cost_ratio}倍")
        print()
    
    print(f"💡 实际应用建议:")
    print(f"   • 轻症筛查: 成本比例 5:1，阈值约 {optimal_thresholds[1]:.3f}")
    print(f"   • 重症诊断: 成本比例 20:1，阈值约 {optimal_thresholds[3]:.3f}")
    print(f"   • 急诊场景: 成本比例更高，阈值更低")

def practical_application_demo():
    """实际应用演示"""
    print("\n" + "="*60)
    print("🚀 实际应用演示")
    print("="*60)
    
    # 模拟实际的模型预测结果
    np.random.seed(123)
    
    # 生成更真实的测试数据
    n_patients = 200
    
    # 模拟患者信息
    patients = []
    for i in range(n_patients):
        age = np.random.randint(20, 80)
        is_high_risk = age > 65 or np.random.random() < 0.1  # 高危患者
        
        # 真实诊断结果
        if is_high_risk:
            true_label = np.random.choice([0, 1], p=[0.4, 0.6])  # 高危患者更可能有肺炎
        else:
            true_label = np.random.choice([0, 1], p=[0.8, 0.2])  # 低危患者较少肺炎
        
        # 模型预测概率（加入一些真实的变异）
        if true_label == 1:  # 真的有肺炎
            base_prob = 0.7 + np.random.normal(0, 0.2)
        else:  # 没有肺炎
            base_prob = 0.3 + np.random.normal(0, 0.2)
        
        # 年龄影响（年龄大的更容易被预测为肺炎）
        age_factor = (age - 40) * 0.003
        predicted_prob = np.clip(base_prob + age_factor, 0, 1)
        
        patients.append({
            'id': f'P{i+1:03d}',
            'age': age,
            'high_risk': is_high_risk,
            'true_label': true_label,
            'predicted_prob': predicted_prob
        })
    
    # 提取数据
    y_true = np.array([p['true_label'] for p in patients])
    y_scores = np.array([p['predicted_prob'] for p in patients])
    
    # ROC分析
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    auc_score = auc(fpr, tpr)
    
    # 找到医学最佳阈值
    high_tpr_indices = np.where(tpr >= 0.95)[0]
    if len(high_tpr_indices) > 0:
        medical_optimal = high_tpr_indices[np.argmin(fpr[high_tpr_indices])]
        medical_threshold = thresholds[medical_optimal]
    else:
        medical_optimal = np.argmax(tpr)
        medical_threshold = thresholds[medical_optimal]
    
    # 应用阈值进行分类
    predictions = (y_scores >= medical_threshold).astype(int)
    
    # 生成临床报告
    print(f"📋 临床AI辅助诊断报告")
    print(f"   患者总数: {n_patients}")
    print(f"   AI模型AUC: {auc_score:.3f}")
    print(f"   建议阈值: {medical_threshold:.3f}")
    print()
    
    # 混淆矩阵分析
    cm = confusion_matrix(y_true, predictions)
    tn, fp, fn, tp = cm.ravel()
    
    print(f"🎯 诊断结果统计:")
    print(f"   正确识别肺炎患者: {tp} 例")
    print(f"   正确识别健康人群: {tn} 例")
    print(f"   误诊健康人为肺炎: {fp} 例 (需要进一步检查)")
    print(f"   漏诊肺炎患者: {fn} 例 (⚠️ 需要关注)")
    print()
    
    # 计算关键指标
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0  # 阳性预测值
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0  # 阴性预测值
    
    print(f"📈 关键性能指标:")
    print(f"   敏感性 (召回率): {sensitivity:.3f} ({sensitivity*100:.1f}%)")
    print(f"   特异性: {specificity:.3f} ({specificity*100:.1f}%)")
    print(f"   阳性预测值: {ppv:.3f} ({ppv*100:.1f}%)")
    print(f"   阴性预测值: {npv:.3f} ({npv*100:.1f}%)")
    print()
    
    # 医学建议
    print(f"🏥 临床应用建议:")
    if sensitivity >= 0.95:
        print(f"✅ 敏感性达标 ({sensitivity:.1%})，可作为筛查工具")
    else:
        print(f"⚠️  敏感性不足 ({sensitivity:.1%})，需要降低阈值或改进模型")
    
    if specificity >= 0.8:
        print(f"✅ 特异性良好 ({specificity:.1%})，假警报率可接受")
    else:
        print(f"⚠️  特异性偏低 ({specificity:.1%})，可能产生过多假警报")
    
    if fn > 0:
        print(f"🚨 注意：有 {fn} 例肺炎患者被漏诊，建议:")
        print(f"   1. 对AI阴性结果进行人工复查")
        print(f"   2. 结合临床症状和其他检查")
        print(f"   3. 定期随访观察")
    
    # 可视化临床应用场景
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # ROC曲线
    ax1.plot(fpr, tpr, color='blue', lw=3, label=f'AI模型 (AUC={auc_score:.3f})')
    ax1.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5, label='随机分类器')
    ax1.plot(fpr[medical_optimal], tpr[medical_optimal], 'ro', markersize=12,
             label=f'工作点 (阈值={medical_threshold:.3f})')
    ax1.axhline(0.95, color='red', linestyle=':', alpha=0.7, label='目标敏感性=95%')
    
    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([0.0, 1.05])
    ax1.set_xlabel('假正率 (1-特异性)')
    ax1.set_ylabel('真正率 (敏感性)')
    ax1.set_title('临床AI的ROC性能')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 混淆矩阵
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax2,
                xticklabels=['健康', '肺炎'], yticklabels=['健康', '肺炎'])
    ax2.set_title('临床诊断混淆矩阵')
    ax2.set_xlabel('AI预测')
    ax2.set_ylabel('实际诊断')
    
    plt.tight_layout()
    plt.show()

def main():
    """主演示函数"""
    print("🏥 ROC曲线详细演示 - 胸部X光片分类项目")
    print("=" * 70)
    
    # 1. 基础概念演示
    plot_roc_basics()
    
    # 2. 医学优化演示
    medical_threshold, youden_threshold = demonstrate_medical_optimization()
    
    # 3. 成本敏感分析
    demonstrate_cost_sensitive_analysis()
    
    # 4. 实际应用演示
    practical_application_demo()
    
    print("\n" + "="*70)
    print("🎓 ROC曲线学习要点总结")
    print("="*70)
    print("1. ROC曲线展示了模型在所有阈值下的性能")
    print("2. AUC提供了模型判别能力的整体评估")
    print("3. 在医学应用中，要优先保证高敏感性(TPR)")
    print("4. 阈值选择应该基于成本效益分析")
    print("5. 要结合混淆矩阵进行详细的性能分析")
    print("\n💡 下一步建议:")
    print("   1. 阅读 ROC曲线详解.md 了解理论细节")
    print("   2. 运行 python main.py eval 分析你的模型")
    print("   3. 根据分析结果优化模型和阈值")
    print("   4. 在真实数据上验证性能")

if __name__ == "__main__":
    main() 