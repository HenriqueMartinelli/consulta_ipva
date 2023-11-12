import json
import concurrent.futures
from datetime import datetime
import pandas as pd
from src.ipvaNet import ConsultaIPVA
from src.extract_data import Extract

from dotenv import load_dotenv
import os


class queryConcurrent(ConsultaIPVA, Extract):
    def __init__(self):
        super().__init__(os.getenv("CAPTCHA_TOKEN"), os.getenv("SITE_KEY"))


    def executar(self, infos):
        try:
            result = self.run_query(infos['renavam'], infos['placa'])
            result_dict = self.extract_data(result.content)
        except Exception as e:
            result_dict = {
                            "renavam": infos['renavam'],
                            "placa": infos['placa'],
                            "error": True,
                             "msg": e.args[0]
                           }
        infos.update(result_dict)
        return infos

    def concurrent_calls(self, datas):
        results = list()
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results_iterador = executor.map(self.executar, datas['data'])
            for result in results_iterador:
                results.append(result)
            return results
            
    
    def save_dict_to_json(self, list_datas):
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{current_datetime}.json"

        with open(file_name, 'w') as file:
            json.dump(list_datas, file)
        return file_name
    
    def start(self, **kwargs):
         result = self.concurrent_calls(kwargs)
         self.save_dict_to_json(result)


if __name__ == "__main__":
    load_dotenv()  

    kwargs = [
        {"renavam": "1352263499", "placa": "GEI2A34"},
        {"renavam": "1349246473", "placa": "GDO8F84"},
        {"renavam": "1349238101", "placa": "CPN3F26"},
        {"renavam": "1348959824", "placa": "GCR5J54"},
        {"renavam": "1351175120", "placa": "GBE1C42"},
        {"renavam": "1349109433", "placa": "FUT2F14"},
        {"renavam": "1349902877", "placa": "CUP5G59"},

    ]

    query_instance = queryConcurrent()
    query_instance.start(data=kwargs)
