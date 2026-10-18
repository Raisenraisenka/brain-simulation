import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run_simulation():
    Ne = 800
    Ni = 200
    N = Ne + Ni
    
    re = np.random.rand(Ne)
    ri = np.random.rand(Ni)
    
    a = np.concatenate([0.02 * np.ones(Ne), 0.02 + 0.08 * ri])
    b = np.concatenate([0.2 * np.ones(Ne), 0.25 - 0.05 * ri])
    c = np.concatenate([-65 + 15 * re**2, -65 * np.ones(Ni)])
    d = np.concatenate([8 - 6 * re**2, 2 * np.ones(Ni)])
    
    # Proven Gamma weights
    S_E_base = 0.8 * np.random.rand(N, Ne)
    S_I_base = -1.5 * np.random.rand(N, Ni)
    
    v = -65 + 5 * np.random.randn(N)
    u = b * v
    
    spike_times = []
    spike_neurons = []
    activity_history = []
    
    print("Epilepsy Simulation Starting...")
    
    for t in range(3000):
        # ===== 3 PHASES =====
        if t < 1000:
            se_mult = 1.0
            si_mult = 1.0
            state = "Normal"
        elif t < 2000:
            se_mult = 2.5       # Claude's suggestion: 5.0 -> 2.5
            si_mult = 0.0
            state = "Seizure"
        else:
            se_mult = 1.0
            si_mult = 4.0
            state = "Medication"
        
        S_E = S_E_base * se_mult
        S_I = S_I_base * si_mult
        S_active = np.concatenate([S_E, S_I], axis=1)
        
        # Thalamic gamma drive
        gamma_drive = 8 * np.sin(2 * np.pi * 40 * t / 1000)
        I = np.concatenate([
            5 * np.random.randn(Ne),
            2 * np.random.randn(Ni)
        ]) + gamma_drive
        
        # Spike detection
        fired = np.where(v >= 30)[0]
        
        # Reset fired neurons
        v[fired] = c[fired]
        u[fired] = u[fired] + d[fired]
        
        # Add synaptic input
        if len(fired) > 0:
            I = I + np.sum(S_active[:, fired], axis=1)
        
        # ===== CLAUDE'S FIX =====
        I = np.clip(I, -100.0, 100.0)
        
        for _ in range(2):  # two half-steps
            v = v + 0.5 * (0.04 * v**2 + 5 * v + 140 - u + I)
            v = np.clip(v, -100.0, 30.0)   # clip between each half-step
        
        u = u + a * (b * v - u)            # update u with clipped v
        u = np.clip(u, -50.0, 50.0)        # clip u to prevent blow-up
        # ========================
        
        for idx in fired:
            spike_times.append(t)
            spike_neurons.append(idx)
        activity_history.append(len(fired))
        
        # Window average print (not just 1 ms)
        if t % 500 == 0 and t > 0:
            print(f"   t={t:4d} ms  →  {np.mean(activity_history[-100:]):.1f} neurons/ms | {state}")

    # ===== VISUALIZATION =====
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), facecolor='#0a0a1a', gridspec_kw={'height_ratios': [2, 1]})
    colors = np.array(['#ff3366'] * Ne + ['#00ccff'] * Ni)
    
    ax1.set_facecolor('#0a0a1a')
    ax1.scatter(spike_times, spike_neurons, c=colors[spike_neurons], s=1, alpha=0.6)
    ax1.set_ylabel('Neuron #', color='white')
    ax1.set_title('Epilepsy Model: Normal → Seizure → Medication', color='white', fontsize=14)
    ax1.tick_params(colors='white')
    for sp in ax1.spines.values(): sp.set_color('white')
    ax1.axvline(x=1000, color='yellow', linestyle='--', linewidth=2)
    ax1.axvline(x=2000, color='#00ff00', linestyle='--', linewidth=2)
    
    ax2.set_facecolor('#0a0a1a')
    ax2.plot(activity_history, color='#ff3366', linewidth=1)
    ax2.fill_between(range(3000), activity_history, color='#ff3366', alpha=0.3)
    ax2.set_xlabel('Time (ms)', color='white')
    ax2.set_ylabel('Active Neurons', color='white')
    ax2.tick_params(colors='white')
    for sp in ax2.spines.values(): sp.set_color('white')
    ax2.axvline(x=1000, color='yellow', linestyle='--', linewidth=2)
    ax2.axvline(x=2000, color='#00ff00', linestyle='--', linewidth=2)
    
    plt.tight_layout()
    plt.savefig('/sdcard/Download/epilepsy_sim.png', dpi=100, facecolor='#0a0a1a')
    print("📸 Image saved: /sdcard/Download/epilepsy_sim.png")

if __name__ == "__main__":
    run_simulation()
