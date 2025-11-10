class DataMapper:
    def __init__(self, log=None):
        self.log = log

    def map_log_data(self, log_data):
        if self.log:
            self.log.log_info("map_log_data() not implemented in skeleton")
        return None
