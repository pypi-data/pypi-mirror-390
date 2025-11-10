class ProductManager:
    def __init__(self, db, log):
        self.db = db
        self.log = log

    def load_products(self):
        self.log.log_info("load_products() not implemented in skeleton")
        return []
