import os
from datetime import datetime

import pytz

from dictionary import address, status

from errors import ImportEmpty


def convert_time_to_gmt5(timestamp: int) -> str:
    """
          Covert timestamp to GMT 5

          with template %d.%m.%Y %H:%M

          :param timestamp: text into file
          :type timestamp: int
          :return: Return time in GMT 5
          :rtype: str
          """g
    ekb_timezone = pytz.timezone('Asia/Yekaterinburg')
    current_datetime = datetime.fromtimestamp(timestamp, tz=ekb_timezone)
    formatted_datetime = current_datetime.strftime('%d.%m.%Y %H:%M')
    return formatted_datetime


def formatting_request(select_all_result) -> str:
    output_lines = []

    for row in select_all_result:
        formatted_datetime = convert_time_to_gmt5(row[5])
        formatted_row = (f"Ключ: {row[0]}, Имя педагога: {row[1]}, Адрес: {address[row[2]]}, Кабинет: {row[3]}, "
                         f"Сообщение: {row[4]}, Дата: {formatted_datetime}, TG_ID: {row[6]}, Статус: {status[row[7]]}")
        output_lines.append(formatted_row)

    output = '\n'.join(output_lines)
    return output


def create_txt(into: str, filename="req.txt") -> str:
    """
      Create txt file

      Require two params, string into, and file name

      :param into: text into file
      :type into: str
      :param filename: Name of a file:
      :type filename: str
      :return: realpath of created file
      :rtype: str
      """

    if not into:
        raise ImportEmpty

    req_txt = open(filename, "w+")
    req_txt.write(into)
    req_txt.close()

    file_path = os.path.realpath("req.txt")
    return file_path
