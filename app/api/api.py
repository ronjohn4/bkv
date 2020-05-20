from flask import jsonify
from app import db
from app.api import bp
from app.models import Keyval, Key, Instance, Bag
from sqlalchemy import func


# todo - add authentication
@bp.route('/baginstance/<bag>/<instance>', methods=['GET'])
def bag_instance(bag, instance):
    # use filter so can make the query case insensitive
    bag_single = Bag.query.filter(func.upper(Bag.name) == bag.upper(), Bag.is_active).first_or_404()
    instance_single = Instance.query.filter(func.upper(Instance.name) == instance.upper(),
                                            Instance.bag_id == bag_single.id,
                                            Instance.is_active).first_or_404()

    keyvallist = db.session.query(Keyval, Key).\
        join(Key, Key.id == Keyval.key_id).\
        filter(Keyval.instance_id == instance_single.id, Key.is_active, Keyval.is_active).\
        add_columns(Keyval.val, Keyval.last_loaded, Keyval.last_changed,
                    Keyval.is_dirty, Keyval.count_loaded, Keyval.count_changed, Key.name).all()

    kv_dict = {}
    for kv in keyvallist:
        kv_dict[kv.name] = kv.val

    return jsonify(kv_dict)
