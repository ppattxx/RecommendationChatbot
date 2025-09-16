import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import time
FILE_INPUT = 'restaurants.csv'
FILE_OUTPUT = 'restaurants_processed.csv'
def train_dataset():
    print(f"Memuat dataset dari '{FILE_INPUT}'...")
    try:
        df = pd.read_csv(FILE_INPUT)
    except FileNotFoundError:
        print(f"Error: File '{FILE_INPUT}' tidak ditemukan. Mohon siapkan datanya terlebih dahulu.")
        return
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    print("Menggabungkan kolom 'preferences' dan 'about'...")
    konten_gabungan = (df['preferences'] + ' ' + df['about']).fillna('').str.lower()
    print("Memulai proses stemming...")
    start_time = time.time()
    df['konten_stemmed'] = konten_gabungan.apply(stemmer.stem)
    end_time = time.time()
    print(f"Proses stemming selesai dalam {end_time - start_time:.2f} detik.")
    try:
        df.to_csv(FILE_OUTPUT, index=False)
        print(f"Dataset berhasil di-'train' dan disimpan sebagai '{FILE_OUTPUT}'")
    except Exception as e:
        print(f"Gagal menyimpan file yang sudah diproses: {e}")
if __name__ == '__main__':
    train_dataset()