class APIHandlerBase:
    def __init__(self, config, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run

    def send_transactions(self, transactions):
        raise NotImplementedError("This method should be implemented by subclasses.")
