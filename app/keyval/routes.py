from flask import render_template, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.keyval import bp
from app.models import Keyval, BagAudit, sex, load_user
from app.keyval.forms import KeyvalForm
from datetime import datetime
import dateutil.parser



lastpagelist = 0
lastpageaudit = 0
next_page = None


@bp.route('/list/')
@login_required
def keyvallist():
    global lastpagelist

    page = request.args.get('page', lastpagefull, type=int)
    lastpagefull = page
    keyvallist = Keyval.query.paginate(page, current_app.config['ROWS_PER_PAGE_FULL'], False)
    next_url = url_for('.keyvallist', page=keyvallist.next_num) if keyvallist.has_next else None
    prev_url = url_for('.keyvallist', page=keyvallist.prev_num) if keyvallist.has_prev else None
    return render_template('keyvallist.html', keyvals=keyvallist.items, sex=sex, next_url=next_url, prev_url=prev_url)


@bp.route('/add/', methods=["GET", "POST"])
@login_required
def keyvaladd():
    form = KeyvalForm()
    if request.method == 'POST' and form.validate_on_submit():
        var = Keyval(name=request.form['name'],
                     email=request.form['email'],
                     sex=int(request.form['sex']),
                     dob=datetime.strptime(str(dateutil.parser.parse(request.form['dob'])).split(" ", 1)[0],
                                           '%Y-%m-%d'),
                     is_active='is_active' in request.form,
                     income_amount=request.form['income_amount']
                     )
        db.session.add(var)
        db.session.commit()
        return redirect('/keyval/list')
    return render_template('keyvaladd.html', form=form)


@bp.route('/view/<int:id>', methods=["GET", "POST"])
@login_required
def keyvalview(id):
    global lastpageaudit

    page = request.args.get('page', lastpagefilter, type=int)
    lastpagefilter = page
    keyvalsingle = Keyval.query.filter_by(id=id).first_or_404()
    auditlist = BagAudit.query.filter_by(parent_id=keyvalsingle.id).paginate(page, current_app.config['ROWS_PER_PAGE_FILTER'], False)
    next_url = url_for('.keyvalview', id=id, page=auditlist.next_num) if auditlist.has_next else None
    prev_url = url_for('.keyvalview', id=id, page=auditlist.prev_num) if auditlist.has_prev else None
    return render_template('keyvalview.html', keyval=keyvalsingle, auditlist=auditlist.items,
                           sex=sex, next_url=next_url, prev_url=prev_url)


@bp.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def keyvaledit(id):
    global next_page

    form = KeyvalForm()
    if request.method == "POST" and form.validate_on_submit():
        data = Keyval.query.filter_by(id=id).first_or_404()
        before = str(data.to_dict())
        data.name = request.form['name']
        data.email = request.form['email']
        data.sex = int(request.form['sex'])
        data.dob = datetime.strptime(str(dateutil.parser.parse(request.form['dob'])).split(" ", 1)[0], '%Y-%m-%d')
        data.is_active = 'is_active' in request.form
        data.income_amount = request.form['income_amount']

        after = str(data.to_dict())
        var = BagAudit(parent_id=data.id,
                       a_datetime=datetime.now(),
                       a_user_id=current_user.id,
                       a_username=load_user(current_user.id).username,
                       action="change",
                       before=before,
                       after=after
                       )

        db.session.add(var)
        db.session.commit()
        return redirect(next_page)

    if request.method == 'GET':
        next_page = request.referrer
        keyvalsingle = Keyval.query.filter_by(id=id).first_or_404()
        form.load(keyvalsingle)
    return render_template('keyvaledit.html', form=form, next=request.referrer)


@bp.route('/delete/<int:id>', methods=["GET", "POST"])
@login_required
def keyvaldelete(id):
    global lastpagelist

    Keyval.query.filter_by(id=id).delete()
    db.session.commit()

    page = request.args.get('page', lastpagefull, type=int)
    lastpagefull = page
    keyvallist = Keyval.query.paginate(page, current_app.config['ROWS_PER_PAGE_FULL'], False)
    next_url = url_for('.keyvallist', page=keyvallist.next_num) if keyvallist.has_next else None
    prev_url = url_for('.keyvallist', page=keyvallist.prev_num) if keyvallist.has_prev else None
    return render_template('keyvallist.html', keyvals=keyvallist.items, sex=sex, next_url=next_url, prev_url=prev_url)


# Use to add test data to the Parent model.
# /keyval/keyvaladdtest?addcount=30 adds 30 entries
# may need to remove the @login_required
@bp.route('/keyvaladdtest/', methods=["GET", "POST"])
@login_required
def keyvaladdtest():
    addcount = request.args.get('addcount', 20, type=int)
    for addone in range(addcount):
        var = Keyval(name=f'name{addone}',
                     email='email@domain.com',
                     sex=0,
                     dob=datetime.strptime('1999-01-01', '%Y-%m-%d'),
                     is_active=0,
                     income_amount=123.45
                     )
        db.session.add(var)
    db.session.commit()
    return redirect('/list')
