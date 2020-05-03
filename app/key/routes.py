from flask import render_template, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.key import bp
from app.models import Key, Audit, Keyval, Instance, load_user
from app.key.forms import KeyForm
from datetime import datetime


lastpagelist = None
lastpagekeyval = None


@bp.route('/list/')
@login_required
def list():
    global lastpagelist

    page = request.args.get('page', lastpagelist, type=int)
    lastpagelist = page
    datalist = Key.query.paginate(page, current_app.config['ROWS_PER_PAGE_FULL'], False)
    next_url = url_for('.list', page=datalist.next_num) if datalist.has_next else None
    prev_url = url_for('.list', page=datalist.prev_num) if datalist.has_prev else None
    return render_template('key/list.html', datalist=datalist.items, next_url=next_url, prev_url=prev_url)


# adding a key to a specific bag
@bp.route('/add/<int:bag_id>', methods=["GET", "POST"])
@login_required
def add(bag_id):
    form = KeyForm()
    if request.method == 'POST' and form.validate_on_submit():
        var = Key(name=request.form['name'], desc=request.form['desc'],
                  is_active='is_active' in request.form, bag_id=request.form['bag_id'])
        db.session.add(var)
        db.session.flush()  # flush() so the id is populated after add
        writeaudit(var.id, None, str(var.to_dict()))
        writekeyvalinstances(var.id, None, True)

        db.session.commit()
        return redirect(url_for('bag.view', id=var.bag_id))
    if request.method == 'GET':
        form.bag_id.default = bag_id
        form.process()
    return render_template('key/add.html', form=form)


@bp.route('/view/<int:id>', methods=["GET", "POST"])
@login_required
def view(id):
    global lastpagekeyval

    page = request.args.get('page', lastpagekeyval, type=int)
    lastpagekeyval = page

    data_single = Key.query.filter_by(id=id).first_or_404()
    keyvallist = db.session.query(Keyval, Instance).\
        join(Instance, Instance.id == Keyval.instance_id).filter(Keyval.key_id == id).\
        add_columns(Keyval.id, Keyval.val, Keyval.is_active, Instance.name).\
        paginate(page, current_app.config['ROWS_PER_PAGE_FILTER'], False)

    next_url = url_for('.view', id=id, page=keyvallist.next_num) if keyvallist.has_next else None
    prev_url = url_for('.view', id=id, page=keyvallist.prev_num) if keyvallist.has_prev else None
    return render_template('key/view.html', datasingle=data_single, keyvallist=keyvallist.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    form = KeyForm()
    if request.method == "POST" and form.validate_on_submit():
        data_single = Key.query.filter_by(id=id).first_or_404()
        before = str(data_single.to_dict())
        data_single.name = request.form['name']
        data_single.desc = request.form['desc']
        data_single.is_active = 'is_active' in request.form

        after = str(data_single.to_dict())
        writeaudit(data_single.id, before, after)
        db.session.commit()
        return redirect(url_for('.view', id=data_single.id))

    if request.method == 'GET':
        data_single = Key.query.filter_by(id=id).first_or_404()
        form.load(data_single)
    return render_template('key/edit.html', form=form)


@bp.route('/delete/<int:id>', methods=["GET", "POST"])
@login_required
def delete(id):
    key_single = Key.query.filter_by(id=id).first_or_404()
    Key.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('bag.view', id=key_single.bag_id))


def writeaudit(parent_id, before, after):
    if before:
        change = "change"
    else:
        change = "add"
    var = Audit(model='key',
                parent_id=parent_id,
                a_datetime=datetime.now(),
                a_user_id=current_user.id,
                a_username=load_user(current_user.id).username,
                action=change,
                before=before,
                after=after
                )

    db.session.add(var)


def writekeyvalinstances(key_id, val, is_active):
    key_single = Key.query.filter_by(id=key_id).first_or_404()
    instance_list = Instance.query.filter_by(bag_id=key_single.bag_id)
    for instance in instance_list:
        var = Keyval(instance_id=instance.id,
                     key_id=key_id,
                     val=val,
                     is_active=is_active
                     )
        db.session.add(var)
