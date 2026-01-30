import requests
from icalendar import Calendar
import json
from datetime import datetime

def update_copom_from_ics():
    url = "https://www.bcb.gov.br/api/exportarics/sitebcb/agendaics?lista=Reuniões do Copom"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        gcal = Calendar.from_ical(response.content)
        meetings_dict = {}

        for component in gcal.walk():
            if component.name == "VEVENT":
                # Extrai a data de início
                dt = component.get('dtstart').dt
                if isinstance(dt, datetime):
                    dt = dt.date()
                
                # Agrupamos pelo mês/ano para identificar os dois dias da reunião
                key = dt.strftime('%Y-%m')
                if key not in meetings_dict:
                    meetings_dict[key] = []
                meetings_dict[key].append(dt.strftime('%Y-%m-%d'))

        # Para o monitor, nos interessa o ÚLTIMO dia de cada reunião (dia da decisão)
        final_dates = []
        for month in sorted(meetings_dict.keys()):
            dates = sorted(meetings_dict[month])
            decision_date = dates[-1] # Pega o segundo dia
            final_dates.append({
                "data_decisao": decision_date,
                "ano": decision_date[:4]
            })

        with open('calendario_copom.json', 'w', encoding='utf-8') as f:
            json.dump({"meetings": final_dates}, f, indent=4)
            
        print(f"Sucesso! {len(final_dates)} reuniões mapeadas.")

    except Exception as e:
        print(f"Erro ao processar ICS: {e}")

if __name__ == "__main__":
    update_copom_from_ics()
