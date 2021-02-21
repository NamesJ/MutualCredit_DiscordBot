


def _create_table(conn, sql):
    if conn is not None:
        try:
            c = self.conn.cursor()
            c.execute(sql)
        except Error as e:
            print(e)
    else:
        raise Exception('Failed to create database connection')


def _init_accounts_table(conn):
    _create_table(conn, ''' CREATE TABLE IF NOT EXISTS accounts (
                                id text PRIMARY KEY,
                                balance integer NOT NULL,
                                max_balance integer NOT NULL,
                                min_balance integer NOT NULL
                        ); ''')


def _init_offer_categories_table(conn):
    _create_table(conn, ''' CREATE TABLE IF NOT EXISTS offer_categories(
                                offer_id text,
                                category text,
                                PRIMARY KEY (offer_id, category)
                            ); ''')


def _init_offers_table(conn):
    _create_table(conn, ''' CREATE TABLE IF NOT EXISTS offers (
                                id text,
                                account_id integer,
                                description text NOT NULL,
                                price integer NOT NULL,
                                title text NOT NULL,
                                PRIMARY KEY (id, account_id),
                                FOREIGN KEY(account_id) REFERENCES members(id)
                            ); ''')


def _init_transactions_table(conn):
    _create_table(conn, ''' CREATE TABLE IF NOT EXISTS transactions (
                                id text PRIMARY KEY,
                                buyer_id text NOT NULL,
                                seller_id text NOT NULL,
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
    sql = '''INSERT INTO offers(id, account_id, description, price, title)
             VALUES(?, ?, ?, ?, ?)'''
    conn.execute(sql, offer)


def create_offer_category(conn, offer_category):
    sql = '''INSERT INTO offer_categories(offer_id, category)
             VALUES(?, ?)'''
    conn.execute(sql, offer_category)


def create_transaction(conn, tx):
    sql = '''INSERT INTO transactions(id, buyer_id, seller_id, offer_id,
                start_timestamp, end_timestamp)
             VALUES(?, ?, ?, ?, ?, ?)'''
    conn.execute(sql, tx)


def delete_account(conn, account_id):
    sql = '''DELETE FROM accounts
             WHERE id=?'''
    conn.execute(sql, (account_id,))


def delete_offer(conn, offer_id):
    sql = '''DELETE FROM offers
             WHERE id=?'''
    conn.execute(sql, (offer_id,))


def delete_offer_category(conn, offer_category):
    sql = '''DELETE FROM offer_categories
             WHERE offer_id=? AND category=?'''
    conn.execute(sql, offer_category)


def get_account_balance(conn, account_id):
    sql = '''SELECT balance
             FROM accounts
             WHERE id=?'''
    rows = cursor.execute(sql, (account_id,))
    return rows


# get min,max balance range for account
def get_account_range(conn, account_id):
    sql = '''SELECT min_balance, max_balance
             FROM accounts
             WHERE id=?'''
    rows = cursor.execute(sql, (account_id,))
    return rows


def get_offers_by_account(conn, account_id):
    sql = '''SELECT *
             FROM offers
             WHERE account_id=?'''
    rows = conn.execute(sql, (account_id,))
    return rows


def get_offer_categories(conn, offer_id):
    sql = '''SELECT *
             FROM offer_categories
             WHERE offer_id=?'''
    rows = conn.execute(sql, (offer_id,))
    return rows


def get_offer_price(conn, offer_id):
    sql = '''SELECT price
             FROM offers
             WHERE account_id=?'''
    rows = conn.execute(sql, (offer_id,))
    return rows


def get_offer_seller(conn, seller_id):
    sql = '''SELECT seller
             FROM offers
             WHERE account_id=?'''
    rows = conn.execute(sql, (offer_id,))
    return rows


def get_pending_tx_for_buyer(conn, account_id):
    sql = '''SELECT *
             FROM transactions
             WHERE buyer_id=? AND status=PENDING'''
    rows = conn.execute(sql, (account_id,))
    return rows


def get_pending_tx_for_seller(conn, account_id):
    sql = '''SELECT *
             FROM transactions
             WHERE seller_id=? AND status=PENDING'''
    rows = conn.execute(sql, (account_id,))
    return rows


def get_transaction(conn, tx_id):
    sql = '''SELECT *
             FROM transactions
             WHERE id=?'''
    rows = conn.execute(sql, (tx_id,))
    return rows


def get_transaction_status(conn, tx_id):
    sql = '''SELECT status
             FROM transactions
             WHERE id=?'''
    rows = conn.execute(sql, (tx_id,))
    return rows


def update_account_balance(conn, account_id, balance):
    sql = '''UPDATE accounts
             SET balance=?
             WHERE id=?'''
    conn.execute(sql, (balance, account_id))


# used for cancel, deny, and approve (checks)
def update_transaction_status(conn, tx_id, status):
    sql = '''UPDATE transactions
             SET status=?
             WHERE id=?'''
    conn.execute(sql, (status, tx_id))
