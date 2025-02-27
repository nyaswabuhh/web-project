from flask import Flask, render_template, request, redirect,flash

from database import conn, cur 

from datetime import datetime


app=Flask(__name__)
app.secret_key = 'ferfe sdsewgew'

@app.route("/")

def index():
    return render_template("index.html")

@app.route("/about")

def about():
    return render_template("about.html")

@app.route("/contact-us")
def contact():
    return render_template("contact.html")

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/products",  methods=["GET", "POST"])
def products():
    if request.method=="GET":

        cur.execute("SELECT * FROM products")
        product = cur.fetchall()
        # print(product)
        return render_template("products.html", product=product)
    else:
        name = request.form["name"]
        buying_price = float(request.form["buying_price"])
        selling_price = float(request.form["selling_price"])
        stock_quantity = int(request.form["stock_quantity"])
        query = "INSERT INTO products(name, buying_price, selling_price, stock_quantity)" \
                 " VALUES ('{}',{},{},{})".format(name,buying_price,selling_price,stock_quantity)
        cur.execute(query)
        conn.commit() 
        return redirect("/products")      
   

@app.route("/sales", methods=["GET","POST"])
def sales():
    if request.method=="GET":
        cur.execute("select sales.id, products.name, sales.quantity, sales.created_at from sales join products on products.id=sales.pid")
        # cur.execute("SELECT * FROM sales")
        sales = cur.fetchall()
        # print(sales)
        cur.execute("SELECT * FROM products ORDER BY name ASC")
        products=cur.fetchall()
        return render_template("sales.html", sales=sales, products=products)
    else:
        pid=request.form["pid"]
        quantity=request.form["quantity"]
        query_make_sale="INSERT INTO sales(pid,quantity,created_at)"\
                        "VALUES({}, {}, now())".format(pid,quantity)
        cur.execute(query_make_sale)
        conn.commit()
        return redirect("/sales")
        # product_id=int(request.form["product_id"])
        # quantity=float(request.form["quantity"])
        # created_at=datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        # query="INSERT INTO sales(pid,quantity,created_at)"\
        #         "VALUES({},{},{})".format(product_id,quantity,created_at)
        # cur.execute(query)
        # conn.commit()
        # return redirect("/sales")

@app.route("/dashboard")
def dashboard():
    query_sales_per_product = "SELECT products.name as product_name, SUM(sales.quantity*products.selling_price) as total_sales FROM sales JOIN products on products.id=sales.pid GROUP BY products.name"
    query_profit_per_product = "SELECT products.name as product_name, SUM(sales.quantity*(products.selling_price - products.buying_price )) as total_profit FROM sales JOIN products on products.id=sales.pid GROUP BY products.name"

    cur.execute(query_profit_per_product)
    profit = cur.fetchall()
    cur.execute(query_sales_per_product)
    sales =cur.fetchall()
    x = []
    y = []
    for i in sales:
        x.append(i[0])
        y.append(float(i[1]))
    a =[]
    b = []
    for i in profit:
        a.append(i[0])
        b.append(float(i[1]))
    return render_template("dashboard.html", x=x, y=y, a=a, b=b)  

@app.route("/update-products", methods=["POST"])
def update_products():
    id=request.form["id"]
    name = request.form["name"]
    buying_price = float(request.form["buying_price"])
    selling_price = float(request.form["selling_price"])
    stock_quantity = int(request.form["stock_quantity"])

    query= "UPDATE products SET name = '{}', buying_price={}, selling_price={}, stock_quantity={} WHERE id = {}".format(name,buying_price,selling_price,stock_quantity,id)

    cur.execute(query)
    conn.commit()

    return redirect("/products")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method =="POST":

        fullName = request.form["fullName"]
        email = request.form["email"]
        password = request.form["password"]

        new_user_query ="INSERT INTO users(full_name,email,password)"\
                        "VALUES('{}', '{}', '{}')".format(fullName,email, password)
        
        cur.execute(new_user_query)
        conn.commit()

        return redirect('/register')
    else:
        return render_template('/register.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        query_login = "SELECT user_id FROM users WHERE email='{}' and password='{}'".format(email,password)
        cur.execute(query_login)
        user=cur.fetchone()
        # if user is None:
        #     return render_template('/login.html')      
        # else:
        #     print('Log in success')
        #     return redirect('/dashboard')  
        if user:
            flash ('Log in success')
            return redirect('/dashboard')
        else:
            flash ('Invalid credentials')
            return render_template('/login.html')
    else:
     return render_template('/login.html')


app.run(debug=True)