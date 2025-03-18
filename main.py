from flask import Flask, render_template, request, redirect,flash, session, url_for
from functools import wraps
from database import conn, cur 
from datetime import datetime
from flask_bcrypt import Bcrypt

app=Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'ferfe565sdsewgew'

# cur.execute("CREATE TABLE IF NOT EXISTS products(id SERIAL PRIMARY KEY, prduct_name VARCHAR(100), buying_price NUMERIC(14,2),selling_price NUMERIC(14,2), stock_quantity INTEGER);")

# cur.execute ("CREATE TABLE IF NOT EXISTS sales (id SERIAL PRIMARY KEY, pid INTEGER REFERENCES products(id), quantity INTEGER NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")

# conn.commit()

def login_required(f):
    @wraps(f)
    def protected(*args, **kwargs):
        if 'email' not in session:
            flash('You must first log in')
            next_url = request.url  # Store the requested URL
            return redirect(url_for('login', next=next_url))  # Pass next_url
        return f(*args, **kwargs)
    return protected



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
@login_required
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

@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    if request.method=="GET":
        cur.execute("SELECT * FROM PURCHASES ORDER BY purchase_date DESC")
        expenses=cur.fetchall()
        return render_template("expenses.html", expenses=expenses)
    else:
        expense_category = request.form["expense_category"] 
        description = request.form["description"]
        amount = int(request.form["amount"]) 

        query_create_expense="INSERT INTO purchases(expense_category, description, amount, purchase_date)"\
                        "VALUES('{}','{}',{}, now())".format(expense_category,description,amount)
        cur.execute(query_create_expense)
        conn.commit()
        return redirect("/expenses")

   
@app.route("/stock", methods=["GET", "POST"])
@login_required
def stock():
    if request.method=="GET":
        cur.execute("SELECT stock.stock_id, products.name, stock.quantity, stock.stock_in_date FROM stock join products on products.id=stock.pid")
        stock=cur.fetchall()
        cur.execute("SELECT * FROM products ORDER BY name ASC")
        products=cur.fetchall()
        return render_template("stock.html", stock=stock, products=products)
    else:
        pid=request.form["pid"]
        quantity=request.form["quantity"]
        query_update_stock="INSERT INTO stock(quantity, pid,stock_in_date)"\
                            "VALUES({},{},now())".format(quantity,pid)
        cur.execute(query_update_stock)
        conn.commit()
        return redirect("/stock")

@app.route("/sales", methods=["GET","POST"])
@login_required
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
@login_required
def dashboard():
    # query_sales_per_product = "SELECT products.name as product_name, SUM(sales.quantity*products.selling_price) as total_sales FROM sales JOIN products on products.id=sales.pid GROUP BY products.name"
    today_query_sales_per_product = "SELECT products.name as product_name, SUM(sales.quantity*products.selling_price) as total_sales FROM sales JOIN products on products.id=sales.pid WHERE cast(created_at as DATE) = CURRENT_DATE GROUP BY products.name"
    # query_profit_per_product = "SELECT products.name as product_name, SUM(sales.quantity*(products.selling_price - products.buying_price )) as total_profit FROM sales JOIN products on products.id=sales.pid GROUP BY products.name"
    today_query_profit_per_product = "SELECT products.name as product_name, SUM(sales.quantity*(products.selling_price - products.buying_price )) as total_profit FROM sales JOIN products on products.id=sales.pid WHERE cast(created_at as DATE) = CURRENT_DATE GROUP BY products.name"
    query_today_profit= "SELECT COALESCE(SUM(sales.quantity*(products.selling_price - products.buying_price )),0) as total_profit FROM sales JOIN products on products.id=sales.pid WHERE cast(created_at as DATE) = CURRENT_DATE"
    query_today_expenses="select COALESCE(sum(amount),0) from purchases where  cast(purchase_date as DATE) = CURRENT_DATE"

    cur.execute(query_today_profit)
    todayprofit = cur.fetchone()
    tprofit=int(todayprofit[0])     


    cur.execute(query_today_expenses)
    todayexpenses= cur.fetchone()
    texpenses=int(todayexpenses[0])

    todaynetprofit = tprofit - texpenses
    

    # cur.execute(query_profit_per_product)
    cur.execute(today_query_profit_per_product)
    profit = cur.fetchall()
    # cur.execute(query_sales_per_product)
    cur.execute(today_query_sales_per_product)
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
    return render_template("dashboard.html", x=x, y=y, a=a, b=b, tprofit=tprofit, texpenses=texpenses, todaynetprofit=todaynetprofit)  

@app.route("/update-products", methods=["POST"])
@login_required
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

        query_email_exists = "SELECT user_id FROM users WHERE email='{}'".format(email)
        cur.execute(query_email_exists)
        user = cur.fetchone()

        print(f'{user} is the user')        

        if user is not None:
            flash ('Email exists!')
            return render_template('/register.html')
        
        else:
            hash_password=bcrypt.generate_password_hash(password).decode('utf-8')

            new_user_query ="INSERT INTO users(full_name,email,password)"\
                            "VALUES('{}', '{}', '{}')".format(fullName,email, hash_password)
            
            print(f'{hash_password} is the hashed password')
            
            cur.execute(new_user_query)
            conn.commit()

            return redirect('/login')
    else:
        return render_template('/register.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():    
    next_url = request.args.get('next')  # Get next URL if provided
    print("---------tdtstgssh---", next_url)
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
       
        cur.execute("select user_id from users where email='{}'".format(email))
        email_exists = cur.fetchone()
  
        if  email_exists is None:            
            flash('Email does not exist. Please register.')
            return redirect("/login")
        else:
            cur.execute("select password from users where email = '{}'".format(email))
            saved_hashed = cur.fetchone()[0]
            pass_bool = bcrypt.check_password_hash(saved_hashed, password)
            
            if pass_bool == False:
                flash("Invalid Credentials")
                return redirect("/login")
            else:
                print("-----ssdd--sdd--", request.form["next_url"])
                next_url = request.form["next_url"]
                session['email'] =email
                if next_url == "None":
                    return redirect("/dashboard")
                else:
                    url = "/"+next_url.split('/')[-1]
                    return redirect(url)
    return render_template("login.html", next_url=next_url)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')

# def logout():
#     session.clear()
#     return redirect("/login")

if __name__ == '__main__':        
    app.run(debug=True)