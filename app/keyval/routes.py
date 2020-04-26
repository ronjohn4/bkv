from flask import render_template, redirect, request, url_for
from flask_login import login_required, current_user
from app import db
from app.keyval import bp
from app.models import Keyval, Key, Audit, load_user
from app.keyval.forms import KeyvalForm
from datetime import datetime


rtn = None


@bp.route('/view/<int:id>', methods=["GET", "POST"])
@login_required
def view(id):
    global rtn

    data_single = Keyval.query.filter_by(id=id).first_or_404()
    key_single = Key.query.filter_by(id=data_single.key_id).first_or_404()

    # only set the return url if it points out of the keyval app.  Otherwise it will return to keyval edit.
    if request.method == 'GET':
        if "/keyval/" not in request.referrer:
            rtn = request.referrer
    return render_template('keyval/view.html', datasingle=data_single, keysingle=key_single, rtn=rtn)


# todo - show the keyval name on edit (which comes from the parent key)
@bp.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    form = KeyvalForm()
    if request.method == "POST" and form.validate_on_submit():
        data_single = Keyval.query.filter_by(id=id).first_or_404()
        before = str(data_single.to_dict())
        data_single.is_active = 'is_active' in request.form
        data_single.val = request.form['val']

        after = str(data_single.to_dict())
        writeaudit(data_single.id, before, after)
        db.session.commit()
        return redirect(url_for('.view', id=data_single.id))

    if request.method == 'GET':
        data_single = Keyval.query.filter_by(id=id).first_or_404()
        form.load(data_single)
    return render_template('keyval/edit.html', form=form)


def writeaudit(parent_id, before, after):
    if before:
        change = "change"
    else:
        change = "add"
    var = Audit(model='keyval',
                parent_id=parent_id,
                a_datetime=datetime.now(),
                a_user_id=current_user.id,
                a_username=load_user(current_user.id).username,
                action=change,
                before=before,
                after=after
                )

    db.session.add(var)
