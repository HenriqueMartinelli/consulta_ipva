from bs4 import BeautifulSoup

class Extract():

    def extract_info_table(self, table_content, keys_indexes):
        extracted_data = {}
        rows = table_content.find_all('tr', class_=lambda x: x != 'alinharCentro' if x else True)
        
        for row in rows[1:]:
            columns = row.findAll("td")
            if "ATENÇÃO: " in columns[0].text: continue

            for key, index in keys_indexes.items():
                extracted_data[columns[key].text.replace(":","").strip()] = columns[index].text.replace(":","").strip()        
        return extracted_data

    def extract_payment_info(self, table_content):
        payments = []
        if table_content is None:
            tableConteudo = table_content.select_one("#conteudoPaginaPlaceHolder_tbPagtosEfetuados")
            rows = tableConteudo.findAll("tr")
        else:
            rows = table_content.find("table").findAll("tr")
        
        for row in rows[1:]:
            columns = row.findAll("td")
            if "NADA CONSTA" in columns[0].text.strip(): return None

            if columns[0].text.strip() != "" and columns[1].text.strip() != "":
                payment = {
                    "vista com desconto": columns[0].text.strip(),
                    "Vencimento": columns[1].text.strip(),
                    "Valor": columns[4].text.strip()
                }
                payments.append(payment)
        
        return payments

    def extract_multas(self, table_content):
        multas = []
        rows = table_content.findAll("tr")[1:]
        
        for row in rows:
            columns = row.findAll("td")
            if "NADA CONSTA" in columns[0].text.strip(): return None

            multa = {
                "orgao": columns[0].text.strip(),
                "Quantidade": columns[1].text.strip(),
                "Valor": columns[4].text.strip(),
            }
            multas.append(multa)
        
        return multas

    def extract_data(self, placa, renavam, consulta_content):
        soup = BeautifulSoup(consulta_content, "html.parser")
        
        # extracted_info = self.extract_info_table(soup.select_one("#conteudoPaginaPlaceHolder_Panel1 > table:nth-child(5)"), {0: 1, 2: 3})
        extracted_base_calculo = self.extract_info_table(soup.select_one("#conteudoPaginaPlaceHolder_Panel1 > table:nth-child(11)"), {0: 3})
        # extracted_payments = self.extract_payment_info(soup.select_one("#conteudoPaginaPlaceHolder_pnlModalidadesPagto > table:nth-child(2)"))
        # extracted_multas = self.extract_multas(soup.select_one("#conteudoPaginaPlaceHolder_tbMultaResumo"))
        
        return {
            "placa": placa,
            "renavam": renavam,
            'base_calculo': extracted_base_calculo,
            "error": False,
            "msg": None
        }