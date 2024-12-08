import os
import pandas as pd  # Импортируем библиотеку pandas для анализа данных и работы с таблицами


class PriceMachine:
    def __init__(self):
        # Создаем пустой DataFrame с заданными столбцами
        self.prices = pd.DataFrame(columns=['№', 'Наименование', 'Цена', 'Вес', 'Цена за кг.', 'Файл'])

    def load_prices(self, file_path=None):
        if file_path is None:
            file_path = os.path.dirname(os.path.realpath(__file__))  # Получаем путь к директории текущего файла

        # Получаем список всех CSV файлов в указанной директории
        csv_files = self._get_price_files(file_path)
        for file in csv_files:
            print(f'Чтение данных из файла {file}')  # Информируем о начале чтения файла
            # Читаем данные из CSV файла в DataFrame
            df_from_file = self._read_csv(file_path, file)
            # Извлекаем данные о продуктах и их ценах
            new_df = self._search_product_price_weight(df_from_file)
            new_df['Файл'] = file.split('.')[0]  # Добавляем название файла в DataFrame
            # Объединяем новый DataFrame с основным
            self.prices = pd.concat([self.prices, new_df], ignore_index=True)

        # Завершаем обработку цен
        self._finalize_prices()

    def _get_price_files(self, file_path):
        # Возвращаем список файлов с расширением .csv, содержащих 'price' в названии
        return [file for file in os.listdir(file_path) if file.endswith('.csv') and 'price' in file]

    def _read_csv(self, file_path, file):
        # Читаем CSV файл и возвращаем его содержимое в виде DataFrame
        return pd.read_csv(os.path.join(file_path, file), encoding='utf-8')

    def _search_product_price_weight(self, data_frame):
        # Удаляем пустые столбцы и создаем копию DataFrame
        data_frame = data_frame.dropna(how="all", axis=1).copy()
        # Определяем соответствие заголовков
        mapping = {
            'название': 'Наименование',
            'продукт': 'Наименование',
            'товар': 'Наименование',
            'наименование': 'Наименование',
            'цена': 'Цена',
            'розница': 'Цена',
            'вес': 'Вес',
            'масса': 'Вес',
            'фасовка': 'Вес'
        }
        # Переименовываем столбцы в соответствии с заданным соответствием
        for header in data_frame.columns:
            lower_header = header.lower()
            if lower_header in mapping:
                data_frame[mapping[lower_header]] = data_frame[header]

        # Возвращаем DataFrame с нужными столбцами
        return data_frame[['Наименование', 'Цена', 'Вес']].copy()

    def _finalize_prices(self):
        # Вычисляем цену за килограмм
        self.prices['Цена за кг.'] = self.prices['Цена'] / self.prices['Вес']
        # Сортируем DataFrame по цене за килограмм
        self.prices.sort_values(by='Цена за кг.', ascending=True, inplace=True)
        self.prices.reset_index(drop=True, inplace=True)  # Сбрасываем индексы
        self.prices['№'] = range(1, len(self.prices) + 1)  # Добавляем номер позиции

    def export_to_html(self, df, file_name='output.html'):
        # Генерируем HTML-контент из DataFrame и сохраняем в файл
        html_content = self._generate_html(df)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_html(self, df):
        # Формируем строки таблицы из DataFrame
        rows = ''.join([
            f'<tr><td align="right">{row["№"]}</td><td>{row["Наименование"]}</td>'
            f'<td align="right">{row["Цена"]}</td><td align="right">{row["Вес"]}</td>'
            f'<td>{row["Файл"]}</td><td align="right">{round(row["Цена за кг."], 1)}</td></tr>'
            for _, row in df.iterrows()
        ])
        # Возвращаем полный HTML-код
        return f'''<!DOCTYPE html>
            <html>
            <head>
                <title>Позиции продуктов</title>
                <style>
                    table {{ border-spacing: 16px 0px; }}
                </style>
            </head>
            <body>
                <table>
                    <tr>
                        <th>Номер</th>
                        <th>Название</th>
                        <th>Цена</th>
                        <th>Фасовка</th>
                        <th>Файл</th>
                        <th>Цена за кг.</th>
                    </tr>
                    {rows}
                </table>
            </body>
            </html>'''

    def find_text(self, search_text):
        # Ищем продукты по наименованию в DataFrame
        matches = self.prices[self.prices['Наименование'].str.contains(search_text, case=False)]
        if not matches.empty:
            self.export_to_html(matches)  # Экспортируем найденные результаты в HTML
            return matches
        else:
            print(f'Продукта с наименованием: {search_text}, не найдено.')
            return self.find_text('Пелядь крупная х/к потр')  # Поиск по умолчанию


if __name__ == "__main__":
    pm = PriceMachine()  # Создаем экземпляр класса PriceMachine
    pm.load_prices()  # Загружаем цены из файлов
    print('Все файлы прочитаны')
    pm.export_to_html(pm.prices)  # Экспортируем все данные в HTML файл
    print('Данные выгружены в html файл: output.html')

    while True:
        search_text = input('\nВведите наименование продукта: ')  # Запрашиваем у пользователя наименование продукта
        if search_text.lower().strip() == "exit":
            break  # Выход из цикла, если пользователь ввел "exit"
        elif search_text == "all":
            print(pm.prices)  # Выводим все данные
        else:
            print(pm.find_text(search_text))  # Ищем и выводим информацию о продукте
    print('Работа завершена.')  # Завершение работы программы
