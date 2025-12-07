"""
Script untuk generate visualisasi data untuk Bab 4 (Karakteristik Data)
Hasil gambar akan disimpan di folder 'visualizations/'
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import ast
from collections import Counter
import numpy as np

# Set style untuk grafik yang lebih profesional
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10

# Path ke data
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_data():
    """Load data restoran"""
    csv_file = DATA_DIR / "restaurants_entitas.csv"
    df = pd.read_csv(csv_file)
    print(f"✓ Data loaded: {len(df)} restaurants")
    return df

def plot_location_distribution(df):
    """Gambar 4.1: Distribusi Restoran Berdasarkan Lokasi"""
    print("\n1. Generating Location Distribution...")
    
    location_counts = df['entitas_lokasi'].value_counts().head(10)
    
    plt.figure(figsize=(12, 6))
    colors = sns.color_palette("husl", len(location_counts))
    bars = plt.bar(range(len(location_counts)), location_counts.values, color=colors)
    plt.xlabel('Lokasi', fontsize=12, fontweight='bold')
    plt.ylabel('Jumlah Restoran', fontsize=12, fontweight='bold')
    plt.title('Distribusi Restoran Berdasarkan Lokasi di Lombok', 
              fontsize=14, fontweight='bold', pad=20)
    plt.xticks(range(len(location_counts)), location_counts.index, rotation=45, ha='right')
    
    # Tambahkan nilai di atas bar
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'gambar_4_1_distribusi_lokasi.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: gambar_4_1_distribusi_lokasi.png")

def plot_rating_distribution(df):
    """Gambar 4.2: Distribusi Rating Restoran"""
    print("\n2. Generating Rating Distribution...")
    
    plt.figure(figsize=(10, 6))
    rating_counts = df['rating'].value_counts().sort_index(ascending=False)
    
    colors = sns.color_palette("RdYlGn", len(rating_counts))
    bars = plt.barh(range(len(rating_counts)), rating_counts.values, color=colors)
    plt.ylabel('Rating', fontsize=12, fontweight='bold')
    plt.xlabel('Jumlah Restoran', fontsize=12, fontweight='bold')
    plt.title('Distribusi Rating Restoran', fontsize=14, fontweight='bold', pad=20)
    plt.yticks(range(len(rating_counts)), rating_counts.index)
    
    # Tambahkan nilai di samping bar
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2.,
                f'{int(width)}',
                ha='left', va='center', fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'gambar_4_2_distribusi_rating.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: gambar_4_2_distribusi_rating.png")

def plot_cuisine_distribution(df):
    """Gambar 4.3: Distribusi Jenis Cuisine"""
    print("\n3. Generating Cuisine Distribution...")
    
    # Extract all cuisines
    all_cuisines = []
    for cuisines_str in df['cuisines'].dropna():
        try:
            cuisines_list = ast.literal_eval(cuisines_str)
            all_cuisines.extend(cuisines_list)
        except:
            pass
    
    cuisine_counts = Counter(all_cuisines).most_common(15)
    cuisines, counts = zip(*cuisine_counts)
    
    plt.figure(figsize=(12, 8))
    colors = sns.color_palette("viridis", len(cuisines))
    bars = plt.barh(range(len(cuisines)), counts, color=colors)
    plt.ylabel('Jenis Cuisine', fontsize=12, fontweight='bold')
    plt.xlabel('Jumlah Restoran', fontsize=12, fontweight='bold')
    plt.title('Top 15 Jenis Masakan (Cuisine) di Lombok', 
              fontsize=14, fontweight='bold', pad=20)
    plt.yticks(range(len(cuisines)), cuisines)
    
    # Tambahkan nilai
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2.,
                f' {int(width)}',
                ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'gambar_4_3_distribusi_cuisine.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: gambar_4_3_distribusi_cuisine.png")

def plot_features_distribution(df):
    """Gambar 4.4: Features Restoran yang Paling Umum"""
    print("\n4. Generating Features Distribution...")
    
    # Extract all features
    all_features = []
    for features_str in df['entitas_features'].dropna():
        try:
            features_list = ast.literal_eval(features_str)
            all_features.extend(features_list)
        except:
            pass
    
    feature_counts = Counter(all_features).most_common(12)
    features, counts = zip(*feature_counts)
    
    plt.figure(figsize=(12, 7))
    colors = sns.color_palette("coolwarm", len(features))
    bars = plt.barh(range(len(features)), counts, color=colors)
    plt.ylabel('Fitur/Fasilitas', fontsize=12, fontweight='bold')
    plt.xlabel('Jumlah Restoran', fontsize=12, fontweight='bold')
    plt.title('Fitur dan Fasilitas Restoran yang Paling Umum', 
              fontsize=14, fontweight='bold', pad=20)
    plt.yticks(range(len(features)), features)
    
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2.,
                f' {int(width)}',
                ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'gambar_4_4_distribusi_features.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: gambar_4_4_distribusi_features.png")

def create_wordcloud(df):
    """Gambar 4.5: Word Cloud dari Deskripsi Restoran"""
    print("\n5. Generating Word Cloud...")
    
    try:
        from wordcloud import WordCloud
        
        # Gabungkan semua about text
        text = ' '.join(df['about'].dropna().astype(str))
        
        # Generate word cloud
        wordcloud = WordCloud(width=1600, height=800, 
                            background_color='white',
                            colormap='viridis',
                            max_words=100,
                            relative_scaling=0.5,
                            min_font_size=10).generate(text)
        
        plt.figure(figsize=(16, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Word Cloud dari Deskripsi Restoran', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout(pad=0)
        plt.savefig(OUTPUT_DIR / 'gambar_4_5_wordcloud.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ Saved: gambar_4_5_wordcloud.png")
        
    except ImportError:
        print("   ⚠ WordCloud library not installed. Skipping...")
        print("     Install with: pip install wordcloud")

def plot_rating_by_location(df):
    """Gambar 4.6: Rating Rata-rata per Lokasi"""
    print("\n6. Generating Rating by Location...")
    
    # Hitung rata-rata rating per lokasi
    location_rating = df.groupby('entitas_lokasi')['rating'].agg(['mean', 'count'])
    location_rating = location_rating[location_rating['count'] >= 3]  # Min 3 restoran
    location_rating = location_rating.sort_values('mean', ascending=False).head(10)
    
    plt.figure(figsize=(12, 7))
    colors = plt.cm.RdYlGn(location_rating['mean'] / 5.0)
    bars = plt.barh(range(len(location_rating)), location_rating['mean'], color=colors)
    plt.ylabel('Lokasi', fontsize=12, fontweight='bold')
    plt.xlabel('Rating Rata-rata', fontsize=12, fontweight='bold')
    plt.title('Rating Rata-rata Restoran per Lokasi', 
              fontsize=14, fontweight='bold', pad=20)
    plt.yticks(range(len(location_rating)), location_rating.index)
    plt.xlim(0, 5)
    
    for i, bar in enumerate(bars):
        width = bar.get_width()
        count = location_rating.iloc[i]['count']
        plt.text(width, bar.get_y() + bar.get_height()/2.,
                f' {width:.2f} ({int(count)} rest.)',
                ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'gambar_4_6_rating_per_lokasi.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: gambar_4_6_rating_per_lokasi.png")

def create_summary_statistics_table(df):
    """Tabel 4.1: Statistik Deskriptif Dataset"""
    print("\n7. Creating Summary Statistics Table...")
    
    stats = {
        'Metric': [
            'Total Restoran',
            'Jumlah Lokasi Unik',
            'Jumlah Cuisine Unik',
            'Rating Tertinggi',
            'Rating Terendah',
            'Rating Rata-rata',
            'Restoran dengan Rating 5.0',
            'Restoran dengan WiFi',
            'Restoran dengan Parking'
        ],
        'Value': []
    }
    
    # Hitung metrics
    stats['Value'].append(len(df))
    stats['Value'].append(df['entitas_lokasi'].nunique())
    
    # Count unique cuisines
    all_cuisines = []
    for cuisines_str in df['cuisines'].dropna():
        try:
            all_cuisines.extend(ast.literal_eval(cuisines_str))
        except:
            pass
    stats['Value'].append(len(set(all_cuisines)))
    
    stats['Value'].append(df['rating'].max())
    stats['Value'].append(df['rating'].min())
    stats['Value'].append(f"{df['rating'].mean():.2f}")
    stats['Value'].append(len(df[df['rating'] == 5.0]))
    
    # Count WiFi
    wifi_count = sum(df['entitas_features'].astype(str).str.contains('Wifi|WiFi|wifi', na=False))
    stats['Value'].append(wifi_count)
    
    # Count Parking
    parking_count = sum(df['entitas_features'].astype(str).str.contains('Parking', na=False))
    stats['Value'].append(parking_count)
    
    # Create table image
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=[[m, v] for m, v in zip(stats['Metric'], stats['Value'])],
                    colLabels=['Metrik', 'Nilai'],
                    cellLoc='left',
                    loc='center',
                    colWidths=[0.6, 0.2])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)
    
    # Style header
    for i in range(2):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(stats['Metric']) + 1):
        if i % 2 == 0:
            for j in range(2):
                table[(i, j)].set_facecolor('#f0f0f0')
    
    plt.title('Statistik Deskriptif Dataset Restoran', 
             fontsize=14, fontweight='bold', pad=20)
    plt.savefig(OUTPUT_DIR / 'tabel_4_1_statistik_deskriptif.png', 
               dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: tabel_4_1_statistik_deskriptif.png")

def plot_data_sample(df):
    """Tabel 4.2: Contoh Sample Data"""
    print("\n8. Creating Data Sample Table...")
    
    # Pilih 3 restoran sebagai sample
    sample_df = df.head(3)[['name', 'rating', 'entitas_lokasi', 'cuisines']].copy()
    
    # Truncate cuisines untuk display
    sample_df['cuisines'] = sample_df['cuisines'].apply(
        lambda x: str(ast.literal_eval(x)[:3])[1:-1].replace("'", "") if pd.notna(x) else ""
    )
    
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis('tight')
    ax.axis('off')
    
    cell_text = []
    for idx, row in sample_df.iterrows():
        cell_text.append([
            row['name'][:30] + '...' if len(row['name']) > 30 else row['name'],
            str(row['rating']),
            row['entitas_lokasi'],
            row['cuisines'][:40] + '...' if len(row['cuisines']) > 40 else row['cuisines']
        ])
    
    table = ax.table(cellText=cell_text,
                    colLabels=['Nama Restoran', 'Rating', 'Lokasi', 'Jenis Cuisine'],
                    cellLoc='left',
                    loc='center',
                    colWidths=[0.35, 0.1, 0.15, 0.4])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Style header
    for i in range(4):
        table[(0, i)].set_facecolor('#2196F3')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    plt.title('Contoh Sample Data Restoran dari Dataset', 
             fontsize=14, fontweight='bold', pad=20)
    plt.savefig(OUTPUT_DIR / 'tabel_4_2_sample_data.png', 
               dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: tabel_4_2_sample_data.png")

def main():
    print("="*60)
    print("GENERATING VISUALIZATIONS FOR BAB 4")
    print("Karakteristik Data - Chatbot Rekomendasi Restoran")
    print("="*60)
    
    # Load data
    df = load_data()
    
    # Generate all visualizations
    plot_location_distribution(df)
    plot_rating_distribution(df)
    plot_cuisine_distribution(df)
    plot_features_distribution(df)
    create_wordcloud(df)
    plot_rating_by_location(df)
    create_summary_statistics_table(df)
    plot_data_sample(df)
    
    print("\n" + "="*60)
    print("✓ ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
    print(f"✓ Check folder: {OUTPUT_DIR}")
    print("="*60)
    print("\nFiles generated:")
    print("  1. gambar_4_1_distribusi_lokasi.png")
    print("  2. gambar_4_2_distribusi_rating.png")
    print("  3. gambar_4_3_distribusi_cuisine.png")
    print("  4. gambar_4_4_distribusi_features.png")
    print("  5. gambar_4_5_wordcloud.png (if wordcloud installed)")
    print("  6. gambar_4_6_rating_per_lokasi.png")
    print("  7. tabel_4_1_statistik_deskriptif.png")
    print("  8. tabel_4_2_sample_data.png")
    print("\nCopy these images to your thesis document!")

if __name__ == "__main__":
    main()
