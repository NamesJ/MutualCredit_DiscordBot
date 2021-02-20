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





class Offer (object):
    # 'price' is a dict containing one or more key-value pairs where the key is the
    #   currency identifier string (e.g. 'USD' for US dollars, 'MC' for mutual credit)
    #   and the value is the amount of that currency. E.g.
    #   { 'currency0': amount0, 'currency1': amount1, ... }

    def __init__(self, description, price, title, offerId=None):
        self.description = description
        if offerId:
            self.id = offerId
        else:
            self.id = str(uuid.uuid4())
        self.title = title
        self.price = price

    def asDict(self):
        return {
            'description': self.description,
            'offerId': self.id,
            'price': self.price,
            'title': self.title
            }



# `accountId` == discord username
class Account (object):

    def __init__(self, accountId, maxBalance, minBalance, balance=0, offers={}, pendingTxs={}):
        self.id = accountId
        self.maxBalance = maxBalance
        self.minBalance = minBalance
        self.balance = balance
        self.offers = offers
        self.pendingTxs = pendingTxs

    def canDebit(self, amount):
        return self.balance - amount > self.minBalance

    def canCredit(self, amount):
        return self.balance + amount < self.maxBalance

    def hasOffer(self, offerId):
        return offerId in self.offers

    def addOffer(self, offer):
        self.offers[offer.id] = offer

    def removeOffer(self, offerId):
        del self.offers[offerId]

    def updateOffer(self, offerId, name, value):
        setattr(self.offers[offerId], name, value)

    def asDict(self):
        return {
                'accountId': self.id,
                'balance': self.balance,
                'maxBalance': self.maxBalance,
                'minBalance': self.minBalance,
                'offers': self.offersAsDict()
            }

    def offersAsDict(self):
        result = {}

        for k, v in self.offers.items():
            result[k] = v.asDict()

        return result



class Transaction (object):

    def __init__(self, buyerId='', sellerId='', offerId='', status='PENDING'):
        self.id = str(uuid.uuid4())
        self.buyerId = buyerId
        self.sellerId = sellerId
        self.offerId = offerId
        self.status = status

    def asDict(self):
        return {
            'txId': self.id,
            'buyerId': self.buyerId,
            'sellerId': self.sellerId,
            'offerId': self.offerId
            }

    def approve(self):
        if not self.status == 'PENDING':
            raise Exception(f'Only pending transactions can be confirmed. Transaction status={self.status}')
        self.status = 'CONFIRMED'


    def cancel(self):
        if not self.status == 'PENDING':
            raise Exception(f'Only pending transactions can be cancelled. Transaction status={self.status}')
        self.status = 'CANCELLED'


    def deny(self):
        if not self.status == 'PENDING':
            raise Exception(f'Only pending transactions can be denied. Transaction status={self.status}')
        self.status = 'DENIED'



class CreditSystem (object):

    def __init__(self):
        self.minBalance = -100
        self.maxBalance = 100
        self.accounts = {}
        self.txs = {}

    def addAccount(self, accountId, maxBalance, minBalance):
        if accountId in self.accounts:
            raise AccountAlreadyExistsError(accountId)
        self.accounts[accountId] = Account(accountId, maxBalance, minBalance)
        return self.accounts[accountId].asDict()

    def createAccount(self, accountId):
        if accountId in self.accounts:
            raise AccountAlreadyExistsError(accountId)
        self.accounts[accountId] = Account(accountId, self.maxBalance, self.minBalance)
        return self.accounts[accountId].asDict()

    def getAccountBalance(self, accountId):
        if not accountId in self.accounts:
            raise InvalidAccountIdError(accountId)
        return self.accounts[accountId].balance

    def removeAccount(self, accountId):
        if not accountId in self.accounts:
            raise InvalidAccountIdError(accountId)
        del self.accounts[accountId]

    def addAccountOffer(self, accountId, offerId, description, title, price):
        if not accountId in self.accounts:
            raise InvalidAccountIdError(accountId)
        offer = Offer(description, title, price, offerId=offerId)
        self.accounts[accountId].addOffer(offer)

    def createAccountOffer(self, accountId, description, title, price):
        if not accountId in self.accounts:
            raise InvalidAccountIdError(accountId)
        offer = Offer(description, title, price)
        self.accounts[accountId].addOffer(offer)
        return offer.asDict()

    def getAccountOfferData(self, accountId, offerId):
        if not accountId in self.accounts:
            raise InvalidAccountIdError(accountId)
        account = self.accounts[accountId]
        if not account.hasOffer(offerId):
            raise InvalidOfferIdError(accountId, offerId)
        return account.offers[offerId].asDict()

    def getAccountOffersData(self, accountId):
        if not accountId in self.accounts:
            raise InvalidAccountIdError(accountId)
        account = self.accounts[accountId]
        return account.offersAsDict()

    def removeAccountOffer(self, accountId, offerId):
        if not accountId in self.accounts:
            raise InvalidAccountIdError(accountId)
        self.accounts[accountId].removeOffer(offerId)

    # Not being used as of now
    def updateAccountOffer(self, accountId, offerId, name, value):
        if not accountId in self.accounts:
            raise InvalidAccountIdError(accountId)
        account = self.accounts[accountId]
        if not account.hasOffer(offerId):
            raise InvalidOfferIdError(accountId, offerId)
        self.accounts[accountId].updateOffer(offerId, name, value)

    def getTransactionData(self, txId):
        if not txId in self.txs:
            raise InvalidTransactionIdError(txId)
        tx = self.txs[txId]
        return tx.asDict()

    def requestTransaction(self, buyerId, sellerId, offerId):
        if buyerId == sellerId:
            raise BuyerIsSellerError(buyerId)
        buyer = self.accounts[buyerId]
        seller = self.accounts[sellerId]
        if not seller.hasOffer(offerId):
            raise InvalidOfferIdError(sellerId, offerId)
        offer = seller.offers[offerId]
        if not buyer.canDebit(offer.price):
            raise AccountBalanceBelowMinError(txId, buyerId, buyer.minBalance)
        tx = Transaction(buyerId, sellerId, offerId)
        self.txs[tx.id] = tx
        return tx.asDict()

    def approveTransaction(self, txId):
        if not txId in self.txs:
            raise InvalidTransactionIdError(txId)
        buyerId = self.txs[txId].buyerId
        sellerId = self.txs[txId].sellerId
        seller = self.accounts[sellerId]
        offerId = self.txs[txId].offerId
        if not seller.hasOffer(offerId):
            raise InvalidOfferIdError(sellerId, offerId)
        offer = seller.offers[offerId]
        if not seller.canCredit(offer.price):
            raise AccountBalanceAboveMaxError(sellerId, txId, seller.maxBalance)
        self.txs[txId].approve()
        self.accounts[buyerId].balance -= offer.price
        self.accounts[sellerId].balance += offer.price

    def cancelTransaction(self, txId):
        if not txId in self.txs:
            raise InvalidTransactionIdError(txId)
        self.txs[txId].cancel()

    def denyTransaction(self, txId):
        if not txId in self.txs:
            raise InvalidTransactionIdError(txId)
        self.txs[txId].deny()
