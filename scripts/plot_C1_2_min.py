# Plot Fig.C1-2 from outputs/C1/metrics.json
import json, matplotlib.pyplot as plt, pathlib

with open("outputs/C1/metrics.json","r",encoding="utf-8") as f:
    data = json.load(f)

p = [r["p"] for r in data["results"]]
cr = [r["CR"] for r in data["results"]]
sp = [r["SP"] for r in data["results"]]

fig, ax1 = plt.subplots(figsize=(7,4))
ax1.plot(p, cr, 'o-', color='#3498db', label='CR'); ax1.set_ylim(0,1)
ax1.set_xlabel('Pruning Rate (p)'); ax1.set_ylabel('CR', color='#3498db')
ax1.tick_params(axis='y', labelcolor='#3498db')
ax1.grid(alpha=0.3, color='#eaeaea')

ax2 = ax1.twinx()
ax2.plot(p, sp, '^--', color='#e67e22', label='SP'); ax2.set_ylim(0,1)
ax2.set_ylabel('SP', color='#e67e22')
ax2.tick_params(axis='y', labelcolor='#e67e22')

ax1.axvspan(0.3,0.6, alpha=0.15, color='#95a5a6')
ax1.axhline(0.6, ls=':', color='gray'); ax2.axhline(0.6, ls=':', color='gray')
fig.suptitle('Fig.C1-2 (mini)')
pathlib.Path("figs/C1").mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig("figs/C1/fig_C1_2.svg", dpi=200)
