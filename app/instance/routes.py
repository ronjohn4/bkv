from flask import render_template, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.instance import bp
from app.models import Instance, Key, Audit, Keyval, load_user
from app.instance.forms import InstanceForm
from datetime import datetime


lastpagekeyval = None


# todo - add keyval for every key in this bag and this new instance
# adding an instance to a specific bag
@bp.route('/add/<int:bag_id>', methods=["GET", "POST"])
@login_required
def add(bag_id):
    form = InstanceForm()
    if request.method == 'POST' and form.validate_on_submit():
        var = Instance(name=request.form['name'], desc=request.form['desc'],
                       is_active='is_active' in request.form, bag_id=request.form['bag_id'])
        db.session.add(var)
        db.session.flush()  # flush() so the id is populated after add
        writeaudit(var.id, None, str(var.to_dict()))
        db.session.commit()
        return redirect(url_for('bag.view', id=var.bag_id))
    if request.method == 'GET':
        form.bag_id.default = bag_id
        form.process()
    return render_template('instance/add.html', form=form)


@bp.route('/view/<int:id>', methods=["GET", "POST"])
@login_required
def view(id):
    global lastpagekeyval

    page = request.args.get('page', lastpagekeyval, type=int)
    lastpagekeyval = page

    data_single = Instance.query.filter_by(id=id).first_or_404()
    key_single = Key.query.filter_by(bag_id=data_single.bag_id).first_or_404()

    keyvallist = db.session.query(Keyval, Key).\
        join(Key, Key.id == Keyval.key_id).filter(Keyval.instance_id == id).\
        add_columns(Keyval.id, Keyval.val, Keyval.is_active, Key.name).\
        paginate(page, current_app.config['ROWS_PER_PAGE_FILTER'], False)

    next_url = url_for('.view', id=id, page=keyvallist.next_num) if keyvallist.has_next else None
    prev_url = url_for('.view', id=id, page=keyvallist.prev_num) if keyvallist.has_prev else None

    if request.method == 'GET':
        rtn = request.referrer
    return render_template('instance/view.html', datasingle=data_single, keysingle=key_single,
                            keyvallist=keyvallist.items, next_url=next_url, prev_url=prev_url)


@bp.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    form = InstanceForm()
    if request.method == "POST" and form.validate_on_submit():
        data_single = Instance.query.filter_by(id=id).first_or_404()
        before = str(data_single.to_dict())
        data_single.name = request.form['name']
        data_single.desc = request.form['desc']
        data_single.is_active = 'is_active' in request.form

        after = str(data_single.to_dict())
        writeaudit(data_single.id, before, after)
        db.session.commit()
        return redirect(url_for('.view', id=data_single.id))

    if request.method == 'GET':
        data_single = Instance.query.filter_by(id=id).first_or_404()
        form.load(data_single)
    return render_template('instance/edit.html', form=form)


# todo - double check delete
# todo - cascade delete to keyval and audit
@bp.route('/delete/<int:id>', methods=["GET", "POST"])
@login_required
def delete(id):
    Audit.query.filter_by(model='instance', parent_id=id).delete()
    Instance.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect('/instance/list')


def writeaudit(parent_id, before, after):
    if before:
        change = "change"
    else:
        change = "add"
    var = Audit(model='instance',
                parent_id=parent_id,
                a_datetime=datetime.now(),
                a_user_id=current_user.id,
                a_username=load_user(current_user.id).username,
                action=change,
                before=before,
                after=after
                )

    db.session.add(var)
