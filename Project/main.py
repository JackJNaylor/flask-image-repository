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


def get_image(image_id):

    post = Images.query.filter_by(imageId=image_id).first()
    if post is None:
        abort(404)
    return post


def get_order(order_id):
    post = Orders.query.filter_by(orderId=order_id).first()
    if post is None:
        abort(404)
    return post


def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = base64.b64encode(file.read())
    return blobData


@main.route('/')
@login_required
def index():
    posts = db.session.query(Images).filter(and_(Images.private == False, Images.inventory > 0))
    return render_template('index.html', posts=posts)


@main.route('/profile')
@login_required
def profile():
    posts = db.session.query(Images).filter_by(userId=current_user.id)
    sales = db.session.query(Orders).filter_by(sellerId=current_user.id)
    revenue = 0
    for sale in sales:
        revenue += sale.price
    # revenue = db.session.query(func.sum(Orders.price)).filter_by(sellerId=current_user.id)
    # revenue = sum(orders['price'])
    revenue = "${:,.2f}".format(revenue)
    return render_template('profile.html', name=current_user.name, posts=posts, revenue=revenue)


@main.route('/<int:image_id>')
@login_required
def post(image_id):
    post = get_image(image_id)
    post.data.decode('utf-8')
    return render_template('post.html', post=post)


@main.route('/image/upload', methods=('GET', 'POST'))
@login_required
def image():
    target = os.path.join(app_root, 'static/img/')
    if not os.path.isdir(target):
        os.mkdir(target)
    if request.method == 'POST':
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
            blob = convertToBinaryData(destination)
            os.remove(destination)

            new_image = Images(imageName=imageName, unitPrice=unitPrice, inventory=inventory,
                               description=description, data=blob, userId=current_user.id, private=private)
            db.session.add(new_image)
            db.session.commit()

            return redirect(url_for('main.index'))

    return render_template('create.html')


@main.route('/<int:image_id>/edit', methods=('GET', 'POST'))
@login_required
def edit(image_id):
    post = get_image(image_id)
    if current_user.id != post.userId:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
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
            image.data = post.data
            db.session.commit()
            return redirect(url_for('main.index'))

    return render_template('edit.html', post=post)


@main.route('/<int:image_id>/order', methods=('GET', 'POST'))
@login_required
def order(image_id):

    if request.method == 'POST':
        image = get_image(image_id)
        quantity = request.form.get('quantity')
        oldprice = float(quantity) * float(image.unitPrice)
        price = round(oldprice, 2)
        sellerId = image.userId

        if not quantity:
            flash('Quantity is required!')

        else:
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

    return render_template('index.html')


@main.route('/orders')
@login_required
def orders():
    posts = db.session.query(Orders).filter_by(buyerId=current_user.id)
    return render_template('orders.html', name=current_user.name, posts=posts)


@main.route('/outgoing')
@login_required
def outgoing():
    posts = db.session.query(Orders).filter_by(sellerId=current_user.id)
    return render_template('outgoing.html', name=current_user.name, posts=posts)


@main.route('/<int:order_id>/outgoing', methods=('GET', 'POST'))
@login_required
def update_status(order_id):
    post = get_order(order_id)
    if current_user.id != post.sellerId:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        status = request.form.get('status')

        if not status:
            flash('Status update is required!')
        else:
            order = db.session.query(Orders).filter(Orders.orderId == order_id).one()
            order.status = status
            db.session.commit()
            return redirect(url_for('main.outgoing'))

    return render_template('outgoing.html', post=post)

