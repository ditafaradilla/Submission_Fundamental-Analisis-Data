import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime as dt
from matplotlib.ticker import MaxNLocator
import warnings
import os
from matplotlib.ticker import ScalarFormatter

warnings.simplefilter(action='ignore', category=FutureWarning)

# Konfigurasi tampilan halaman Streamlit
st.set_page_config(page_title="E-Commerce Performance Dashboard", layout="wide")
sns.set(style='dark')

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================

def create_top_categories_df(df):
    top_categories = df.groupby("product_category_name_english")["price"].sum().sort_values(ascending=False).reset_index().head(5)
    return top_categories

def create_rfm_df(df):
    max_purchase_timestamp = df['order_purchase_timestamp'].max()
    current_date = max_purchase_timestamp + pd.Timedelta(days=1)

    rfm_df = df.groupby('customer_unique_id').agg(
        recency=('order_purchase_timestamp', lambda date: (current_date - date.max()).days),
        frequency=('order_id', 'nunique'),
        monetary=('price', 'sum')
    ).reset_index()

    rfm_df = rfm_df.rename(columns={'customer_unique_id': 'customer_id'})
    return rfm_df

# ==========================================
# 2. LOAD DATA
# ==========================================

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'main_data.csv')
    all_df = pd.read_csv(file_path)
    
    datetime_columns = ["order_purchase_timestamp", "order_approved_at", 
                        "order_delivered_carrier_date", "order_delivered_customer_date", 
                        "order_estimated_delivery_date"]
    
    for column in datetime_columns:
        if column in all_df.columns:
            all_df[column] = pd.to_datetime(all_df[column])
    return all_df

all_df = load_data()

# ==========================================
# 3. SIDEBAR & FILTER
# ==========================================

min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

with st.sidebar:
    st.title(" E-Commerce Analytics")
    st.write(f"**Analis Data:** Dita Faradilla")
    st.markdown("---")
    
    # Filter Rentang Waktu 
    start_date, end_date = st.date_input(
        label='Rentang Waktu Analisis',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter Data Utama
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

top_categories_df = create_top_categories_df(main_df)
rfm_df = create_rfm_df(main_df)

# ==========================================
# 4. MAIN CONTENT
# ==========================================

st.title("E-Commerce Public Dataset Analysis ")

# --- Section 1: Product Category ---
st.header("1. Product Category Performance")
st.info("**Pertanyaan:** Apa saja Top 5 kategori produk yang menyumbang total pendapatan (revenue) tertinggi selama periode tahun 2017, guna menentukan prioritas alokasi stok dan anggaran pemasaran (marketing) pada kuartal berikutnya?")

col1, col2 = st.columns([2, 1])

with col1:
    fig_cat, ax_cat = plt.subplots(figsize=(12, 7))
    sns.barplot(
        x="price",
        y="product_category_name_english",
        data=top_categories_df,
        palette="Paired",
        hue="product_category_name_english",
        legend=False,
        ax=ax_cat
    )
    ax_cat.set_title("5 Kategori Produk dengan Pendapatan Tertinggi", fontsize=18, pad=20)
    ax_cat.set_xlabel("Total Pendapatan (Revenue)", fontsize=14)
    ax_cat.set_ylabel("Kategori Produk", fontsize=14)

    formatter = ScalarFormatter()
    formatter.set_scientific(False) 
    ax_cat.xaxis.set_major_formatter(formatter)
    ax_cat.xaxis.set_major_locator(MaxNLocator(integer=True)) 

    st.pyplot(fig_cat)

with col2:
    st.subheader("Insight Pertanyaan 1")
    st.write("""
    - Kategori **Bed Bath Table** menjadi penyumbang utama pendapatan, diikuti oleh **Watches Gifts** dan **Health Beauty**.
    - Strategi pemasaran pada kategori kebutuhan rumah tangga terbukti paling efektif dalam menarik daya beli.
    - Perlu perhatian khusus pada ketersediaan stok kategori ini karena kontribusinya yang masif.
    """)

st.markdown("---")

# --- Section 2: RFM Analysis ---
st.header("2. Customer Segmentation (RFM Analysis)")
st.info("**Pertanyaan:** Berdasarkan analisis RFM dari keseluruhan riwayat transaksi hingga bulan terakhir, siapa saja Top 5 pelanggan yang memiliki tingkat pembelian paling sering (Frequency) dan nilai transaksi terbesar (Monetary), agar tim pemasaran dapat merancang dan menawarkan program loyalitas eksklusif/VIP kepada mereka?")

# Menyiapkan data Top 5 RFM
top_5_recency = rfm_df.sort_values(by="recency", ascending=True).head(5) 
top_5_frequency = rfm_df.sort_values(by="frequency", ascending=False).head(5)
top_5_monetary = rfm_df.sort_values(by="monetary", ascending=False).head(5)

# Visualisasi RFM
fig_rfm, ax_rfm = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
vibrant_colors = ["#FF1493", "#FFD700", "#00BFFF", "#32CD32", "#FF8C00"]

# --- Visualisasi By Recency ---
sns.barplot(y="recency", x="customer_id", data=top_5_recency, palette=vibrant_colors, hue="customer_id", legend=False, ax=ax_rfm[0])
ax_rfm[0].set_ylabel("Days", fontsize=25)
ax_rfm[0].set_xlabel("Customer ID", fontsize=25)
ax_rfm[0].set_title("By Recency (Days)", loc="center", fontsize=35)
ax_rfm[0].set_xticks(range(len(top_5_recency)))
ax_rfm[0].set_xticklabels([str(x) for x in top_5_recency["customer_id"]], rotation=90, ha='center', fontsize=15)
ax_rfm[0].tick_params(axis='y', labelsize=20)
ax_rfm[0].yaxis.set_major_locator(MaxNLocator(integer=True))

# --- Visualisasi By Frequency ---
sns.barplot(y="frequency", x="customer_id", data=top_5_frequency, palette=vibrant_colors, hue="customer_id", legend=False, ax=ax_rfm[1])
ax_rfm[1].set_ylabel("Order Count", fontsize=25)
ax_rfm[1].set_xlabel("Customer ID", fontsize=25)
ax_rfm[1].set_title("By Frequency", loc="center", fontsize=35)
ax_rfm[1].set_xticks(range(len(top_5_frequency)))
ax_rfm[1].set_xticklabels([str(x) for x in top_5_frequency["customer_id"]], rotation=90, ha='center', fontsize=15)
ax_rfm[1].tick_params(axis='y', labelsize=20)
ax_rfm[1].yaxis.set_major_locator(MaxNLocator(integer=True))

# --- Visualisasi By Monetary ---
sns.barplot(y="monetary", x="customer_id", data=top_5_monetary, palette=vibrant_colors, hue="customer_id", legend=False, ax=ax_rfm[2])
ax_rfm[2].set_ylabel("Revenue (R$)", fontsize=25)
ax_rfm[2].set_xlabel("Customer ID", fontsize=25)
ax_rfm[2].set_title("By Monetary", loc="center", fontsize=35)
ax_rfm[2].set_xticks(range(len(top_5_monetary)))

ax_rfm[2].set_xticklabels([str(x) for x in top_5_monetary["customer_id"]], rotation=90, ha='center', fontsize=15)
ax_rfm[2].tick_params(axis='y', labelsize=20)

fig_rfm.suptitle("Top Customers Based on RFM Parameters", fontsize=50, fontweight='bold')
plt.subplots_adjust(top=0.88, bottom=0.3, wspace=0.3, hspace=0.4)

st.pyplot(fig_rfm)



st.subheader("Insight")
st.write("""
- **Frequency & Monetary:** Kita menemukan pelanggan loyal dengan kontribusi nilai transaksi mencapai lebih dari R$ 13.000.
- **Recency:** Mengidentifikasi pelanggan yang baru saja bertransaksi untuk menjaga retensi tetap tinggi.
""")

st.markdown("---")

# --- Section 3: Conclusion & Recommendation ---
st.header("Conclusion & Recommendation")

col_c1, col_c2 = st.columns(2)

with col_c1:
    st.subheader("Conclusion")
    st.write("""
    Pertanyaan 1: Kategori produk dengan pendapatan tertinggi pada tahun 2017 adalah bed_bath_table, watches_gifts, dan health_beauty. Hal ini membuktikan adanya permintaan pasar yang kuat dan stabil pada sektor perlengkapan rumah tangga serta kebutuhan gaya hidup sepanjang tahun tersebut.
    Pertanyaan 2: Analisis RFM menunjukkan adanya segmen pelanggan dengan kontribusi nilai transaksi (Monetary) yang sangat signifikan. Di sisi lain, analisis musiman pada kategori unggulan mendeteksi adanya lonjakan pesanan yang drastis pada bulan November, yang mengindikasikan sensitivitas pelanggan terhadap momen promosi besar seperti Black Friday.
    """)

with col_c2:
    st.subheader("Recommendation")
    st.write("""
    1. Tim operasional disarankan untuk meningkatkan ketersediaan stok produk pada kategori top-performing setidaknya dua bulan sebelum bulan November untuk mengantisipasi lonjakan musiman yang berulang setiap tahunnya.
2. Meluncurkan program loyalitas eksklusif untuk menjaga retensi pelanggan di segmen High Monetary, serta melakukan kampanye pemasaran ulang (re-engagement) melalui promo khusus bagi pelanggan dengan nilai Recency tinggi agar mereka kembali bertransaksi sebelum benar-benar berpindah ke kompetitor.
    """)

st.caption("Copyright © Dita Faradilla 2026")