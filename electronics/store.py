from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from electronics.auth import login_required
from electronics.db import get_db

bp = Blueprint('store', __name__)


@bp.route('/')
def index():
    db = get_db()
    product = db.execute(
        'SELECT p.id, product_price, product_name, product_description, product_image, created, product_id, username'
        ' FROM product p JOIN user u ON p.product_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('storefront/store.html', product=product)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        pname = request.form['product_name']
        product_description = request.form['product_description']
        product_image = request.form['product_image']
        product_price = request.form['product_price']
        error = None

        if not pname:
            error = 'Product name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO product (product_id,product_price,product_name, product_description, product_image)'
                ' VALUES (?, ?, ?,?, ?)',
                (pname, product_description, product_image, product_price, g.user['id'])
            )
            db.commit()
            return redirect(url_for('store.index'))

    return render_template('storefront/create.html')


def get_product(id, check_product=True):
    product = get_db().execute(
        'SELECT p.id, product_name, product_description, created, product_id, username'
        ' FROM post p JOIN user u ON p.product_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if product is None:
        abort(404, f"Product id {id} doesn't exist.")

    if check_product and product['product_id'] != g.user['id']:
        abort(403)

    return product


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_product(id)

    if request.method == 'POST':
        product_name = request.form['product_name']
        product_description = request.form['product_description']
        error = None

        if not product_name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET product_name = ?, product_description = ?'
                ' WHERE id = ?',
                (product_name, product_description, id)
            )
            db.commit()
            return redirect(url_for('storefront.index'))

    return render_template('storefront/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_product(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('storefront.index'))
