from system.connection.Postgre import Postgre as PostgreSystem


class Postgre(PostgreSystem):
    # Взять поля таблицы
    async def connection(self):
        if res := await super().connection():
            await self.sql("create sequence if not exists counter_1 increment 1 start 1")
        return res

    async def get_counter(self):
        res = await self.sql("select nextval('counter_1')")
        return res[0]['nextval']
