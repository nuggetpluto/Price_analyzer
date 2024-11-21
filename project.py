import os
import csv
import webbrowser


class PriceAnalyzer:
    def __init__(self):
        self.data = []  # Здесь будут храниться обработанные данные

    @staticmethod
    def search_product_price_weight(headers):
        """Ищет нужные заголовки колонок в прайс-листе."""
        column_mappings = {
            "название": "name", "продукт": "name", "товар": "name", "наименование": "name",
            "№,название": "name",
            "цена": "price", "розница": "price", "цена опт": "price",
            "вес": "weight", "масса": "weight", "фасовка": "weight", "опт,масса": "weight"
        }

        name_column = next((header for header in headers if column_mappings.get(header.lower()) == "name"), None)
        price_column = next((header for header in headers if column_mappings.get(header.lower()) == "price"), None)
        weight_column = next((header for header in headers if column_mappings.get(header.lower()) == "weight"), None)

        return name_column, price_column, weight_column

    def load_prices(self, data_folder):
        """Метод для загрузки и обработки прайс-листов."""
        for csv_file in os.listdir(data_folder):
            if "price" in csv_file.lower() and csv_file.endswith(".csv"):
                file_path = os.path.join(data_folder, csv_file)
                with open(file_path, encoding="utf-8") as file:
                    reader = csv.DictReader(file, delimiter=",")
                    headers = reader.fieldnames
                    name_column, price_column, weight_column = self.search_product_price_weight(headers)

                    if not (name_column and price_column and weight_column):
                        continue

                    for row in reader:  # type: dict
                        product_name = row.get(name_column, "").strip()
                        product_price = row.get(price_column, "").strip()
                        product_weight = row.get(weight_column, "").strip()

                        if product_name and product_price and product_weight:
                            try:
                                product_price = float(product_price)
                                product_weight = float(product_weight)
                                self.data.append((product_name, product_price, product_weight, csv_file))
                            except ValueError:
                                continue
        print(f"Всего загружено записей: {len(self.data)}")

    def find_text(self, search_text):
        """Метод для поиска товаров по названию."""
        search_text = search_text.lower()
        search_results = [
            (product_name, product_price, product_weight, source_file, product_price / product_weight)
            for product_name, product_price, product_weight, source_file in self.data
            if search_text in product_name.lower()
        ]

        search_results.sort(key=lambda x: x[4])  # Сортировка по цене за килограмм
        return search_results

    def export_to_html(self, filename="output.html"):
        """Метод для экспорта данных в HTML файл с улучшенным отображением."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Прайс-листы</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f9f9f9;
                }
                h2 {
                    text-align: center;
                    color: #333;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    background-color: white;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                }
                th {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                }
                tr:hover {
                    background-color: #f1f1f1;
                }
                td:last-child {
                    font-weight: bold;
                    color: #d9534f; /* Красный для цены за кг */
                }
                th, td {
                    text-align: center;
                }
                thead th {
                    position: sticky;
                    top: 0;
                    z-index: 2;
                }
            </style>
        </head>
        <body>
            <h2>Сводная таблица товаров</h2>
            <table>
                <thead>
                    <tr>
                        <th>№</th>
                        <th>Название</th>
                        <th>Цена</th>
                        <th>Вес</th>
                        <th>Файл</th>
                        <th>Цена за кг.</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx, (product_name, product_price, product_weight, source_file_name) in enumerate(self.data, start=1):
            unit_price = product_price / product_weight
            html_content += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{product_name}</td>
                    <td>{product_price:.2f}</td>
                    <td>{product_weight:.2f}</td>
                    <td>{source_file_name}</td>
                    <td>{unit_price:.2f}</td>
                </tr>
            """

        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """

        with open(filename, "w", encoding="utf-8") as file:
            file.write(html_content)

        print(f"Данные успешно экспортированы в файл {filename}")


if __name__ == "__main__":
    folder_path = "prices"
    analyzer = PriceAnalyzer()

    print("Загрузка данных...")
    analyzer.load_prices(folder_path)
    print("Данные успешно загружены.")

    while True:
        user_input = input("Введите текст для поиска (или 'exit' для выхода): ").strip()
        if user_input.lower() == "exit":
            break

        results = analyzer.find_text(user_input)
        if results:
            print(f"\n{'№':<5}{'Наименование':<30}{'Цена':<10}{'Вес':<10}{'Файл':<15}{'Цена за кг.':<10}")
            for i, (name, price, weight, file_name, price_per_kg) in enumerate(results, start=1):
                print(f"{i:<5}{name:<30}{price:<10.2f}{weight:<10.2f}{file_name:<15}{price_per_kg:<10.2f}")
        else:
            print("Товары не найдены.")

    while True:
        export_choice = input("Нужно ли экспортировать данные в HTML? (y/n): ").strip().lower()
        if export_choice in {"y", "n"}:
            if export_choice == "y":
                output_file = "output.html"
                analyzer.export_to_html(output_file)
                print("Данные экспортированы в файл output.html.")
                # Открыть HTML-файл в браузере по умолчанию
                webbrowser.open(output_file)
            else:
                print("Экспорт данных отменён.")
            break
        else:
            print("Пожалуйста, введите 'y' (да) или 'n' (нет).")
