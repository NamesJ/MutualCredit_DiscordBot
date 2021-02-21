import os
import sqlite3
from sqlite3 import Error
import sys
import time
import uuid


class AccountAlreadyExistsError(Exception):

    def __init__(self, accountId):
        self.message = f'Account "{accountId}" already exists.'


class AccountBalanceNotInRangeError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class AccountBalanceBelowMinError(AccountBalanceNotInRangeError):

    def __init__(self, accountId, txId, minBalance):
        self.message = f'Transaction "{txId}" would put buyer account "{accountId}" balance below minimum of {minBalance}'


class AccountBalanceAboveMaxError(AccountBalanceNotInRangeError):

    def __init__(self, accountId, txId, maxBalance):
        self.message = f'Transaction "{txId}" would put seller account "{accountId}" balance above maximum of {maxBalance}'


class BuyerIsSellerError(Exception):

    def __init__(self, accountId):
        self.message = f'Account cannot transact with itself. Account: "{accountId}".'


class InvalidAccountIdError(Exception):

    def __init__(self, accountId):
        self.message = f'Account with ID "{accountId}" does not exist'
        super().__init__(self.message)


class InvalidOfferIdError(Exception):

    def __init__(self, accountId, offerId):
        self.message = f'Account "{accountId}" does not have an offer with ID "{offerId}"'
        super().__init__(self.message)


class InvalidTransactionIdError(Exception):

    def __init__(self, txId):
        self.message = f'Transaction with ID "{txId}" does not exist.'



class CreditSystemDB(object):

    def __init__(self, dbFile):
        self.conn = self._create_connection(dbFile)
        self._init_accounts_table()
        self._init_offers_table()
        self._init_offer_categories_table()
        self._init_transactions_table()

    def _create_connection(self, dbFile):
        conn = None
        try:
            conn = sqlite3.connect(dbFile)
        except Error as e:
            print(e)

        return conn

    def _create_table(self, create_table_sql):
        if self.conn is not None:
            try:
                c = self.conn.cursor()
                c.execute(create_table_sql)
            except Error as e:
                print(e)
        else:
            raise Exception('Failed to create database connection.')

    def _init_offers_table(self):
        self._create_table('''  CREATE TABLE IF NOT EXISTS offers (
                                    id text,
                                    account_id integer,
                                    description text NOT NULL,
                                    price integer NOT NULL,
                                    title text NOT NULL,
                                    PRIMARY KEY (id, account_id),
                                    FOREIGN KEY(account_id) REFERENCES members(id)
                                ); ''')

    def _init_offer_categories_table(self):
        self._create_table('''  CREATE TABLE IF NOT EXISTS offer_categories(
                                    offer_id text,
                                    category text,
                                    PRIMARY KEY (offer_id, category)
                                ); ''')

    def _init_accounts_table(self):
        self._create_table('''  CREATE TABLE IF NOT EXISTS accounts (
                                    id text PRIMARY KEY,
                                    balance integer NOT NULL,
                                    max_balance integer NOT NULL,
                                    min_balance integer NOT NULL
                            ); ''')

    def _init_transactions_table(self):
        self._create_table('''  CREATE TABLE IF NOT EXISTS transactions (
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

    def create_account(self, account):
        sql = ''' INSERT INTO accounts(id, balance, max_balance, min_balance)
                    VALUES(?,?,?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, account)
        self.conn.commit()
        return cur.lastrowid

    def delete_account(self, accountId):
        sql = f'''  DELETE FROM accounts
                    WHERE id="{accountId}";'''
        cur = conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def create_offer(self, offer):
        sql = '''   INSERT INTO offers(id, account_id, description, price, title)
                    VALUES(?,?,?,?,?);'''
        cur = self.conn.cursor()
        cur.execute(sql, offer)
        self.conn.commit()
        return cur.lastrowid

    def create_offer_category(self, offerId, category):
        sql = f'''   INSERT INTO offer_categories(offer_id, category)
                        VALUES("{offerId}", "{category}");'''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.lastrowid

    def delete_offer_category(self, offerId, category):
        sql = f'''  DELETE FROM offer_categories
                    WHERE offer_id="{offerId}" AND category="{category}" ;'''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def delete_offer(self, offerId):
        sql = f'''  DELETE FROM offers
                    WHERE id="{offerId}";'''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    # create transaction
    def create_transaction(self, tx_id, buyer_id, seller_id, offer_id, status,
                                                start_timestamp, end_timestamp):
        if end_timestamp is None: end_timestamp = "Null"
        sql = f'''  INSERT INTO transactions(id,
                                             buyer_id,
                                             seller_id,
                                             offer_id,
                                             status,
                                             start_timestamp,
                                             end_timestamp)
                    VALUES("{tx_id}",
                           "{buyer_id}",
                           "{seller_id}",
                           "{offer_id}",
                           "{status}",
                           {start_timestamp},
                           {end_timestamp})'''
        #print(f'create_transaction(): sql="{sql}"')
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.lastrowid

    def get_account_balance(self, accountId):
        sql = f'''  SELECT balance
                    FROM accounts
                    WHERE id="{accountId}"; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall() # should only be one
        return rows[0][0]

    def get_offer_categories(self, offerId):
        sql = f'''  SELECT category
                    FROM offer_categories
                    WHERE offer_id="{offerId}";'''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    def update_account_balance(self, accountId, newBalance):
        sql = f'''  UPDATE accounts
                    SET balance={newBalance}
                    WHERE id="{accountId}"; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def approve_transaction(self, txId):
        sql = f'''  UPDATE transactions
                    SET status="APPROVED", end_timestamp={int(time.time())}
                    WHERE id="{txId}"; '''
        #print(f'approve_transaction(): sql="{sql}"')
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def cancel_transaction(self, txId):
        sql = f'''  UPDATE transactions
                    SET status="CANCELLED"
                    WHERE id="{txId}"; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def deny_transaction(self, txId):
        sql = f'''  UPDATE transactions
                    SET status="DENIED"
                    WHERE id="{txId}"; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def get_account_min_balance(self, accountId):
        sql = f'''  SELECT min_balance
                    FROM accounts
                    WHERE id="{accountId}"; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall() # should only be one
        return rows[0][0]

    def get_account_max_balance(self, accountId):
        sql = f'''  SELECT max_balance
                    FROM accounts
                    WHERE id="{accountId}"; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall() # should only be one
        return rows[0][0]

    def get_account_offers(self, accountId):
        sql = f'''  SELECT *
                    FROM offers
                    WHERE account_id="{accountId}"; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    def get_offer_price(self, offerId):
        sql = f'''  SELECT price
                    FROM offers
                    WHERE id="{offerId}"; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows[0][0]

    def get_seller_by_offer(self, offerId):
        sql = f'''  SELECT account_id
                    FROM offers
                    WHERE id="{offerId}"; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows[0][0]

    def get_transaction(self, txId):
        sql = f'''  SELECT *
                    FROM transactions
                    WHERE id="{txId}"; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall() # should only be one
        return rows[0]

    def get_pending_transactions_by_buyer(self, accountId):
        sql = f'''  SELECT *
                    FROM transactions
                    WHERE buyer_id="{accountId}"
                          AND status=PENDING; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    def get_pending_transactions_by_seller(self, accountId):
        sql = f''' SELECT *
                    FROM offers
                    WHERE seller_id={accountId} AND status=PENDING; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows



class CreditSystem (object):

    def __init__(self, dbFile='credit_system.db'):
        self.minBalance = -100
        self.maxBalance = 100
        self.accounts = {}
        self.txs = {}
        self.db = CreditSystemDB(dbFile)

    def createAccount(self, accountId, maxBalance=None, minBalance=None):
        if maxBalance is None: maxBalance = self.maxBalance
        if minBalance is None: minBalance = self.minBalance
        account = (accountId, 0, maxBalance, minBalance)
        self.db.create_account(account)

    def addOfferCategory(self, offerId, category):
        self.db.create_offer_category(offerId, category)

    def getOfferCategories(self, offerId):
        result = self.db.get_offer_categories(offerId)
        return list([row[0] for row in result])

    def deleteOfferCategory(self, offerId, category):
        self.db.delete_offer_category(offerId, category)

    def createOffer(self, accountId, description, price, title):
        offer = (str(uuid.uuid4()), accountId, description, price, title)
        self.db.create_offer(offer)
        return offer[0]

    # Should use a "pending balance" rather than actual balance of buyer
    def createTransaction(self, buyerId, offerId):
        buyerBalance = self.db.get_account_balance(buyerId)
        buyerMinBalance = self.db.get_account_min_balance(buyerId)
        offerPrice = self.db.get_offer_price(offerId)

        sellerId = self.db.get_seller_by_offer(offerId)
        # TODO: check that offer exists

        if buyerId == sellerId:
            raise Exception('Buyer ID must be different from seller ID')

        if buyerBalance - offerPrice < buyerMinBalance:
            raise Exception('Buyer balance too low for transaction')

        txId = str(uuid.uuid4())
        tx = (txId, buyerId, sellerId, offerId, "PENDING",
                int(time.time()), None)
        self.db.create_transaction(txId, buyerId, sellerId, offerId, "PENDING",
                                                        int(time.time()), None)
        return tx[0]

    # delete could be dangerous, instead maybe have an 'enabled' flag
    def deleteAccount(self, accountId):
        self.db.delete_account(accountId)

    # delete could be dangerous, instead maybe have an 'enabled' flag
    def deleteOffer(self, offerId):
        self.db.delete_offer(offerId)

    def cancelTransaction(self, txId):
        tx = self.db.get_transaction(txId)
        txStatus = tx[4]
        if txStatus != 'PENDING':
            raise Exception('Transaction status is not pending')
        self.db.cancel_transaction(txId)

    def denyTransaction(self, txId):
        tx = self.db.get_transaction(txId)
        txStatus = tx[4]
        if txStatus != 'PENDING':
            raise Exception('Transaction status is not pending')
        self.db.deny_transaction(txId)

    def approveTransaction(self, txId):
        tx = self.db.get_transaction(txId)
        buyerId = tx[1]
        sellerId = tx[2]
        offerId = tx[3]
        txStatus = tx[4]
        buyerBalance = self.db.get_account_balance(buyerId)
        buyerMinBalance = self.db.get_account_min_balance(buyerId)
        sellerBalance = self.db.get_account_balance(sellerId)
        sellerMaxBalance = self.db.get_account_max_balance(sellerId)
        offerPrice = self.db.get_offer_price(offerId)
        if txStatus != 'PENDING':
            raise Exception('Transaction status is not pending')
        if sellerBalance + offerPrice > sellerMaxBalance:
            raise Exception('Seller account too high for transaction')
        if buyerBalance - offerPrice < buyerMinBalance:
            raise Exception('Buyer account too low for transaction')
        # check that transaction status is still 'PENDING'
        self.db.approve_transaction(txId)
        # update account balances
        self.db.update_account_balance(buyerId, buyerBalance - offerPrice)
        self.db.update_account_balance(sellerId, sellerBalance + offerPrice)

    def getBalance(self, accountId):
        return self.db.get_account_balance(accountId)

    def getOffers(self, accountId):
        return self.db.get_account_offers(accountId)

    def getSellerIdByOfferId(self, offerId):
        return self.db.get_seller_by_offer(offerId)

    def getTransaction(self, txId):
        return self.db.get_transaction(txId)

    def getPendingBuyRequests(self, accountId):
        return self.db.get_pending_transactions_by_buyer(accountId)

    def getPendingSellRequests(self, accountId):
        return self.db.get_pending_transactions_by_seller(accountId)


if __name__ == '__main__':
    creditSystem = CreditSystem()
