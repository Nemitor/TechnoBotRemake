import os
from datetime import datetime

import sqlalchemy as db

from dictionary import address, status
from errors import EmptyBase, IdNotExsist

engine = db.create_engine('sqlite:///repair_requests.db')
connection = engine.connect()
metadata = db.MetaData()
requests = db.Table('requests', metadata,
                    db.Column('request_id', db.Integer, primary_key=True),
                    db.Column('teacher_name', db.Text, ),
                    db.Column('address', db.Integer),
                    db.Column('cabinet', db.Text),
                    db.Column('message', db.Text),
                    db.Column('request_time', db.Integer),
                    db.Column('telegram_id', db.Integer),
                    db.Column('status', db.Boolean))

metadata.create_all(engine)


def insert_in_db(name: str, address: int, cabinet: str, message: str, request_time: int, telegram_id: int,
                 status: bool):
    query = requests.insert().values(
        teacher_name=name,
        address=address,
        cabinet=cabinet,
        message=message,
        request_time=request_time,
        telegram_id=telegram_id,
        status=status
    )
    connection.execute(query)
    connection.commit()


def get_txt_requests() -> str:
    select_all_query = db.select(requests)
    select_all_result = connection.execute(select_all_query)

    output_lines = []

    for row in select_all_result:
        current_datetime = datetime.fromtimestamp(row[5])
        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')
        formatted_row = (f"Ключ: {row[0]}, Имя педагога: {row[1]}, Адрес: {address[row[2]]}, Кабинет: {row[3]}, "
                         f"Сообщение: {row[4]}, Время: {formatted_datetime}, TG_ID: {row[6]}, Статус: {status[row[7]]}")
        output_lines.append(formatted_row)

    output = '\n'.join(output_lines)

    if not output_lines:
        raise EmptyBase

    req_txt = open("req.txt", "w+")
    req_txt.write(output)
    req_txt.close()

    file_path = os.path.realpath("req.txt")
    return file_path


def get_active_status(id):
    if id == 0:
        query = db.select(requests).where(requests.c.status == True)
    else:
        query = db.select(requests).where((requests.c.address == id) & (requests.c.status == True))

    result = connection.execute(query)
    rows = result.fetchall()
    return rows


def change_status(req_id: int) -> int:
    select_query = db.select(requests).where(requests.c.request_id == req_id)
    result = connection.execute(select_query).fetchone()

    if result is None:
        raise IdNotExsist

    update_query = db.update(requests).where(requests.c.request_id == req_id).values(status=False)
    connection.execute(update_query)
    connection.commit()
    return result[6]

def main():

    change_status(3)


if __name__ == '__main__':
    main()
