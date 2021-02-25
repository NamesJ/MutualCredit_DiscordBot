class AccountIDError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class MinBalanceError(Exception):

    def __init__(self, account_id, tx_id, min_balance):
        self.message = f'Transaction "{tx_id}" would put buyer account \
                            "{account_id}" balance below minimum of {min_balance}'
        super().__init__(self.message)


class MaxBalanceError(Exception):

    def __init__(self, account_id, tx_id, max_balance):
        self.message = f'Transaction "{tx_id}" would put seller account \
                            "{account_id}" balance above maximum of {max_balance}'
        super().__init__(self.message)


class SelfTransactionError(Exception):

    def __init__(self, account_id):
        self.message = f'Account {account_id} tried to transact with itself.'
        super().__init__(self.message)


class OfferIDError(Exception):

    def __init__(self, account_id, offer_id):
        self.message = f'Account "{account_id}" does not have an offer with ID "{offer_id}"'
        super().__init__(self.message)


class TransactionIDError(Exception):

    def __init__(self, tx_id):
        self.message = f'Transaction with ID "{tx_id}" does not exist.'
        super().__init__(self.message)


class TransactionStatusError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class UserPermissionError (Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
