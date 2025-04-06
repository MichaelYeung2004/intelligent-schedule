import os
import json
import time
import random
from flask import Flask, request, jsonify, render_template, session

# --- 配置 ---
app = Flask(__name__, template_folder='templates')
# !!! 重要: 在生产环境中请使用更安全的随机密钥 !!!
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_and_random_key_for_dev')
# 设置 Session 的 cookie 属性，增强安全性
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax', # 或 'Strict'
    # SESSION_COOKIE_SECURE=True,  # 仅在 HTTPS 环境下启用
)

DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 诗词数据 (来自前端)
poetryDatabase = [
    { "content": "人生得意须尽欢，莫使金樽空对月。", "author": "李白《将进酒》" },
    { "content": "会当凌绝顶，一览众山小。", "author": "杜甫《望岳》" },
    { "content": "海上生明月，天涯共此时。", "author": "张九龄《望月怀远》" },
    { "content": "春风又绿江南岸，明月何时照我还。", "author": "王安石《泊船瓜洲》" },
    { "content": "落霞与孤鹜齐飞，秋水共长天一色。", "author": "王勃《滕王阁序》" },
    # ... (可以添加更多诗词)
]

# --- 数据处理函数 ---
def get_user_data_path():
    """获取当前用户的数据文件路径"""
    user_id = session.get('user_id', 'guest') # 默认为 'guest'
    # 基本的文件名清理，防止路径遍历
    safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ('_', '-')).rstrip()
    if not safe_user_id: # 如果清理后为空，则使用 guest
        safe_user_id = 'guest'
    return os.path.join(DATA_DIR, f"{safe_user_id}.json")

def load_data():
    """加载当前用户的数据"""
    path = get_user_data_path()
    if not os.path.exists(path):
        return {'courses': []} # 返回默认结构
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 确保返回的数据总是有 'courses' 键，且是列表
            if 'courses' not in data or not isinstance(data['courses'], list):
                return {'courses': []}
            # 确保每个课程都有必要的字段 (基本验证)
            valid_courses = []
            for course in data['courses']:
                if isinstance(course, dict) and all(k in course for k in ('id', 'name', 'day', 'time', 'color')):
                    valid_courses.append(course)
                else:
                    print(f"Warning: Skipping invalid course data for user '{session.get('user_id', 'guest')}': {course}")
            return {'courses': valid_courses}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading data from {path}: {e}")
        return {'courses': []} # 出错时返回空

def save_data(data):
    """保存当前用户的数据"""
    path = get_user_data_path()
    try:
        # 确保 data 包含 'courses' 键
        if 'courses' not in data or not isinstance(data['courses'], list):
            print(f"Error: Invalid data structure passed to save_data for user '{session.get('user_id', 'guest')}'. Aborting save.")
            return False # 表示保存失败
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True # 表示保存成功
    except IOError as e:
        print(f"Error saving data to {path}: {e}")
        return False # 表示保存失败

# --- 路由 ---

# 1. 根路由 - 提供前端页面
@app.route('/')
def index():
    """渲染主页面"""
    return render_template('index.html')

# 2. API - 获取当前用户状态
@app.route('/api/status', methods=['GET'])
def get_status():
    """检查用户登录状态"""
    user_id = session.get('user_id')
    if user_id:
        return jsonify({'user': {'username': user_id, 'initial': user_id[0].upper()}})
    else:
        return jsonify({'user': None})

# 3. API - 登录
@app.route('/api/login', methods=['POST'])
def login():
    """处理用户登录"""
    data = request.json
    username = data.get('username')
    password = data.get('password') # 实际应用中需要验证密码

    if not username or not password:
        return jsonify({'error': '请输入用户名和密码'}), 400

    # --- 简化版登录逻辑 ---
    # 在实际应用中，这里应该查询数据库并验证密码哈希值
    print(f"Login attempt for user: {username}") # 打印日志
    session['user_id'] = username # 登录成功，设置 session
    return jsonify({'username': username, 'initial': username[0].upper()})

# 4. API - 注册
@app.route('/api/register', methods=['POST'])
def register():
    """处理用户注册"""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': '请填写所有注册信息'}), 400
    if len(password) < 6:
         return jsonify({'error': '密码长度不能少于6位'}), 400

    # --- 简化版注册逻辑 ---
    # 实际应用中：检查用户名/邮箱是否已存在，哈希密码，存储用户信息
    print(f"Registration attempt: username={username}, email={email}") # 打印日志

    # 注册成功后直接登录
    session['user_id'] = username
    return jsonify({'username': username, 'initial': username[0].upper()}), 201 # 返回 201 Created

# 5. API - 登出
@app.route('/api/logout', methods=['POST'])
def logout():
    """处理用户登出"""
    user_id = session.pop('user_id', None) # 从 session 移除 user_id
    print(f"User logged out: {user_id}")
    return jsonify({'message': '登出成功'})

# 6. API - 获取课程 (Read)
@app.route('/api/courses', methods=['GET'])
def get_courses():
    """获取当前用户的所有课程"""
    user_data = load_data()
    return jsonify(user_data.get('courses', [])) # 确保总返回列表

# 7. API - 添加课程 (Create)
@app.route('/api/courses', methods=['POST'])
def add_course():
    """添加新课程"""
    new_course_data = request.json
    if not new_course_data or not all(k in new_course_data for k in ('name', 'teacher', 'location', 'day', 'time', 'color')):
        return jsonify({'error': '缺少课程信息'}), 400

    user_data = load_data()
    courses = user_data.get('courses', [])

    # 为新课程分配唯一 ID (使用时间戳 + 随机数避免快速点击冲突)
    new_course_data['id'] = int(time.time() * 1000) + random.randint(0, 999)

    # 检查颜色逻辑：如果新课程名已存在，使用已存在的颜色
    existing_color = None
    for course in courses:
        if course.get('name') == new_course_data['name'] and course.get('color'):
            existing_color = course.get('color')
            break
    if existing_color:
        new_course_data['color'] = existing_color
    # 如果新课程名不存在，但有其他同名课程需要更新颜色，则一起更新
    elif 'color' in new_course_data:
        target_color = new_course_data['color']
        for course in courses:
            if course.get('name') == new_course_data['name']:
                course['color'] = target_color


    courses.append(new_course_data)
    user_data['courses'] = courses # 更新回字典

    if save_data(user_data):
        return jsonify(new_course_data), 201 # 返回新创建的课程和 201状态码
    else:
        return jsonify({'error': '保存课程失败'}), 500

# 8. API - 修改课程 (Update)
@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """修改指定 ID 的课程"""
    update_data = request.json
    if not update_data:
        return jsonify({'error': '缺少更新数据'}), 400

    user_data = load_data()
    courses = user_data.get('courses', [])
    target_course = None
    original_name = None
    target_index = -1

    for i, course in enumerate(courses):
        if course.get('id') == course_id:
            target_course = course
            original_name = course.get('name')
            target_index = i
            break

    if target_course is None:
        return jsonify({'error': '课程未找到'}), 404

    # 更新字段
    target_course.update(update_data)
    # 确保 ID 不变
    target_course['id'] = course_id

    # 颜色同步逻辑: 如果课程名称改变，则不强制同步；如果名称不变，则将此颜色应用到所有同名课程
    if target_course.get('name') == original_name and 'color' in update_data:
        new_color = update_data['color']
        for course in courses:
            if course.get('name') == original_name:
                course['color'] = new_color
    # 如果课程名称改变，检查新名称是否已有颜色，有则使用，无则使用提交的颜色
    elif target_course.get('name') != original_name:
        new_name = target_course.get('name')
        existing_color_for_new_name = None
        for course in courses:
             # 查找其他同名课程(排除当前正在编辑的这个)
            if course.get('name') == new_name and course.get('id') != course_id and course.get('color'):
                existing_color_for_new_name = course.get('color')
                break
        if existing_color_for_new_name:
            target_course['color'] = existing_color_for_new_name
            # 同时更新其他同新名课程的颜色(如果它们之前颜色不同)
            for course in courses:
                 if course.get('name') == new_name:
                    course['color'] = existing_color_for_new_name
        # else: 使用 update_data 中提交的颜色(或者 target_course 中已有的)

    courses[target_index] = target_course # 放回列表
    user_data['courses'] = courses # 更新回字典

    if save_data(user_data):
        return jsonify(target_course)
    else:
        return jsonify({'error': '更新课程失败'}), 500

# 9. API - 删除课程 (Delete)
@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """删除指定 ID 的课程"""
    user_data = load_data()
    courses = user_data.get('courses', [])
    original_length = len(courses)

    # 使用列表推导式过滤掉要删除的课程
    courses = [course for course in courses if course.get('id') != course_id]

    if len(courses) == original_length:
        return jsonify({'error': '课程未找到'}), 404

    user_data['courses'] = courses # 更新回字典

    if save_data(user_data):
        # 返回 204 No Content 通常表示成功删除且无内容返回
        # 但前端可能需要一个确认信息，所以返回 200 OK + message
        return jsonify({'message': '课程删除成功'})
        # 或者 return '', 204
    else:
        return jsonify({'error': '删除课程失败'}), 500

# 10. API - 导入课程 (Create/Replace)
@app.route('/api/courses/import', methods=['POST'])
def import_courses():
    """从 JSON 数组导入课程，覆盖当前用户的所有课程"""
    imported_courses_data = request.json
    if not isinstance(imported_courses_data, list):
        return jsonify({'error': '导入数据必须是一个 JSON 数组'}), 400

    user_data = load_data() # 加载现有数据(虽然会被覆盖，但为了结构一致性)
    valid_imported_courses = []
    next_id = int(time.time() * 1000) # 起始ID
    imported_name_color_map = {} # 用于统一导入课程的颜色

    for index, item in enumerate(imported_courses_data):
        if not isinstance(item, dict):
            print(f"Import Warning: Skipping non-dict item at index {index}")
            continue

        # 基本验证 (类似前端的 isValidCourse)
        if not item.get('name') or not isinstance(item.get('day'), int) or not isinstance(item.get('time'), int):
             print(f"Import Warning: Skipping item with missing/invalid basic fields at index {index}: {item}")
             continue

        course = {
            'id': next_id,
            'name': str(item.get('name', '')).strip(),
            'teacher': str(item.get('teacher', 'N/A')).strip(),
            'location': str(item.get('location', 'N/A')).strip(),
            'day': item['day'],
            'time': item['time'],
            'color': str(item.get('color', '')).strip() # 稍后处理颜色
        }
        next_id += 1 + random.randint(0, 9) # 增加ID

        # 颜色处理: 记录每个课程名称第一次出现的颜色
        if course['name'] not in imported_name_color_map:
             # 如果导入的数据没提供有效颜色，则基于名字分配一个 (需要getOrAssignColor逻辑)
             # 简化：直接用它提供的，或者用默认
             default_colors = ['bg-red-400', 'bg-blue-400', 'bg-green-400', 'bg-yellow-400', 'bg-purple-400', 'bg-pink-400', 'bg-indigo-400', 'bg-teal-400', 'bg-orange-400', 'bg-gray-400']
             valid_color = course['color'] if course['color'].startswith('bg-') and course['color'].split('-')[1].isdigit() else default_colors[len(imported_name_color_map) % len(default_colors)]
             imported_name_color_map[course['name']] = valid_color
             course['color'] = valid_color
        else:
            # 使用该名称记录的第一个颜色
            course['color'] = imported_name_color_map[course['name']]

        valid_imported_courses.append(course)

    if not valid_imported_courses:
        return jsonify({'error': '导入的文件不包含有效的课程数据'}), 400

    # 覆盖当前用户的课程列表
    user_data['courses'] = valid_imported_courses

    if save_data(user_data):
        return jsonify({'message': f'成功导入 {len(valid_imported_courses)} 门课程'})
    else:
        return jsonify({'error': '保存导入的课程失败'}), 500

# 11. API - 获取诗词
@app.route('/api/poetry', methods=['GET'])
def get_poetry():
    """随机获取一首诗词"""
    if not poetryDatabase:
        return jsonify({'error': '诗词库为空'}), 500
    poem = random.choice(poetryDatabase)
    return jsonify(poem)


# --- 运行 Flask 应用 ---
if __name__ == '__main__':
    # debug=True 只应在开发环境中使用
    # host='0.0.0.0' 允许局域网访问，如果只需要本机访问，用 '127.0.0.1'
    app.run(debug=True, host='0.0.0.0', port=5000)