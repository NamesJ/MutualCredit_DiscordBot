import sqlite3
from sqlite3 import Error


def _create_table(conn, sql):
    if conn is not None:
        try:
            conn.execute(sql)
            conn.commit()
        except Error as e:
            print(e)
    else:
        raise Exception('Failed to create database cursorection')


def init_accounts_table(conn):
    _create_table(conn, ''' CREATE TABLE IF NOT EXISTS accounts (
                                id int PRIMARY KEY,
                                balance integer NOT NULL,
                                max_balance integer NOT NULL,
                                min_balance integer NOT NULL
                        ); ''')


def init_offer_categories_table(conn):
    _create_table(conn, ''' CREATE TABLE IF NOT EXISTS offer_categories(
                                offer_id text,
                                category text,
                                PRIMARY KEY (offer_id, category)
                            ); ''')


def init_offers_table(conn):
    _create_table(conn, ''' CREATE TABLE IF NOT EXISTS offers (
                                id text,
                                seller_id integer,
                                description text NOT NULL,
                                price integer NOT NULL,
                                title text NOT NULL,
                                PRIMARY KEY (id, seller_id),
                                FOREIGN KEY(seller_id) REFERENCES members(id)
                            ); ''')


def init_transactions_table(conn):
    _create_table(conn, ''' CREATE TABLE IF NOT EXISTS transactions (
                                id text PRIMARY KEY,
                                buyer_id int NOT NULL,
                                seller_id int NOT NULL,
                                offer_id text NOT NULL,
                                status text NOT NULL,
                                start_timestamp int NOT NULL,
                                end_timestamp int,
                                FOREIGN KEY(buyer_id) REFERENCES members(id),
                                FOREIGN KEY(seller_id) REFERENCES members(id),
                                FOREIGN KEY(offer_id) REFERENCES offers(id)
                            );''')


def create_account(conn, account):
    sql = '''INSERT INTO accounts(id, balance, max_balance, min_balance)
             VALUES(?, ?, ?, ?)'''
    conn.execute(sql, account)


def create_offer(conn, offer):
    sql = '''INSERT INTO offers(id, seller_id, description, price, title)
             VALUES(?, ?, ?, ?, ?)'''
    conn.execute(sql, offer)


def create_offer_category(conn, offer_category):
    print(f'db.create_offer_category(): offer_category={offer_category}')
    sql = '''INSERT INTO offer_categories(offer_id, category)
             VALUES(?, ?)'''
    print(conn)
    conn.execute(sql, offer_category)


def create_transaction(conn, tx):
    sql = '''INSERT INTO transactions(id, buyer_id, seller_id, offer_id, status,
                start_timestamp, end_timestamp)
             VALUES(?, ?, ?, ?, ?, ?, ?)'''
    conn.execute(sql, tx)


def delete_account(cursor, account_id):
    sql = '''DELETE FROM accounts
             WHERE id=?'''
    cursor.execute(sql, (account_id,))


def delete_offer(cursor, offer_id):
    sql = '''DELETE FROM offers
             WHERE id=?'''
    cursor.execute(sql, (offer_id,))


def delete_offer_category(conn, offer_category):
    sql = '''DELETE FROM offer_categories
             WHERE offer_id=? AND category=?'''
    conn.execute(sql, offer_category)


def get_account_balance(cursor, account_id):
    sql = '''SELECT balance
             FROM accounts
             WHERE id=?'''
    rows = cursor.execute(sql, (account_id,)).fetchall()
    return rows[0][0]


# get min,max balance range for account
def get_account_range(cursor, account_id):
    sql = '''SELECT min_balance, max_balance
             FROM accounts
             WHERE id=?'''
    rows = cursor.execute(sql, (account_id,)).fetchall()
    return rows[0]


def get_offers_by_seller(cursor, seller_id):
    sql = '''SELECT *
             FROM offers
             WHERE seller_id=?'''
    rows = cursor.execute(sql, (seller_id,)).fetchall()
    return rows


def get_offer_categories(cursor, offer_id):
    sql = '''SELECT category
             FROM offer_categories
             WHERE offer_id=?'''
    rows = cursor.execute(sql, (offer_id,)).fetchall()
    return rows


def get_offer_price(cursor, offer_id):
    sql = '''SELECT price
             FROM offers
             WHERE id=?'''
    rows = cursor.execute(sql, (offer_id,)).fetchall()
    return rows[0][0]


def get_offer_seller(cursor, offer_id):
    sql = '''SELECT seller_id
             FROM offers
             WHERE id=?'''
    rows = cursor.execute(sql, (offer_id,)).fetchall()
    return rows[0][0]


def get_pending_tx_for_buyer(cursor, account_id):
    sql = '''SELECT *
             FROM transactions
             WHERE buyer_id=? AND status=PENDING'''
    rows = cursor.execute(sql, (account_id,)).fetchall()
    return rows


def get_pending_tx_for_seller(cursor, account_id):
    sql = '''SELECT *
             FROM transactions
             WHERE seller_id=? AND status=PENDING'''
    rows = cursor.execute(sql, (account_id,)).fetchall()
    return rows


def get_transaction(cursor, tx_id):
    sql = '''SELECT *
             FROM transactions
             WHERE id=?'''
    rows = cursor.execute(sql, (tx_id,)).fetchall()
    return rows[0]


def get_transaction_buyer(conn, tx_id):
    sql = '''SELECT buyer_id
             FROM transactions
             WHERE id=?'''
    rows = conn.execute(sql, (tx_id,)).fetchall()
    return rows[0][0]


def get_transaction_seller(conn, tx_id):
    sql = '''SELECT seller_id
             FROM transactions
             WHERE id=?'''
    rows = conn.execute(sql, (tx_id,)).fetchall()
    return rows[0][0]


def get_transaction_status(cursor, tx_id):
    sql = '''SELECT status
             FROM transactions
             WHERE id=?'''
    rows = cursor.execute(sql, (tx_id,)).fetchall()
    return rows[0][0]


def update_account_balance(conn, account_id, balance):
    sql = '''UPDATE accounts
             SET balance=?
             WHERE id=?'''
    conn.execute(sql, (balance, account_id))


# used for cancel, deny, and approve (checks)
def update_transaction_status(cursor, tx_id, status):
    sql = '''UPDATE transactions
             SET status=?
             WHERE id=?'''
    cursor.execute(sql, (status, tx_id))
