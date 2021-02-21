import db

import os
import sqlite3
from sqlite3 import Error
import sys
import time
import uuid
from contextlib import closing



class CreditSystem (object):

    def __init__(self, db_file='credit_system.db'):
        self.minBalance = -100
        self.maxBalance = 100
        self.db_file = db_file


    def addCategoryToOffer(self, offer_id, category):
        # TODO: check that offer does not already have that category
        offer_category = (offer_id, category)
        with closing(sqlite3.connect(self.db_file)) as conn:
            db.create_offer_category(conn, offer_category)


    def approveTransaction(self, tx_id):
        with closing(sqlite3.connect(self.db_file)) as conn:
            buyer_id, seller_id, offer_id, tx_status = db.get_transaction(txId)
            buyer_balance = db.get_account_balance(buyer_id)
            buyer_min, buyer_max = db.get_account_range(buyer_id)
            seller_balance = db.get_account_balance(seller_id)
            seller_min, seller_max = db.get_account_range(seller_id)
            price = db.get_offer_price(offer_id)
            if tx_status != 'PENDING':
                raise Exception('Transaction status is not pending')
            if seller_balance + price > seller_max:
                raise Exception('Seller account too high for transaction')
            if buyer_balance - price < buyer_min:
                raise Exception('Buyer account too low for transaction')
            # check that transaction status is still 'PENDING'
            db.update_transaction_status(tx_id, 'APPROVED')
            # update account balances
            db.update_account_balance(buyer_id, buyer_balance - price)
            db.update_account_balance(seller_id, seller_balance + price)


    def cancelTransaction(self, tx_id):
        with closing(sqlite3.connect(self.db_file)) as conn:
            tx_status = db.get_transaction_status(tx_id)
            if tx_status != 'PENDING':
                raise Exception('Transaction status is not pending')
            db.cancel_transaction(tx_id)


    def createAccount(self, account_id):
        account = (account_id, 0, self.max_balance, self.min_balance)
        with closing(sqlite3.connect(self.db_file)) as conn:
            db.create_account(conn, account)


    def createOffer(self, accountId, description, price, title):
        offer = (str(uuid.uuid4()), accountId, description, price, title)
        with closing(sqlite3.connect(self.db_file)) as conn:
            db.create_offer(conn, offer)
        return offer[0]


    # Should use a "pending balance" rather than actual balance of buyer
    def createTransaction(self, buyer_id, offer_id):
        with closing(sqlite3.connect(self.db_file)) as conn:
            buyer_balance = db.get_account_balance(buyer_id)
            buyer_min, buyer_max = db.get_account_range(buyer_id)
            price = db.get_offer_price(offer_id)
            seller_id = db.get_offer_seller(offer_id)
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
        with closing(sqlite3.connect(self.db_file)) as conn:
            db.delete_account(account_id)


    # delete could be dangerous, instead maybe have an 'enabled' flag
    def deleteOffer(self, offerId):
        with closing(sqlite3.connect(self.db_file)) as conn:
            db.delete_offer(offerId)


    def denyTransaction(self, tx_id):
        with closing(sqlite3.connect(self.db_file)) as conn:
            txStatus = db.get_transaction_status(conn, tx_id)
            if txStatus != 'PENDING':
                raise Exception('Transaction status is not pending')
            db.update_transaction_status(tx_id)


    def getOfferCategories(self, offer_id):
        with closing(sqlite3.connect(self.db_file)) as conn:
            db.get_offer_categories(offerId)
        result = db.get_offer_categories(offer_id)
        return list([row[0] for row in result])


    def getBalance(self, account_id):
        with closing(sqlite3.connect(self.db_file)) as conn:
            balance = db.get_account_balance(account_id)
        return balance


    def getOffers(self, account_id):
        with closing(sqlite3.connect(self.db_file)) as conn:
            offers = db.get_account_offers(account_id)
        return offers


    def getOfferSeller(self, offer_id):
        with closing(sqlite3.connect(self.db_file)) as conn:
            seller_id = db.get_seller_by_offer(offer_id)
        return seller_id


    def getTransaction(self, tx_id):
        with closing(sqlite3.connect(self.db_file)) as conn:
            tx = self.db.get_transaction(tx_id)
        return tx


    def getPendingBuys(self, account_id):
        with closing(sqlite3.connect(self.db_file)) as conn:
            buys = db.get_pending_tx_for_buyer(conn, account_id)
        return buys


    def getPendingSales(self, accountId):
        with closing(sqlite3.connect(self.db_file)) as conn:
            sales = db.get_pending_tx_for_seller(accountId)
        return sales


    def removeCategoryFromOffer(self, offerId, category):
        offer_category = (offerId, category)
        with closing(sqlite3.connect(self.db_file)) as conn:
            db.delete_offer_category(conn, offer_category)


if __name__ == '__main__':
    creditSystem = CreditSystem()
