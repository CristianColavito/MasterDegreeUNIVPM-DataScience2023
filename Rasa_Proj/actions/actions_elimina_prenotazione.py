from typing import Any, Text, Dict, List
import rasa_sdk
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import json
import datetime
from datetime import datetime
import phonenumbers


class Validate_elimina_prenotazione_form(FormValidationAction):

     def name(self) -> Text:
         return "validate_elimina_prenotazione_form"
     

     def validate_data(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:    
            try:
                with open("Prenotazioni.json", "r")as f:
                    dict_pren= json.load(f)
                now= datetime.today().strftime('%Y-%m-%d')
                if datetime.strptime(slot_value, '%Y-%m-%d') and now <= slot_value and slot_value in dict_pren['giorno']:
                    return {"data":slot_value}
                else:
                    dispatcher.utter_message(text = "La tua data non è registrata, oppure controlla di aver rispettato il formato")
                    return {"data": None}

            except:
                dispatcher.utter_message(text = "Errore inserimento data")
                return {"data": None}





     def validate_recapito(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
         try:
          slot_value=int(slot_value)
          slot_value=str(slot_value)
          data=tracker.get_slot('data')
          numero= phonenumbers.parse(slot_value, "IT")
          if phonenumbers.is_valid_number(numero):
               with open("Prenotazioni.json","r",encoding="utf-8") as f:
                   dict_pren=json.load(f)
               flag= False
               for k in dict_pren['giorno'][data]['turno'].keys():

                    if dict_pren['giorno'][data]['turno'][k]:
                        list(dict_pren['giorno'][data]['turno'][k].values())

                        if slot_value in list(dict_pren['giorno'][data]['turno'][k].values()):
                            flag=True
               if flag == True:
                   return {"recapito": slot_value}
               else: 
                   dispatcher.utter_message(text="il numero inserito non è presente per la data inserita")
                   return{"recapito": None}
                        
                        
          else:
               dispatcher.utter_message(text="Il numero inserito non è registrato")
               return {"recapito": None}
               #return {"recapito": None ,"cognome":None}
                
              
         except:
             dispatcher.utter_message(text="Il numero di telefono sembra sbagliato")
             return { "recapito": None} 
         




class Elimina_prenotazione(Action):
    def name(self) -> Text:
        return "elimina_prenotazione"
    

    async def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict)-> List[Dict[Text, Any]]:
     if tracker.get_slot("conferma"):
        data= tracker.get_slot("data")
  

        numero= tracker.get_slot('recapito')

        with open("Prenotazioni.json", "r") as f:
            dict_pren=json.load(f)
        for k in dict_pren['giorno'][data]['turno'].keys():
            if dict_pren['giorno'][data]['turno'][k] != {} and numero in dict_pren['giorno'][data]['turno'][k].values():
                dict_pren['giorno'][data]['turno'][k]={}

        flag = False
        for x in dict_pren['giorno'][data]['turno'].values():
            
            if x != {}:
                  flag=True
        if flag==False:
             del dict_pren['giorno'][data]

        with open("Prenotazioni.json", "w") as f:
            json.dump(dict_pren, f,indent=4)
        dispatcher.utter_message(text= "L'operazione si è conclusa con successo")
     else: 
         dispatcher.utter_message(text="L'operazione non ha avuto successo")
