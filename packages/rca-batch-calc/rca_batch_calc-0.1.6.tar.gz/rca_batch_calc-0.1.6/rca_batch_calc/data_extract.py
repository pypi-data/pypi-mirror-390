import pandas as pd
import os


class DataExtract:
    def find_product(self, folder_path, prod: list):
        """
        Find product and save it to csv file
        """
        files = [file for file in os.listdir(folder_path) if os.path.splitext(file)[0].split("_")[0] == "BACI"]
        delimiters = [',', ';', '\t', '|']
        results = []

        for file in files:
            print(f"Extracting file: {file}")
            file_path = os.path.join(folder_path, file)
            for delimiter in delimiters:
                try:
                    df = pd.read_csv(file_path, sep=delimiter)
                    product_lines = df[df["k"].isin(prod)]
                    if not product_lines.empty:
                        results.append(product_lines)
                    print(f"Extracting finished: {file}")
                    break
                except pd.errors.ParserError:
                    continue
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue

        if results:
            return pd.concat(results, ignore_index=True)
        else:
            print("No matching products found.")
            return None

    def save_csv(self, product_lines, folder_path):
        """
        Save csv file
        """
        if product_lines is not None:
            output_file = f"{folder_path}/output.csv"
            if os.path.exists(output_file):
                existing_data = pd.read_csv(output_file)
                combined_data = pd.concat([existing_data, product_lines], ignore_index=True)
            else:
                combined_data = product_lines

            combined_data.to_csv(output_file, index=False)
            print("Extracted data saved.")
            print("---------------------")
        else:
            print("No data available to save to a CSV file.")

    def convert_countries(self, original_file_path, comparison_file_path):
        """
        Convert code to countries
        """
        df_output = pd.read_csv(original_file_path)
        df_country = pd.read_csv(comparison_file_path)

        mapping_dict = pd.Series(df_country.country_name.values, index=df_country.country_code).to_dict()
        
        column_pairs = [
            ('i', 'j'),
            ('importer', 'exporter'),
            ('Importer', 'Exporter')
        ]

        for col_i, col_j in column_pairs:
            if col_i in df_output.columns and col_j in df_output.columns:
                df_output[col_i] = df_output[col_i].map(mapping_dict)
                df_output[col_j] = df_output[col_j].map(mapping_dict)
                
                output_file_path = f'{original_file_path.split(".csv")[0]}_(country_name).csv'
                df_output.to_csv(output_file_path, index=False)
                break
        else:
            print("Error: No valid column pairs ('i'/'j' or 'importer'/'exporter') found.")
