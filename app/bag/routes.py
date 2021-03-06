from flask import render_template, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.bag import bp
from app.models import Bag, Audit, Instance, Key, Keyval, load_user
from app.bag.forms import BagForm
from datetime import datetime


lastpagelist = 0
instance_lastpage = 0
key_lastpage = 0


@bp.route('/list/')
@login_required
def list():
    global lastpagelist

    page = request.args.get('page', lastpagelist, type=int)
    lastpagelist = page
    datalist = Bag.query.paginate(page, current_app.config['ROWS_PER_PAGE_FULL'], False)
    next_url = url_for('.list', page=datalist.next_num) if datalist.has_next else None
    prev_url = url_for('.list', page=datalist.prev_num) if datalist.has_prev else None
    return render_template('bag/list.html', datalist=datalist.items, next_url=next_url, prev_url=prev_url)


@bp.route('/add/', methods=["GET", "POST"])
@login_required
def add():
    form = BagForm()
    if request.method == 'POST' and form.validate_on_submit():
        var = Bag(name=request.form['name'], desc=request.form['desc'], is_active='is_active' in request.form)
        db.session.add(var)
        db.session.flush()  # flush() so the id is populated after add
        writeaudit(var.id, None, str(var.to_dict()) )
        db.session.commit()
        return redirect('/bag/list')
    return render_template('bag/add.html', form=form)


@bp.route('/view/<int:id>', methods=["GET", "POST"])
@login_required
def view(id):
    global instance_lastpage
    global key_lastpage

    instancepage = request.args.get('instancepage', instance_lastpage, type=int)
    instance_lastpage = instancepage

    keypage = request.args.get('keypage', key_lastpage, type=int)
    key_lastpage = keypage

    data_single = Bag.query.filter_by(id=id).first_or_404()

    instancelist = Instance.query.filter_by(bag_id=data_single.id).paginate(instancepage,
                    current_app.config['ROWS_PER_PAGE_FILTER'], False)
    instance_next_url = url_for('.view', id=id, instancepage=instancelist.next_num,
                                keypage=keypage) if instancelist.has_next else None
    instance_prev_url = url_for('.view', id=id, instancepage=instancelist.prev_num,
                                keypage=keypage) if instancelist.has_prev else None

    keylist = Key.query.filter_by(bag_id=data_single.id).paginate(keypage,
                current_app.config['ROWS_PER_PAGE_FILTER'], False)
    key_next_url = url_for('.view', id=id, instancepage=instancepage,
                           keypage=keylist.next_num) if keylist.has_next else None
    key_prev_url = url_for('.view', id=id, instancepage=instancepage,
                           keypage=keylist.prev_num) if keylist.has_prev else None

    return render_template('bag/view.html', datasingle=data_single,
                            instancelist=instancelist.items,
                            instance_next_url=instance_next_url, instance_prev_url=instance_prev_url,
                            keylist=keylist.items,
                            key_next_url=key_next_url, key_prev_url=key_prev_url)


@bp.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    form = BagForm()
    if request.method == "POST" and form.validate_on_submit():
        data_single = Bag.query.filter_by(id=id).first_or_404()
        before = str(data_single.to_dict())
        data_single.name = request.form['name']
        data_single.desc = request.form['desc']
        data_single.is_active = 'is_active' in request.form

        after = str(data_single.to_dict())
        writeaudit(data_single.id, before, after)
        db.session.commit()
        return redirect(url_for('.view', id=data_single.id))

    if request.method == 'GET':
        data_single = Bag.query.filter_by(id=id).first_or_404()
        form.load(data_single)
    return render_template('bag/edit.html', form=form)


@bp.route('/delete/<int:id>', methods=["GET", "POST"])
@login_required
def delete(id):
    Bag.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect('/bag/list')


def writeaudit(parent_id, before, after):
    if before:
        change = "change"
    else:
        change = "add"
    var = Audit(model='bag',
                parent_id=parent_id,
                a_datetime=datetime.now(),
                a_user_id=current_user.id,
                a_username=load_user(current_user.id).username,
                action=change,
                before=before,
                after=after
                )

    db.session.add(var)
