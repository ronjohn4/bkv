from flask import render_template, request, url_for, current_app
from flask_login import login_required
from app.audit import bp
from app.models import Audit


lastpagelist = 0
lastpageaudit = 0
next_page = None
rtn = None


@bp.route('/view/<int:id>', methods=['GET', 'POST'])
@login_required
def view(id):
    audit_single = Audit.query.filter_by(id=id).first_or_404()
    return render_template('audit/view.html', audit=audit_single, rtn=request.referrer)


@bp.route('/list/<int:id>')
@login_required
def list(id):
    global lastpageaudit
    global rtn

    model = request.args.get('model', 'bag', type=str)

    page = request.args.get('page', lastpageaudit, type=int)
    lastpageaudit = page

    audit_list = Audit.query.filter_by(model=model, parent_id=id).paginate(page,
                            current_app.config['ROWS_PER_PAGE_FULL'], False)
    next_url = url_for('.auditlist', id=id, page=audit_list.next_num) if audit_list.has_next else None
    prev_url = url_for('.auditlist', id=id, page=audit_list.prev_num) if audit_list.has_prev else None
    if request.method == 'GET':
        if "/audit/" not in request.referrer:
            rtn = request.referrer
    return render_template('audit/list.html', parent_id=id, auditlist=audit_list.items, next_url=next_url,
                           prev_url=prev_url, rtn=rtn)
