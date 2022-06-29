import os
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def file_lines_into_list(file):
    with open(file, 'r') as f:
        lines = f.read().splitlines() 
    return lines


def filter_html_content(html_content, filter):
    try:
        result = html_content.find(True, {"class": filter}).text.strip()
    except:
        result = ""
    return result


def get_url_content_as_dict(url):
    content = {}
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    content["url"] = url
    content['job title'] = filter_html_content(soup, "sub-nav-cta__header")
    content['company'] = filter_html_content(soup, "sub-nav-cta__optional-url")
    content['location'] = filter_html_content(soup, "sub-nav-cta__meta-text")
    content['description'] = filter_html_content(soup, "show-more-less-html__markup show-more-less-html__markup--clamp-after-5")
    
    return content


def get_all_keys_as_list(list_of_dictionaries):
    # retorna todas as chaves presentes em uma lista de dicionários
    all_keys = list( set().union( *(dict.keys() for dict in list_of_dictionaries) ) )
    return all_keys


class Spreadsheet():

    SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    CONSOLIDATION_WORKSHEET = "DATA CONSOLIDATION"
    HEADER_INDEX = 1
    HEADER_FIRST_CELL = CONSOLIDATION_WORKSHEET+"!A1"

    def __init__(self, credentials, spreadsheet_key):
        # a inicialização consiste em se conectar com a referente planilha e deixá-la disponível para trabalho
        self.spreadsheet_key = spreadsheet_key
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials, Spreadsheet.SCOPE)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_key)

    def _create_worksheet(self, worksheet_name):
        return self.spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)

    def list_worksheets(self):
        worksheet_objs = self.spreadsheet.worksheets()
        worksheets_list = [worksheet.title for worksheet in worksheet_objs]
        return worksheets_list

    def _arrange_values_for_insertion(self, data, column_header):
        list_values_to_insert = []
        # mapeamento cabeçalho e chave
        header_to_key = { i : i for i in column_header }
        
        # organizar os dados de acordo com o cabeçalho
        # caso um registro não tenha determinada chave, o valor referente ficará em branco
        for instance in data:
            arrange_key_to_header = []
            for column in column_header:
                try:
                    arrange_key_to_header.append( instance[ header_to_key[column] ] )
                except:
                    arrange_key_to_header.append("")
            list_values_to_insert.append(arrange_key_to_header)

        return list_values_to_insert
    
    def insert_values(self, data, column_header, worksheet_name):
        self.data = data
        self.last_header = column_header

        if worksheet_name not in self.list_worksheets(): self._create_worksheet(worksheet_name)
        self.current_worksheet = self.spreadsheet.worksheet(worksheet_name)
        
        # insere cabeçalho
        self.current_worksheet.insert_row(self.last_header, Spreadsheet.HEADER_INDEX)

        # anexa os dados alinhando conteúdo e cabeçalho
        list_values_to_insert = self._arrange_values_for_insertion(self.data, self.last_header)
        self.spreadsheet.values_append(worksheet_name, {'valueInputOption': 'USER_ENTERED'}, {'values': list_values_to_insert})

    def consolidation(self):
        if Spreadsheet.CONSOLIDATION_WORKSHEET not in self.list_worksheets(): self._create_worksheet(Spreadsheet.CONSOLIDATION_WORKSHEET)
        self.data_consolidation_worksheet = self.spreadsheet.worksheet(Spreadsheet.CONSOLIDATION_WORKSHEET)
        
        # insere cabeçalho considerando o já existente na aba DATA CONSOLIDATION,
        # além de possíveis novas colunas da última aba criada
        self.current_header = self.data_consolidation_worksheet.row_values(Spreadsheet.HEADER_INDEX)
        self.current_header.extend([i for i in self.last_header if i not in self.current_header])
        self.spreadsheet.values_update(Spreadsheet.HEADER_FIRST_CELL, {'valueInputOption': 'USER_ENTERED'}, {'values': [self.current_header]})

        # lista com todos os urls presentes na aba DATA CONSOLIDATION
        key = "url"
        key_cell = self.data_consolidation_worksheet.find(key)
        values_in_data_consolidation = self.data_consolidation_worksheet.col_values(key_cell.col)[1:]

        # urls da última aba criada que ainda não constam na aba "DATA CONSOLIDATION"
        new_rows = [instance for instance in self.data if instance.get(key) not in values_in_data_consolidation]

        # anexa os dados alinhando conteúdo e cabeçalho
        list_values_to_insert = self._arrange_values_for_insertion(new_rows, self.current_header)
        self.spreadsheet.values_append(Spreadsheet.CONSOLIDATION_WORKSHEET, {'valueInputOption': 'USER_ENTERED'}, {'values': list_values_to_insert})


def main():

    CREDENTIALS_FILE = "../data/client_secrets.json"
    SPREADSHEET_KEY = "1KSsI8nJFyp_vYyaKFBZFJ-w-wZqou85dAdIj9E6a3zI"
    JOB_LINKS_PATH = "../job-links/"
    SAVED_JOB_LINKS_PATH = JOB_LINKS_PATH + "sent/"

    spreadsheet = Spreadsheet(CREDENTIALS_FILE, SPREADSHEET_KEY)

    files_with_job_links = [f for f in os.listdir(JOB_LINKS_PATH) if os.path.isfile(os.path.join(JOB_LINKS_PATH, f))]
    
    for urls_file in files_with_job_links:
        job_data = []
        
        for url in file_lines_into_list(JOB_LINKS_PATH+urls_file):
            job_data.append(get_url_content_as_dict(url))

        data_keys = sorted(get_all_keys_as_list(job_data))

        # nome da aba é o carimbo data e hora da extração dos links das vagas 
        # = nome do arquivo sem a sua extensão
        worksheet_name = urls_file.split('.')[0]

        spreadsheet.insert_values(job_data, data_keys, worksheet_name)

        spreadsheet.consolidation()

        if not os.path.exists(SAVED_JOB_LINKS_PATH): os.makedirs(SAVED_JOB_LINKS_PATH)
        os.replace(JOB_LINKS_PATH+urls_file, SAVED_JOB_LINKS_PATH+urls_file)


if __name__ == '__main__':
    main()    