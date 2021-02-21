import db

import os
import sqlite3
import sys
import time
import uuid



class CreditSystem (object):

    def __init__(self, db_file='credit_system.db'):
        self.min_balance = -100
        self.max_balance = 100
        self.db_file = db_file
        self._init_db()


    def _init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            db.init_accounts_table(conn)
            db.init_offers_table(conn)
            db.init_offer_categories_table(conn)
            db.init_transactions_table(conn)


    def addCategoryToOffer(self, offer_id, category):
        print(f'credit_system.addCategoryToOffer(): offer_id={offer_id}, category={category}')
        # TODO: check that offer does not already have that category
        offer_category = (offer_id, category)
        with sqlite3.connect(self.db_file) as conn:
            db.create_offer_category(conn, offer_category)


    def approveTransaction(self, tx_id):
        with sqlite3.connect(self.db_file) as conn:
            tx = db.get_transaction(conn, tx_id)
            print(f'tx: {tx}')
            buyer_balance = db.get_account_balance(conn, tx[1])
            buyer_min, buyer_max = db.get_account_range(conn, tx[1])
            seller_balance = db.get_account_balance(conn, tx[2])
            seller_min, seller_max = db.get_account_range(conn, tx[2])
            price = db.get_offer_price(conn, tx[3])
            if tx[4] != 'PENDING':
                raise Exception('Transaction status is not pending')
            if seller_balance + price > seller_max:
                raise Exception('Seller account too high for transaction')
            if buyer_balance - price < buyer_min:
                raise Exception('Buyer account too low for transaction')
            # check that transaction status is still 'PENDING'
            db.update_transaction_status(conn, tx_id, 'APPROVED')
            # update account balances
            db.update_account_balance(conn, tx[1], buyer_balance - price)
            db.update_account_balance(conn, tx[2], seller_balance + price)


    def cancelTransaction(self, tx_id):
        with sqlite3.connect(self.db_file) as conn:
            tx_status = db.get_transaction_status(conn, tx_id)
            if tx_status != 'PENDING':
                raise Exception('Transaction status is not pending')
            db.update_transaction_status(conn, tx_id, 'CANCELLED')


    def cleanDB(self):
        os.remove(self.db_file)
        self._init_db()


    def createAccount(self, account_id):
        account = (account_id, 0, self.max_balance, self.min_balance)
        with sqlite3.connect(self.db_file) as conn:
            db.create_account(conn, account)


    def createOffer(self, account_id, description, price, title):
        offer = (str(uuid.uuid4()), account_id, description, price, title)
        with sqlite3.connect(self.db_file) as conn:
            db.create_offer(conn, offer)
        return offer[0]


    # Should use a "pending balance" rather than actual balance of buyer
    def createTransaction(self, buyer_id, offer_id):
        with sqlite3.connect(self.db_file) as conn:
            buyer_balance = db.get_account_balance(conn, buyer_id)
            buyer_min, buyer_max = db.get_account_range(conn, buyer_id)
            price = db.get_offer_price(conn, offer_id)
            seller_id = db.get_offer_seller(conn, offer_id)
            # TODO: check that offer exists

            if buyer_id == seller_id:
                raise Exception('Buyer ID must be different from seller ID')
            if buyer_balance - price < buyer_min:
                raise Exception('Buyer balance too low for transaction')
            # TODO: seller_id in tx is technically unnecessary
            tx = (str(uuid.uuid4()), buyer_id, seller_id, offer_id, "PENDING",
                                                        int(time.time()), None)
            db.create_transaction(conn, tx)
        return tx[0]


    # delete could be dangerous, instead maybe have an 'enabled' flag
    def deleteAccount(self, account_id):
        with sqlite3.connect(self.db_file) as conn:
            with conn.cursor() as cur:
                db.delete_account(cur, account_id)


    # delete could be dangerous, instead maybe have an 'enabled' flag
    def deleteOffer(self, offer_id):
        with sqlite3.connect(self.db_file) as conn:
            #with conn.cursor() as cur:
                db.delete_offer(conn, offer_id)


    def denyTransaction(self, tx_id):
        with sqlite3.connect(self.db_file) as conn:
            tx_status = db.get_transaction_status(conn, tx_id)
            if tx_status != 'PENDING':
                raise Exception('Transaction status is not pending')
            db.update_transaction_status(conn, tx_id, 'DENIED')


    def getOfferCategories(self, offer_id):
        with sqlite3.connect(self.db_file) as conn:
            result = db.get_offer_categories(conn, offer_id)
        if len(result) > 0:
            result = list([item[0] for item in result])
        return result


    def getBalance(self, account_id):
        with sqlite3.connect(self.db_file) as conn:
            balance = db.get_account_balance(conn, account_id)
        return balance


    def getOffers(self, account_id):
        with sqlite3.connect(self.db_file) as conn:
            offers = db.get_offers_by_seller(conn, account_id)
        return offers


    def getOfferSeller(self, offer_id):
        with sqlite3.connect(self.db_file) as conn:
            seller_id = db.get_offer_seller(conn, offer_id)
        return seller_id


    def getTransaction(self, tx_id):
        with sqlite3.connect(self.db_file) as conn:
            tx = db.get_transaction(conn, tx_id)
        return tx


    def getPendingBuys(self, account_id):
        with sqlite3.connect(self.db_file) as conn:
            buys = db.get_pending_tx_for_buyer(conn, account_id)
        return buys


    def getPendingSales(self, accountId):
        with sqlite3.connect(self.db_file) as conn:
            sales = db.get_pending_tx_for_seller(conn, accountId)
        return sales


    def removeCategoryFromOffer(self, offerId, category):
        offer_category = (offerId, category)
        with sqlite3.connect(self.db_file) as conn:
            db.delete_offer_category(conn, offer_category)
