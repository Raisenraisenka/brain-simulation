import numpy as np
import wave

SAMPLE_RATE = 44100
DURATION = 12.0
samples = int(SAMPLE_RATE * DURATION)
t = np.linspace(0, DURATION, samples, False)

# Nota frekansları (A minor tonu)
notalar = {
    'A2': 110.00, 'C3': 130.81, 'E3': 164.81,
    'A3': 220.00, 'C4': 261.63, 'E4': 329.63,
    'G3': 196.00, 'B3': 246.94, 'D4': 293.66,
    'F3': 174.61, 'A4': 440.00, 'G4': 392.00,
}

ses = np.zeros(samples)

def nota(freq, start, sure, guc=0.3):
    """Bir nota üret (fundamental + harmonikler)"""
    n_start = int(start * SAMPLE_RATE)
    n_sure = int(sure * SAMPLE_RATE)
    n_end = min(n_start + n_sure, samples)
    if n_end <= n_start:
        return
    tt = np.linspace(0, sure, n_end - n_start, False)
    
    # ADSR envelope (yumuşak giriş/çıkış)
    env = np.ones_like(tt)
    attack = int(0.05 * SAMPLE_RATE)
    release = int(0.3 * SAMPLE_RATE)
    if len(env) > attack + release:
        env[:attack] = np.linspace(0, 1, attack)
        env[-release:] = np.linspace(1, 0, release)
    
    # Fundamental + harmonikler (zengin ton)
    dalga = (
        1.0 * np.sin(2 * np.pi * freq * tt) +
        0.4 * np.sin(2 * np.pi * 2 * freq * tt) +
        0.2 * np.sin(2 * np.pi * 3 * freq * tt) +
        0.1 * np.sin(2 * np.pi * 4 * freq * tt)
    )
    ses[n_start:n_end] += guc * dalga * env

# Akor ilerlemesi: Am - F - C - G (4 akor, her biri 3 saniye)
# Am
nota(notalar['A2'], 0.0, 3.0, 0.25)
nota(notalar['C4'], 0.0, 3.0, 0.15)
nota(notalar['E4'], 0.0, 3.0, 0.15)

# F
nota(notalar['F3'], 3.0, 3.0, 0.25)
nota(notalar['A3'], 3.0, 3.0, 0.15)
nota(notalar['C4'], 3.0, 3.0, 0.15)

# C
nota(notalar['C3'], 6.0, 3.0, 0.25)
nota(notalar['E4'], 6.0, 3.0, 0.15)
nota(notalar['G3'], 6.0, 3.0, 0.15)

# G
nota(notalar['G3'], 9.0, 3.0, 0.25)
nota(notalar['B3'], 9.0, 3.0, 0.15)
nota(notalar['D4'], 9.0, 3.0, 0.15)

# Melodi (üstte süzülen notalar)
melodi = [
    ('E4', 0.5, 0.8), ('G4', 1.5, 0.8), ('A4', 2.5, 0.5),
    ('C4', 3.5, 0.8), ('A3', 4.5, 0.8), ('F3', 5.5, 0.5),
    ('G3', 6.5, 0.8), ('E4', 7.5, 0.8), ('C4', 8.5, 0.5),
    ('D4', 9.5, 0.8), ('B3', 10.5, 0.8), ('G3', 11.5, 0.5),
]
for isim, bas, sure in melodi:
    nota(notalar[isim], bas, sure, 0.2)

# Normalize et (kırpma önle)
ses = ses / np.max(np.abs(ses)) * 0.9

# WAV olarak kaydet (Python'un daxili wave modulu ile)
with wave.open('muzik.wav', 'w') as wav_file:
    wav_file.setnchannels(1)      # mono
    wav_file.setsampwidth(2)      # 16-bit
    wav_file.setframerate(SAMPLE_RATE)
    
    # float -> int16
    ses_int16 = (ses * 32767).astype(np.int16)
    wav_file.writeframes(ses_int16.tobytes())

print("✅ muzik.wav yaradıldı")
print(f"   Müddət: {DURATION} saniyə")
print(f"   Format: {SAMPLE_RATE} Hz, mono")
