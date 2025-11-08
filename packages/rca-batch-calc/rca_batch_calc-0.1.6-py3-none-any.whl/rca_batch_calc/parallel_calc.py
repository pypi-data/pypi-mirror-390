'''
 # @ Author: Ning An
 # @ Create Time: 2025-05-06 10:23:08
 # @ Modified by: Ning An
 # @ Modified time: 2025-05-06 10:36:33
 '''

import os
import pandas as pd
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from rca_batch_calc.rca_calc import *


def execution_time(func):
    """
    Decorator for calculating execution time.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"Total execution time: {elapsed_time:.2f} seconds")
        return result
    return wrapper

class Parallel_Calculator:
    def __init__(self):
        self.rca_calc = RCA_Calculator()

    @execution_time
    def parallel_run(self, folder_path, process_function, process_name, column_names=None, max_workers=None):
        """
        General parallel processing functions

        Parameters:
        * folder_path: The folder path to process
        * process_function: Specific file processing logic (function)
        * max_workers: Maximum number of threads, default number of CPU cores * 2
        """
        is_dataframe = False
        all_rows = []

        if max_workers is None:
            max_workers = os.cpu_count() * 2 if os.cpu_count() else 4

        files = [file for file in os.listdir(folder_path) if os.path.splitext(file)[0].split("_")[0] == "BACI"]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_function, folder_path, file): file for file in files}
            
            for future in as_completed(futures):
                file = futures[future]
                try:
                    data = future.result()
                    if isinstance(data, pd.DataFrame):
                        if not data.empty:
                            all_rows.append(data)
                            is_dataframe = True
                    else:
                        if data:
                            all_rows.extend(data)
                except Exception as exc:
                    print(f"{file} generated an exception: {exc}")
        if is_dataframe == True:
            final_df = pd.concat(all_rows, ignore_index=True)
            final_df = final_df.rename(columns={'t': 'Year', 'i': 'Exporter', 'j': 'Importer', 'k': 'Product', 'v': 'V', 'q': 'Q'})
            final_df.to_csv(f"{folder_path}/xij.csv", index=False)
        else:
            output_all_rows = pd.DataFrame(all_rows, columns=column_names)
            output_all_rows.to_csv(f"{folder_path}/{process_name}.csv", index=False)

    def run_xij(self, folder_path, file, prod):
        print(f"Processing {file} in thread: {threading.get_ident()}")

        selected_df = self.rca_calc.generate_xij(folder_path, file, prod, "all")

        print(f"{file} is done.")

        return selected_df
    
    def run_xin(self, folder_path, file, val, prod):
        print(f"Processing {file} in thread: {threading.get_ident()}")
        
        country_all_rows = self.rca_calc.generate_xin(folder_path, file, val, prod)

        print(f"{file} is done.")

        return country_all_rows

    def run_xwj(self, folder_path, file, val):
        """
        Logic for processing xwj files.
        """
        print(f"Processing {file} in thread: {threading.get_ident()}")
        
        country_all_rows = self.rca_calc.generate_xwj(folder_path, file, val, "all")

        print(f"{file} is done.")
        
        return country_all_rows
    
    def run_xwn(self, folder_path, file, val):
        print(f"Processing {file} in thread: {threading.get_ident()}")
        
        world_all_rows = self.rca_calc.generate_xwn(folder_path, file, val)

        print(f"{file} is done.")
        
        return world_all_rows

    def run_rca(self, val, file_path_list):
        print(f"Processing in thread: {threading.get_ident()}")
        df = self.rca_calc.rca_calc_new(val, *file_path_list)
        
        return df