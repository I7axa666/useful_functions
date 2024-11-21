import os
import re
import pandas as pd
from PyPDF2 import PdfReader

def extract_data_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Ищем все слова и словосочетания в кавычках
        matches = re.findall(r'\"(.*?)\"', text)
        return matches

def process_pdfs(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory, filename)
            extracted_phrases = extract_data_from_pdf(file_path)
            for phrase in extracted_phrases:
                data.append([filename, phrase])

    # Создаем DataFrame и сохраняем в Excel
    df = pd.DataFrame(data, columns=['Filename', 'Extracted Data'])

    # Создаем директорию, если она не существует
    os.makedirs('../results', exist_ok=True)

    # Сохраняем файл в директорию results
    df.to_excel('results/output.xlsx', index=False)

# Укажите путь к директории с PDF-файлами
directory_path = '../pdf/'
process_pdfs(directory_path)