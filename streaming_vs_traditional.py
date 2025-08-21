from flask import Flask, Response, jsonify
import time
import json

app = Flask(__name__)

# 传统方式：一次性传输
@app.route('/traditional')
def traditional_approach():
    """一次性返回所有数据"""
    # 模拟长时间处理任务
    results = []
    for i in range(5):
        results.append(f"步骤 {i+1} 完成")
        time.sleep(1)  # 模拟处理时间
    
    # 一次性返回所有结果
    return jsonify({
        "results": results,
        "status": "completed"
    })

# 流式方式：逐步传输
@app.route('/streaming')
def streaming_approach():
    """流式返回数据"""
    def generate():
        for i in range(5):
            # 每个步骤完成后立即返回
            data = json.dumps({
                "step": f"步骤 {i+1} 完成",
                "progress": (i + 1) * 20
            })
            yield f"data: {data}\n\n"
            time.sleep(1)  # 模拟处理时间
    
    return Response(generate(), mimetype='text/plain')

# SSE流式传输
@app.route('/sse')
def sse_stream():
    """SSE流式传输"""
    def generate():
        yield "retry: 5000\n\n"  # 重连时间
        for i in range(5):
            data = json.dumps({
                "step": f"步骤 {i+1} 完成",
                "progress": (i + 1) * 20
            })
            yield f"event: update\ndata: {data}\n\n"
            time.sleep(1)
        yield "event: end\ndata: 处理完成\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(port=5001, debug=True)