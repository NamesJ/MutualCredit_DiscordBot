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
