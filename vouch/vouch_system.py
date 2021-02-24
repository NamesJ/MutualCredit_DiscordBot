from . import db

import math
import sqlite3



DFLT_CONFIG = {
    "bootstrap": True # to allow first member to join without vouches
}


def _init_db():
    with db.connect() as conn:
        db.create_config_table(conn)
        db.create_members_table(conn)
        db.create_vouches_table(conn)

        # ensure config table is initialized properly
        for key, value in DFLT_CONFIG.items():
            # Add missing options with dflt value
            if db.get_config_value(conn, key) is None:
                db.create_config(conn, (key, value))


def _approveMembership(vouchee_id):
    with db.connect() as conn:
        db.create_member(conn, (vouchee_id,))


def _isApproved(vouchee_id):
    with db.connect() as conn:
        total_members = db.get_member_count(conn)
        value = db.get_vouchee_value(conn, vouchee_id)
        approve = thresholdApprove()

    if value is None:
        return None

    if approve <= value:
        return True
    return False


def _isBootstrappable():
    with db.connect() as conn:
        result = int(db.get_config_value(conn, 'bootstrap'))
    return result


"""
def _isRevoked(vouchee_id):
    with db.connect() as conn:
        total_members = db.get_member_count(conn)
        value = db.get_vouchee_value(conn, vouchee_id)
        #revoke = int(db.get_config_value(conn, 'member_revoke_threshold'))
        revoke = _thresholdRevoke()
        if value is None:
            return None

        if value <= revoke:
            return True
        return False
"""


"""
def _thresholdRevoke():
    with db.connect() as conn:
        total_members = db.get_member_count(conn)
        if total_members == 0:
            return -1 # avoid memberless situation
        elif total_members < 3:
            return -2
        else:
            return -1 * math.ceil(math.log(total_members, 1.323))
"""


def _membershipCheck(vouchee_id):
    """
    if isMember(vouchee_id): # member
        if _isRevoked(vouchee_id): # loses support of group
            _revokeMembership(vouchee_id) # and is revoked
    else: # non-member
    """
    if isMember(vouchee_id): # already a member
        return
    if not _isApproved(vouchee_id): # not even vouch
        return
    _approveMembership(vouchee_id)

"""
def _revokeMembership(vouchee_id):
    with db.connect() as conn:
        with conn.cursor() as cur:
            db.delete_member(cur, vouchee_id)
"""


def _vouch(voucher_id, vouchee_id, value):
    if voucher_id == vouchee_id:
        raise Exception('You can\'t vouch for yourself!')
    if not isMember(voucher_id):
        raise Exception('Only members can vouch for other users!')
    with db.connect() as conn:
        if db.get_vouch_value(conn, voucher_id, vouchee_id) is None:
            db.create_vouch(conn, (voucher_id, vouchee_id, value))
        else:
            db.update_vouch_value(conn, voucher_id, vouchee_id, value)
    # perform membership check on vouchee
    _membershipCheck(vouchee_id)



def bootstrap(member_id):
    if not _isBootstrappable():
        raise Exception('Bootstrap denied. Cannot bootstrap more than once!')

    with db.connect() as conn:
        db.update_config_value(conn, 'bootstrap', False)
    _approveMembership(member_id)


def getVoucheeValue(vouchee_id):
    with db.connect() as conn:
        return db.get_vouchee_value(conn, vouchee_id)


def isMember(vouchee_id):
    with db.connect() as conn:
        membership = db.get_member(conn, vouchee_id)

    if membership:
        return True
    else:
        return False


# formula for threshold required to gain membership as a function of the total
#   current members
def thresholdApprove():
    with db.connect() as conn:
        total_members = db.get_member_count(conn)
        if total_members < 2:
            return 0
        else:
            return math.floor(math.log(total_members, 1.4))


def vouchNegative(voucher_id, vouchee_id):
    _vouch(voucher_id, vouchee_id, -1)



def vouchNeutral(voucher_id, vouchee_id):
    _vouch(voucher_id, vouchee_id, 0)


def vouchPositive(voucher_id, vouchee_id):
    _vouch(voucher_id, vouchee_id, 1)



_init_db()
