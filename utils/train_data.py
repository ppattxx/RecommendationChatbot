import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import time
FILE_INPUT = 'restaurants.csv'
FILE_OUTPUT = 'restaurants_processed.csv'
def train_dataset():
    try:
        df = pd.read_csv(FILE_INPUT)
    except FileNotFoundError:
        return
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    konten_gabungan = (df['preferences'] + ' ' + df['about']).fillna('').str.lower()
    start_time = time.time()
    df['konten_stemmed'] = konten_gabungan.apply(stemmer.stem)
    end_time = time.time()
    try:
        df.to_csv(FILE_OUTPUT, index=False)
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == '__main__':
    train_dataset()