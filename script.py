
import numpy as np
from flask import Flask, request, render_template, session
import sqlite3
from flask_session import Session

# 创建Flask应用
app = Flask(__name__, static_url_path="/static", static_folder="static")
# 设置会话配置
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNATURE'] = True
app.secret_key = 'your_secret_key'  # 替换为一个真正的密钥，用于加密会话数据
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
                submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
)
conn.commit()
# 创建用户表（如果不存在）
c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                password TEXT
            )''')
conn.commit()
c.close()
conn.close()


@app.route("/")
def home():
     if 'user_id' in session:
        return render_template("index.html",form_data={})
     else:
         return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['username']
        password = request.form['password']
        # 这里可以生成一个唯一的user_id，例如使用哈希函数对用户名和时间戳等信息进行处理，简单起见，暂时使用用户名作为user_id
        user_id = username
        conn = sqlite3.connect('jcc.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (user_id, username, password) VALUES (?,?,?)", (user_id, username, password))
            conn.commit()
            print(f"用户 {username} 注册成功")
            return render_template('login.html', message="注册成功，请登录")
        except sqlite3.IntegrityError:
            print(f"用户名 {username} 已存在")
            return render_template('register.html', message="用户名已存在")
        finally:
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('jcc.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE username =? AND password =?", (username, password))
    result = c.fetchone()
    
    conn.close()
    if result:
        user_id = result[0]
        # 这里可以使用Flask的会话（session）来存储user_id，以便在其他路由中使用
        print("session:",session)
        session['user_id'] = user_id
        print("-----------------")
        init()
        print("****************")
        return render_template('index.html',form_data={})
    return render_template('login.html', message="用户名或密码错误")


@app.route("/init", methods=["POST"])
def init():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = sqlite3.connect("jcc.db")
        print(user_id)
        c = conn.cursor()
        zero_matrix = np.zeros((8, 8))
        str_x = np.array2string(zero_matrix, separator=" ")
        c.execute(
            f"""INSERT OR REPLACE INTO mat(user_id,matrix) VALUES ('{user_id}', '{str_x}')"""
        )  # 提交事务
        conn.commit()
        c.close()
        conn.close()
        form_data={}
        form_data["mat"] = zero_matrix.tolist()
        return render_template("index.html", form_data=form_data)
    else:
        #提示请先登录
        return render_template("login.html", message="请先登录")

@app.route("/submit", methods=["POST"])
def submit_form():
    user_id = session['user_id']
    nameA = request.form["usernameA"]
    nameB = request.form["usernameB"]
    nameC = request.form["usernameC"]
    nameD = request.form["usernameD"]
    nameE = request.form["usernameE"]
    nameF = request.form["usernameF"]
    nameG = request.form["usernameG"]
    nameH = request.form["usernameH"]

    opponentA = request.form["selectA"]
    opponentB = request.form["selectB"]
    opponentC = request.form["selectC"]
    opponentD = request.form["selectD"]
    opponentE = request.form["selectE"]
    opponentF = request.form["selectF"]
    opponentG = request.form["selectG"]
    opponentH = request.form["selectH"]

    homeA = bool(request.form.get("homeA"))
    homeB = bool(request.form.get("homeB"))
    homeC = bool(request.form.get("homeC"))
    homeD = bool(request.form.get("homeD"))
    homeE = bool(request.form.get("homeE"))
    homeF = bool(request.form.get("homeF"))
    homeG = bool(request.form.get("homeG"))
    homeH = bool(request.form.get("homeH"))

    isOutA = bool(request.form.get("isOutA"))
    isOutB = bool(request.form.get("isOutB"))
    isOutC = bool(request.form.get("isOutC"))
    isOutD = bool(request.form.get("isOutD"))
    isOutE = bool(request.form.get("isOutE"))
    isOutF = bool(request.form.get("isOutF"))
    isOutG = bool(request.form.get("isOutG"))
    isOutH = bool(request.form.get("isOutH"))

    # 创建数据库连接
    conn = sqlite3.connect("jcc.db")
    c = conn.cursor()
    # 获取历史矩阵
    c.execute(f"SELECT matrix FROM mat WHERE user_id = '{user_id}'")
    # c.execute(f"SELECT matrix FROM mat")
    matrix_str = c.fetchone()[0]

    str_x = (
        matrix_str.replace("\n", "")
        .replace("[", "")
        .replace("]", "")
        .replace(".", "")
        .split(" ")
    )
    list_x = list(map(int, str_x))
    mat = np.array(list_x).reshape(8, 8)

    # 计算对战矩阵
    player_map = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
    mat += 1 # 所有局数+1
    for i in range(8): #主对角线值为零
        mat[i][i] = 0
    #刚交战的值为1
    mat[0][player_map[opponentA]] = 1
    mat[1][player_map[opponentB]] = 1
    mat[2][player_map[opponentC]] = 1
    mat[3][player_map[opponentD]] = 1
    mat[4][player_map[opponentE]] = 1
    mat[5][player_map[opponentF]] = 1
    mat[6][player_map[opponentG]] = 1
    mat[7][player_map[opponentH]] = 1
    # 已出局的置为0
    if isOutA:
        mat[0] = 0
        mat[:,0]=0
    if isOutB:
        mat[1] = 0
        mat[:,1]=0
    if isOutC:
        mat[2] = 0
        mat[:,2]=0
    if isOutD:
        mat[3] = 0
        mat[:,3]=0
    if isOutE:
        mat[4] = 0
        mat[:,4]=0
    if isOutF:
        mat[5] = 0
        mat[:,5]=0
    if isOutG:
        mat[6] = 0
        mat[:,6]=0
    if isOutH:
        mat[7] = 0
        mat[:,7]=0
    update_mat = np.array2string(mat, separator=" ")
    c.execute(
        f"""INSERT OR REPLACE INTO mat(user_id,matrix) VALUES ('{user_id}', '{update_mat}')"""
    )  # 提交事务
    conn.commit()
    # conn.commit()
    conn.close()
    form_data = {}
    form_data["mat"] = mat.tolist()
    # 预测遇到每个对手的概率
    predict_result = [
        {"player_code":'A',"player_name":nameA,"top1": f"{nameA}:35%", "top2": f"{nameB}:25%", "top3": f"{nameC}:10%"},
        {"player_code":'B',"player_name":nameB,"top1": f"{nameB}:35%", "top2": f"{nameC}:25%", "top3": f"{nameD}:10%"},
        {"player_code":'C',"player_name":nameC,"top1": f"{nameC}:35%", "top2": f"{nameD}:25%", "top3": f"{nameE}:10%"},
        {"player_code":'D',"player_name":nameD,"top1": f"{nameD}:35%", "top2": f"{nameE}:25%", "top3": f"{nameF}:10%"},
        {"player_code":'E',"player_name":nameE,"top1": f"{nameE}:35%", "top2": f"{nameF}:25%", "top3": f"{nameG}:10%"},
        {"player_code":'F',"player_name":nameF,"top1": f"{nameF}:35%", "top2": f"{nameG}:25%", "top3": f"{nameH}:10%"},
        {"player_code":'G',"player_name":nameG,"top1": f"{nameG}:35%", "top2": f"{nameH}:25%", "top3": f"{nameA}:10%"},
        {"player_code":'H',"player_name":nameH,"top1": f"{nameH}:35%", "top2": f"{nameA}:25%", "top3": f"{nameB}:10%"},
   
    ]
    form_data["predict_result"] = predict_result
    return render_template("index.html", form_data=form_data)


if __name__ == "__main__":
    app.run(port=9527, debug=True)
