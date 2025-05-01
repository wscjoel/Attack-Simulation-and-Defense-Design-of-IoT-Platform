# server.py
from flask import Flask, request, redirect, send_from_directory, url_for

app = Flask(__name__, static_folder='.', static_url_path='')

# 默认把根路径和任何不存在的文件都映射到 login.html
@app.route('/', defaults={'path':'login.html'})
@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('.', path)

# 接收 POST /login
@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('username')
    pwd  = request.form.get('password')
    # 只有正确才放行到本地仪表盘
    if user == 'iot123' and pwd == 'iot321':
        return redirect('/dashnewv10.html')
    # 失败则回到登录页
    return redirect(url_for('static_file', path='login.html') + '?error=1')

if __name__ == '__main__':
    # 以调试模式启动，监听所有接口
    app.run(host='0.0.0.0', port=8080, debug=True)

# if __name__ == '__main__':
#     app.run(
#         host='0.0.0.0',
#         port=8443,
#         debug=True,
#         ssl_context=('./ssl/iot-dash.crt',
#                      './ssl/iot-dash.key')
#     )
