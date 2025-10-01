from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from database import db
from models import User, Product, ProductImage, ProductIngredient, Order, Store

backend_bp = Blueprint('backend', __name__)

@backend_bp.before_request
def require_admin():
    #   ?? ??  ?  ??
    if request.endpoint in ['backend.login', 'backend.logout']:
        return None
    
    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('backend.login'))

@backend_bp.route('/')
def dashboard():
    
    #   ?   
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    
    # ?   ???
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('backend/dashboard.html', 
                         total_products=total_products,
                         total_orders=total_orders,
                         total_users=total_users,
                         pending_orders=pending_orders,
                         recent_orders=recent_orders)

@backend_bp.route('/products')
def products():
    
    from sqlalchemy.orm import joinedload
    products = Product.query.options(
        joinedload(Product.images),
        joinedload(Product.ingredients)
    ).all()
    return render_template('backend/products.html', products=products)

@backend_bp.route('/products/create', methods=['GET', 'POST'])
def create_product():
    
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        special_price = request.form.get('special_price', 0)
        cold_price = request.form.get('cold_price', 0)
        hot_price = request.form.get('hot_price', 0)
        description = request.form.get('description')
        
        product = Product(
            name=name,
            price=price,
            special_price=special_price,
            cold_price=cold_price,
            hot_price=hot_price,
            description=description
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Operation completed', 'success')
        return redirect(url_for('backend.products'))
    
    return render_template('backend/create_product.html')

@backend_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.price = request.form.get('price')
        product.special_price = request.form.get('special_price', 0)
        product.cold_price = request.form.get('cold_price', 0)
        product.hot_price = request.form.get('hot_price', 0)
        product.description = request.form.get('description')
        product.is_active = bool(request.form.get('is_active'))
        
        db.session.commit()
        
        flash('Operation completed', 'success')
        return redirect(url_for('backend.products'))
    
    return render_template('backend/edit_product.html', product=product)

@backend_bp.route('/products/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    db.session.commit()
    
    flash('Operation completed', 'success')
    return redirect(url_for('backend.products'))

@backend_bp.route('/orders')
def orders():
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('backend/orders.html', orders=orders)

@backend_bp.route('/orders/<int:order_id>')
def order_detail(order_id):
    
    order = Order.query.get_or_404(order_id)
    return render_template('backend/order_detail.html', order=order)

@backend_bp.route('/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash('Operation completed', 'success')
    else:
        flash('Operation failed', 'error')
    
    return redirect(url_for('backend.order_detail', order_id=order_id))

@backend_bp.route('/users')
def users():
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('backend/users.html', users=users)


@backend_bp.route('/users/create', methods=['GET', 'POST'])
def create_user():
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        is_admin = bool(request.form.get('is_admin'))
        is_active = bool(request.form.get('is_active'))

        if not name or not email or not password:
            flash('Operation failed', 'error')
            return render_template('backend/create_user.html', form_data=request.form)

        if User.query.filter_by(email=email).first():
            flash('Operation failed', 'error')
            return render_template('backend/create_user.html', form_data=request.form)

        user = User(
            name=name,
            email=email,
            phone=phone,
            is_admin=is_admin,
            is_active=is_active
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Operation completed', 'success')
        return redirect(url_for('backend.users'))

    return render_template('backend/create_user.html', form_data=None)


@backend_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Operation failed', 'error')
        return redirect(url_for('backend.users'))

    if user.is_admin:
        flash('Operation failed', 'error')
        return redirect(url_for('backend.users'))

    db.session.delete(user)
    db.session.commit()

    flash('Operation completed', 'success')
    return redirect(url_for('backend.users'))


@backend_bp.route('/stores')
def stores():
    
    from sqlalchemy.orm import joinedload

    stores = Store.query.options(joinedload(Store.product)).all()
    return render_template('backend/stores.html', stores=stores)

@backend_bp.route('/stores/create', methods=['GET', 'POST'])
def create_store():
    
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    selected_product_id = None

    if request.method == 'POST':
        selected_product_id = request.form.get('product_id')
        try:
            product_id = int(selected_product_id)
        except (TypeError, ValueError):
            product_id = None

        if not product_id:
            flash('Operation failed', 'error')
            return render_template('backend/create_store.html', products=products, selected_product_id=selected_product_id)

        if not any(product.id == product_id for product in products):
            flash('Operation failed', 'error')
            return render_template('backend/create_store.html', products=products, selected_product_id=selected_product_id)

        store = Store(
            product_id=product_id,
            name=request.form.get('name'),
            description=request.form.get('description'),
            work_time=request.form.get('work_time'),
            address=request.form.get('address'),
            phone=request.form.get('phone'),
            is_active=bool(request.form.get('is_active'))
        )

        db.session.add(store)
        db.session.commit()

        flash('Operation completed', 'success')
        return redirect(url_for('backend.stores'))

    return render_template('backend/create_store.html', products=products, selected_product_id=selected_product_id)


@backend_bp.route('/stores/<int:store_id>/edit', methods=['GET', 'POST'])
def edit_store(store_id):
    
    store = Store.query.get_or_404(store_id)
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()

    if store.product and not store.product.is_active and store.product not in products:
        products.append(store.product)
        products.sort(key=lambda product: product.name)

    selected_product_id = str(store.product_id) if store.product_id else None

    if request.method == 'POST':
        selected_product_id = request.form.get('product_id')
        try:
            product_id = int(selected_product_id)
        except (TypeError, ValueError):
            product_id = None

        if not product_id:
            flash('Operation failed', 'error')
            return render_template('backend/edit_store.html', store=store, products=products, selected_product_id=selected_product_id)

        if product_id != store.product_id:
            product = Product.query.get(product_id)
            if not product or not product.is_active:
                flash('Operation failed', 'error')
                return render_template('backend/edit_store.html', store=store, products=products, selected_product_id=selected_product_id)
            store.product_id = product.id

        store.name = request.form.get('name')
        store.description = request.form.get('description')
        store.work_time = request.form.get('work_time')
        store.address = request.form.get('address')
        store.phone = request.form.get('phone')
        store.is_active = bool(request.form.get('is_active'))

        db.session.commit()

        flash('Operation completed', 'success')
        return redirect(url_for('backend.stores'))

    return render_template('backend/edit_store.html', store=store, products=products, selected_product_id=selected_product_id)


@backend_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        #    ?  ?  ?  ?  
        if email == 'admin@admin.com':
            # ?  ?     ?  ?  
            admin_user = User.query.filter_by(email='admin@admin.com').first()
            if not admin_user:
                # ?    ?  ??  ??
                admin_user = User(
                    name='Administrator',
                    email='admin@admin.com',
                    is_admin=True,
                    is_active=True
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
            
            if admin_user.check_password(password) and admin_user.is_admin:
                from flask_login import login_user
                login_user(admin_user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('backend.dashboard'))
            else:
                flash('Operation failed', 'error')
        else:
            flash('Operation failed', 'error')
    
    return render_template('backend/login.html')

@backend_bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    flash('Information', 'info')
    return redirect(url_for('backend.login'))






