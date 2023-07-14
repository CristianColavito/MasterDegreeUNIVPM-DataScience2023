from typing import Any, Text, Dict, List
import rasa_sdk
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import json
import datetime
from datetime import datetime
import phonenumbers
from rasa_sdk.events import SlotSet
from rasa_sdk.events import AllSlotsReset

class ValidatePrenotazioneForm(FormValidationAction):

     def name(self) -> Text:
         return "validate_colleziona_dati_prenotazione_form"
     
     def validate_recapito(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
         try:
          slot_value=int(slot_value)
          slot_value=str(slot_value)
          numero= phonenumbers.parse(slot_value, "IT")
          if phonenumbers.is_valid_number(numero):
               return {"recapito":slot_value}
          else:
               dispatcher.utter_message(text="Il numero inserito non è corretto")
               return {"recapito": None}             
              
         except:
             dispatcher.utter_message(text="Il numero di telefono sembra sbagliato")
             return { "recapito": None} 
          
          

         

     def validate_data(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:    
            try:
                now= datetime.today().strftime('%Y-%m-%d')
                if datetime.strptime(slot_value, '%Y-%m-%d') and now <= slot_value:
                    with open("Prenotazioni.json", "r")as f:
                        dict_pren= json.load(f)
            
                    if slot_value in dict_pren["giorno"]:
                        lista_orari = [k for k, v in dict_pren["giorno"][slot_value]["turno"].items() if v == {}] 
                        if lista_orari==[]:
                            dispatcher.utter_message(text = "Per questo giorno non ci sono turni disponibili, inserisci un altra data per prenotare")
                            return {"data": None}
                        else:
                            return {"data":slot_value}
                    else:
                        return {"data":slot_value}
                else:
                    dispatcher.utter_message(text = "La tua data non è stata inserita correttamente, controlla che sia una data prenotabile oppure controlla il formato. Ecco un esempio di data inserita correttamente: 2035-08-15")
                    return {"data": None}

            except:
                dispatcher.utter_message(text = "Errore inserimento data")
                return {"data": None}

     def validate_orario(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]: 
         if slot_value=="None":
             
            return {"orario":None,"data":None}
         else: 
            return {"orario":slot_value}



class AskForSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_colleziona_dati_prenotazione_form_orario"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict,):
        with open("Prenotazioni.json", "r")as f:
            dict_pren= json.load(f)
            data= tracker.get_slot('data')
            if data in dict_pren["giorno"]:
                lista_orari = [k for k, v in dict_pren["giorno"][data]["turno"].items() if v == {}] 
                self.scegli_orari(tracker,dispatcher, lista_orari,data)

            else:
                dict_pren["giorno"][data] = {"turno": {"8-9":{},"9-10":{},"10-11":{},"11-12":{},"12-13":{},"14-15":{},"15-16":{},"17-18":{},"18-19":{}}}
                lista_orari = [k for k, v in dict_pren["giorno"][data]["turno"].items() if v == {}]
                with open("Prenotazioni.json","w")as f:
                    json.dump(dict_pren, f,indent=4)
                self.scegli_orari(tracker,dispatcher, lista_orari,data)
                return []


    def scegli_orari(self, tracker, dispatcher, lista_orari,data):
            list_buttons=[]
            now= datetime.today().strftime('%Y-%m-%d')
            ora=datetime.now().strftime('%H')
            if str(now)==data:
                for orario in lista_orari:
                    limite_orario =  orario.split('-',1)
                    if int(limite_orario[0])>int(str(ora)):
                            list_buttons.append({'payload': '/inserimento_orario{"orario": "' + orario + '"}', 'title': orario})
                list_buttons.append({'payload': '/inserimento_orario{"orario":"None"}', 'title': 'Voglio cambiare data'})
                dispatcher.utter_message(text= "Scegli un orario", buttons= list_buttons, button_type="vertical")

            else:
                for orario in lista_orari:
                    list_buttons.append({'payload': '/inserimento_orario{"orario": "' + orario + '"}', 'title': orario})
                list_buttons.append({'payload': '/inserimento_orario{"orario":"None"}', 'title': 'Voglio cambiare data'})
                dispatcher.utter_message(text= "Scegli un orario", buttons= list_buttons, button_type="vertical")  
        
            return []

             
class Prenotazione(Action):
     def name(self) -> Text:
         return "scrivi_prenotazione"
     

     async def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict)-> List[Dict[Text, Any]]:
          if tracker.get_slot("conferma"):
            nome = tracker.get_slot("nome")
            cognome = tracker.get_slot("cognome")
            recapito = tracker.get_slot("recapito")
            taglio = tracker.get_slot("taglio")
            data = tracker.get_slot("data")
            orario = tracker.get_slot("orario")
            with open("Prenotazioni.json", "r") as f:
                dict_pren=json.load(f)
            dict_pren["giorno"][data]["turno"][orario]["nome"]=nome
            dict_pren["giorno"][data]["turno"][orario]["cognome"]=cognome
            dict_pren["giorno"][data]["turno"][orario]["recapito"]=recapito
            dict_pren["giorno"][data]["turno"][orario]["taglio"]=taglio
            with open("Prenotazioni.json","w")as f:
                json.dump(dict_pren, f,indent=4)

            dispatcher.utter_message(text="Grazie per aver inserito i tuoi dati. L'operazione si è conclusa con successo.")
            return [AllSlotsReset()]

          else:
              dispatcher.utter_message(text="L'operazione non ha avuto successo")

