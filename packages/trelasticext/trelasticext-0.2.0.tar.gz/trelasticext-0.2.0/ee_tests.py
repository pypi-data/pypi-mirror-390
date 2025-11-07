#This modification adds the parent directory to the Python path
import sys
import os
# Get the absolute path to the parent directory of the current file's directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to the Python path if it's not already there
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


import TRelasticExt as ee


def main():
    es_params={"ehost": 'http://localhost:9200', "index": "rabba4"}
    record = ee.get_es_records_by_field("location", "Rabba_Margaliot__Vayikra_2_5", es_params=es_params)
    print(record[0])

if __name__ == '__main__':
    main()
