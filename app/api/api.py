from flask import jsonify
from app import db
from app.api import bp
from app.models import Keyval, Key, Instance, Bag


# todo - add authentication
@bp.route('/baginstance/<bag>/<instance>', methods=['GET'])
def bag_instance(bag, instance):
    bag_single = Bag.query.filter_by(name=bag, is_active=True).first_or_404()
    instance_single = Instance.query.filter_by(name=instance, bag_id=bag_single.id, is_active=True).first_or_404()

    keyvallist = db.session.query(Keyval, Key).\
        join(Key, Key.id == Keyval.key_id).\
        filter(Keyval.instance_id == instance_single.id, Key.is_active, Keyval.is_active).\
        add_columns(Keyval.val, Keyval.last_loaded, Keyval.last_changed,
                    Keyval.is_dirty, Keyval.count_loaded, Keyval.count_changed, Key.name).all()
    l = []
    d1 = {}
    d2 = {}
    for kv in keyvallist:
        d1['key.name'] = kv.name
        d1['keyval.val'] = kv.val
        # d1['keyval.last_loaded'] = kv.last_loaded
        # d1['keyval.last_changed'] = kv.last_changed
        # d1['keyval.is_dirty'] = kv.is_dirty
        # d1['keyval.count_loaded'] = kv.count_loaded
        # d1['keyval.count_changed'] = kv.count_changed
        l.append(d1)
        d1 = {}

    d2['bag.name'] = bag_single.name
    d2['instance.name'] = instance_single.name
    d2['keyvals'] = l
    return jsonify(d2)
