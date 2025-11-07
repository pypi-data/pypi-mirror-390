from app.module.validate_json_header import MessageHeaderCounter

from system.module.Validator import Validator
from system.worker.BaseWorker import BaseWorker


validator = Validator()


class MyCounter(BaseWorker):
    @validator.validate(validate_header=MessageHeaderCounter)
    async def main(self, route, msg_obj, message_num, **kwargs):
        # rabbit_json = self.rabbitmq.gen_msg(
        #     msg_obj.system_from, msg_obj.object, f"{msg_obj.action}_reply", msg_obj.reference_id, None, {'id': 1})
        # await self.rabbitmq.publish(f"{rabbit_json['object']}.{rabbit_json['action']}", rabbit_json)
        await self.rabbitmq.publish_reply(msg_obj, None, {'id': await self.db.get_counter()})
        return True


# {
#   "action": "get_counter",
#   "object": "mycounter",
#   "priority": "1",
#   "system_from": "temp",
#   "system_to": "mycounter",
#   "message_id": "bc3aae6a-1bc4-4a0b-a35d-22edf186eb06",
#   "api_version": "1.0",
#   "reference_id": "bc3aae6a-1bc4-4a0b-a35d-22edf186eb06",
#   "datetime_created": "2023-03-28T14:22:50"
# }
