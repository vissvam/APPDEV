from os import abort
from flask import Flask, request, render_template, request, redirect, url_for, current_app as app, session,flash
from sqlalchemy import or_
from application.models import *
from datetime import datetime,timedelta

app.secret_key = "vishnuvamseechenga"
@app.route("/")
def home():
    return render_template("home.html", content="Testing")



@app.route("/usersignup", methods=["POST","GET"])
def usersignup():
    if request.method == "POST":
        user = request.form["nm"]
        password = request.form["pw"]
        
        # Check if the user already exists in the database
        user_exists = Users.query.filter_by(username=user).first()
        if user_exists:
            message = "User already exists"
            return render_template("usersignup.html", message=message)
        
        # Insert the new user into the database
        new_user = Users(username=user, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for("userlogin"))
    else:
        return render_template("usersignup.html")
    



    
@app.route("/userlogin", methods=["POST", "GET"])
def userlogin():
    if request.method == "POST":
        user = request.form["nm"]
        password = request.form["pw"]

        user_query = Users.query.filter_by(username=user).first()
        if user_query is None:
            message = "Invalid username or password"
            return render_template("userlogin.html", message=message)

        db_password = user_query.password
        if db_password != password:
            message = "Invalid username or password"
            return render_template("userlogin.html", message=message)

        session["user"] = user  # Set user in session
        all_categories = Categories.query.all()
        print(user)
        print(session)
        return render_template("user/userhome.html", user=user,all_categories=all_categories)  # Note the updated template path

    if "user" in session:
        user = session["user"]
        print(user)
        print(session)
        return render_template("user/userhome.html", user=user,all_categories=all_categories)  # Note the updated template path

    return render_template("userlogin.html")


    
@app.route("/userhome")
def userhome():
    if "user" in session:
        user = session["user"]
        all_categories = Categories.query.all()  # Retrieve all categories from the database
        print(user)
        return render_template("user/userhome.html", user=user,all_categories=all_categories)
    else:
        print('not logged in')
        return redirect(url_for("userlogin"))
    




@app.route("/viewproducts/<int:category_id>")
def viewproducts(category_id):
    # Retrieve the category from the database based on category_id
    print(session)
    category = Categories.query.get(category_id)
    if category is None:
        flash("Category not found.", "error")
        return redirect(url_for("userhome"))

    # Get the products associated with the selected category
    products = Products.query.filter_by(C_ID=category_id).all()

    if request.method == "POST":
        # Handle the form submission to add products to the cart
        product_id = int(request.form.get("product_id"))
        quantity = int(request.form.get("quantity"))

        # Retrieve the product from the database based on product_id
        product = Products.query.get(product_id)
        if product is None:
            flash("Product not found.", "error")
        else:
            # Create a dictionary to represent the cart item
            cart_item = {
                "product_id": product.P_ID,
                "name": product.P_name,
                "price": product.price_per_unit,
                "quantity": quantity,
                "total": quantity * product.price_per_unit,
            }

            # Add the cart item to the cart (you can store the cart in the session or database)
            # For this example, we are using the session to simulate the cart
            if "cart" not in session:
                session["cart"] = []

            # Check if the item is already in the cart
            cart_index = None
            for i, item in enumerate(session["cart"]):
                if item["id"] == product_id:
                    cart_index = i
                    break

            if cart_index is not None:
                # If the item is already in the cart, update the quantity and total
                session["cart"][cart_index]["quantity"] += quantity
                session["cart"][cart_index]["total"] = session["cart"][cart_index]["quantity"] * product.price_per_unit
            else:
                # If the item is not in the cart, add it to the cart
                session["cart"].append(cart_item)

            flash("Product added to cart.", "success")

    # Get the cart items from the session
    cart_items = session.get("cart", [])

    return render_template("user/viewproducts.html", category=category, products=products, cart_items=cart_items)







@app.route("/user/categories/<int:category_id>/products/<int:product_id>/add_to_cart", methods=["POST"])
def add_to_cart(product_id,category_id):
    
    quantity = int(request.form.get("quantity", 1))

    # Retrieve the product from the database based on product_id
    product = Products.query.get(product_id)
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("userhome"))

     # Create or update the cart item in the session
    cart_items = session.get("cart", [])
    cart_index = None
    for i, item in enumerate(cart_items):
        if item["product_id"] == product_id:
            cart_index = i
            break

    if cart_index is not None:
        # If the item is already in the cart, update the quantity
        cart_items[cart_index]["quantity"] += quantity
        cart_items[cart_index]["total"] = cart_items[cart_index]["quantity"] * product.price_per_unit
    else:
        # If the item is not in the cart, add it to the cart
        cart_items.append({
            "product_id": product.P_ID,
            "name": product.P_name,
            "price": product.price_per_unit,
            "quantity": quantity,
            "total": quantity * product.price_per_unit,
        })

    # Update the cart items in the session
    session["cart"] = cart_items

    flash("Product added to cart successfully!", "success")
    print("Cart Items after adding:",cart_items)

    return redirect(url_for("viewproducts", category_id=category_id, cart_items= cart_items))






@app.route("/user/cart", methods=["GET", "POST"])
def view_cart():
    # Get the cart items from the session
    cart_items = session.get("cart", [])
    print("Cart Items in view_cart:",cart_items)
    # Calculate the total amount in the cart
    total_amount = sum(item["total"] for item in cart_items)
    
    
    return render_template("user/view_cart.html", cart_items=cart_items, total_amount=total_amount )



    


@app.route("/user/update_cart_item/<int:product_id>", methods=["POST"])
def update_cart_item(product_id):
    quantity = int(request.form.get("quantity", 1))

    # Update the cart item in the session
    cart_items = session.get("cart", [])
    for item in cart_items:
        if item["product_id"] == product_id:
            item["quantity"] = quantity
            item["total"] = quantity * item["price"]

    session["cart"] = cart_items

    flash("Cart item updated successfully!", "success")
    return redirect(url_for("view_cart"))

@app.route("/user/delete_cart_item/<int:item_id>", methods=["POST"])
def delete_cart_item(item_id):
    # Delete the cart item from the session
    cart_items = session.get("cart", [])
    for item in cart_items:
        if item["product_id"] == item_id:
            cart_items.remove(item)

    session["cart"] = cart_items

    flash("Cart item deleted successfully!", "success")
    return redirect(url_for("view_cart"))



@app.route("/user/buy_products", methods=["POST"])
def buy_products():
    if "user" not in session:
        flash("You need to log in to buy products.", "error")
        return redirect(url_for("userlogin"))

    user = Users.query.filter_by(username=session["user"]).first()
    if user is None:
        flash("User not found.", "error")
        return redirect(url_for("userlogin"))

    cart_items = session.get("cart", [])

    try:
        # Create a new order
        order = Orders(userID=user.userID)
        db.session.add(order)
        db.session.flush()

        # Create order details for each cart item
        for item in cart_items:
            product = Products.query.get(item["product_id"])
            if product is None:
                continue

            if item["quantity"] > product.remaining_quantity:
                flash(f"Insufficient quantity available for {product.P_name}.", "error")
                return redirect(url_for("view_cart"))

            # Update remaining quantity of the product
            product.remaining_quantity -= item["quantity"]

            # Create order detail
            order_detail = OrderDetails(
                orderID=order.orderID,
                productID=product.P_ID,
                quantity=item["quantity"],
                total_price=item["total"],
            )
            db.session.add(order_detail)

        # Commit the changes to the database
        db.session.commit()

        # Clear the cart by assigning an empty list to the session key
        session["cart"] = []

        flash("Order placed successfully!", "success")
        return render_template("/user/order_success.html")

    except Exception as e:
        db.session.rollback()
        flash("An error occurred while processing your order.", "error")
        return render_template("/user/order_error.html")





@app.route("/user/search_products", methods=["GET"])
def search_products():
    min_price = float(request.args.get("min_price", 0))
    max_price = float(request.args.get("max_price", float("inf")))

    # Query products based on search criteria
    products = Products.query.filter(
        Products.price_per_unit >= min_price,
        Products.price_per_unit <= max_price
    )
    
    products = products.all()
    
    return render_template("user/product_search_results.html", products=products)





@app.route("/adminsignup", methods=["POST", "GET"])
def adminsignup():
    if request.method == "POST":
        admin_username = request.form["nm"]
        admin_password = request.form["pw"]
        
        # Check if the admin already exists in the database
        admin_exists = Admin.query.filter_by(username=admin_username).first()
        if admin_exists:
            message = "Admin already exists"
            return render_template("adminsignup.html", message=message)
        
        # Insert the new admin into the database
        new_admin = Admin(username=admin_username, password=admin_password)
        db.session.add(new_admin)
        db.session.commit()
        
        return redirect(url_for("adminlogin"))
    else:
        return render_template("adminsignup.html")



@app.route("/adminlogin", methods=["POST", "GET"])
def adminlogin():
    if request.method == "POST":
        admin_username = request.form["nm"]
        admin_password = request.form["pw"]
        
        # Check if the admin exists in the database
        admin = Admin.query.filter_by(username=admin_username).first()
        if admin is None:
            # If the admin does not exist, return an error message
            message = "Invalid username or password"
            return render_template("adminlogin.html", message=message)
        
        if admin.password != admin_password:
            # If the password does not match, return an error message
            message = "Invalid username or password"
            return render_template("adminlogin.html", message=message)
        
        # If the admin credentials are valid, store the admin's username in the session
        session["admin_username"] = admin_username
        return redirect(url_for("admin"))  # Replace "admin_dashboard" with the endpoint for your admin dashboard page
    else:
        if "admin_username" in session:
            return redirect(url_for("admin"))  # Replace "admin_dashboard" with the endpoint for your admin dashboard page
        return render_template("adminlogin.html")

    




@app.route("/admin/home")
def admin():
     category = Categories.query.first()
     return render_template("admin/adminhome.html", category=category)

@app.route("/admin/categories/", methods=["GET", "POST"])
def viewcategories():
    if request.method == 'POST':
        if 'PresentCategoryName' in request.form and 'NewCategoryName' in request.form:
            oldCategoryName = request.form['PresentCategoryName']
            modifiedCategoryName = request.form['NewCategoryName']
            category_to_update = Categories.query.filter_by(C_name=oldCategoryName).first()
            if category_to_update:
                category_to_update.C_name = modifiedCategoryName
                db.session.commit()
        elif 'CategoryNameToDelete' in request.form:
            deleteCategoryName = request.form['CategoryNameToDelete']
            category_to_delete = Categories.query.filter_by(C_name=deleteCategoryName).first()
            if category_to_delete:
                db.session.delete(category_to_delete)
                db.session.commit()
        elif 'NewCategoryName' in request.form and request.form['NewCategoryName'].strip():
            newCategoryName = request.form['NewCategoryName']
            category = Categories(C_name=newCategoryName)
            db.session.add(category)
            db.session.commit()

    all = Categories.query.all()
    return render_template("admin/viewcategories.html", all=all)

@app.route("/admin/categories/edit/<string:category>/", methods=["GET", "POST"])
def editcategory(category):
    if request.method == 'POST':
        new_category_name = request.form.get('NewCategoryName')
        category_to_update = Categories.query.filter_by(C_name=category).first()
        category_to_update.C_name = new_category_name
        db.session.commit()
        return redirect(url_for('viewcategories'))
    return render_template("admin/editcategory.html", category=category)

@app.route("/admin/categories/add/", methods=["POST"])
def addcategory():
    new_category_name = request.form['NewCategoryName']
    category = Categories(C_name=new_category_name)
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('viewcategories'))




@app.route("/admin/categories/<int:category_id>/products", methods=["GET"])
def view_category_products(category_id):
    # Retrieve the category from the database based on category_id
    category = Categories.query.get(category_id)
    if category is None:
        flash("Category not found.", "error")
        return redirect(url_for("viewcategories"))

    # Get the products associated with the selected category
    products = Products.query.filter_by(C_ID=category_id).all()

    return render_template("admin/viewproducts.html", category=category, products=products)

@app.route("/admin/editproduct/<int:product_id>", methods=["GET", "POST"])
def editproduct(product_id):
    product = Products.query.get_or_404(product_id)

    if request.method == 'POST':
        try:
            new_product_name = request.form['NewProductName']
            product.P_name = new_product_name

            # Update other product attributes similarly
            product.unit = request.form['unit']
            product.price_per_unit = request.form['price_per_unit']
            product.manf_exp_Date = request.form['manf_exp_date']
            product.avable_qunty = request.form['avable_qunty']

            db.session.commit()
            flash('Product updated successfully', 'success')
            return redirect(url_for('view_category_products', category_id=product.C_ID))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update product. Error: {}'.format(str(e)), 'danger')

    return render_template("admin/editproduct.html", product=product)



@app.route("/admin/products/delete/<int:product_id>", methods=["POST"])
def deleteproduct(product_id):
    # Fetch the product with the given product_id from the database
    product = Products.query.get_or_404(product_id)

    # Delete the product from the database
    db.session.delete(product)
    db.session.commit()

    # Redirect back to the view products page after the deletion
    return redirect(url_for('view_category_products', category_id=product.C_ID))


@app.route("/admin/addproduct", methods=["GET", "POST"])
def addproduct():
    # Get the list of categories from the database
    categories = Categories.query.all()

    # Get the list of units of measurement from the database
    units_of_measurement = uom.query.all()

    if request.method == 'POST':
        try:
            # Retrieve form data
            product_name = request.form['product_name']
            unit = request.form['unit']
            price_per_unit = request.form['price_per_unit']
            manf_exp_date = request.form['manf_exp_date']
            avable_qunty = request.form['avable_qunty']
            newUmoId = request.form['umo_id']

            # Get the category ID from the form data
            category_id = request.form.get('category_id', type=int)
            remaining_quantity = int(avable_qunty)

            # Create a new product instance with the specified category ID
            product = Products(C_ID=category_id, P_name=product_name, unit=unit, price_per_unit=price_per_unit,
                               manf_exp_Date=manf_exp_date, avable_qunty=avable_qunty, remaining_quantity=remaining_quantity,umo_id=newUmoId)

            # Add the new product to the database
            db.session.add(product)
            db.session.commit()

            flash("Product added successfully!", "success")
            return redirect(url_for('view_category_products', category_id=category_id))
        except Exception as e:
            # Handle the exception, e.g., display an error message
            flash("Error adding product. Please try again later.", "error")
            print(str(e))

    return render_template("admin/addproduct.html", categories=categories, units_of_measurement=units_of_measurement)




@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))