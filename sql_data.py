import os

import sqlalchemy as db

engine = db.create_engine('sqlite:///repair_requests.db')
connection = engine.connect()
metadata = db.MetaData()
requests = db.Table('requests', metadata,
                    db.Column('request_id', db.Integer, primary_key=True),
                    db.Column('teacher_name', db.Text,),
                    db.Column('address', db.Integer),
                    db.Column('cabinet', db.Text),
                    db.Column('message', db.Text),
                    db.Column('request_time', db.Text),
                    db.Column('telegram_id', db.Integer),
                    db.Column('status', db.Boolean))

metadata.create_all(engine)


def insert_in_db(name: str, address: int, cabinet: str, message: str, request_time: str, telegram_id: int,
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


#insert_in_db("Ss", 1, "2", "mess", "rT", 213123, True)


def get_txt_requests() -> str:
    select_all_query = db.select(requests)
    select_all_result = connection.execute(select_all_query)
    output = '\n'.join(str(row) for row in select_all_result)
    req_txt = open("req.txt", "w+")
    req_txt.write(output)
    req_txt.close()
    file_path = os.path.realpath("req.txt")
    return file_path


# Закрываем соединение и освобождаем ресурсы
# connection.close()
# engine.dispose()
