from system.module.RabbitErrors import RabbitErrors


class WebErrors(RabbitErrors):
    def __init__(self, error_list=None):
        super().__init__(error_list)
        self.status = 200

    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status
