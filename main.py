import requests

from datetime import date
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

SATURDAY = 5
SUNDAY = 6

cancha_sede = {2280:'Cancha 1', 2281:'Cancha 2', 2975:'Cancha 3',}

def create_text(horarios_sabado, horarios_domingo):
    """
    Crea lista con los horarios para sabado y domingo
    Args:
        horarios_*: lista de horarios para el dia *
    Returns:
        text: ej.   sabado:
                        17:00 (Cancha 1)
                        18:00 (Cancha 2)
                    domingo:
                        16:00 (Cancha 3)
    """
    text = "Sábado: \n"
    for horario in horarios_sabado:
        text += '\t' + horario + '\n'
    text += 'Domingo: \n'
    for horario in horarios_domingo:
        text += '\t' + horario + '\n'
    return text

def get_weekday(dia):
    weekday = datetime.date(year=int(dia.split('-')[0]), month=int(dia.split('-')[1]), day=int(dia.split('-')[2])).weekday()
    return weekday

def check_for_spots_in_poli():
    """
    Chequea si hay turnos en el poli para los dias sabados y domingos.
    Devuelve texto con los horarios encontrados
    """
    POLI_URL_DATES = f'https://formulario-sigeci.buenosaires.gob.ar/FechasDisp'
    POLI_URL_HOURS = f'https://formulario-sigeci.buenosaires.gob.ar/getHorasDisp'
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    CHAT_ID = os.environ.get('CHAT_ID')

    sedes = [2280, 2281, 2975]
    dias_sedes = {2280: [], 2281: [], 2975: []}
    horarios_finde = {'sabado': [], 'domingo': []}

    today = date.today() # yyyy_mm_dd

    for sede in sedes:
        DATE_URL = f'{POLI_URL_DATES}?fromDate={today}&sedes={sede}&servicioId=3151'
        cancha = cancha_sede[sede] 
        try:
            response = requests.get(DATE_URL)
            dias_sedes[sede] = response.json()

            for dia in dias_sedes[sede]:
                dia_int = get_weekday(dia)
                print(dia_int)
                if (dia_int == SATURDAY or dia_int == SUNDAY):
                    dia_del_finde = 'sabado' if dia_int == SATURDAY else 'domingo'
                    response_horas = requests.get(f'{POLI_URL_HOURS}?day={dia}&sedeId={sede}&servicioId=3151')
                    response_horas = response_horas.json()

                    for hour in response_horas:
                        time = hour.split('T')[1][:5]
                        horarios_finde[dia_del_finde].append(time + f' - ({cancha})')
        except Exception as e:
            print(e)
    
    horarios_finde['sabado'] = sorted(set(horarios_finde['sabado']))
    horarios_finde['domingo'] = sorted(set(horarios_finde['domingo']))

    text = create_text(horarios_finde['sabado'], horarios_finde['domingo'])
    return text



from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters


BOT_TOKEN = os.environ.get('BOT_TOKEN')
print(BOT_TOKEN)
updater = Updater(BOT_TOKEN,
                  use_context=True)
  
  
def turnos_poli(update: Update, context: CallbackContext):
    update.message.reply_text(check_for_spots_in_poli())

updater.dispatcher.add_handler(CommandHandler('turnos_poli', turnos_poli))

updater.start_polling()