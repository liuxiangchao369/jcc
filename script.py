import numpy as np
from flask import Flask, request, render_template, session
import sqlite3
from flask_session import Session

# 创建Flask应用
app = Flask(__name__, static_url_path="/static", static_folder="static")
# 设置会话配置
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNATURE"] = True
app.secret_key = "your_secret_key"  # 替换为一个真正的密钥，用于加密会话数据
# 初始化会话
Session(app)
# 创建数据库连接
conn = sqlite3.connect("jcc.db")
c = conn.cursor()

# 创建表（如果不存在）
c.execute(
    """CREATE TABLE IF NOT EXISTS mat (
                user_id TEXT PRIMARY KEY,
                matrix TEXT,
                home_list TEXT,
                submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
)
conn.commit()
# 创建用户表（如果不存在）
c.execute(
    """CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                password TEXT
            )"""
)
conn.commit()
c.close()
conn.close()


@app.route("/")
def home():
    form_data = {}
    if "user_id" in session:
        user_id = session["user_id"]
        form_data["player_name"] = []
        form_data["user_id"] = user_id
        return render_template("index.html", form_data=form_data)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        # 这里可以生成一个唯一的user_id，例如使用哈希函数对用户名和时间戳等信息进行处理，简单起见，暂时使用用户名作为user_id
        user_id = username
        conn = sqlite3.connect("jcc.db")
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO users (user_id, username, password) VALUES (?,?,?)",
                (user_id, username, password),
            )
            conn.commit()
            print(f"用户 {username} 注册成功")
            return render_template("login.html", message="注册成功，请登录")
        except sqlite3.IntegrityError:
            print(f"用户名 {username} 已存在")
            return render_template("register.html", message="用户名已存在")
        finally:
            conn.close()


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    conn = sqlite3.connect("jcc.db")
    c = conn.cursor()
    c.execute(
        "SELECT user_id FROM users WHERE username =? AND password =?",
        (username, password),
    )
    result = c.fetchone()

    conn.close()
    if result:
        user_id = result[0]
        # 这里可以使用Flask的会话（session）来存储user_id，以便在其他路由中使用
        print("session:", session)
        session["user_id"] = user_id
        print("-----------------")
        return init()
        # print("****************")
        # return render_template("index.html", form_data={"player_name": []})
    return render_template("login.html", message="用户名或密码错误")


@app.route("/init", methods=["POST"])
def init():
    if "user_id" in session:
        user_id = session["user_id"]
        session["rounds"]=0
        conn = sqlite3.connect("jcc.db")
        print(user_id)
        c = conn.cursor()
        zero_matrix = np.zeros((8, 8))
        str_mat = np.array2string(zero_matrix, separator=" ")
        home_list = np.zeros((8))
        str_home = np.array2string(home_list, separator=" ")
        c.execute(
            f"""INSERT OR REPLACE INTO mat(user_id,matrix,home_list) VALUES ('{user_id}', '{str_mat}', '{str_home}')"""
        )  # 提交事务
        conn.commit()
        c.close()
        conn.close()
        form_data = {}
        form_data["mat"] = zero_matrix.tolist()
        form_data["player_name"] = []
        form_data["isOut"]=[False,False,False,False,False,False,False,False]
        return render_template("index.html", form_data=form_data)
    else:
        # 提示请先登录
        return render_template("login.html", message="请先登录")


@app.route("/submit", methods=["POST"])
def submit_form():
    user_id = session["user_id"]
    rounds = session["rounds"]
    # 创建数据库连接
    conn = sqlite3.connect("jcc.db")
    c = conn.cursor()
    # 获取历史矩阵
    c.execute(f"SELECT matrix,home_list FROM mat WHERE user_id = '{user_id}'")
    # c.execute(f"SELECT matrix FROM mat")
    matrix_str, home_list_str = c.fetchone()

    str_mat = (
        matrix_str.replace("\n", "")
        .replace("[", "")
        .replace("]", "")
        .replace(".", "")
        .split(" ")
    )
    str_mat = [item for item in str_mat if item != ""]
    list_x = list(map(int, str_mat))
    mat = np.array(list_x).reshape(8, 8)

    opponentA = request.form["selectA"]
    opponentB = request.form["selectB"]
    opponentC = request.form["selectC"]
    opponentD = request.form["selectD"]
    opponentE = request.form["selectE"]
    opponentF = request.form["selectF"]
    opponentG = request.form["selectG"]
    opponentH = request.form["selectH"]
    isOutA = bool(request.form.get("isOutA"))
    isOutB = bool(request.form.get("isOutB"))
    isOutC = bool(request.form.get("isOutC"))
    isOutD = bool(request.form.get("isOutD"))
    isOutE = bool(request.form.get("isOutE"))
    isOutF = bool(request.form.get("isOutF"))
    isOutG = bool(request.form.get("isOutG"))
    isOutH = bool(request.form.get("isOutH"))
    # 计算对战矩阵
    player_map = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
    mat += 1  # 所有局数+1
    for i in range(8):  # 主对角线值为零
        mat[i][i] = 0
    # 刚交战的值为1
    mat[0][player_map[opponentA]] = 0
    mat[1][player_map[opponentB]] = 0
    mat[2][player_map[opponentC]] = 0
    mat[3][player_map[opponentD]] = 0
    mat[4][player_map[opponentE]] = 0
    mat[5][player_map[opponentF]] = 0
    mat[6][player_map[opponentG]] = 0
    mat[7][player_map[opponentH]] = 0
    # 已出局的置为0
    players = 8
    if isOutA:
        mat[0] = 0
        mat[:, 0] = 0
        players -= 1
    if isOutB:
        mat[1] = 0
        mat[:, 1] = 0
        players -= 1
    if isOutC:
        mat[2] = 0
        mat[:, 2] = 0
        players -= 1
    if isOutD:
        mat[3] = 0
        mat[:, 3] = 0
        players -= 1
    if isOutE:
        mat[4] = 0
        mat[:, 4] = 0
        players -= 1
    if isOutF:
        mat[5] = 0
        mat[:, 5] = 0
        players -= 1
    if isOutG:
        mat[6] = 0
        mat[:, 6] = 0
        players -= 1
    if isOutH:
        mat[7] = 0
        mat[:, 7] = 0
        players -= 1
    update_mat = np.array2string(mat, separator=" ")
    # 计算主场列表
    homeA = bool(request.form.get("homeA"))
    homeB = bool(request.form.get("homeB"))
    homeC = bool(request.form.get("homeC"))
    homeD = bool(request.form.get("homeD"))
    homeE = bool(request.form.get("homeE"))
    homeF = bool(request.form.get("homeF"))
    homeG = bool(request.form.get("homeG"))
    homeH = bool(request.form.get("homeH"))
    str_home_list = (
        home_list_str.replace("[", "").replace("]", "")
        # .replace(" ", "")
        .replace(".", "")
    )

    home_list = str_home_list.split(" ")

    home_list = [item for item in home_list if item != ""]
    home_list = list(map(int, home_list))
    home_list = np.array(home_list)
    home_list[0] += 1 if homeA else -1
    home_list[1] += 1 if homeB else -1
    home_list[2] += 1 if homeC else -1
    home_list[3] += 1 if homeD else -1
    home_list[4] += 1 if homeE else -1
    home_list[5] += 1 if homeF else -1
    home_list[6] += 1 if homeG else -1
    home_list[7] += 1 if homeH else -1

    str_home = np.array2string(home_list, separator=" ")
    c.execute(
        f"""INSERT OR REPLACE INTO mat(user_id,matrix,home_list) VALUES ('{user_id}', '{update_mat}','{str_home}')"""
    )  # 提交事务
    conn.commit()

    conn.close()
    form_data = {}
    form_data["mat"] = mat.tolist()
    nameA = request.form["usernameA"]
    nameB = request.form["usernameB"]
    nameC = request.form["usernameC"]
    nameD = request.form["usernameD"]
    nameE = request.form["usernameE"]
    nameF = request.form["usernameF"]
    nameG = request.form["usernameG"]
    nameH = request.form["usernameH"]

    player_name_map = {
        0: nameA,
        1: nameB,
        2: nameC,
        3: nameD,
        4: nameE,
        5: nameF,
        6: nameG,
        7: nameH,
    }
    # 预测遇到每个对手的概率
    predict_result = calculate_probability(
        mat=mat, home_list=home_list, player_name_map=player_name_map,players=players,rounds=0
    ) 
    form_data["predict_result"] = predict_result
    form_data["player_name"] = [nameA, nameB, nameC, nameD, nameE, nameF, nameG, nameH]    
    session["rounds"]=rounds+1
    form_data["rounds"] = rounds
    form_data["isOut"]=[isOutA, isOutB, isOutC, isOutD, isOutE, isOutF, isOutG, isOutH]
    return render_template("index.html", form_data=form_data)


# 根据mat和home_list计算对战概率
def calculate_probability(mat, home_list, player_name_map,rounds,players=8) -> list:
    """
    :param mat: 对战局数矩阵 关于主对角线对称
    :param home_list: 主客场列表 主场+1，客场-1 连续主场连续+1，连续客场连续-1
    :param player_name_map: 玩家编号与玩家名字的映射
    :param players: 剩余玩家数量
    :param rounds:当前轮数
    :return: 对战概率列表8* {
            "player_code": "H",
            "player_name": "玩家名字",
            "top1": f"{nameH}:35%",
            "top2": f"{nameA}:25%",
            "top3": f"{nameB}:10%",
        }
    """
    player_code_map={
        0:"A",
        1:"B",
        2:"C",
        3:"D",
        4:"E",
        5:"F",
        6:"G",
        7:"H"
    }
    zero_threshold = (players - 1) // 2
    probability = []
    # 概率由两部分度量，1.对战局数值越大，概率越高 2.主客场差距越大，概率越高
    mat_score = mat.astype(float)
    home_score = []
    for i in range(8):
        score = []
        for j in range(8):
            score.append(abs(float(home_list[i] - home_list[j])))
        home_score.append(score)
    # 组合mat_score和home_score
    for i in range(8):
        for j in range(8):
            if mat_score[i][j] <= zero_threshold and rounds>3:
                mat_score[i][j] = 0
            else:
                mat_score[i][j] = mat_score[i][j] + 2 * home_score[i][j] / (home_score[i][j] + 1 )
    # print(mat_score)
    # 构造返回结果probability
    row_sums = mat_score.sum(axis=1)
    ratios = mat_score / row_sums[:, np.newaxis]
    # 每行最大三个值的索引
    top3_indices = np.argsort(ratios, axis=1)[:, -3:]
    # 每行最大的三个值
    top3_values = np.sort(ratios, axis=1)[:, -3:]
    for i in range(8):
        res={
            "player_code": f"{player_code_map[i]}",
            "player_name": f"{player_name_map[i]}",
            "top1": f"{player_name_map[top3_indices[i][2]]}:{round(top3_values[i][2]*100,2)}%",
            "top2": f"{player_name_map[top3_indices[i][1]]}:{round(top3_values[i][1]*100,2)}%",
            "top3": f"{player_name_map[top3_indices[i][0]]}:{round(top3_values[i][0]*100,2)}%"
        }
        probability.append(res)
    return probability


if __name__ == "__main__":
    app.run(port=9527, debug=True)
