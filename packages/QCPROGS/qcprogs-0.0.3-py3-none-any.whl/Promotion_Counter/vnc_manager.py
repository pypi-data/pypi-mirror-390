class VNCManager:
    def __init__(self, ip, user, password, log=None):
        self.ip = ip
        self.user = user
        self.password = password
        self.log = log

    def connect(self):
        if self.log:
            self.log.log_info(f"Connect VNC to {self.ip}")
        return False

    def run_commands(self, commands):
        if self.log:
            self.log.log_info("run_commands() not implemented in skeleton")
