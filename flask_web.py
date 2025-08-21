from flask import Flask, Response, request
import time
import json
from flask_cors import CORS  # 处理跨域

app = Flask(__name__)
CORS(app)  # 允许所有域名跨域访问

# 模拟一个耗时任务（如AI生成文本）
def simulate_task():
    phrases = ["正在初始化模型", "加载上下文...", "生成回答中", "优化结果", "完成！"]
    for i, phrase in enumerate(phrases):
        if i == 2:  # 在第3步模拟错误
            raise Exception("模拟错误")
        progress = int((i + 1) * 100 / len(phrases))
        yield json.dumps({"text": phrase, "progress": progress})
        time.sleep(1)

# SSE 事件流生成器
def sse_generator():
    try:
        # 1. 优先发送重连配置（单位：毫秒）
        yield "retry: 3000\n\n"  
        
        # 2. 发送任务数据
        for data in simulate_task():
            # 格式：event=自定义事件名, data=JSON数据
            yield f"event: update\ndata: {data}\n\n"
        
        # 3. 发送结束事件
        yield "event: end\ndata: 任务已完成\n\n"
    
    except Exception as e:
        # 4. 错误处理（发送错误事件）
        yield f"event: error\ndata: {str(e)}\n\n"
        # 显式结束生成器，确保连接正确关闭
        return

# SSE 路由
@app.route('/sse-stream')
def sse_stream():
    # 核心：返回事件流响应
    return Response(
        sse_generator(),
        mimetype='text/event-stream',  # 必须设置
        headers={
            'Cache-Control': 'no-cache',  # 禁用缓存
            'X-Accel-Buffering': 'no'     # 禁用Nginx缓冲
        }
    )

if __name__ == '__main__':
    app.run(port=5000, debug=True)