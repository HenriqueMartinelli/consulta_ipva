import json
import logging
import pandas as pd
import concurrent.futures
from datetime import datetime
from src.ipvaNet import ConsultaIPVA
from src.extract_data import Extract

from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class queryConcurrent(ConsultaIPVA, Extract):
    def __init__(self):
        super().__init__(os.getenv("CAPTCHA_TOKEN"), os.getenv("SITE_KEY"))


    def executar(self, infos):
        result, result_dict = str(), str()
        
        try:
            local_renavam = infos['renavam']
            local_placa = infos['placa']

            result = self.run_query(local_renavam, local_placa)
            local_result_content = result.content
  
            result_dict = self.extract_data(local_placa, local_renavam, local_result_content)
        except Exception as e:
            placa, renavam = infos["placa"], infos["renavam"]
            logging.error(f"placa: {placa}, renavam: {renavam}")
            result_dict = {
                "renavam": local_renavam,
                "placa": local_placa,
                "base_calculo": None,
                "error": True,
                "msg": e.args[0]
            }
        
        local_infos = {
            "renavam": local_renavam,
            "placa": local_placa,
        }
        local_infos.update(result_dict)
        return local_infos

    def concurrent_calls(self, datas):
        results = list()
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results_iterador = executor.map(self.executar, datas)
            for result in results_iterador:
                results.append(result)
            return results
            

    def save_dict_to_csv(self, list_datas):
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{current_datetime}.csv"
        df = pd.DataFrame(list_datas)
        df.to_csv(file_name, index=False)
        return file_name
    

    def start(self, **kwargs):
         result = self.concurrent_calls(kwargs)
         self.save_dict_to_csv(result)


    def get_csv_path(self):
        while True:
            csv_path = input("Digite o caminho completo do arquivo CSV: ")
            if os.path.exists(csv_path):
                return csv_path
            else:
                print("Arquivo não encontrado. Por favor, forneça um caminho válido.")

    def start(self, **kwargs):
        csv_path = self.get_csv_path()
        df = pd.read_csv(csv_path, sep=';')

        kwargs = list()
        dados = df.to_dict()

        for indice in dados['placa']:
            kwargs.append(
                {
                    "placa": dados['placa'][indice],
                    "renavam": dados['renavam'][indice] 
                }
            )

        query_instance = queryConcurrent()
        query_instance.concurrent_calls(kwargs)

if __name__ == "__main__":
    load_dotenv()  
    query_instance = queryConcurrent()
    query_instance.start()
