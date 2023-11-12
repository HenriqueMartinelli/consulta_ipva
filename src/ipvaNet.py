import requests
from bs4 import BeautifulSoup
from twocaptcha import TwoCaptcha


class ConsultaIPVA:
    def __init__(self, token, site_key):
        self.token = token
        self.site_key = site_key
        self.url = "https://www.ipva.fazenda.sp.gov.br/ipvanet_consulta/consulta.aspx"
        self.session = requests.Session()

    def solve_captcha(self):
        solver = TwoCaptcha(self.token)
        result = solver.hcaptcha(sitekey=self.site_key, url=self.url)
        return result

    def get_html_content(self):
        html_login = self.session.get(self.url)
        return html_login.content

    def extract_viewstate_info(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
        event_validation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
        viewstate_generator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
        return viewstate, event_validation, viewstate_generator

    def prepare_payload(self, renavam, placa, captcha_result):
        viewstate, event_validation, viewstate_generator = self.extract_viewstate_info(self.get_html_content())
        payload = {
            "__VIEWSTATE": viewstate,
            "__EVENTVALIDATION": event_validation,
            "__VIEWSTATEGENERATOR": viewstate_generator,
            "ctl00$conteudoPaginaPlaceHolder$txtRenavam": renavam,
            "ctl00$conteudoPaginaPlaceHolder$txtPlaca": placa,
            "ctl00$conteudoPaginaPlaceHolder$btn_Consultar": "Consultar",
            "h-captcha-response": captcha_result['code'],
            "g-recaptcha-response": captcha_result['code']
        }
        return payload

    def make_request(self, payload):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,it;q=0.6',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.ipva.fazenda.sp.gov.br',
            'Referer': 'https://www.ipva.fazenda.sp.gov.br/ipvanet_consulta/consulta.aspx'
        }
        try: consultation = self.session.post(self.url, data=payload, headers=headers, timeout=10)
        except: raise ValueError("Site está demorando muito a responder, ou está instável")
        return consultation
        

    def run_query(self, renavam, placa):
        captcha_result = self.solve_captcha()
        payload = self.prepare_payload(renavam, placa, captcha_result)
        consultation = self.make_request(payload)
        return consultation
