from flask import render_template, request
from flask_login import login_required
from app.audit import bp
from app.models import BagAudit


lastpagelist = 0
next_page = None


# todo combine all audit records into one model
@bp.route('/auditview/<int:id>', methods=['GET', 'POST'])
@login_required
def auditview(id):
    audit_single = BagAudit.query.filter_by(id=id).first_or_404()
    return render_template('audit/auditview.html', audit=audit_single, rtn=request.referrer)
