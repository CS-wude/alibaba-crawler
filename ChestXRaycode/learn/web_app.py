#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
胸部X光片分析Web应用
提供图片上传、分析和报告展示的完整Web界面
"""

import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path
import traceback

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import base64

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

# 初始化导入标志
MULTIMODAL_AVAILABLE = False
BASIC_PREDICTION_AVAILABLE = False

# 尝试导入基础预测器
try:
    from deploy_simple import ChestXRayPredictor
    BASIC_PREDICTION_AVAILABLE = True
    print("✅ 基础预测器模块导入成功")
except ImportError as e:
    print(f"❌ 基础预测器导入失败: {e}")
    BASIC_PREDICTION_AVAILABLE = False

# 尝试导入多模态服务
try:
    from multimodal_service import MedicalMultimodalAI
    MULTIMODAL_AVAILABLE = True
    print("✅ 多模态服务模块导入成功")
except ImportError as e:
    print(f"⚠️  多模态服务不可用: {e}")
    MULTIMODAL_AVAILABLE = False

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'chest-xray-analysis-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB最大文件大小
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['REPORTS_FOLDER'] = 'static/reports'

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# 全局变量
ai_system = None
basic_predictor = None

# 初始化标志
_ai_initialized = False

def create_directories():
    """创建必要的目录"""
    dirs = [
        app.config['UPLOAD_FOLDER'],
        app.config['REPORTS_FOLDER'],
        'templates',
        'static/css',
        'static/js',
        'static/images'
    ]
    
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_ai_systems():
    """初始化AI系统"""
    global ai_system, basic_predictor, _ai_initialized
    
    if _ai_initialized:
        return True
    
    model_path = 'checkpoints/best_model.pth'
    
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        print("请确保已训练模型")
        return False
    
    try:
        print("🔧 开始初始化AI系统...")
        
        # 尝试初始化多模态系统
        if MULTIMODAL_AVAILABLE:
            print("🔧 正在初始化多模态AI系统...")
            try:
                ai_system = MedicalMultimodalAI(model_path, 'llama2')
                print("✅ 多模态AI系统初始化成功")
            except Exception as e:
                print(f"⚠️  多模态系统初始化失败: {e}")
                ai_system = None
        else:
            print("⚠️  多模态系统不可用，使用基础预测器")
            ai_system = None
        
        # 初始化基础预测器作为备用
        if BASIC_PREDICTION_AVAILABLE:
            print("🔧 正在初始化基础预测器...")
            basic_predictor = ChestXRayPredictor(model_path)
            print("✅ 基础预测器初始化成功")
        else:
            print("❌ 基础预测器不可用")
            basic_predictor = None
        
        # 检查是否至少有一个系统可用
        if ai_system is None and basic_predictor is None:
            print("❌ 没有可用的AI系统")
            return False
        
        _ai_initialized = True
        print("✅ AI系统初始化完成")
        return True
        
    except Exception as e:
        print(f"❌ AI系统初始化失败: {e}")
        traceback.print_exc()
        return False

def ensure_ai_initialized():
    """确保AI系统已初始化"""
    if not _ai_initialized:
        print("🔄 检测到AI系统未初始化，正在初始化...")
        return initialize_ai_systems()
    return True

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传和分析"""
    try:
        # 确保AI系统已初始化
        if not ensure_ai_initialized():
            return jsonify({'error': 'AI系统初始化失败，请检查模型文件和依赖'}), 500
        
        # 检查请求中是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'不支持的文件格式，请上传: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # 生成安全的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        safe_filename = f"{timestamp}_{unique_id}_{name}{ext}"
        
        # 保存文件
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(filepath)
        
        print(f"📁 文件已保存: {filepath}")
        
        # 获取用户选择的报告类型
        use_ollama = request.form.get('use_ollama', 'false').lower() == 'true'
        print(f"🎯 用户选择: {'完整AI报告 (Ollama)' if use_ollama else '增强版专业报告'}")
        
        # 分析图像
        analysis_result = analyze_image(filepath, unique_id, use_ollama)
        
        if 'error' in analysis_result:
            return jsonify(analysis_result), 500
        
        # 添加文件信息
        analysis_result['file_info'] = {
            'filename': filename,
            'safe_filename': safe_filename,
            'upload_time': timestamp,
            'file_size': os.path.getsize(filepath),
            'analysis_id': unique_id
        }
        
        return jsonify(analysis_result)
        
    except RequestEntityTooLarge:
        return jsonify({'error': '文件太大，请选择小于16MB的图片'}), 413
    except Exception as e:
        error_msg = f"处理文件时发生错误: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

def analyze_image(filepath, analysis_id, use_ollama=False):
    """分析图像并生成报告"""
    try:
        print(f"🔍 开始分析图像: {filepath}")
        print(f"   AI系统状态: ai_system={'已初始化' if ai_system else '未初始化'}")
        print(f"   基础预测器状态: basic_predictor={'已初始化' if basic_predictor else '未初始化'}")
        print(f"   用户选择: {'完整AI报告 (Ollama)' if use_ollama else '增强版专业报告'}")
        
        result = {}
        
        # 根据用户选择决定分析方法
        if use_ollama and ai_system is not None:
            # 用户选择使用Ollama，且多模态系统可用
            print("🤖 使用多模态AI系统分析（Ollama）...")
            multimodal_result = ai_system.analyze_xray_with_report(filepath)
            
            if 'error' not in multimodal_result:
                result = {
                    'analysis_type': 'multimodal',
                    'image_analysis': multimodal_result['image_analysis'],
                    'medical_report': multimodal_result['medical_report'],
                    'comprehensive_assessment': multimodal_result['comprehensive_assessment'],
                    'system_info': multimodal_result['system_info'],
                    'user_choice': 'ollama'
                }
                
                # 创建报告目录（如果不存在）
                Path(app.config['REPORTS_FOLDER']).mkdir(parents=True, exist_ok=True)
                
                # 保存详细报告
                report_path = os.path.join(app.config['REPORTS_FOLDER'], f"report_{analysis_id}.json")
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(multimodal_result, f, ensure_ascii=False, indent=2)
                
                result['report_file'] = f"report_{analysis_id}.json"
                print("✅ 多模态AI分析完成")
                
            else:
                print("⚠️  多模态分析失败，降级到增强版报告")
                result = analyze_with_basic_predictor(filepath, analysis_id)
                result['user_choice'] = 'ollama_fallback'
                
        elif basic_predictor is not None:
            # 用户选择增强版报告，或者Ollama不可用时的备用方案
            if use_ollama:
                print("⚠️  用户选择Ollama但多模态系统不可用，使用增强版报告")
            else:
                print("📋 按用户选择使用增强版专业报告...")
            result = analyze_with_basic_predictor(filepath, analysis_id)
            result['user_choice'] = 'enhanced' if not use_ollama else 'enhanced_fallback'
        
        else:
            error_msg = f'AI系统未初始化 - ai_system: {ai_system}, basic_predictor: {basic_predictor}'
            print(f"❌ {error_msg}")
            return {'error': error_msg}
        
        return result
        
    except Exception as e:
        error_msg = f"分析过程中发生错误: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {'error': error_msg}

def analyze_with_basic_predictor(filepath, analysis_id):
    """使用基础预测器分析"""
    prediction_result = basic_predictor.predict_single_image(filepath)
    
    if 'error' in prediction_result:
        return prediction_result
    
    # 生成简化的医学建议
    medical_advice = basic_predictor.get_medical_recommendation(prediction_result)
    
    # 尝试使用增强版医学报告生成器
    enhanced_report = None
    try:
        from enhanced_medical_report import create_enhanced_report
        enhanced_report = create_enhanced_report(prediction_result)
        print("✅ 生成了增强版医学报告")
    except Exception as e:
        print(f"⚠️  增强版报告生成失败: {e}")
        enhanced_report = None
    
    result = {
        'analysis_type': 'enhanced_basic' if enhanced_report else 'basic',
        'image_analysis': prediction_result,
        'medical_advice': medical_advice,
        'enhanced_report': enhanced_report,
        'system_info': {
            'analysis_time': datetime.now().isoformat(),
            'image_model': 'ResNet50-ChestXRay',
            'report_generator': 'Enhanced Basic' if enhanced_report else 'Basic',
            'analysis_id': analysis_id
        }
    }
    
    # 创建报告目录（如果不存在）
    Path(app.config['REPORTS_FOLDER']).mkdir(parents=True, exist_ok=True)
    
    # 保存基础报告
    report_path = os.path.join(app.config['REPORTS_FOLDER'], f"report_{analysis_id}.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    result['report_file'] = f"report_{analysis_id}.json"
    
    # 保存增强报告（如果有）
    if enhanced_report:
        try:
            enhanced_report_path = os.path.join(app.config['REPORTS_FOLDER'], f"enhanced_report_{analysis_id}.json")
            with open(enhanced_report_path, 'w', encoding='utf-8') as f:
                json.dump(enhanced_report, f, ensure_ascii=False, indent=2)
            result['enhanced_report_file'] = f"enhanced_report_{analysis_id}.json"
            print(f"✅ 增强报告已保存: {enhanced_report_path}")
        except Exception as e:
            print(f"⚠️  保存增强报告失败: {e}")
    
    return result

@app.route('/report/<report_id>')
def view_report(report_id):
    """查看详细报告页面"""
    report_file = f"report_{report_id}.json"
    report_path = os.path.join(app.config['REPORTS_FOLDER'], report_file)
    
    if not os.path.exists(report_path):
        return "报告未找到", 404
    
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        return render_template('report.html', report=report_data, report_id=report_id)
        
    except Exception as e:
        return f"读取报告时发生错误: {e}", 500

@app.route('/download/<report_id>')
def download_report(report_id):
    """下载报告"""
    report_file = f"report_{report_id}.json"
    
    if not os.path.exists(os.path.join(app.config['REPORTS_FOLDER'], report_file)):
        return "报告未找到", 404
    
    return send_from_directory(app.config['REPORTS_FOLDER'], report_file, as_attachment=True)

@app.route('/static/<path:filename>')
def static_files(filename):
    """提供静态文件"""
    return send_from_directory('static', filename)

@app.route('/health')
def health_check():
    """健康检查"""
    # 确保AI系统已初始化
    ai_initialized = ensure_ai_initialized()
    
    status = {
        'status': 'healthy' if ai_initialized else 'ai_not_ready',
        'timestamp': datetime.now().isoformat(),
        'ai_systems': {
            'initialization_status': 'success' if _ai_initialized else 'failed',
            'multimodal_available': ai_system is not None,
            'basic_predictor_available': basic_predictor is not None
        }
    }
    return jsonify(status)

@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({'error': '文件太大，请选择小于16MB的图片'}), 413

@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """500错误处理"""
    return render_template('500.html'), 500

def create_templates():
    """创建HTML模板"""
    # 这个函数将在下面的文件中实现模板创建
    pass

# 在应用启动时预初始化
def setup_app():
    """设置应用"""
    print("🚀 启动胸部X光片分析Web应用")
    print("=" * 50)
    
    # 创建必要的目录
    create_directories()
    
    # 尝试预初始化AI系统（非阻塞）
    print("🔧 预初始化AI系统...")
    try:
        initialize_ai_systems()
    except Exception as e:
        print(f"⚠️  预初始化失败，将在首次请求时重试: {e}")
    
    # 创建模板文件（如果不存在）
    create_templates()
    
    print("\n🌐 Web应用配置:")
    print(f"   上传目录: {app.config['UPLOAD_FOLDER']}")
    print(f"   报告目录: {app.config['REPORTS_FOLDER']}")
    print(f"   最大文件大小: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024)}MB")
    print(f"   支持格式: {', '.join(ALLOWED_EXTENSIONS)}")
    
    print(f"\n✅ 服务器启动成功！")
    print(f"🔗 访问地址: http://localhost:5000")
    print(f"📱 移动端也支持响应式设计")
    print("\n按 Ctrl+C 停止服务器")

# Flask应用启动前的设置
setup_app()

if __name__ == '__main__':
    # 启动开发服务器
    app.run(host='0.0.0.0', port=5000, debug=True) 