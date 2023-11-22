from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPDigestAuth
from .database import init_db
from .models import Stocks, Sales

db = SQLAlchemy()
auth = HTTPDigestAuth()

# Digest認証アカウント
users = {
    "aws": "test"
}

def create_app():
    app = Flask(__name__)
    app.config.from_object('flask_sample.config.Config')
    app.secret_key = 'AmazonWebServiceTest'
    init_db(app)

    return app

#Index ページ
@app.route('/')
def index():
    return "AWS"

#Digest認証、secret 返却
@app.route('/secret')
@auth.login_required
def secret():
    return "SUCCESS"

#在庫の更新、作成
@app.route('/v1/stocks', methods=['POST'])
def update_stock():

    form_name = request.form.get('name') #request.form.get amount がなければ失敗と表示
    form_amount = request.form.get('amount', 1) #入力がない時は、初期値１

    # amountが文字列で提供されたか確認
    try:
        form_amount = int(form_amount)
    except ValueError:
        return jsonify({"error": "数字だけ入力してください"}), 400
    
    # 既存登録確認
    stock = Stocks.query.filter_by(name=form_name).first()

    if stock:
    # 既に登録された場合、amount更新
        stock.amount = form_amount
    else:
        # 新しい項目追加
        stock = Stocks(name=form_name, amount=form_amount)
        db.session.add(stock)

    db.session.commit()

    return jsonify({"name": form_name, "amount": form_amount})
 
@app.route('/v1/stocks/', defaults={'name': None}, methods=['GET'])
@app.route('/v1/stocks/<string:name>', methods=['GET'])
def check_stock_detail(name):
    #name 入力がある場合、
    if name:
        stock = Stocks.query.filter_by(name=name).first()
        amount = stock.amount if stock else 0
        return jsonify({"name": name, "amount": amount})
    
    #name 入力がない場合、全体の結果を出力
    else:
        stocks = Stocks.query.order_by(Stocks.name).all()
        return jsonify([{"name": stock.name, "amount": stock.amount} for stock in stocks])

#削除
@app.route('/v1/stocks', methods=['DELETE'])
def delete_all():
    db.session.query(Stocks).delete()
    db.session.query(Sales).delete()
    db.session.commit()
    return jsonify({"All DB have been deleted."})

#販売,#売り上げ
@app.route('/v1/sales', methods=["GET", "POST"])
def sales():
    if request.method == "POST":
        form_name = request.form.get('name') 
        form_amount = request.form.get('amount', 1)

        # amountが文字列で提供される場合?
        try:
            form_amount = int(form_amount)
        except ValueError:
            return jsonify({"error": "数字だけ入力してください"}), 400
        
        #販売価格入力対象の商品の価格（0より大きい数値）を指定する。 
        form_price = request.form.get('price')

        #在庫更新
        stock = Stocks.query.filter_by(name=form_name).first()
        stock.amount -= form_amount
        db.session.add(stock)

        #amount < 0 エラー
        if stock.amount < 0:
            return jsonify({"error": "在庫が足りないです。"}), 400

        #Stocks から 製品IDを獲得
        item_id = stock.id

        #price入力
        form_price = request.form.get('price')

        #Salesテーブル更新、price 入力された時のみ、price x amount をincomeに加算する
        if form_price:
            try:
                form_price = float(form_price)
            except ValueError:
                return jsonify({"error": "価格は数字で入力してください"}), 400

            # Salesテーブル更新、price x amount をincomeに加算
            sale = Sales(
                item=item_id,
                amount=form_amount,
                price=form_price,
                income=form_amount * form_price
            )
            db.session.add(sale)
        else:
            # priceが提供されていない場合、Salesテーブルをamountとitemのみで更新
            sale = Sales(
                item=item_id,
                amount=form_amount
            )
            db.session.add(sale)

        db.session.commit()

        if form_price:
            return jsonify({"name": form_name, "amount": form_amount, "price": form_price})
        else:
            return jsonify({"name": form_name, "amount": form_amount})

    #POSTの時
    else:
        #Sales のincome を受け取る
        incomes = Sales.query.order_by(Sales.income).all()
        #incomes の全体の値を合わせる、各値にround(1)して加算
        total_income = sum([income.income for income in incomes])
        return jsonify({"selling": total_income})
    
app = create_app()
