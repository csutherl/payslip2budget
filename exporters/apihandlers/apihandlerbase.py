class APIHandlerBase:
    def __init__(self, config):
        self.config = config

    def send_transactions(self, transactions):
        raise NotImplementedError("This method should be implemented by subclasses.")
