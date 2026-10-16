import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


def calistir():
    # ===== Izhikevich 2003 + Talamik Gamma + STDP =====
    Ne = 800
    Ni = 200
    N = Ne + Ni
    
    re = np.random.rand(Ne)
    ri = np.random.rand(Ni)
    
    a = np.concatenate([0.02 * np.ones(Ne), 0.02 + 0.08 * ri])
    b = np.concatenate([0.2 * np.ones(Ne), 0.25 - 0.05 * ri])
    c = np.concatenate([-65 + 15 * re**2, -65 * np.ones(Ni)])
    d = np.concatenate([8 - 6 * re**2, 2 * np.ones(Ni)])
    
    # Başlangıç sinaptik ağırlıkları
    S = np.concatenate([
        0.8 * np.random.rand(N, Ne),
        -1.5 * np.random.rand(N, Ni)
    ], axis=1)
    S_baslangic = S.copy()
    
    # STDP parametreleri
    A_plus = 0.01
    A_minus = 0.012
    tau_pre = 20.0
    tau_post = 20.0
    W_max = 2.0
    
    # İzler (traces)
    pre_trace = np.zeros(N)
    post_trace = np.zeros(N)
    
    v = -65 * np.ones(N)
    u = b * v
    
    spike_zamanlari = []
    spike_hucreleri = []
    aktivite_gecmisi = []
    zaman_gecmisi = []
    agirlik_gecmisi = []
    
    print("Beyin Sinir Hücresi Ağı - STDP Öğrenme")
    print("=" * 55)
    print(f"   Model: Izhikevich 2003 + Talamik Sürücü + STDP")
    print(f"   Yapı:  {Ne} uyarıcı + {Ni} engelleyici = {N} hücre")
    print(f"   STDP:  A+ = {A_plus}, A- = {A_minus}, tau = {tau_pre} ms")
    print(f"   Simülasyon: 2000 ms")
    print("=" * 55)
    print()
    
    for t in range(2000):
        # Talamik gamma sürücüsü
        gamma_drive = 8 * np.sin(2 * np.pi * 40 * t / 1000)
        
        I = np.concatenate([
            5 * np.random.randn(Ne),
            2 * np.random.randn(Ni)
        ]) + gamma_drive
        
        # Ateşleyen hücreler
        fired = np.where(v >= 30)[0]
        
        # Sıfırla
        v[fired] = c[fired]
        u[fired] = u[fired] + d[fired]
        
        # ===== STDP ÖĞRENME =====
        if len(fired) > 0:
            post_trace[fired] = 1.0
            
            for i in fired:
                S[i, :] += A_plus * pre_trace * (S[i, :] >= 0)
                S[i, :] -= A_minus * post_trace * (S[i, :] >= 0)
            
            I = I + np.sum(S[:, fired], axis=1)
        
        # İki yarım adım
        v = v + 0.5 * (0.04 * v**2 + 5 * v + 140 - u + I)
        v = v + 0.5 * (0.04 * v**2 + 5 * v + 140 - u + I)
        u = u + a * (b * v - u)
        
        # İzleri söndür
        pre_trace *= np.exp(-1.0 / tau_pre)
        post_trace *= np.exp(-1.0 / tau_post)
        
        if len(fired) > 0:
            pre_trace[fired] = 1.0
        
        # Sınırla
        S = np.clip(S, -W_max, W_max)
        
        # Kaydet
        for idx in fired:
            spike_zamanlari.append(t)
            spike_hucreleri.append(idx)
        aktivite_gecmisi.append(len(fired))
        zaman_gecmisi.append(t)
        
        if t % 200 == 0:
            agirlik_gecmisi.append(np.mean(np.abs(S)))
            print(f"   t={t:4d} ms  →  {len(fired):3d} hücre  |  Ort. ağırlık: {np.mean(np.abs(S)):.3f}")
    
    ortalama = sum(aktivite_gecmisi) / len(aktivite_gecmisi)
    print()
    print(f"✅ Tamamlandı!")
    print(f"   Toplam spike:      {sum(aktivite_gecmisi)}")
    print(f"   Ortalama aktivite: {ortalama:.1f} spike/ms")
    print(f"   Ağırlık değişimi:  {np.mean(np.abs(S_baslangic)):.3f} → {np.mean(np.abs(S)):.3f}")
    print()
    
    # ===== GÖRSELLEŞTİRME =====
    fig = plt.figure(figsize=(15, 10), facecolor='#0a0a1a')
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    renkler = np.array(['#ff3366'] * Ne + ['#00ccff'] * Ni)
    
    # 1. Aktivite Haritası
    ax1 = fig.add_subplot(gs[:, 0])
    ax1.set_facecolor('#0a0a1a')
    ax1.scatter(spike_zamanlari, spike_hucreleri,
                c=renkler[spike_hucreleri], s=2, alpha=0.6)
    ax1.set_xlabel('Zaman (ms)', color='white', fontsize=11)
    ax1.set_ylabel('Hücre #', color='white', fontsize=11)
    ax1.set_title('Aktivite Haritası', color='white', fontsize=12)
    ax1.tick_params(colors='white')
    for sp in ax1.spines.values():
        sp.set_color('white')
    ax1.grid(True, alpha=0.15, color='white')
    
    # 2. Popülasyon Aktivitesi
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#0a0a1a')
    ax2.plot(zaman_gecmisi, aktivite_gecmisi, color='#ff3366', linewidth=0.8)
    ax2.fill_between(zaman_gecmisi, aktivite_gecmisi, color='#ff3366', alpha=0.3)
    ax2.set_xlabel('Zaman (ms)', color='white', fontsize=11)
    ax2.set_ylabel('Aktif hücreler', color='white', fontsize=11)
    ax2.set_title('Popülasyon Aktivitesi', color='white', fontsize=12)
    ax2.tick_params(colors='white')
    for sp in ax2.spines.values():
        sp.set_color('white')
    ax2.grid(True, alpha=0.15, color='white')
    
    # 3. Öğrenme Eğrisi
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor('#0a0a1a')
    zamanlar = list(range(0, 2000, 200))
    ax3.plot(zamanlar, agirlik_gecmisi, color='#00ccff', linewidth=2, marker='o')
    ax3.set_xlabel('Zaman (ms)', color='white', fontsize=11)
    ax3.set_ylabel('Ortalama |ağırlık|', color='white', fontsize=11)
    ax3.set_title('Öğrenme Eğrisi (STDP)', color='white', fontsize=12)
    ax3.tick_params(colors='white')
    for sp in ax3.spines.values():
        sp.set_color('white')
    ax3.grid(True, alpha=0.15, color='white')
    
    # 4. Ağırlık Dağılımı
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor('#0a0a1a')
    ax4.hist(S_baslangic.flatten(), bins=50, alpha=0.5, 
             color='#00ccff', label='Başlangıç', density=True)
    ax4.hist(S.flatten(), bins=50, alpha=0.5, 
             color='#ff3366', label='Sonra', density=True)
    ax4.set_xlabel('Ağırlık', color='white', fontsize=11)
    ax4.set_ylabel('Yoğunluk', color='white', fontsize=11)
    ax4.set_title('Ağırlık Dağılımı', color='white', fontsize=12)
    ax4.legend(facecolor='#0a0a1a', edgecolor='white', labelcolor='white')
    ax4.tick_params(colors='white')
    for sp in ax4.spines.values():
        sp.set_color('white')
    
    # 5. Hücre Tipi
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.set_facecolor('#0a0a1a')
    bars = ax5.bar(['Uyarıcı', 'Engelleyici'], [Ne, Ni],
                   color=['#ff3366', '#00ccff'], edgecolor='white')
    for bar, val in zip(bars, [Ne, Ni]):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                 str(val), ha='center', color='white', fontsize=11)
    ax5.set_ylabel('Hücre sayısı', color='white', fontsize=11)
    ax5.set_title('Hücre Tipi', color='white', fontsize=12)
    ax5.tick_params(colors='white')
    for sp in ax5.spines.values():
        sp.set_color('white')
    
    plt.suptitle('Beyin Ağı - STDP Öğrenme',
                 color='white', fontsize=16, y=0.98)
    plt.savefig('/sdcard/Download/brain_stdp.png', dpi=100, facecolor='#0a0a1a')
    print("📸 /sdcard/Download/brain_stdp.png")


if __name__ == "__main__":
    calistir()
