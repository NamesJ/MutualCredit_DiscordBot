class AccountIDError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class MinBalanceError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class MaxBalanceError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class SelfTransactionError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class OfferIDError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class TransactionIDError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class TransactionStatusError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class UserPermissionError (Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
