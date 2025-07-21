import gspread
from google.oauth2.service_account import Credentials

# Настройка авторизации
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file("src/data/secrets/krekbottable-9a40985c56e2.json", scopes=SCOPES)
client = gspread.authorize(creds)

# Открываем таблицу по названию или ID
spreadsheet = client.open_by_key("16t28W1nlexAS-J26Mk18EgtPUX3344XdB18c5glA3Fg")

# Выбираем лист
sheet = spreadsheet.worksheet("Ответы на форму")  # имя листа, например "Sheet1"

# Получаем все значения в виде списка списков
data = sheet.get_all_values()

# Печатаем
for row in data:
	print(row)