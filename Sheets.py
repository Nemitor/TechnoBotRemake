import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

credentials_file = 'credentials.json'
spreadsheet_id = '12WcDQ3_Gtxl18dK3Vfg83yEh2MleKjg8Jqq3facPNpo'

scopes = ['https://www.googleapis.com/auth/spreadsheets']

credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scopes)

http_auth = credentials.authorize(httplib2.Http())
sheets_service = build('sheets', 'v4', http=http_auth)

range_name = 'Tasks'
result = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
values = result.get('values', [])

if not values:
    # Если таблица пуста, начнем с первой строки
    next_row = 1
else:
    # Иначе, найдем первую пустую строку
    next_row = len(values) + 1


def set_new_sheet_data(user_data):
    new_data = ["Имя педагога", "Корпус", "Кабинет", "Сообщение", "Телеграм ID", "Время"]
    range_name = 'Tasks'  # Указываем только имя листа
    body = {'values': [new_data]}


    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        body=body,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS"
    ).execute()

print(f"Добавлена новая строка в таблицу: {range_name}")