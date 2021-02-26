from . import db
from .errors import (
    AccountIDError,
    MaxBalanceError,
    MinBalanceError,
    OfferIDError,
    SelfTransactionError,
    TransactionIDError,
    TransactionStatusError,
    UserPermissionError
)

import os
import sqlite3
import sys


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

    if seller_id is None:
        raise OfferIDError(f'An offer with ID {offer_id} does not exist.')

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


def cancelTransaction(account_id, tx_id):
    with db.connect() as conn:
        tx = db.get_transaction(conn, tx_id)

    if tx is None:
        raise TransactionIDError(f'Transaction with ID {tx_id} does not exist')

    buyer_id, status = tx[1], tx[4]

    if account_id != buyer_id:
        raise UserPermissionError(f'User with ID {account_id} tried to alter another members transaction')

    if status != 'PENDING':
        raise TransactionStatusError('Transaction status is not pending')

    with db.connect() as conn:
        db.update_transaction_status(conn, tx_id, 'CANCELLED')


def createAccount(account_id):
    account = (account_id, 0, DFLT_CONFIG['max_balance'],
                                                    DFLT_CONFIG['min_balance'])

    with db.connect() as conn:
        balance = db.get_account_balance(conn, account_id)

        if balance is not None: # account already exists
            raise AccountIDError(f'Account with ID {account_id} already exists.')

        db.create_account(conn, account)


def createOffer(seller_id, description, price, title):
    offer = (seller_id, description, price, title)

    with db.connect() as conn:
        offer_id = db.create_offer(conn, offer)

    return offer_id


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
        tx = (buyer_id, seller_id, offer_id)
        tx_id = db.create_transaction(conn, tx)

    return tx_id


# delete could be dangerous, instead maybe have an 'enabled' flag
def deleteAccount(account_id):
    with db.connect() as conn:
        with conn.cursor() as cur:
            db.delete_account(cur, account_id)


# delete could be dangerous, instead maybe have an 'enabled' flag
def deleteOffer(account_id, offer_id):
    with db.connect() as conn:
        seller_id = db.get_offer_seller(conn, offer_id)

    if seller_id is None:
        raise OfferIDError(f'Offer with ID {offer_id} does not exist.')

    if account_id != seller_id:
        raise UserPermissionError('User tried to delete another user\'s offer')

    with db.connect() as conn:
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

    if result is None:
        raise AccountIDError(f'getAccountRange(): Account with ID {account_id} does not exist.')

    return result


def getOfferCategories(offer_id):
    with db.connect() as conn:
        seller_id = db.get_offer_seller(conn, offer_id)
        result = db.get_offer_categories(conn, offer_id)

    if len(result) == 0:
        raise OfferIDError(f'Offer with ID {offer_id} does not exist')

    if len(result) > 0:
        result = list([item[0] for item in result])

    return result


def getAccountBalance(account_id):
    with db.connect() as conn:
        balance = db.get_account_balance(conn, account_id)

    if balance is None:
        raise AccountIDError(f'No account with ID {account_id} exists.')

    return balance


# available balance is the the amount of credit left to use
# available_balance = account_balance - sum(pending_debits) - min_balance
def getAvailableBalance(account_id):
    min_balance, max_balance = getAccountRange(account_id)
    balance = getAccountBalance(account_id)
    pending_debits = getTotalPendingDebits(account_id)

    return balance - pending_debits - min_balance


def getOffers(seller_id):
    if not isMember(seller_id):
        raise AccountIDError(f'No account with ID {seller_id} exists')

    with db.connect() as conn:
        offers = db.get_offers_by_seller(conn, seller_id)

    return offers


def getOfferSeller(offer_id):
    with db.connect() as conn:
        seller_id = db.get_offer_seller(conn, offer_id)

    if seller_id is None:
        raise OfferIDError(f'No offer with ID {offer_id} exists.')

    return seller_id


# returns sum of price of pending sales
def getTotalPendingCredits(account_id):
    with db.connect() as conn:
        credits = db.get_total_pending_credits_by_account(conn, account_id)

    return credits


# returns sum of price of pending buys
def getTotalPendingDebits(account_id):
    with db.connect() as conn:
        debits = db.get_total_pending_debits_by_account(conn, account_id)

    return debits


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


def removeCategoryFromOffer(member_id, offer_id, category):
    with db.connect() as conn:
        seller_id = db.get_offer_seller(conn, offer_id)
        current_categories = db.get_offer_categories(conn, offer_id)

    if seller_id is None:
        raise OfferIDError(f'Offer with ID {offer_id} does not exist.')

    if member_id != seller_id:
        raise UserPermissionError(f'User tried to alter offer of another user.')

    if category not in current_categories:
        return

    with db.connect() as conn:
        db.delete_offer_category(conn, offer_id, category)


def removeCategoriesFromOffer(member_id, offer_id, categories):
    with db.connect() as conn:
        seller_id = db.get_offer_seller(conn, offer_id)
        current_categories = db.get_offer_categories(conn, offer_id)

    if seller_id is None:
        raise OfferIDError(f'Offer with ID {offer_id} does not exist')

    if member_id != seller_id:
        raise UserPermissionError('User tried to alter another members offer')


    with db.connect() as conn:
        removed = []

        for category in categories:
            if category in current_categories and category not in removed:
                continue

            db.delete_offer_category(conn, offer_id, category)
            removed.append(category)



_init_db()
