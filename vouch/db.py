import sqlite3
from sqlite3 import Error


DB_FILE = 'vouch.db'


def _create_table(conn, sql):
    if conn is not None:
        try:
            conn.execute(sql)
            conn.commit()
        except Error as e:
            print(e)
    else:
        raise Exception('Failed to create database connection')


def connect():
    return sqlite3.connect(DB_FILE)


def create_config_table(conn):
    sql = '''CREATE TABLE IF NOT EXISTS config (
                key     TEXT    PRIMARY KEY,
                value   TEXT
             );'''
    _create_table(conn, sql)


def create_members_table(conn):
    sql = '''CREATE TABLE IF NOT EXISTS members (
                id  INT PRIMARY KEY
             )'''
    _create_table(conn, sql)


# When entries in members table are deleted, rows in vouches table with matching
#   vouches.voucher_id = members.id will also be deleted
def create_vouches_table(conn):
    sql = '''CREATE TABLE IF NOT EXISTS vouches (
                voucher_id  INT     NOT NULL,
                vouchee_id  INT     NOT NULL,
                value       INT     NOT NULL,
                PRIMARY KEY (voucher_id, vouchee_id),
                CONSTRAINT voucher_column
                    FOREIGN KEY (voucher_id)
                    REFERENCES members(id)
                    ON DELETE CASCADE
                CHECK (value >= -1 AND value <= 1)
             );'''
    _create_table(conn, sql)


def create_config(conn, config):
    sql = '''INSERT INTO config(key, value)
             VALUES(?, ?)'''
    conn.execute(sql, config)


def create_member(conn, member):
    sql = '''INSERT INTO members(id)
             VALUES(?)'''
    conn.execute(sql, member)


def create_vouch(conn, vouch):
    sql = '''INSERT INTO vouches(voucher_id, vouchee_id, value)
             VALUES(?, ?, ?)'''
    conn.execute(sql, vouch)


def delete_member(cursor, member_id):
    sql = '''DELETE FROM members
             WHERE id=?'''
    cursor.execute(sql, (member_id,))


def get_config(conn):
    sql = '''SELECT *
             FROM config'''
    rows = conn.execute(sql).fetchall()
    return rows


def get_config_value(conn, key):
    sql = '''SELECT value
             FROM config
             WHERE key=?'''
    row = conn.execute(sql, (key, )).fetchone()
    if row:
        row = row[0]
    return row


def get_member(conn, member_id):
    sql = '''SELECT *
             FROM members
             WHERE id=?'''
    row = conn.execute(sql, (member_id,)).fetchone()
    print(f'get_member: row={row}')
    return row


def get_member_count(conn):
    sql = '''SELECT COUNT(*)
             FROM members;'''
    row = conn.execute(sql).fetchone()
    return row[0]


def get_vouch_value(conn, voucher_id, vouchee_id):
    sql = '''SELECT value
             FROM vouches
             WHERE voucher_id=? AND vouchee_id=?'''
    row = conn.execute(sql, (voucher_id, vouchee_id)).fetchone()
    if row:
        row = row[0]
    return row


def get_vouchee_value(conn, vouchee_id):
    sql = '''SELECT SUM(value)
             FROM vouches
             WHERE vouchee_id=?'''
    row = conn.execute(sql, (vouchee_id,)).fetchone()
    row = row[0]
    if row is None:
        row = 0
    return row


def get_vouches_by_vouchee(conn, vouchee_id):
    sql = '''SELECT *
             FROM vouches
             WHERE vouchee_id=?'''
    rows = conn.execute(sql, (vouchee_id,)).fetchall()
    return rows


def get_vouches_by_voucher(conn, voucher_id):
    sql = '''SELECT *
             FROM vouches
             WHERE voucher_id=?'''
    rows = conn.execute(sql, (voucher_id,)).fetchall()
    return rows


def update_config_value(conn, key, value):
    sql = '''UPDATE config
             SET value=?
             WHERE key=?'''
    conn.execute(sql, (value, key))


def update_vouch_value(conn, voucher_id, vouchee_id, value):
    sql = '''UPDATE vouches
             SET value=?
             WHERE voucher_id=? AND vouchee_id=?'''
    conn.execute(sql, (value, voucher_id, vouchee_id))
