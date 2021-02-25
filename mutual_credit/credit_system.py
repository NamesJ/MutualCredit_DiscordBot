from . import db
from .errors import (
    MaxBalanceError,
    MinBalanceError,
    SelfTransactionError,
    TransactionIDError,
    TransactionStatusError,
    UserPermissionError
)

import os
import sqlite3
import sys
import uuid


#changes


DFLT_CONFIG = {
    'min_balance': -1000,
    'max_balance': 1000,
}


def _init_db():
    with db.connect() as conn:
        db.init_accounts_table(conn)
        db.init_offers_table(conn)
        db.init_offer_categories_table(conn)
        db.init_transactions_table(conn)


def addCategoryToOffer(member_id, offer_id, category):
    with db.connect() as conn:
        seller_id = db.get_offer_seller(conn, offer_id)
        categories = db.get_offer_categories(conn, offer_id)

    if member_id != seller_id:
        raise UserPermissionError('User tried to alter another members offer')

    if category in categories:
        return

    offer_category = (offer_id, category)
    with db.connect() as conn:
        db.create_offer_category(conn, offer_category)


def addCategoriesToOffer(member_id, offer_id, categories):
    with db.connect() as conn:
        seller_id = db.get_offer_seller(conn, offer_id)
        current_categories = db.get_offer_categories(conn, offer_id)

    if member_id != seller_id:
        raise UserPermissionError('User tried to alter another members offer')

    with db.connect() as conn:
        added = []

        for category in categories:
            if category in current_categories or category in added:
                continue

            offer_category = (offer_id, category)
            db.create_offer_category(conn, offer_category)
            added.append(category)


def approveTransaction(account_id, tx_id):
    with db.connect() as conn:
        tx = db.get_transaction(conn, tx_id)

    if tx is None:
        raise TransactionIDError(f'Transaction with ID {tx_id} does not exist')

    buyer_id, seller_id, offer_id, status = tx[1], tx[2], tx[3], tx[4]

    if account_id != seller_id:
        raise UserPermissionError(f'User with ID {account_id} tried to alter another members transaction')


    with db.connect() as conn:
        buyer_balance = db.get_account_balance(conn, buyer_id)
        buyer_min, buyer_max = db.get_account_range(conn, buyer_id)
        seller_balance = db.get_account_balance(conn, seller_id)
        seller_min, seller_max = db.get_account_range(conn, seller_id)
        price = db.get_offer_price(conn, offer_id)

    if status != 'PENDING':
        raise TransactionStatusError('Transaction status is not pending')
    if seller_balance + price > seller_max:
        raise MaxBalanceError('Seller account too high for transaction')
    if buyer_balance - price < buyer_min:
        raise MinBalanceError('Buyer account too low for transaction')

    with db.connect() as conn:
        db.update_transaction_status(conn, tx_id, 'APPROVED')
        db.update_account_balance(conn, buyer_id, buyer_balance - price)
        db.update_account_balance(conn, seller_id, seller_balance + price)


def cancelTransaction(tx_id):
    with db.connect() as conn:
        tx_status = db.get_transaction_status(conn, tx_id)
        if tx_status != 'PENDING':
            raise Exception('Transaction status is not pending')
        db.update_transaction_status(conn, tx_id, 'CANCELLED')


def createAccount(account_id):
    account = (account_id, 0, DFLT_CONFIG['max_balance'],
                                                    DFLT_CONFIG['min_balance'])
    with db.connect() as conn:
        db.create_account(conn, account)


def createOffer(account_id, description, price, title):
    offer = (str(uuid.uuid4()), account_id, description, price, title)
    with db.connect() as conn:
        db.create_offer(conn, offer)
    return offer[0]


# Should use a "pending balance" rather than actual balance of buyer
def createTransaction(buyer_id, offer_id):
    with db.connect() as conn:
        buyer_balance = getAvailableBalance(buyer_id)
        buyer_min, buyer_max = db.get_account_range(conn, buyer_id)
        price = db.get_offer_price(conn, offer_id)
        seller_id = db.get_offer_seller(conn, offer_id)
        # TODO: check that offer exists

        if buyer_id == seller_id:
            raise SelfTransactionError('Buyer ID must be different from seller ID')
        if buyer_balance - price < buyer_min:
            raise MinBalanceError('Buyer balance too low for transaction')
        # TODO: seller_id in tx is technically unnecessary
        tx = (str(uuid.uuid4()), buyer_id, seller_id, offer_id, "PENDING")
        db.create_transaction(conn, tx)
    return tx[0]


# delete could be dangerous, instead maybe have an 'enabled' flag
def deleteAccount(account_id):
    with db.connect() as conn:
        with conn.cursor() as cur:
            db.delete_account(cur, account_id)


# delete could be dangerous, instead maybe have an 'enabled' flag
def deleteOffer(offer_id):
    with db.connect() as conn:
        #with conn.cursor() as cur:
            db.delete_offer(conn, offer_id)


def denyTransaction(tx_id):
    with db.connect() as conn:
        tx_status = db.get_transaction_status(conn, tx_id)
        if tx_status != 'PENDING':
            raise Exception('Transaction status is not pending')
        db.update_transaction_status(conn, tx_id, 'DENIED')


def getAccountRange(account_id):
    with db.connect() as conn:
        result = db.get_account_range(conn, account_id)
    return result


def getOfferCategories(offer_id):
    with db.connect() as conn:
        result = db.get_offer_categories(conn, offer_id)
    if len(result) > 0:
        result = list([item[0] for item in result])
    return result


def getBalance(account_id):
    with db.connect() as conn:
        balance = db.get_account_balance(conn, account_id)
    return balance


# available balance = balance - sum(pending buy requests)
def getAvailableBalance(account_id):
    with db.connect() as conn:
        available_balance = db.get_account_balance(conn, account_id)
        pending_buys = db.get_pending_tx_for_buyer(conn, account_id)

        for tx in pending_buys:
            offer_id = tx[3]
            price = db.get_offer_price(conn, offer_id)
            available_balance -= price

    return available_balance


def getOffers(account_id):
    with db.connect() as conn:
        offers = db.get_offers_by_seller(conn, account_id)
    return offers


def getOfferSeller(offer_id):
    with db.connect() as conn:
        seller_id = db.get_offer_seller(conn, offer_id)
    return seller_id


def getTransaction(tx_id):
    with db.connect() as conn:
        tx = db.get_transaction(conn, tx_id)
    return tx


def getTransactionBuyer(tx_id):
    with db.connect() as conn:
        tx_buyer = db.get_transaction_buyer(conn, tx_id)
    return tx_buyer


def getTransactionSeller(tx_id):
    with db.connect() as conn:
        tx_seller = db.get_transaction_seller(conn, tx_id)
    return tx_seller


def getPendingBuys(account_id):
    with db.connect() as conn:
        buys = db.get_pending_tx_for_buyer(conn, account_id)
    return buys


def getPendingSales(accountId):
    with db.connect() as conn:
        sales = db.get_pending_tx_for_seller(conn, accountId)
    return sales


def isMember(account_id):
    # TODO
    return True


def removeCategoryFromOffer(offerId, category):
    offer_category = (offerId, category)
    with db.connect() as conn:
        db.delete_offer_category(conn, offer_category)



_init_db()
