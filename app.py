from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 設定資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 設定圖片上傳
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# 資料表：分類
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# 資料表：商品
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    shop = db.Column(db.String(100))
    price = db.Column(db.Integer)
    image_filename = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))


@app.before_first_request
def create_tables():
    db.create_all()


# 首頁：商品列表 + 搜尋列
@app.route('/')
def index():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template("index.html", products=products, categories=categories)


# 商品搜尋
@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get("keyword", "")
    products = Product.query.filter(Product.content.contains(keyword)).all()
    return render_template("search.html", products=products, keyword=keyword)


# 商品上傳
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        content = request.form.get("content")
        shop = request.form.get("shop")
        price = request.form.get("price")
        category_id = request.form.get("category")

        img = request.files.get("image")

        filename = None
        if img:
            filename = secure_filename(img.filename)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        product = Product(
            content=content,
            shop=shop,
            price=int(price),
            image_filename=filename,
            category_id=int(category_id) if category_id else None
        )

        db.session.add(product)
        db.session.commit()

        return redirect(url_for("index"))

    categories = Category.query.all()
    return render_template("upload.html", categories=categories)


# 新增分類
@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form.get("category_name")
    if name:
        new_cat = Category(name=name)
        db.session.add(new_cat)
        db.session.commit()
    return redirect(url_for("upload"))


if __name__ == '__main__':
    app.run(debug=True)
