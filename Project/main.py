from flask import Flask, render_template, request, url_for, flash, redirect, Blueprint
from flask_login import login_required, current_user
from werkzeug.exceptions import abort
import os
import base64
from . import db
from .models import Images, Orders
from sqlalchemy import and_


main = Blueprint('main', __name__)
app_root = os.path.dirname(os.path.abspath(__file__))


# Get image from DB
def get_image(image_id):
    image = Images.query.filter_by(imageId=image_id).first()
    if image is None:
        abort(404)
    return image


# Get order from DB
def get_order(order_id):
    order = Orders.query.filter_by(orderId=order_id).first()
    if order is None:
        abort(404)
    return order


def convert_to_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = base64.b64encode(file.read())
    return blobData


# Routes
@main.route('/')
@login_required
def index():
    images = db.session.query(Images).filter(and_(Images.private == False, Images.inventory > 0))
    return render_template('index.html', posts=images)


@main.route('/profile')
@login_required
def profile():
    images = db.session.query(Images).filter_by(userId=current_user.id)
    sales = db.session.query(Orders).filter_by(sellerId=current_user.id)
    revenue = 0
    for sale in sales:
        revenue += sale.price
    # revenue = db.session.query(func.sum(Orders.price)).filter_by(sellerId=current_user.id)
    # revenue = sum(orders['price'])
    revenue = "${:,.2f}".format(revenue)
    return render_template('profile.html', name=current_user.name, posts=images, revenue=revenue)


@main.route('/image/<int:image_id>')
@login_required
def post(image_id):
    image = get_image(image_id)
    image.data.decode('utf-8')
    return render_template('post.html', post=image)


@main.route('/image/upload')
@login_required
def upload_page():
    return render_template('create.html')


@main.route('/edit/<int:image_id>')
@login_required
def edit_image(image_id):
    image = get_image(image_id)
    if current_user.id != image.userId:
        return redirect(url_for('main.index'))
    return render_template('edit.html', post=image)


@main.route('/orders')
@login_required
def orders():
    orders = db.session.query(Orders).filter_by(buyerId=current_user.id)
    return render_template('orders.html', name=current_user.name, posts=orders)


@main.route('/outgoing')
@login_required
def outgoing():
    outgoing_orders = db.session.query(Orders).filter_by(sellerId=current_user.id)
    return render_template('outgoing.html', name=current_user.name, posts=outgoing_orders)


# API Calls
@main.route('/api/image/upload', methods=['POST'])
@login_required
def upload():
    target = os.path.join(app_root, 'static/img/')
    if not os.path.isdir(target):
        os.mkdir(target)
    imageName = request.form.get('imageName')
    unitPrice = request.form.get('unitPrice')
    inventory = request.form.get('inventory')
    description = request.form.get('description')
    private = True if request.form.get('private') else False
    data = request.files['data']

    if not imageName:
        flash('Image Title is required!')
    elif not data:
        flash('Image is required!')
    else:
        file_name = data.filename or ''
        destination = '/'.join([target, file_name])
        data.save(destination)
        blob = convert_to_binary_data(destination)
        os.remove(destination)

        new_image = Images(imageName=imageName, unitPrice=unitPrice, inventory=inventory,
                           description=description, data=blob, userId=current_user.id, private=private)
        db.session.add(new_image)
        db.session.commit()

        return redirect(url_for('main.index'))


@main.route('/api/edit/<int:image_id>', methods=['POST'])
@login_required
def edit(image_id):
    imageName = request.form.get('imageName')
    unitPrice = request.form.get('unitPrice')
    inventory = request.form.get('inventory')
    description = request.form.get('description')
    private = True if request.form.get('private') else False

    if not imageName:
        flash('Image Title is required!')
    else:
        image = db.session.query(Images).filter(Images.imageId == image_id).one()
        image.imageName = imageName
        image.unitPrice = unitPrice
        image.inventory = inventory
        image.description = description
        image.private = private
        db.session.commit()
        return redirect(url_for('main.index'))


@main.route('/order/<int:image_id>', methods=['POST'])
@login_required
def order(image_id):
    image = get_image(image_id)
    quantity = request.form.get('quantity')
    if not quantity:
        flash('Order Not Placed, Quantity Is Required!')
    else:
        oldprice = float(quantity) * float(image.unitPrice)
        price = round(oldprice, 2)
        sellerId = image.userId
        newImage = db.session.query(Images).filter(Images.imageId == image_id).one()
        oldInventory = newImage.inventory
        newInventory = int(oldInventory) - int(quantity)
        newImage.inventory = newInventory
        status = "Your order has been received"
        new_order = Orders(imageId=image_id, price=price, quantity=quantity,
                           sellerId=sellerId, buyerId=current_user.id, status=status)
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for('main.index'))
    return redirect(url_for('main.index'))


@main.route('/outgoing/<int:order_id>', methods=['POST'])
@login_required
def update_status(order_id):
    order = get_order(order_id)
    if current_user.id != order.sellerId:
        return redirect(url_for('main.index'))

    status = request.form.get('status')

    if not status:
        flash('Status update is required!')
    else:
        order = db.session.query(Orders).filter(Orders.orderId == order_id).one()
        order.status = status
        db.session.commit()
        return redirect(url_for('main.outgoing'))

