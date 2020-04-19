from flask import render_template, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.bag import bp
from app.models import Bag, BagAudit, load_user
from app.bag.forms import BagForm
from datetime import datetime


lastpagelist = 0
lastpageaudit = 0
next_page = None


@bp.route('/list/')
@login_required
def list():
    global lastpagelist

    page = request.args.get('page', lastpagelist, type=int)
    lastpagelist = page
    datalist = Bag.query.paginate(page, current_app.config['ROWS_PER_PAGE_FULL'], False)
    next_url = url_for('.list', page=datalist.next_num) if datalist.has_next else None
    prev_url = url_for('.list', page=datalist.prev_num) if datalist.has_prev else None
    return render_template('list.html', datalist=datalist.items, next_url=next_url, prev_url=prev_url)


@bp.route('/add/', methods=["GET", "POST"])
@login_required
def add():
    form = BagForm()
    if request.method == 'POST' and form.validate_on_submit():
        var = Bag(name=request.form['name'], is_active='is_active' in request.form)
        db.session.add(var)
        db.session.flush()  # flush() so the id is populated after add
        writeaudit(var.id, str(var.to_dict()), None)
        db.session.commit()
        return redirect('/bag/list')
    return render_template('add.html', form=form)


@bp.route('/view/<int:id>', methods=["GET", "POST"])
@login_required
def view(id):
    data_single = Bag.query.filter_by(id=id).first_or_404()
    return render_template('view.html', datasingle=data_single)


@bp.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    global next_page

    form = BagForm()
    if request.method == "POST" and form.validate_on_submit():
        data_single = Bag.query.filter_by(id=id).first_or_404()
        before = str(data_single.to_dict())
        data_single.name = request.form['name']
        data_single.desc = request.form['desc']
        data_single.is_active = 'is_active' in request.form

        after = str(data_single.to_dict())
        writeaudit(data_single.id, before, after)

        return redirect(next_page)

    if request.method == 'GET':
        next_page = request.referrer
        data_single = Bag.query.filter_by(id=id).first_or_404()
        form.load(data_single)
    return render_template('edit.html', form=form, next=request.referrer)


# todo - double check delete
@bp.route('/delete/<int:id>', methods=["GET", "POST"])
@login_required
def delete(id):
    BagAudit.query.filter_by(parent_id=id).delete()
    Bag.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect('/bag/list')


@bp.route('/auditlist/<int:id>')
@login_required
def auditlist(id):
    global lastpageaudit

    page = request.args.get('page', lastpageaudit, type=int)
    lastpageaudit = page

    audit_list = BagAudit.query.\
        filter_by(parent_id=id).paginate(page, current_app.config['ROWS_PER_PAGE_FULL'], False)
    next_url = url_for('.auditlist', id=id, page=audit_list.next_num) if audit_list.has_next else None
    prev_url = url_for('.auditlist', id=id, page=audit_list.prev_num) if audit_list.has_prev else None
    return render_template('auditlist.html', parent_id=id, auditlist=audit_list.items, next_url=next_url,
                           prev_url=prev_url)


# Use to add test data to the App model.
# /bag/addtest?addcount=30 adds 30 entries
# may need to remove the @login_required
@bp.route('/addtest/', methods=["GET", "POST"])
@login_required
def addtest():
    add_count = request.args.get('addcount', 20, type=int)
    for addone in range(add_count):
        var = Bag(name=f'name{addone}',
                  desc=f'desc{addone}',
                  is_active=0
                  )
        db.session.add(var)
        db.session.flush()
        writeaudit(var.id, str(var.to_dict()), None)
    db.session.commit()
    return redirect('/bag/list')


def writeaudit(parent_id, before, after):
    if after is None:
        change = "add"
    else:
        change = "change"
    var = BagAudit(parent_id=parent_id,
                   a_datetime=datetime.now(),
                   a_user_id=current_user.id,
                   a_username=load_user(current_user.id).username,
                   action=change,
                   before=before,
                   after=after
                   )

    db.session.add(var)
