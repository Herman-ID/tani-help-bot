import requests
from bottle import Bottle, response, request as bottle_request
import pyowm
from firebase import firebase
import wikipediaapi

class BotHandlerMixin:

    BOT_URL = None

    def get_chat_id(self, data):
        chat_id = data['message']['chat']['id']
        return chat_id

    def get_hama(self, data):
        wiki_wiki = wikipediaapi.Wikipedia('id')
        ln = len(data.split(' '))
        try :
            xfirebase = firebase.FirebaseApplication('https://tanihelp-id.firebaseio.com', None)
            result = xfirebase.get('/hama', None)
            if ln == 1 :
                kata = "berikut daftar hama tersedia, silahkan ketikan /hama namahama untuk detail:\n\n"
                for index, key in enumerate(result):
                    kata += "{0}. {1}\n".format(index+1, key['nama'])
                return kata
            else :
                hama = data.split(' ')[1]
                for item in result :
                    if hama == item['nama']:
                        page_py = wiki_wiki.page(item['link'])
                        return page_py.summary[0:300] + "...\n\n\nlebih lanjut : " +page_py.fullurl
                    else:
                        return "maaf {0} tidak ada dalam database kami".format(hama)
        except:
            return "salah"

    def get_message(self, data):
        message_text = data['message']['text']

        return message_text

    def send_message(self, prepared_data):
        message_url = self.BOT_URL + 'sendMessage'
        requests.post(message_url, json=prepared_data)

    def get_weather(self, city):
        ln = len(city.split(' '))
        if ln == 1:
            return "Masukan nama kota"
        else:
            owm = pyowm.OWM('1789aa89c04361a84efad4f11fc3c110')
            observation = owm.weather_at_place(city.split(' ')[1])
            w = observation.get_weather()
            wind = w.get_wind()
            temp = w.get_temperature('celsius')
            cloud = w.get_clouds()
            status = w.get_status()
            if status == "Clouds":
                status = "berawan"
            return ("Cuaca untuk {0} adalah : \n\nstatus : {1}\nsuhu : {2} C\nawan : {3}\nkecepatan angin : {4}\narah angin : {5}".format(city.split(' ')[1], status, temp['temp'], cloud, wind['speed'], wind['deg']))


class TelegramBot(BotHandlerMixin, Bottle):
    BOT_URL = 'https://api.telegram.org/bot645521822:AAHuphQaQ0f1loHHl1EARMQHOSVNfm4KeaU/'

    def __init__(self, *args, **kwargs):
        super(TelegramBot, self).__init__()
        self.route('/', callback=self.post_handler, method="POST")

    def change_text_message(self, text, data):
        term = text.split(' ')[0]
        if(term == "/cuaca"):
            return self.get_weather(text)
        elif(term == "/start"):
            return "Hai!!! ini adalah bot Tani Help\ngunakan /help untuk mengetahui perintah apa saja yang bisa dilakukan !!!"
        elif(term == "/help"):
            return "Saya bisa membantu anda mengetahui cuaca dan hama. silahkan ketikkan perintah berikut: \n /cuaca nama_kota - mengetahui cuaca di sebuah kota\n/hama - melihat database hama\n /hama nama_hama - melihat detail mengenai hama tersebut"
        elif(term=="/hama"):
            return self.get_hama(text)
        else:
            return "maaf tidak diketahui :("

    def prepare_data_for_answer(self, data):
        message = self.get_message(data)
        answer = self.change_text_message(message, data)
        chat_id = self.get_chat_id(data)
        json_data = {
            "chat_id": chat_id,
            "text": answer,
        }

        return json_data

    def post_handler(self):
        data = bottle_request.json
        answer_data = self.prepare_data_for_answer(data)
        self.send_message(answer_data)

        return response


application = TelegramBot()