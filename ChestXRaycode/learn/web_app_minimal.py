#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小版本Web应用 - 绕过复杂的AI初始化问题
仅用于测试和调试
"""

import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """简化的主页"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>胸部X光片AI分析系统 - 调试模式</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { padding: 20px; border-radius: 8px; margin: 20px 0; }
            .error { background: #ffebee; border: 1px solid #f44336; color: #c62828; }
            .info { background: #e3f2fd; border: 1px solid #2196f3; color: #1565c0; }
        </style>
    </head>
    <body>
        <h1>🏥 胸部X光片AI分析系统 - 调试模式</h1>
        
        <div class="error">
            <h3>❌ AI系统未初始化</h3>
            <p>当前运行的是最小版本，用于诊断问题。</p>
        </div>
        
        <div class="info">
            <h3>🔧 诊断步骤</h3>
            <ol>
                <li>运行诊断脚本: <code>python diagnose_issue.py</code></li>
                <li>检查模型文件: <code>ls checkpoints/best_model.pth</code></li>
                <li>安装依赖: <code>pip install -r web_requirements.txt</code></li>
                <li>训练模型: <code>python main.py train</code></li>
            </ol>
        </div>
        
        <p><a href="/health">检查系统状态</a></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """系统状态检查"""
    status = {
        'web_server': 'running',
        'ai_system': 'not_initialized',
        'diagnostic_available': os.path.exists('diagnose_issue.py'),
        'model_file_exists': os.path.exists('checkpoints/best_model.pth'),
        'message': '请运行 python diagnose_issue.py 诊断问题'
    }
    return jsonify(status)

if __name__ == '__main__':
    print("🔧 启动最小版本Web应用（调试模式）")
    print("访问: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 