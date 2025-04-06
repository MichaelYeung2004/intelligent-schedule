# 智能课程表管理系统

本项目是一个基于 Web 的课程表管理应用，使用 Flask 作为后端，纯 HTML/CSS/JavaScript 作为前端。用户可以添加、查看、编辑、删除课程，并支持简单的用户登录/注册、课程导入导出等功能。

**技术栈**

*   **后端:** Python 3, Flask
*   **前端:** HTML, Tailwind CSS (CDN), JavaScript
*   **数据存储:** 本地 JSON 文件 (每个用户一个文件，存储在 `data/` 目录下)

**功能列表**

1.  **添加课程 (Create):** 通过模态框输入课程名称、教师、地点、星期、时间段、颜色，并保存。相同名称的课程会自动应用相同颜色。
2.  **查询课程 (Read):**
    *   在主网格视图中按时间和星期显示课程。
    *   在左侧面板显示所有课程的列表，按课程名称分组。
    *   支持通过课程名称或教师姓名进行实时搜索过滤。
3.  **修改课程 (Update):** 点击课程卡片或列表项查看详情，点击编辑按钮可在模态框中修改课程信息并保存。
4.  **删除课程 (Delete):** 在编辑模态框中，可以删除当前课程。
5.  **用户认证:**
    *   支持简单的用户名密码登录和注册。
    *   用户状态通过 Flask Session 维护。
    *   不同用户的课程数据存储在不同的 JSON 文件中 (`data/<username>.json`)。未登录用户使用 `data/guest.json`。
6.  **数据导入/导出:**
    *   **导出:** 支持将当前用户的课程表导出为 JSON 或 Excel 文件 (前端实现)。
    *   **导入:** 支持从 JSON 或 Excel 文件导入课程，导入会覆盖当前用户的课程表 (前端解析文件，后端处理数据)。
7.  **辅助功能:**
    *   **下一节课提醒:** 左侧面板显示即将到来的下一节课信息及倒计时。
    *   **今日诗词:** 左侧面板显示一句随机诗词，可刷新。
    *   **番茄钟:** 右下角提供一个可配置的番茄工作法计时器 (纯前端实现)。

**环境准备**

1.  **安装 Python 3:** 确保你的系统已安装 Python 3.6 或更高版本。
2.  **克隆仓库 (如果使用 Git):**
    ```bash
    git clone <your-repo-url>
    cd intelligent-schedule
    ```
    或者直接下载代码压缩包并解压。
3.  **创建虚拟环境 (推荐):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
4.  **安装依赖:**
    ```bash
    pip install -r requirements.txt
    ```

**运行程序**

1.  确保虚拟环境已激活。
2.  在项目根目录 (`intelligent-schedule/`) 运行 Flask 应用：
    ```bash
    python app.py
    ```
3.  程序启动后，会提示类似信息：
    ```
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: ...
    ```
4.  打开浏览器，访问 `http://127.0.0.1:5000/` 即可开始使用。

**AI 及个人实操过程**

1.  **需求分析:** 明确需要实现一个包含 CRUD 功能、图形界面、用户认证、导入导出等功能的课程表应用。前端已部分完成。
2.  **技术选型:** 选择 Python Flask 作为后端框架，因为它轻量且易于与现有前端集成。选择 JSON 文件作为数据存储，简化部署和开发初期复杂度。
3.  **后端框架搭建 (AI 辅助):** 使用 AI (如 DeepSeek/ChatGPT/Kimi) 生成 Flask 的基本应用结构，包括 `app.py` 的骨架、路由定义、`requirements.txt` 文件。
    *   *Prompt 示例:* "Create a basic Flask application structure with routes for GET /api/courses, POST /api/courses, PUT /api/courses/<id>, DELETE /api/courses/<id>. Include necessary imports and app run configuration."
4.  **数据处理逻辑 (个人实操 + AI 辅助):**
    *   设计数据存储格式 (每个用户一个 JSON 文件)。
    *   编写 `load_data()` 和 `save_data()` 函数，处理文件读写和 JSON 解析，加入基本的错误处理和数据结构验证。
    *   实现用户与数据文件的关联 (通过 Flask Session 获取 `user_id`)。AI 可帮助生成文件读写模板代码。
5.  **实现 CRUD API (个人实操 + AI 辅助):**
    *   **Create (`POST /api/courses`):** 获取请求 JSON 数据，验证，生成 ID，更新数据文件，返回结果。*AI 辅助点:* 生成请求数据解析、JSON 响应构建的代码片段。*个人思考点:* ID 生成策略、颜色同步逻辑。
    *   **Read (`GET /api/courses`):** 加载用户数据并返回。
    *   **Update (`PUT /api/courses/<id>`):** 查找对应 ID 的课程，更新数据，处理颜色同步，保存文件。*个人思考点:* 如何高效查找和更新列表中的元素，名称更改时的颜色逻辑。
    *   **Delete (`DELETE /api/courses/<id>`):** 查找并移除课程，保存文件。*AI 辅助点:* 列表元素的查找和删除方法。
6.  **实现用户认证 API (个人实操 + AI 辅助):**
    *   添加 `/api/login`, `/api/register`, `/api/logout`, `/api/status` 路由。
    *   使用 Flask Session 存储 `user_id`。*AI 辅助点:* Flask Session 的基本用法示例。*个人思考点:* 简化认证逻辑（不实际验证密码或存储用户），如何关联 session 和数据文件。
7.  **实现导入/诗词 API (个人实操 + AI 辅助):**
    *   `POST /api/courses/import`: 接收前端解析好的 JSON 数组，进行数据验证、ID 分配、颜色统一处理，覆盖保存。*个人思考点:* 导入数据的验证逻辑，ID冲突避免，颜色统一策略。
    *   `GET /api/poetry`: 从预定义的列表中随机选择并返回。
8.  **前端对接 (个人实操 + AI 调试):**
    *   **核心工作:** 将 `index.html` 中所有 `localStorage` 操作替换为对后端 API 的 `fetch` 调用。
    *   修改 `loadCourses`, `saveCourse`, `deleteCourse`, `confirmImport` 等函数。
    *   添加 `checkBackendLoginStatus` 函数，并在页面加载时调用，根据后端返回状态更新 UI。
    *   修改登录、注册、登出逻辑，使其调用后端 API 并根据结果更新 UI。
    *   修改 `fetchPoetry` 调用后端 API。
    *   *AI 辅助点:* `fetch` 的用法示例，Promise 链式调用，错误处理 (`.catch`)，调试 JS 报错信息。
9.  **测试与调试 (个人实操):**
    *   启动后端 (`python app.py`)。
    *   打开浏览器访问前端。
    *   逐一测试所有功能：添加、编辑、删除、搜索、导入（准备测试文件）、导出、登录、注册、登出、诗词刷新、下一节课显示。
    *   使用浏览器开发者工具 (F12) 查看网络请求 (Network tab) 和控制台输出 (Console tab) 来调试前后端交互问题。
10. **文档编写 (个人实操):** 撰写 README 文件，说明项目、功能、使用方法、开发过程。

**四项核心功能实现说明**

1.  **添加课程 (Create):**
    *   **前端:** 用户在 "添加新课程" 模态框中填写信息，点击 "保存"。JavaScript (`saveCourse` 函数) 收集表单数据，构建一个课程对象。
    *   **交互:** 前端使用 `fetch` 发送一个 `POST` 请求到后端的 `/api/courses` 路由，请求体中包含 JSON 格式的课程对象。
    *   **后端:** Flask 路由 (`add_course`) 接收请求，解析 JSON 数据，进行验证，为新课程生成唯一 ID，处理颜色同步逻辑，将其添加到对应用户的数据文件 (`load_data`, `save_data`)，并返回成功创建的课程对象 (包含新 ID) 和 `201 Created` 状态码。
    *   **前端:** `fetch` 成功后，调用 `loadCourses()` 重新从后端加载并刷新界面。

2.  **查询课程 (Read):**
    *   **前端:** 页面加载时或用户登录/登出后，JavaScript (`loadCourses` 函数) 被调用。
    *   **交互:** 前端使用 `fetch` 发送一个 `GET` 请求到后端的 `/api/courses` 路由。
    *   **后端:** Flask 路由 (`get_courses`) 根据当前 session 中的 `user_id` 加载对应的 JSON 数据文件 (`load_data`)，提取课程列表。
    *   **前端:** `fetch` 成功接收到课程数组后，更新全局 `courses` 变量，然后调用 `renderCoursesToSchedule()` 和 `renderCourseList()` 将数据渲染到课程表网格和左侧列表中。搜索功能是纯前端实现的，通过 `searchInput` 的 `input` 事件触发 `renderCourseList()`，并传入过滤条件。

3.  **修改课程 (Update):**
    *   **前端:** 用户点击课程卡片或列表项，弹出详情模态框。点击 "编辑"，进入编辑模态框，预填入当前课程信息。用户修改后点击 "保存"。JavaScript (`saveCourse` 函数) 收集更新后的数据。
    *   **交互:** 前端使用 `fetch` 发送一个 `PUT` 请求到后端的 `/api/courses/<course_id>` 路由 (`<course_id>` 是要修改的课程 ID)，请求体包含更新后的课程信息 JSON。
    *   **后端:** Flask 路由 (`update_course`) 接收请求，获取 `course_id` 和请求体数据。加载用户数据，查找具有该 `id` 的课程，用新数据更新该课程对象，处理颜色同步逻辑，然后保存整个数据文件 (`save_data`)。返回更新后的课程对象。
    *   **前端:** `fetch` 成功后，调用 `loadCourses()` 重新加载并刷新界面。

4.  **删除课程 (Delete):**
    *   **前端:** 用户在编辑模态框中点击 "删除" 按钮。JavaScript (`deleteCourse` 函数) 弹出确认框。
    *   **交互:** 用户确认后，前端使用 `fetch` 发送一个 `DELETE` 请求到后端的 `/api/courses/<course_id>` 路由 (`<course_id>` 是要删除的课程 ID)。
    *   **后端:** Flask 路由 (`delete_course`) 接收请求，获取 `course_id`。加载用户数据，从课程列表中移除具有该 `id` 的课程对象，然后保存更新后的数据文件 (`save_data`)。返回成功信息或 `204 No Content`。
    *   **前端:** `fetch` 成功后，调用 `loadCourses()` 重新加载并刷新界面。

**最终软件运行效果截图**

(这里需要你自己运行程序后截图，展示以下界面)

1.  **主界面截图:** 显示课程表网格、左侧面板（课程列表、下一节课、诗词等）。
    ![主界面](placeholder_main_interface.png)
2.  **添加/编辑课程模态框截图:** 显示正在添加或编辑课程的弹出窗口。
    ![添加编辑模态框](placeholder_modal_add_edit.png)
3.  **课程详情模态框截图:** 显示点击课程后弹出的详情窗口。
    ![课程详情模态框](placeholder_modal_detail.png)
4.  **登录/注册模态框截图:** 显示登录或注册的弹出窗口。
    ![登录注册模态框](placeholder_modal_auth.png)
5.  **导入/导出操作示意截图 (可选):** 显示导入确认或触发导出的界面部分。
    ![导入导出](placeholder_import_export.png)

*(请将 `placeholder_*.png` 替换为实际截图)*

**代码仓库**

*   你可以将 `intelligent-schedule` 文件夹初始化为 Git 仓库，并将代码推送到 GitHub/Gitee。
    ```bash
    cd intelligent-schedule
    git init
    git add .
    git commit -m "Initial commit: Flask backend and integrated frontend"
    # 配置远程仓库并推送
    git remote add origin <your_github_or_gitee_repo_url>
    git push -u origin main # 或者 master
    ```
*   **仓库链接:** (请替换为你自己的链接) `https://github.com/your_username/intelligent-schedule` 或 `https://gitee.com/your_username/intelligent-schedule`