import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()
db.init_app(app)


class Customer(db.Model):
    customer_id = db.Column(db.Integer,
                            nullable=False,
                            unique=True,
                            primary_key=True,
                            autoincrement=True)
    customer_name = db.Column(db.String, nullable=False)
    customer_password = db.Column(db.String, nullable=False)
    customer_email = db.Column(db.String, nullable=False)
    customer_phno = db.Column(db.Integer, nullable=False)
    customer_address = db.Column(db.String, nullable=False)


class Stock(db.Model):
    stock_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stock_name = db.Column(db.String, nullable=False)
    stock_description = db.Column(db.String, nullable=True)
    stock_price = db.Column(db.Integer, nullable=False)
    stock_type = db.Column(db.String, nullable=False)
    stock_image = db.Column(db.String, nullable=True)
    stock_quantity = db.Column(db.Integer, nullable=True)
    stock_per_price = db.Column(db.Integer, nullable=True)


class Buys(db.Model):
    buys_id = db.Column(db.Integer,
                        autoincrement=True,
                        nullable=False,
                        primary_key=True)
    stock_id = db.Column(db.Integer,
                         db.ForeignKey(Stock.stock_id),
                         nullable=False)
    customer_id = db.Column(db.Integer,
                            db.ForeignKey(Customer.customer_id),
                            nullable=False)
    item_quantity = db.Column(db.Integer, nullable=False)


#db.create_all() #but there's data present

try:

    @app.route("/", methods=["GET", "POST"])
    def cust_login():
        if request.method == "GET":
            return render_template("login.html")
        else:
            c_email = (request.form['c_email']).lower()
            c_password = request.form['c_password']
            #to check if email esists in db
            user_logged_in = db.session.query(Customer).filter(
                Customer.customer_email == c_email).first()
            #print(user_logged_in)
            if user_logged_in:
                #print(user_logged_in)
                if (user_logged_in.customer_password == c_password):
                    url = "/dashboard/" + str(
                        c_email.lower())  #try to get id for path
                    return redirect(url)
                else:
                    return render_template('incorrect_pw.html',
                                           c_email=c_email)
            else:
                return render_template('email_DNE.html', c_email=c_email)
except:
    render_template("oops.html")

try:

    @app.route("/sign_up", methods=["GET", "POST"])
    def cust_sign_up():
        if request.method == 'GET':
            return render_template("sign_up.html")
        else:
            new_cust_email = (request.form['c_email']).lower()
            new_cust_password = request.form['c_password']
            new_cust_name = request.form['c_name']
            new_cust_address = request.form['c_address']
            new_cust_phno = request.form['c_phno']
            existing_user = db.session.query(Customer).filter(
                Customer.customer_email == new_cust_email).first()
            #print(existing_user)
            if existing_user is not None:
                return render_template('email_exists.html',
                                       c_email=new_cust_email)  #email exists
            else:
                new_user = Customer(
                    customer_email=new_cust_email,
                    customer_password=new_cust_password,
                    customer_name=new_cust_name,
                    customer_address=new_cust_address,
                    customer_phno=new_cust_phno)  #collect name in form
                db.session.add(new_user)
                db.session.commit()
                url = "/dashboard/" + str(new_cust_email)
                return redirect(url)
except:
    render_template("oops.html")

try:

    @app.route("/dashboard/<string:customer_email>", methods=["GET", "POST"])
    def cust_dashboard(customer_email):
        if request.method == 'GET':
            return render_template("dashboard.html",
                                   customer_email=customer_email)
        else:
            pass
except:
    render_template("oops.html")



try:

    @app.route("/<string:customer_email>", methods=["GET", "POST"])
    def cart_page(customer_email):
        if request.method == 'GET':
            cust_obj1 = Customer.query.filter_by(
                customer_email=customer_email).first(
                )  #to get only 1 record #to obtain cust_id
            buys_obj = Buys.query.filter_by(
                customer_id=cust_obj1.customer_id).all()

            if buys_obj != []:
                all_items = []
                for i in buys_obj:
                    one_item = []
                    stock_id = i.stock_id
                    print(stock_id)
                    stock_user_bought = Stock.query.filter_by(
                        stock_id=stock_id).first()
                    one_item.append(stock_user_bought.stock_name)  #0
                    one_item.append(stock_user_bought.stock_price)  #1
                    one_item.append(i.item_quantity)  #2
                    one_item.append(stock_user_bought.stock_image)  #3
                    one_item.append(stock_user_bought.stock_id)  #4
                    all_items.append(one_item)
                return render_template("cart.html",
                                       customer_email=customer_email,
                                       all_items=all_items)
            else:

                return render_template("noitems.html",
                                       customer_email=customer_email)
                # here add another page which says no items in cart
        else:
            #[to do] to checkout
            return redirect("/" + customer_email + "/checkout")

    @app.route("/<string:customer_email>/<int:stock_id>/removeitem",
               methods=["GET", "POST"])
    def remove_item(customer_email, stock_id):
        if request.method == 'GET':
            remove_this_item = Buys.query.filter_by(stock_id=stock_id).first()
            db.session.delete(remove_this_item)
            db.session.commit()
            return redirect("/" + customer_email)
except:
    render_template("oops.html")

try:

    @app.route("/<string:customer_email>/checkout", methods=["GET", "POST"])
    def checkout(customer_email):
        cust_obj = Customer.query.filter_by(
            customer_email=customer_email).first()

        custid = cust_obj.customer_id
        custobj = Customer.query.filter_by(customer_id=custid).first()
        if request.method == 'GET':

            cust_dict = {
                "cust_email": custobj.customer_email,
                "cust_name": custobj.customer_name,
                "cust_phno": custobj.customer_phno,
                "cust_address": custobj.customer_address
            }
            buys_obj = Buys.query.filter_by(customer_id=custid).all()

            buying_items = []
            for i in buys_obj:

                stockid = i.stock_id
                item = Stock.query.get(stockid)
                one_item = {
                    "stock_id": stockid,
                    "stock_name": item.stock_name,
                    "stock_price": item.stock_price,
                    "stock_quantity": i.item_quantity,
                    "stock_amount": (item.stock_price) * (i.item_quantity)
                }
                buying_items.append(one_item)
            #to calculate total
            tot = 0
            for j in buying_items:
                tot += float(j["stock_amount"])
            gst = (5 / 100) * tot
            final = gst + tot
            return render_template("checkout.html",
                                   customer_email=customer_email,
                                   buying_items=buying_items,
                                   cust_dict=cust_dict,
                                   tot=round(tot, 2),
                                   gst=round(gst, 2),
                                   final=round(final, 2))
        else:
            #remove items from buys
            delete_this_buys = Buys.query.filter_by(customer_id=custid).all()
            for d in delete_this_buys:
                dd = Buys.query.get(d.buys_id)
                db.session.delete(dd)
                db.session.commit()
            return render_template("success.html",
                                   customer_email=customer_email)
except:
    render_template("oops.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
