import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from mpl_toolkits.mplot3d import Axes3D


# ===== AĞ YAPISI =====
N = 300
Ne = 240   # %80 uyarıcı
Ni = 60    # %20 engelleyici

# 3D konumlar (küre içinde)
theta = np.random.uniform(0, 2 * np.pi, N)
phi = np.arccos(2 * np.random.rand(N) - 1)
r = 1.0
x = r * np.sin(phi) * np.cos(theta)
y = r * np.sin(phi) * np.sin(theta)
z = r * np.cos(phi)

# Hücre tipleri
uyarici = np.array([True] * Ne + [False] * Ni)
renk_temel = np.where(uyarici, 0.0, 0.5)  # 0=uyarıcı, 0.5=engelleyici

# Izhikevich parametreleri
a = np.where(uyarici, 0.02, 0.1)
b = np.where(uyarici, 0.2, 0.2)
c = np.where(uyarici, -65.0, -65.0)
d = np.where(uyarici, 8.0, 2.0)

# Sinaptik bağlantılar
S = np.concatenate([
    0.8 * np.random.rand(N, Ne),
    -1.5 * np.random.rand(N, Ni)
], axis=1)

# Görselleştirme için bağlantı listesi (sadece güçlü olanlar)
baglanti_esik = 0.5
baglantilar = []
for i in range(N):
    for j in range(N):
        if abs(S[i, j]) > baglanti_esik and np.random.rand() < 0.15:
            baglantilar.append((i, j, S[i, j]))
baglantilar = np.array(baglantilar)
print(f"Görselleştirilen bağlantı: {len(baglantilar)}")

# Durum
v = -65 * np.ones(N)
u = b * v

# Kayıtlar
kare_sayisi = 200
kareler = []

print("Simülasyon başlıyor...")
print(f"   {N} hücre, {kare_sayisi} kare")

# ===== SİMÜLASYON =====
for kare in range(kare_sayisi):
    t = kare * 5  # her kare = 5 ms
    
    # Gamma sürücüsü
    gamma_drive = 8 * np.sin(2 * np.pi * 40 * t / 1000)
    
    I = np.concatenate([
        5 * np.random.randn(Ne),
        2 * np.random.randn(Ni)
    ]) + gamma_drive
    
    # Ateşleyenler
    fired = np.where(v >= 30)[0]
    
    v[fired] = c[fired]
    u[fired] = u[fired] + d[fired]
    
    if len(fired) > 0:
        I = I + np.sum(S[:, fired], axis=1)
    
    # İki yarım adım
    v = v + 0.5 * (0.04 * v**2 + 5 * v + 140 - u + I)
    v = v + 0.5 * (0.04 * v**2 + 5 * v + 140 - u + I)
    u = u + a * (b * v - u)
    
    # Kare verilerini kaydet
    kareler.append({
        'v': v.copy(),
        'fired': fired.copy()
    })
    
    if kare % 40 == 0:
        print(f"   Kare {kare}/{kare_sayisi}")

print("Simülasyon tamamlandı! Şimdi video oluşturuluyor...")

# ===== 3D ANİMASYON =====
fig = plt.figure(figsize=(10, 10), facecolor='#000010')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#000010')

def guncelle(kare_idx):
    ax.clear()
    ax.set_facecolor('#000010')
    
    veri = kareler[kare_idx]
    v_sim = veri['v']
    fired = veri['fired']
    
    # Ateşleyenler için renk parlaklığı
    aktiflik = np.clip((v_sim + 65) / 65, 0, 1)  # 0 ile 1 arası
    
    # Renk haritası
    renkler = np.zeros((N, 4))
    # Uyarıcı: siyah → kırmızı
    # Engelleyici: siyah → mavi
    for i in range(N):
        if uyarici[i]:
            renkler[i] = [aktiflik[i], 0.1 * aktiflik[i], 0.3 * aktiflik[i], 0.5 + 0.5 * aktiflik[i]]
        else:
            renkler[i] = [0.1 * aktiflik[i], 0.5 * aktiflik[i], 1.0 * aktiflik[i], 0.5 + 0.5 * aktiflik[i]]
    
    # Noktaları çiz
    ax.scatter(x, y, z, c=renkler, s=30, alpha=0.8, edgecolors='none')
    
    # Ateşleyen hücrelerin çevresine hale
    if len(fired) > 0:
        ax.scatter(x[fired], y[fired], z[fired], 
                   c='yellow', s=150, alpha=0.3, edgecolors='none')
    
    # Aktif bağlantıları çiz
    for i, j, w in baglantilar:
        if v_sim[int(i)] > 20 or v_sim[int(j)] > 20:
            renk = '#ff3366' if w > 0 else '#00ccff'
            ax.plot([x[int(i)], x[int(j)]],
                    [y[int(i)], y[int(j)]],
                    [z[int(i)], z[int(j)]],
                    color=renk, alpha=0.4, linewidth=1)
    
    # Kamera açısı (dönen)
    aci = kare_idx * 1.5
    ax.view_init(elev=20, azim=aci)
    
    # Sınırlar ve etiketler
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_zlim(-1.2, 1.2)
    ax.set_axis_off()
    
    ax.set_title(f'3D Beyin Ağı - t={kare_idx*5} ms',
                 color='white', fontsize=14)

print("Video kareleri oluşturuluyor...")
anim = FuncAnimation(fig, guncelle, frames=kare_sayisi, interval=50)

# MP4 olarak kaydet
writer = FFMpegWriter(fps=20, bitrate=2000)
anim.save('/sdcard/Download/brain_3d.mp4', writer=writer, dpi=80)

print("✅ Video kaydedildi: /sdcard/Download/brain_3d.mp4")
plt.close()
