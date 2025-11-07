import re
from datetime import datetime

import asyncpg

from system.connection.BaseConnection import BaseConnection
from system.module.my_json import json_dumps
from system.module.other import dsn_hide_password


class Postgre(BaseConnection):
    def __init__(self, params):
        super().__init__(params)
        self.pool = None

    async def connection(self):
        connection_txt = f"{self.connection_name} = Postgre({dsn_hide_password(self.values['dsn'])})"
        try:
            self.pool = await asyncpg.create_pool(**self.values)
            self.logger.info(f"Успешное соединение: {connection_txt}")
            return True
        except Exception as err:  # (OSError, TypeError, asyncpg.exceptions.InvalidPasswordError)
            self.logger.error(f"Ошибка соединения: {connection_txt}: {err}")
            return False

    @staticmethod
    def datetime_now():
        return datetime.now()

    @staticmethod
    def escape_str(s: str):
        return s.replace("'", '"').replace(';', '').replace('--', '')  # re.escape

    # Формирование WHERE в SQL запросе по переданному словарю.
    # Пример:
    # data_if -> {"info":"OK","id>":100,"text is NULL":None }
    # Результат: ("info=$1 AND id>$2 AND text is NULL", ['OK', 100])
    @staticmethod
    def where_sql(data_if: dict, start_i: int = 1, delimiter: str = ' AND '):
        i = start_i
        sql_data, values = [], []
        is_delimiter_comma = ',' in delimiter
        for field, value in data_if.items():
            sign = ''
            if is_delimiter_comma and isinstance(value, (tuple, set, list)):
                value = json_dumps(list(value))
            if isinstance(value, (tuple, set, list)):
                if not value:
                    continue
                tmp = []
                for item in value:
                    tmp.append(f"${i}")
                    values.append(item)
                    i += 1
                str_eq_value = f" IN({','.join(tmp)})"
            else:
                if field[-1] not in ('>', '<', '='):
                    sign = "="
                if value in (None, '') and field.find(' ', 1) > -1:
                    sign = ""
                    str_eq_value = ""
                else:
                    str_eq_value = f"${i}"
                    if isinstance(value, dict):
                        values.append(json_dumps(value))
                    else:
                        values.append(value)
                    i += 1
            sql_data.append(f"{field}{sign}{str_eq_value}")
        return delimiter.join(sql_data), values, i

    def where_sql_txt(self, data_if, delimiter=' AND '):
        where_sql, where_values, _ = self.where_sql(data_if=data_if, delimiter=delimiter)
        return re.sub(r'\$\d+', '{}', where_sql).format(
            *[f"'{where_value}'" if isinstance(where_value, str) else where_value for where_value in where_values])

    # UPDATE name_table
    async def update(
            self, name_table: str, set_dict: dict, where_dict: dict | None = None, returning_name: str = 'id'):
        if where_dict is None:
            where_dict = {}
        where_sql = ''
        set_dict['dt_updated'] = self.datetime_now()
        set_sql, values_sql, start_i = self.where_sql(set_dict, 1, ', ')
        if where_dict:
            where_sql, where_values, _ = self.where_sql(where_dict, start_i)
            where_sql = f" WHERE {where_sql}"
            values_sql += where_values
        sql_text = f"UPDATE {name_table} SET {set_sql}{where_sql} RETURNING {returning_name}"
        async with self.pool.acquire() as conn:
            ids = await conn.fetch(sql_text, *values_sql)
            return ids

    # Обновить запись если существует, если нет, то добавить
    async def upsert(self, name_table: str, record: dict, name_field_key: str, do_type: str = 'UPDATE',
                     returning_name: str = 'id'):
        record = {**record, 'dt_created': self.datetime_now(), 'dt_updated': self.datetime_now()}
        fields, values, values_123, i = self.values_sql(record)
        if do_type == 'UPDATE':
            del record['dt_created']
            set_sql, values_set, start_i = self.where_sql(record, i + 1, ', ')
            values += values_set
            set_txt = f" SET {set_sql}"
        else:
            set_txt = ''
        sql_text = (f"INSERT INTO {name_table}({",".join(fields)}) VALUES({",".join(values_123)}) "
                    f"ON CONFLICT ({name_field_key}) DO {do_type}{set_txt} RETURNING {returning_name}")
        async with self.pool.acquire() as conn:
            id_key = await conn.fetchval(sql_text, *values)
            return id_key

    async def upserts(self, name_table: str, records: list[dict], name_field_key: str,
                      where_dict: dict | None = None):
        """
        Одним запросом вставляет/обновляет множественное количество записей в базе данных
        :param name_field_key: Название колонки по которой проверяем существование записи в таблице - 'catalog_id'
        :param name_table: Название таблицы - 'example_table'
        :param records: Массив словарей для записи в формате - [{'column1': 'value', 'column2': 2}]
        :param where_dict: Словарь условий в формате -
        {f'EXCLUDED.dt_updated_catalog >= {table_name}.dt_updated_catalog': None}
        """
        if where_dict is None:
            where_dict = {}
        where_sql, values_sql = '', []
        if where_dict:
            where_sql, values_sql, _ = self.where_sql(where_dict)
            where_sql = f" WHERE {where_sql}"
        datetime_cur = self.datetime_now()
        list_values = []
        fields = values_123 = None
        for record in records:
            record = {**record}
            if not record.get('dt_created'):
                record['dt_created'] = datetime_cur
            if not record.get('dt_updated'):
                record['dt_updated'] = datetime_cur
            fields, values, values_123, _ = self.values_sql(record)
            list_values.append(values)
        if list_values and fields and values_123:
            params = values_sql + [value for record in list_values for value in record]
            new_values_123 = [f'{''.join(f"${value_num}")}' for value_num in range(len(params) + 1)]
            sql_values = []
            for i in range(len(values_sql) + 1, len(new_values_123), len(values_123)):
                chunk = new_values_123[i: i + len(values_123)]
                sql_values.append(f'({', '.join(map(str, chunk))})')
            sql_text = (f"INSERT INTO {name_table}({','.join(fields)}) "
                        f"VALUES {','.join(values_pack for values_pack in sql_values)} "
                        f"ON CONFLICT ({name_field_key}) "
                        f"DO UPDATE SET {', '.join([f"{field} = EXCLUDED.{field}"
                                                    for field in fields if field != 'dt_created'])} {where_sql}")
            async with self.pool.acquire() as conn:
                await conn.execute(sql_text, *params)
                return True

    def select_values_sql(self, name_table: str, where_dict: dict | None = None, fields: str | None = None,
                          end_text_sql: str | None = None):
        if where_dict is None:
            where_dict = {}
        where_sql, values_sql = '', []
        if where_dict:
            where_sql, values_sql, _ = self.where_sql(where_dict)
            where_sql = f" WHERE {where_sql}"
        if not fields:
            fields = '*'
        sql_text = f"SELECT {fields} FROM {name_table}{where_sql} {end_text_sql or ''}"
        return sql_text, values_sql

    # SELECT name_table one field
    async def select(self, name_table: str, where_dict: dict | None = None, fields: str | None = None,
                     end_text_sql: str | None = None) -> list | None:
        sql_text, values_sql = self.select_values_sql(name_table, where_dict, fields, end_text_sql)
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql_text, *values_sql)

    async def select_one(self, name_table: str, where_dict: dict | None = None, fields: str | None = None,
                         end_text_sql: str | None = None) -> dict | None:
        sql_text, values_sql = self.select_values_sql(name_table, where_dict, fields, end_text_sql)
        async with self.pool.acquire() as conn:
            if res := await conn.fetchrow(sql_text, *values_sql):
                return dict(res)

    async def select_one_field(self, name_table: str, where_dict: dict | None = None, one_field: str | None = None,
                               end_text_sql: str | None = None):
        sql_text, values_sql = self.select_values_sql(name_table, where_dict, one_field, end_text_sql)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(sql_text, *values_sql)

    @staticmethod
    def values_sql(record: dict, start_i: int = 0):
        fields, values, values_123, i = [], [], [], start_i
        for key, value in record.items():
            fields.append(key)
            if isinstance(value, (list, dict)):
                values.append(json_dumps(value))
            else:
                values.append(value)
            i += 1
            values_123.append(f'${i}')
        return fields, values, values_123, i

    # INSERT name_table
    async def insert(self, name_table: str, record: dict, end_text_sql: str | None = None):  # insert db
        datetime_cur = self.datetime_now()
        record = {**record, 'dt_created': datetime_cur, 'dt_updated': datetime_cur}
        fields, values, values_123, _ = self.values_sql(record)
        sql_text = (f"INSERT INTO {name_table}({",".join(fields)}) VALUES({",".join(values_123)}) "
                    f"{'RETURNING id' if end_text_sql is None else end_text_sql}")
        async with self.pool.acquire() as conn:
            id_key = await conn.fetchval(sql_text, *values)
            return id_key

    async def inserts(self, name_table: str, records: list[dict], end_text_sql: str | None = None):
        list_values = []
        fields = values_123 = None
        datetime_cur = self.datetime_now()
        for record in records:
            record = {**record}
            if not record.get('dt_created'):
                record['dt_created'] = datetime_cur
            if not record.get('dt_updated'):
                record['dt_updated'] = datetime_cur
            fields, values, values_123, _ = self.values_sql(record)
            list_values.append(values)
        if list_values and fields and values_123:
            sql_text = (f"INSERT INTO {name_table}({','.join(fields)}) VALUES({','.join(values_123)}) "
                        f"{end_text_sql or ''}")
            async with self.pool.acquire() as conn:
                await conn.executemany(sql_text, list_values)
                return True

    # DELETE name_table
    async def delete(self, name_table: str, where_dict: dict | None = None):
        if where_dict is None:
            where_dict = {}
        where_sql, values_sql = '', []
        if where_dict:
            where_sql, values_sql, _ = self.where_sql(where_dict)
            where_sql = f" WHERE {where_sql}"
        sql_text = f"DELETE FROM {name_table}{where_sql}"
        # print(f'{sql_text=} {values_sql=}')
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql_text, *values_sql)

    async def sql(self, sql_text: str, values_sql=None):
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql_text, *values_sql) if values_sql else await conn.fetch(sql_text)

    async def close(self):
        await self.pool.close()
