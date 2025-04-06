import os
import json
import time
import random
from flask import Flask, request, jsonify, render_template, session
# 重新引入密码哈希功能
from werkzeug.security import generate_password_hash, check_password_hash

# --- 配置 ---
app = Flask(__name__, template_folder='templates')
# !!! 强烈建议更换一个新的、更复杂的密钥 !!!
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'another_very_secret_random_key_dev_3')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    # SESSION_COOKIE_SECURE=True, # 仅在 HTTPS 下启用
)

DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json') # 用户凭证文件路径

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- 用户数据处理函数 ---
def load_users():
    """加载用户凭证数据"""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
            return users if isinstance(users, dict) else {}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading users from {USERS_FILE}: {e}")
        return {}

def save_users(users):
    """保存用户凭证数据"""
    if not isinstance(users, dict):
         print(f"Error: Invalid data type passed to save_users. Aborting save.")
         return False
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Error saving users to {USERS_FILE}: {e}")
        return False

# --- 课程数据处理函数 (保持不变) ---
def get_user_data_path():
    user_id = session.get('user_id', 'guest')
    safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ('_', '-')).rstrip()
    if not safe_user_id:
        safe_user_id = 'guest'
    return os.path.join(DATA_DIR, f"{safe_user_id}.json")

def load_data():
    path = get_user_data_path()
    if not os.path.exists(path):
        return {'courses': []}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'courses' not in data or not isinstance(data['courses'], list):
                print(f"Warning: Invalid or missing 'courses' list in {path}. Returning empty list.")
                return {'courses': []}
            valid_courses = []
            # 稍微加强课程数据验证
            for course in data.get('courses', []):
                if isinstance(course, dict) and all(k in course for k in ('id', 'name', 'day', 'time')):
                     course.setdefault('color', 'bg-gray-400') # 提供默认值
                     course.setdefault('teacher', 'N/A')
                     course.setdefault('location', 'N/A')
                     valid_courses.append(course)
                else:
                    print(f"Warning: Skipping invalid course data for user '{session.get('user_id', 'guest')}': {course}")
            return {'courses': valid_courses}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading data from {path}: {e}")
        return {'courses': []}

def save_data(data):
    path = get_user_data_path()
    try:
        if 'courses' not in data or not isinstance(data['courses'], list):
            print(f"Error: Invalid data structure passed to save_data for user '{session.get('user_id', 'guest')}' (path: {path}). Aborting save.")
            return False
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Error saving data to {path}: {e}")
        return False

# --- 丰富的诗词数据 ---
poetryDatabase = [
    {"content": "人生得意须尽欢，莫使金樽空对月。", "author": "李白《将进酒》" },
    { "content": "会当凌绝顶，一览众山小。", "author": "杜甫《望岳》" },
    { "content": "海上生明月，天涯共此时。", "author": "张九龄《望月怀远》" },
    { "content": "春风又绿江南岸，明月何时照我还。", "author": "王安石《泊船瓜洲》" },
    { "content": "落霞与孤鹜齐飞，秋水共长天一色。", "author": "王勃《滕王阁序》" },
    { "content": "但愿人长久，千里共婵娟。", "author": "苏轼《水调歌头·明月几时有》" },
    { "content": "不识庐山真面目，只缘身在此山中。", "author": "苏轼《题西林壁》" },
    { "content": "众里寻他千百度，蓦然回首，那人却在，灯火阑珊处。", "author": "辛弃疾《青玉案·元夕》" },
    { "content": "疏影横斜水清浅，暗香浮动月黄昏。", "author": "林逋《山园小梅》" },
    { "content": "无可奈何花落去，似曾相识燕归来。", "author": "晏殊《浣溪沙·一曲新词酒一杯》" },
    { "content": "野火烧不尽，春风吹又生。", "author": "白居易《赋得古原草送别》" },
    { "content": "山重水复疑无路，柳暗花明又一村。", "author": "陆游《游山西村》" },
    { "content": "春蚕到死丝方尽，蜡炬成灰泪始干。", "author": "李商隐《无题》" },
    { "content": "明月松间照，清泉石上流。", "author": "王维《山居秋暝》" },
    { "content": "停车坐爱枫林晚，霜叶红于二月花。", "author": "杜牧《山行》" },
    { "content": "知否？知否？应是绿肥红瘦。", "author": "李清照《如梦令·昨夜雨疏风骤》" },
    { "content": "大江东去，浪淘尽，千古风流人物。", "author": "苏轼《念奴娇·赤壁怀古》" },
    { "content": "两情若是久长时，又岂在朝朝暮暮。", "author": "秦观《鹊桥仙·纤云弄巧》" },
    { "content": "衣带渐宽终不悔，为伊消得人憔悴。", "author": "柳永《蝶恋花·伫倚危楼风细细》" },
    { "content": "人生自古谁无死？留取丹心照汗青。", "author": "文天祥《过零丁洋》" },
    { "content": "花自飘零水自流。一种相思，两处闲愁。", "author": "李清照《一剪梅·红藕香残玉簟秋》" },
    { "content": "莫道不销魂，帘卷西风，人比黄花瘦。", "author": "李清照《醉花阴·薄雾浓云愁永昼》" },
    { "content": "身无彩凤双飞翼，心有灵犀一点通。", "author": "李商隐《无题》" },
    { "content": "曾经沧海难为水，除却巫山不是云。", "author": "元稹《离思五首·其四》" },
    { "content": "玲珑骰子安红豆，入骨相思知不知。", "author": "温庭筠《南歌子词二首 / 新添声杨柳枝词》" },
    { "content": "愿我如星君如月，夜夜流光相皎洁。", "author": "范成大《车遥遥篇》" },
    { "content": "只愿君心似我心，定不负相思意。", "author": "李之仪《卜算子·我住长江头》" },
    { "content": "桃之夭夭，灼灼其华。之子于归，宜其室家。", "author": "《诗经·周南·桃夭》" },
    { "content": "青青子衿，悠悠我心。纵我不往，子宁不嗣音？", "author": "《诗经·郑风·子衿》" },
    { "content": "在天愿作比翼鸟，在地愿为连理枝。", "author": "白居易《长恨歌》" },
    { "content": "自在飞花轻似梦，无边丝雨细如愁。", "author": "秦观《浣溪沙·漠漠轻寒上小楼》" },
    { "content": "人面不知何处去，桃花依旧笑春风。", "author": "崔护《题都城南庄》" },
    { "content": "相见时难别亦难，东风无力百花残。", "author": "李商隐《无题》" },
    { "content": "投我以木桃，报之以琼瑶。匪报也，永以为好也！", "author": "《诗经·卫风·木瓜》" }
]

# --- API 路由 ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    user_id = session.get('user_id')
    if user_id:
        return jsonify({'user': {'username': user_id, 'initial': user_id[0].upper()}})
    else:
        return jsonify({'user': None})

# --- 登录 API (包含密码验证) ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '请输入用户名和密码'}), 400

    users = load_users()
    user_data = users.get(username)

    if user_data is None:
        print(f"Login failed: User '{username}' not found.")
        return jsonify({'error': '用户不存在或密码错误'}), 401 # 统一返回 401

    stored_hash = user_data.get('hashed_password')
    if not stored_hash:
         print(f"Login failed: User '{username}' data is corrupted (no hash).")
         return jsonify({'error': '用户数据错误'}), 500

    if check_password_hash(stored_hash, password):
        # 密码正确
        session['user_id'] = username
        session.pop('available_poem_indices', None) # 清除旧诗词记录
        print(f"Login successful for user: {username}")
        return jsonify({'username': username, 'initial': username[0].upper()})
    else:
        # 密码错误
        print(f"Login failed: Incorrect password for user '{username}'.")
        return jsonify({'error': '用户不存在或密码错误'}), 401 # 统一返回 401

# --- 注册 API (包含密码哈希和用户存储) ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email') # 邮箱暂时只存储
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': '请填写所有注册信息'}), 400
    if len(password) < 6:
         return jsonify({'error': '密码长度不能少于6位'}), 400
    # 可以添加更多验证，如用户名格式、邮箱格式等

    users = load_users()

    if username in users:
        print(f"Registration failed: Username '{username}' already exists.")
        return jsonify({'error': '用户名已存在'}), 409 # 409 Conflict

    # 用户名可用，哈希密码并存储
    hashed_password = generate_password_hash(password)
    users[username] = {
        'hashed_password': hashed_password,
        'email': email
        # 可以添加注册时间等其他信息
        # 'registered_at': time.time()
    }

    if save_users(users):
        # 注册成功，直接登录
        session['user_id'] = username
        session.pop('available_poem_indices', None) # 清除诗词记录
        print(f"Registration successful for user: {username}")
        return jsonify({'username': username, 'initial': username[0].upper()}), 201
    else:
        # 保存用户文件失败
        print(f"Registration failed: Could not save users file.")
        return jsonify({'error': '注册失败，服务器内部错误'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    user_id = session.pop('user_id', None)
    session.pop('available_poem_indices', None) # 登出时清除诗词记录
    print(f"User logged out: {user_id}")
    return jsonify({'message': '登出成功'})

# --- 课程 API (保持不变) ---
@app.route('/api/courses', methods=['GET'])
def get_courses():
    user_data = load_data()
    return jsonify(user_data.get('courses', []))

@app.route('/api/courses', methods=['POST'])
def add_course():
    new_course_data = request.json
    if not new_course_data or not all(k in new_course_data for k in ('name', 'day', 'time', 'color')): # teacher, location can be optional
        return jsonify({'error': '缺少必要的课程信息(名称, 星期, 时间段, 颜色)'}), 400
    # 为可选字段提供默认值
    new_course_data.setdefault('teacher', 'N/A')
    new_course_data.setdefault('location', 'N/A')

    user_data = load_data()
    courses = user_data.get('courses', [])
    new_course_data['id'] = int(time.time() * 1000) + random.randint(0, 999)

    existing_color = None
    for course in courses:
        if course.get('name') == new_course_data['name'] and course.get('color'):
            existing_color = course.get('color')
            break
    if existing_color:
        new_course_data['color'] = existing_color
    else: # 如果是新名称，确保提交的颜色应用给其他同名课程（虽然此时应该没有）
        target_color = new_course_data['color']
        for course in courses:
            if course.get('name') == new_course_data['name']:
                 course['color'] = target_color

    courses.append(new_course_data)
    user_data['courses'] = courses

    if save_data(user_data):
        return jsonify(new_course_data), 201
    else:
        return jsonify({'error': '保存课程失败'}), 500

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
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

    target_course.update(update_data)
    target_course['id'] = course_id # 确保ID不变

    current_name = target_course.get('name')
    new_color = update_data.get('color', target_course.get('color')) # 获取新颜色

    # 颜色同步逻辑: 总是将当前修改的课程颜色，同步给所有同名课程
    if current_name and new_color:
        for course in courses:
            if course.get('name') == current_name:
                course['color'] = new_color

    courses[target_index] = target_course
    user_data['courses'] = courses

    if save_data(user_data):
        return jsonify(target_course)
    else:
        return jsonify({'error': '更新课程失败'}), 500


@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    user_data = load_data()
    courses = user_data.get('courses', [])
    original_length = len(courses)
    courses = [course for course in courses if course.get('id') != course_id]

    if len(courses) == original_length:
        return jsonify({'error': '课程未找到'}), 404

    user_data['courses'] = courses
    if save_data(user_data):
        return jsonify({'message': '课程删除成功'})
    else:
        return jsonify({'error': '删除课程失败'}), 500

@app.route('/api/courses/import', methods=['POST'])
def import_courses():
    imported_courses_data = request.json
    if not isinstance(imported_courses_data, list):
        return jsonify({'error': '导入数据必须是一个 JSON 数组'}), 400

    valid_imported_courses = []
    next_id = int(time.time() * 1000)
    imported_name_color_map = {}
    default_colors = ['bg-red-400', 'bg-blue-400', 'bg-green-400', 'bg-yellow-400', 'bg-purple-400', 'bg-pink-400', 'bg-indigo-400', 'bg-teal-400', 'bg-orange-400', 'bg-gray-400']

    for index, item in enumerate(imported_courses_data):
        if not isinstance(item, dict): continue
        if not item.get('name') or not isinstance(item.get('day'), int) or not isinstance(item.get('time'), int): continue

        course = {
            'id': next_id,
            'name': str(item.get('name', '')).strip(),
            'teacher': str(item.get('teacher', 'N/A')).strip(),
            'location': str(item.get('location', 'N/A')).strip(),
            'day': item['day'],
            'time': item['time'],
            'color': str(item.get('color', '')).strip()
        }
        next_id += 1 + random.randint(0, 9)

        # 改进的验证和颜色分配
        is_valid_color = course['color'].startswith('bg-') and len(course['color'].split('-')) > 1 and course['color'].split('-')[1].isdigit()

        if course['name'] not in imported_name_color_map:
            final_color = course['color'] if is_valid_color else default_colors[len(imported_name_color_map) % len(default_colors)]
            imported_name_color_map[course['name']] = final_color
            course['color'] = final_color
        else:
            course['color'] = imported_name_color_map[course['name']]

        valid_imported_courses.append(course)

    if not valid_imported_courses:
        return jsonify({'error': '导入的文件不包含有效的课程数据'}), 400

    # 用验证和处理后的课程覆盖当前用户数据
    user_data = {'courses': valid_imported_courses}

    if save_data(user_data):
        return jsonify({'message': f'成功导入 {len(valid_imported_courses)} 门课程'})
    else:
        return jsonify({'error': '保存导入的课程失败'}), 500


# --- 诗词 API (使用 session 记录状态) ---
@app.route('/api/poetry', methods=['GET'])
def get_poetry():
    if not poetryDatabase:
        return jsonify({'error': '诗词库为空'}), 500

    available_indices = session.get('available_poem_indices')

    if not available_indices: # 如果是空列表或 None
        available_indices = list(range(len(poetryDatabase)))
        random.shuffle(available_indices)
        user_display = session.get('user_id', 'guest')
        print(f"用户 '{user_display}' 的诗词索引已重置/初始化。")

    # 检查列表是否真的还有内容（理论上 shuffle 后重新赋值不会为空，除非诗词库为空）
    if not available_indices:
         # 如果意外为空，可能是并发问题或 session 问题，重新生成
         available_indices = list(range(len(poetryDatabase)))
         random.shuffle(available_indices)
         print(f"警告：用户 '{session.get('user_id', 'guest')}' 的可用诗词索引意外为空，已重新生成。")
         # 即使重新生成后，如果诗词库只有0或1首，pop 可能失败
         if not available_indices:
             return jsonify(poetryDatabase[0]) if poetryDatabase else jsonify({'error': '无法获取诗词'}), 500

    chosen_index = available_indices.pop()
    poem = poetryDatabase[chosen_index]

    # 更新 session
    session['available_poem_indices'] = available_indices
    # session.modified = True # 在 Flask 中直接赋值通常不需要这句

    user_display = session.get('user_id', 'guest')
    print(f"向用户 '{user_display}' 提供诗词索引 {chosen_index}。剩余可用: {len(available_indices)}")

    return jsonify(poem)

# --- 运行 Flask 应用 ---
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000) # 生产环境建议 debug=False
