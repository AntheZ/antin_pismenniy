# pip install gspread oauth2client
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_credentials.json', scope)
client_gs = gspread.authorize(creds)
sheet = client_gs.open('YOUR_SPREADSHEET_NAME').sheet1

@client.on(events.NewMessage(chats='CHANNEL_USERNAME'))
async def handler(event):
    message = event.message.text
    sheet.append_row([message])

client.start(phone)
client.run_until_disconnected()
