"""
Script untuk generate tabel sample data dengan entitas yang digunakan sistem
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import ast

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

def create_sample_data_table_full(df):
    """Tabel 4.2: Sample Data dengan Semua Entitas"""
    print("\nGenerating Sample Data Table with All Entities...")
    
    # Pilih 3 restoran sebagai sample
    sample_indices = [0, 1, 4]  # Francesco's Pizza, Tiki Grove, Italy Pizzeria
    sample_df = df.iloc[sample_indices].copy()
    
    # Siapkan data untuk tabel
    table_data = []
    
    for idx, row in sample_df.iterrows():
        # Truncate dan format data
        name = row['name'][:35] + '...' if len(str(row['name'])) > 35 else row['name']
        rating = f"{row['rating']:.1f}"
        lokasi = row['entitas_lokasi'] if pd.notna(row['entitas_lokasi']) else '-'
        
        # Parse cuisines
        try:
            cuisines = ast.literal_eval(row['cuisines']) if pd.notna(row['cuisines']) else []
            cuisines_str = ', '.join(cuisines[:2]) + ('...' if len(cuisines) > 2 else '')
        except:
            cuisines_str = '-'
        
        # Parse jenis makanan
        try:
            jenis_makanan = ast.literal_eval(row['entitas_jenis_makanan']) if pd.notna(row['entitas_jenis_makanan']) else []
            jenis_str = ', '.join(jenis_makanan[:2]) if jenis_makanan else '-'
        except:
            jenis_str = '-'
        
        # Parse features
        try:
            features = ast.literal_eval(row['entitas_features']) if pd.notna(row['entitas_features']) else []
            features_str = ', '.join(features[:3]) + ('...' if len(features) > 3 else '') if features else '-'
        except:
            features_str = '-'
        
        table_data.append([
            name,
            rating,
            lokasi,
            cuisines_str[:30] + '...' if len(cuisines_str) > 30 else cuisines_str,
            jenis_str,
            features_str[:35] + '...' if len(features_str) > 35 else features_str
        ])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 5))
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    table = ax.table(
        cellText=table_data,
        colLabels=['Nama Restoran', 'Rating', 'Lokasi', 'Cuisine', 'Jenis Makanan', 'Features'],
        cellLoc='left',
        loc='center',
        colWidths=[0.25, 0.08, 0.12, 0.18, 0.15, 0.22]
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.8)
    
    # Style header
    for i in range(6):
        cell = table[(0, i)]
        cell.set_facecolor('#2196F3')
        cell.set_text_props(weight='bold', color='white', size=10)
        cell.set_height(0.08)
    
    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(6):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#f5f5f5')
            cell.set_height(0.08)
    
    plt.title('Tabel 4.2 Contoh Sample Data Restoran dengan Entitas', 
             fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig(OUTPUT_DIR / 'tabel_4_2_sample_data_entitas.png', 
               dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("   ✓ Saved: tabel_4_2_sample_data_entitas.png")

def create_sample_data_table_detailed(df):
    """Tabel 4.3: Sample Data Detail untuk Satu Restoran"""
    print("\nGenerating Detailed Sample Data Table...")
    
    # Ambil satu restoran sebagai contoh detail
    sample = df.iloc[0]
    
    # Siapkan data atribut
    attributes = []
    
    # ID dan Name
    attributes.append(['ID', str(sample['id'])])
    attributes.append(['Nama', sample['name']])
    attributes.append(['Rating', f"{sample['rating']:.1f} / 5.0"])
    
    # About (truncated)
    about_text = str(sample['about'])[:120] + '...' if len(str(sample['about'])) > 120 else sample['about']
    attributes.append(['Deskripsi (About)', about_text])
    
    # Cuisines
    try:
        cuisines = ast.literal_eval(sample['cuisines']) if pd.notna(sample['cuisines']) else []
        cuisines_str = ', '.join(cuisines)
    except:
        cuisines_str = '-'
    attributes.append(['Cuisines', cuisines_str])
    
    # Entitas Lokasi
    attributes.append(['Entitas Lokasi', sample['entitas_lokasi'] if pd.notna(sample['entitas_lokasi']) else '-'])
    
    # Entitas Jenis Makanan
    try:
        jenis = ast.literal_eval(sample['entitas_jenis_makanan']) if pd.notna(sample['entitas_jenis_makanan']) else []
        jenis_str = ', '.join(jenis) if jenis else '-'
    except:
        jenis_str = '-'
    attributes.append(['Entitas Jenis Makanan', jenis_str])
    
    # Entitas Features
    try:
        features = ast.literal_eval(sample['entitas_features']) if pd.notna(sample['entitas_features']) else []
        features_str = ', '.join(features[:6]) + ('...' if len(features) > 6 else '') if features else '-'
    except:
        features_str = '-'
    attributes.append(['Entitas Features', features_str])
    
    # Preferences
    try:
        prefs = ast.literal_eval(sample['entitas_preferensi']) if pd.notna(sample['entitas_preferensi']) else []
        prefs_str = ', '.join(prefs[:6]) + ('...' if len(prefs) > 6 else '') if prefs else '-'
    except:
        prefs_str = '-'
    attributes.append(['Entitas Preferensi', prefs_str])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    table = ax.table(
        cellText=attributes,
        colLabels=['Atribut', 'Nilai'],
        cellLoc='left',
        loc='center',
        colWidths=[0.25, 0.75]
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Style header
    for i in range(2):
        cell = table[(0, i)]
        cell.set_facecolor('#4CAF50')
        cell.set_text_props(weight='bold', color='white', size=11)
    
    # Style rows
    for i in range(1, len(attributes) + 1):
        # Attribute name column (bold)
        table[(i, 0)].set_text_props(weight='bold')
        table[(i, 0)].set_facecolor('#e8f5e9')
        
        # Value column
        if i % 2 == 0:
            table[(i, 1)].set_facecolor('#f5f5f5')
    
    plt.title('Tabel 4.3 Contoh Detail Data Restoran dengan Semua Atribut dan Entitas', 
             fontsize=13, fontweight='bold', pad=20)
    
    plt.savefig(OUTPUT_DIR / 'tabel_4_3_sample_data_detail.png', 
               dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("   ✓ Saved: tabel_4_3_sample_data_detail.png")

def create_entity_comparison_table(df):
    """Tabel 4.4: Perbandingan Entitas dari 3 Restoran"""
    print("\nGenerating Entity Comparison Table...")
    
    # Pilih 3 restoran dengan karakteristik berbeda
    sample_indices = [0, 1, 5]  # Asian, Mexican, Italian
    sample_df = df.iloc[sample_indices].copy()
    
    # Siapkan data
    table_data = []
    
    for idx, row in sample_df.iterrows():
        # Parse entitas
        try:
            lokasi = row['entitas_lokasi'] if pd.notna(row['entitas_lokasi']) else '-'
        except:
            lokasi = '-'
        
        try:
            cuisine = ast.literal_eval(row['cuisines']) if pd.notna(row['cuisines']) else []
            cuisine_str = ', '.join(cuisine[:2]) + ('...' if len(cuisine) > 2 else '') if cuisine else '-'
        except:
            cuisine_str = '-'
        
        try:
            features = ast.literal_eval(row['entitas_features']) if pd.notna(row['entitas_features']) else []
            features_count = len(features)
            features_preview = ', '.join(features[:2]) + ('...' if len(features) > 2 else '') if features else '-'
        except:
            features_count = 0
            features_preview = '-'
        
        try:
            preferensi = ast.literal_eval(row['entitas_preferensi']) if pd.notna(row['entitas_preferensi']) else []
            pref_str = ', '.join(preferensi[:2]) + ('...' if len(preferensi) > 2 else '') if preferensi else '-'
        except:
            pref_str = '-'
        
        name = row['name'][:35] + '...' if len(str(row['name'])) > 35 else row['name']
        rating = f"{row['rating']:.1f}" if pd.notna(row['rating']) else '-'
        
        table_data.append([
            name,
            rating,
            lokasi,
            cuisine_str[:30] + '...' if len(cuisine_str) > 30 else cuisine_str,
            features_preview[:35] + '...' if len(features_preview) > 35 else features_preview,
            pref_str[:30] + '...' if len(pref_str) > 30 else pref_str
        ])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(18, 5))
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    table = ax.table(
        cellText=table_data,
        colLabels=['Nama Restoran', 'Rating', 'Lokasi', 'Cuisine/Jenis Makanan', 'Features', 'Preferensi'],
        cellLoc='left',
        loc='center',
        colWidths=[0.20, 0.08, 0.12, 0.20, 0.22, 0.18]
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.8)
    
    # Style header
    for i in range(6):
        cell = table[(0, i)]
        cell.set_facecolor('#FF9800')
        cell.set_text_props(weight='bold', color='white', size=10)
    
    # Style rows with color coding
    colors = ['#fff3e0', '#ffe0b2', '#ffcc80']
    for i in range(1, len(table_data) + 1):
        for j in range(6):
            cell = table[(i, j)]
            cell.set_facecolor(colors[i-1])
            if j == 1:  # Rating column
                cell.set_text_props(weight='bold')
    
    plt.title('Tabel 4.4 Perbandingan Entitas dari Tiga Restoran dengan Karakteristik Berbeda', 
             fontsize=13, fontweight='bold', pad=20)
    
    plt.savefig(OUTPUT_DIR / 'tabel_4_4_entity_comparison.png', 
               dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("   ✓ Saved: tabel_4_4_entity_comparison.png")

def create_entity_statistics_table(df):
    """Tabel 4.5: Statistik Entitas Dataset"""
    print("\nGenerating Entity Statistics Table...")
    
    # Hitung statistik untuk setiap entitas
    stats_data = []
    
    # 1. Lokasi
    unique_locations = df['entitas_lokasi'].nunique()
    filled_locations = df['entitas_lokasi'].notna().sum()
    stats_data.append(['Entitas Lokasi', unique_locations, filled_locations, f"{(filled_locations/len(df)*100):.1f}%"])
    
    # 2. Jenis Makanan
    jenis_count = 0
    jenis_filled = 0
    all_jenis = set()
    for val in df['entitas_jenis_makanan'].dropna():
        try:
            items = ast.literal_eval(val)
            if items:
                jenis_filled += 1
                all_jenis.update(items)
        except:
            pass
    stats_data.append(['Entitas Jenis Makanan', len(all_jenis), jenis_filled, f"{(jenis_filled/len(df)*100):.1f}%"])
    
    # 3. Cuisine
    all_cuisine = set()
    cuisine_filled = 0
    for val in df['cuisines'].dropna():
        try:
            items = ast.literal_eval(val)
            if items:
                cuisine_filled += 1
                all_cuisine.update(items)
        except:
            pass
    stats_data.append(['Cuisine', len(all_cuisine), cuisine_filled, f"{(cuisine_filled/len(df)*100):.1f}%"])
    
    # 4. Features
    all_features = set()
    features_filled = 0
    for val in df['entitas_features'].dropna():
        try:
            items = ast.literal_eval(val)
            if items:
                features_filled += 1
                all_features.update(items)
        except:
            pass
    stats_data.append(['Entitas Features', len(all_features), features_filled, f"{(features_filled/len(df)*100):.1f}%"])
    
    # 5. Preferences
    all_prefs = set()
    prefs_filled = 0
    for val in df['entitas_preferensi'].dropna():
        try:
            items = ast.literal_eval(val)
            if items:
                prefs_filled += 1
                all_prefs.update(items)
        except:
            pass
    stats_data.append(['Entitas Preferensi', len(all_prefs), prefs_filled, f"{(prefs_filled/len(df)*100):.1f}%"])
    
    # Total summary
    stats_data.append(['TOTAL DATASET', len(df), len(df), '100%'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    table = ax.table(
        cellText=stats_data,
        colLabels=['Jenis Entitas', 'Nilai Unik', 'Restoran Terisi', 'Coverage (%)'],
        cellLoc='left',
        loc='center',
        colWidths=[0.35, 0.2, 0.25, 0.2]
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Style header
    for i in range(4):
        cell = table[(0, i)]
        cell.set_facecolor('#673AB7')
        cell.set_text_props(weight='bold', color='white', size=12)
    
    # Style rows
    for i in range(1, len(stats_data) + 1):
        for j in range(4):
            cell = table[(i, j)]
            if i == len(stats_data):  # Total row
                cell.set_facecolor('#E1BEE7')
                cell.set_text_props(weight='bold')
            elif i % 2 == 0:
                cell.set_facecolor('#f5f5f5')
            
            # Bold for first column
            if j == 0:
                cell.set_text_props(weight='bold')
    
    plt.title('Tabel 4.5 Statistik dan Coverage Entitas dalam Dataset', 
             fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig(OUTPUT_DIR / 'tabel_4_5_entity_statistics.png', 
               dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("   ✓ Saved: tabel_4_5_entity_statistics.png")

def main():
    print("="*60)
    print("GENERATING SAMPLE DATA TABLES WITH ENTITIES")
    print("="*60)
    
    # Load data
    df = load_data()
    
    # Generate all tables
    create_sample_data_table_full(df)
    create_sample_data_table_detailed(df)
    create_entity_comparison_table(df)
    create_entity_statistics_table(df)
    
    print("\n" + "="*60)
    print("✓ ALL SAMPLE DATA TABLES GENERATED!")
    print(f"✓ Check folder: {OUTPUT_DIR}")
    print("="*60)
    print("\nFiles generated:")
    print("  1. tabel_4_2_sample_data_entitas.png")
    print("     → 3 restoran dengan semua entitas penting")
    print("  2. tabel_4_3_sample_data_detail.png")
    print("     → Detail lengkap 1 restoran dengan semua atribut")
    print("  3. tabel_4_4_entity_comparison.png")
    print("     → Perbandingan entitas dari 3 restoran berbeda")
    print("  4. tabel_4_5_entity_statistics.png")
    print("     → Statistik coverage entitas di dataset")
    print("\nReady to use in your thesis!")

if __name__ == "__main__":
    main()
