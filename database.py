import sqlalchemy as db

from errors import IdNotExists, EmptyBase, StatusAlreadyFalse

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
    result = connection.execute(query)
    connection.commit()
    return result.lastrowid


def get_all_requests():
    select_all_query = db.select(requests)
    select_all_result = connection.execute(select_all_query)

    if not select_all_result:
        raise EmptyBase

    return select_all_result


def get_active_status(id):
    if id == 0:
        query = db.select(requests).where(requests.c.status == True)
    else:
        query = db.select(requests).where((requests.c.address == id) & (requests.c.status == True))

    result = connection.execute(query)
    rows = result.fetchall()
    return rows


def change_status(req_id: int):
    select_query = db.select(requests).where(requests.c.request_id == req_id)
    result = connection.execute(select_query).fetchone()

    if result is None:
        raise IdNotExists

    if result[7] is False:
        raise StatusAlreadyFalse

    update_query = db.update(requests).where(requests.c.request_id == req_id).values(status=False)
    connection.execute(update_query)
    connection.commit()
    return result
