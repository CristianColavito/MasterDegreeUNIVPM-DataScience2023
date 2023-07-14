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



class Validate_modifica_prenotazione_form(FormValidationAction):

     def name(self) -> Text:
         return "validate_modifica_prenotazione_form"
     

     def validate_data(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:    
            try:
                with open("Prenotazioni.json", "r")as f:
                    dict_pren= json.load(f)
                now= datetime.today().strftime('%Y-%m-%d')
                if datetime.strptime(slot_value, '%Y-%m-%d') and now <= slot_value and slot_value in dict_pren['giorno']:
                    return {"data":slot_value}
                else:
                    dispatcher.utter_message(text = "Non ci sono appuntamenti per questa data")
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
               if flag== True:
                    return {"recapito": slot_value}
               else:
                    dispatcher.utter_message(text= "Il numero non è registrato per la data scelta")
                    return{"recapito": None}
          else:
               dispatcher.utter_message(text="Il numero inserito non è registrato")
               return {"recapito": None}
               
              
         except:
             dispatcher.utter_message(text="Il numero di telefono sembra sbagliato")
             return { "recapito": None} 

     def validate_data_mod(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
            try:
                now= datetime.today().strftime('%Y-%m-%d')
                if datetime.strptime(slot_value, '%Y-%m-%d') and now <= slot_value:
                    with open("Prenotazioni.json", "r")as f:
                        dict_pren= json.load(f)
                    if slot_value in dict_pren["giorno"]:
                        lista_orari = [k for k, v in dict_pren["giorno"][slot_value]["turno"].items() if v == {}] 
                        if lista_orari==[]:
                            dispatcher.utter_message(text = "Per questo giorno non ci sono turni disponibili, inserisci un altra data per prenotare")
                            return {"data_mod": None}
                        else:
                            return {"data_mod":slot_value}
                    else: 
                        return {"data_mod":slot_value}

                    
                    
                else:
                    dispatcher.utter_message(text = "La tua data non è stata inserita correttamente, controlla che sia una data prenotabile oppure controlla il formato. Ecco un esempio di data inserita correttamente: 2035-08-15")
                    return {"data_mod": None}

            except:
                dispatcher.utter_message(text = "Errore inserimento data")
                return {"requested_slot": None}


     def validate_orario(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]: 
         if slot_value=="None":
             
            return {"orario":None,"conferma_data":None, "data_mod": None, "conferma_orario": None, "orario": None}
         else: 
             return {"orario":slot_value}
         

     def validate_conferma_data(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]: 
         if slot_value != None:
             return {"conferma_data": slot_value}
         else:
             return {"conferma_data":None}
         

     def validate_conferma_orario(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]: 
         if slot_value != None:
             return {"conferma_orario": slot_value}
         else:
             return {"conferma_orario":None}    
         
     def validate_conferma_taglio(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]: 
         if slot_value != None:
             return {"conferma_taglio": slot_value}
         else:
             return {"conferma_taglio":None}  
    

         

     async def required_slots(self, domain_slots: List[Text], dispatcher: "CollectingDispatcher", tracker: "Tracker", domain: "DomainDict",) -> List[Text]:
        updated_slots = domain_slots.copy()
        if tracker.get_slot("conferma_data") is False:
            updated_slots.remove("data_mod")
            if tracker.get_slot("conferma_orario") is None:
                return updated_slots
            elif tracker.get_slot("conferma_orario") is True:
                if tracker.get_slot('conferma_taglio') is None:
                    return updated_slots
                elif tracker.get_slot('conferma_taglio') is True:
                    return updated_slots
                else: 
                    updated_slots.remove("taglio")
                    return updated_slots
            else:
                updated_slots.remove("orario")
                if tracker.get_slot('conferma_taglio') is None:
                    return updated_slots
                elif tracker.get_slot('conferma_taglio') is True:
                    return updated_slots
                else: 
                    updated_slots.remove("taglio")
                    return updated_slots

        elif tracker.get_slot("conferma_data") is True:
            updated_slots.remove("conferma_orario")
            if tracker.get_slot('conferma_taglio') is None:
                return updated_slots
            elif tracker.get_slot('conferma_taglio') is True:
                return updated_slots
            else:
                updated_slots.remove("taglio")
                return updated_slots
        else:
            return updated_slots
        



class AskForSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_modifica_prenotazione_form_orario"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict,):
        with open("Prenotazioni.json", "r")as f:
            dict_pren= json.load(f)
        if tracker.get_slot("data_mod") != None:
            data= tracker.get_slot('data_mod')
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
        else:
            data= tracker.get_slot('data')
            lista_orari = [k for k, v in dict_pren["giorno"][data]["turno"].items() if v == {}] 
            if lista_orari==[]:
                dispatcher.utter_message(text = "Per questo giorno non ci sono turni disponibili")
                return {"conferma_data": None}
            else:
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
               dispatcher.utter_message(text= "Scegli un orario",buttons= list_buttons, button_type="vertical")

          else:
               for orario in lista_orari:
                    list_buttons.append({'payload': '/inserimento_orario{"orario": "' + orario + '"}', 'title': orario})
               list_buttons.append({'payload': '/inserimento_orario{"orario":"None"}', 'title': 'Voglio cambiare data'})
               dispatcher.utter_message(text= "Scegli un orario",buttons= list_buttons, button_type="vertical")
               
        
          return []
 


class Modifica_prenotazione(Action):
    def name(self) -> Text:
        return "modifica_prenotazione"
    

    async def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict)-> List[Dict[Text, Any]]:
     if tracker.get_slot("conferma"):
        data= tracker.get_slot("data")
        numero= tracker.get_slot('recapito')
        data_mod= tracker.get_slot("data_mod")
        orario_mod= tracker.get_slot("orario")
        taglio_mod= tracker.get_slot("taglio")
        with open("Prenotazioni.json", "r", encoding="utf-8")as f:
            dict_pren= json.load(f)
        if data_mod== None and orario_mod == None and taglio_mod==None:
            return[]
        elif data_mod==None and (orario_mod != None or taglio_mod != None):
            for k in dict_pren['giorno'][data]['turno'].keys():
                if dict_pren['giorno'][data]['turno'][k] and numero in dict_pren['giorno'][data]['turno'][k].values():
                    taglio_vecchio= list(dict_pren['giorno'][data]['turno'][k].values())[3]
                    orario_vecchio= k
                    nome=list(dict_pren['giorno'][data]['turno'][k].values())[0]
                    cognome= list(dict_pren['giorno'][data]['turno'][k].values())[1]
            if orario_mod==None:
               dict_pren['giorno'][data]['turno'][orario_vecchio]['taglio']=taglio_mod
            else:
               dict_pren['giorno'][data]['turno'][orario_vecchio]={}
               dict_pren['giorno'][data]['turno'][orario_mod]['nome']=nome
               dict_pren['giorno'][data]['turno'][orario_mod]['cognome']=cognome
               dict_pren['giorno'][data]['turno'][orario_mod]['recapito']=numero
               if taglio_vecchio != taglio_mod and taglio_mod!= None:
                    dict_pren['giorno'][data]['turno'][orario_mod]['taglio']=taglio_mod
               else:
                      dict_pren['giorno'][data]['turno'][orario_mod]['taglio']=taglio_vecchio
        else:
            for k in dict_pren['giorno'][data]['turno'].keys():
                    if dict_pren['giorno'][data]['turno'][k] and numero in dict_pren['giorno'][data]['turno'][k].values():
                        taglio_vecchio= list(dict_pren['giorno'][data]['turno'][k].values())[3]
                        orario_vecchio= k
                        nome=list(dict_pren['giorno'][data]['turno'][k].values())[0]
                        cognome= list(dict_pren['giorno'][data]['turno'][k].values())[1]
            dict_pren['giorno'][data]['turno'][orario_vecchio]={}
            dict_pren['giorno'][data_mod]['turno'][orario_mod]['nome']=nome
            dict_pren['giorno'][data_mod]['turno'][orario_mod]['cognome']=cognome
            dict_pren['giorno'][data_mod]['turno'][orario_mod]['recapito']=numero
            if taglio_vecchio != taglio_mod and taglio_mod!= None:
                    dict_pren['giorno'][data_mod]['turno'][orario_mod]['taglio']=taglio_mod
            else:
                    dict_pren['giorno'][data_mod]['turno'][orario_mod]['taglio']=taglio_vecchio
        flag = False
        for x in dict_pren['giorno'][data]['turno'].values():
            
            if x != {}:
                  flag=True
        if flag==False:
             del dict_pren['giorno'][data]

        with open("Prenotazioni.json", "w") as f:
            json.dump(dict_pren, f,indent=4)

        dispatcher.utter_message(text="Grazie per aver inserito i tuoi dati. L'operazione si è conclusa con successo.")
     else:
         dispatcher.utter_message(text="L'operazione non ha avuto successo")