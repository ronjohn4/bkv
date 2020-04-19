from flask import render_template, redirect, request
from flask_login import login_required, current_user
from app import db
from app.audit import bp
from app.models import BagAudit, load_user
from datetime import datetime



lastpagelist = 0
next_page = None


@bp.route('/auditview/<int:id>', methods=['GET', 'POST'])
@login_required
def auditview(id):
    auditsingle = BagAudit.query.filter_by(id=id).first_or_404()
    return render_template('auditview.html', audit=auditsingle, rtn=request.referrer)


# Use to add test data to the AppAudit model.
# /audit/auditaddtest?addcount=30&parentid=3 adds 30 entries to parent 3
# may need to remove the @login_required
@bp.route('/auditaddtest/', methods=["GET", "POST"])
@login_required
def auditaddtest():
    addcount = request.args.get('addcount', 20, type=int)
    parentid = request.args.get('parentid', 1, type=int)
    for addone in range(addcount):
        var = BagAudit(parent_id=parentid,
                       a_datetime=datetime.now(),
                       a_user_id=current_user.id,
                       a_username=load_user(current_user.id).username,
                       action="change",
                       before="snapshot of parent before",
                       after="snapshot of parent after"
                       )
        db.session.add(var)
    db.session.commit()
    return redirect('/list')
