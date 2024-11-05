from flask import Flask, request, render_template

app = Flask(__name__, static_url_path='/static', static_folder='static')


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/submit', methods=['POST'])
def submit_form():
    nameA = request.form['usernameA']
    nameB = request.form['usernameB']
    nameC = request.form['usernameC']
    nameD = request.form['usernameD']
    nameE = request.form['usernameE']
    nameF = request.form['usernameF']
    nameG = request.form['usernameG']
    nameH = request.form['usernameH']
    # 在这里处理表单提交的数据   
    form_data = [
        {'player_code': '玩家A', 'player_name': nameA,"top1":f"{nameB}:45%","top2":f"{nameC}:35%","top3":f"{nameD}:20%"},
        {'player_code': '玩家B', 'player_name': nameB,"top1":f"{nameA}:45%","top2":f"{nameC}:35%", "top3":f"{nameD}:20%"},
        {'player_code': '玩家C', 'player_name': nameC,"top1":f"{nameA}:45%","top2":f"{nameB}:35%", "top3":f"{nameD}:20%"},
        {'player_code': '玩家D', 'player_name': nameD,"top1":f"{nameA}:45%","top2":f"{nameB}:35%", "top3":f"{nameC}:20%"},
        {'player_code': '玩家E', 'player_name': nameE,"top1":f"{nameF}:45%","top2":f"{nameG}:35%", "top3":f"{nameH}:20%"},
        {'player_code': '玩家F', 'player_name': nameF,"top1":f"{nameE}:45%","top2":f"{nameG}:35%", "top3":f"{nameH}:20%"},
        {'player_code': '玩家G', 'player_name': nameG,"top1":f"{nameE}:45%","top2":f"{nameF}:35%", "top3":f"{nameH}:20%"},
        {'player_code': '玩家H', 'player_name': nameH,"top1":f"{nameE}:45%","top2":f"{nameF}:35%", "top3":f"{nameG}:20%"},
    ]
    return render_template('index.html', form_data=form_data)

if __name__ == '__main__':
    app.run(port=9527, debug=True)