import asyncio

from system.connection.Cron import Cron


class CronPrint(Cron):
    async def cron_work(self):
        hour = self.values.get('hour_run', 0)
        while True:
            await self.sleep_up_to_start_cron_hour('тест', hour, self.db.datetime_now())

    async def cron_run(self):
        try:
            await self.cron_work()
        except Exception as err:
            await self.dispatcher.stop(f"{err.__class__.__name__}: {err}")

    async def connection(self):
        self.logger.debug('Старт крона')
        asyncio.ensure_future(self.cron_run())
        return True
