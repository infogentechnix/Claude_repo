# Enough Light — score, foley and narration → out/mix.wav (48 kHz stereo).
# Run with the library's Python: "$LIB/.venv/bin/python" mix.py   (LIB = the Lemo-Opuscar library)
# Reads events.json (from core/render/events.mjs), voices/*.wav; writes out/score.wav and out/mix.wav.
import json, os, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly, fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.environ.get('LIB') or os.path.expanduser('~/lemo-opuscar')
sys.path.insert(0, LIB)
os.chdir(LIB)                                    # the sampler finds its instruments relative to the library
from core.audio import sampler as S
from core.audio.sfx import SR, bp, lp, hp, add, compress, limit, ding

EVF = json.load(open(os.path.join(HERE, 'events.json')))
DUR = EVF['dur']; EV = EVF['ev']; N = int(DUR * SR)
rng = np.random.default_rng(7)
BPM = 72; BEAT = 60 / BPM; BAR = 4 * BEAT
def at(b, beat=1.0): return (b - 1) * BAR + (beat - 1) * BEAT
def noise(d): return rng.standard_normal(int(round(d * SR)))
def norm(x, p=1.0): m = np.abs(x).max(); return x * (p / m) if m > 0 else x
def tt(d): return np.arange(int(round(d * SR))) / SR
def dbfs(x): return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12)

# ---------------- score (cue map in TREATMENT.md §6) ----------------
S.seed(3)
sc = []
def n(t, inst, p, d, v, pan=0.0, **k): sc.append(dict(t=t, inst=inst, pitch=p, dur=d, vel=v, pan=pan, **k))
# bars 1–2 · Rain: felt piano alone, A minor
for b, (lh, rh) in enumerate([(['A2', 'E3'], ['E5', 'C5', 'B4', 'C5']), (['F2', 'C3'], ['A4', 'C5', 'E5', 'D5'])], start=1):
    for i, p in enumerate(lh): n(at(b) + i * .05, 'piano', p, BAR, .32, -.15)
    for i, p in enumerate(rh): n(at(b, 1 + i), 'piano', p, BEAT * 1.6, .30 if i else .36, .15)
# bars 3–4 · Alone: piano + quiet cello pad
n(at(3), 'cellos', 'D3', BAR, .26, .25, attack=.8); n(at(4), 'cellos', 'E3', BAR, .26, .25, attack=.6)
for b, (lh, rh) in enumerate([(['D3', 'A3'], ['F4', 'A4', 'C5', 'A4']), (['E2', 'B2'], ['B4', 'E5', 'D5', 'B4'])], start=3):
    for i, p in enumerate(lh): n(at(b) + i * .05, 'piano', p, BAR, .3, -.15)
    for i, p in enumerate(rh): n(at(b, 1 + i), 'piano', p, BEAT * 1.6, .28, .15)
# bar 5 · Breath: one chord held, almost silence
for i, p in enumerate(['A2', 'E3', 'C4']): n(at(5) + i * .08, 'piano', p, BAR, .26, 0)
n(at(5, 2), 'violins', 'E4', BAR * .9, .14, .3, attack=1.2)
# bar 6 · Turn: strings swell, piano left hand walks up to C major
n(at(6), 'cellos', 'F2', BAR / 2, .34, .25, attack=.4); n(at(6, 3), 'cellos', 'G2', BAR / 2, .4, .25, attack=.2)
n(at(6), 'violas', 'A3', BAR / 2, .3, -.1, attack=.5); n(at(6, 3), 'violas', 'B3', BAR / 2, .36, -.1, attack=.2)
n(at(6), 'violins', 'C5', BAR / 2, .3, .3, attack=.6); n(at(6, 3), 'violins', 'D5', BAR / 2, .38, .3, attack=.3)
for i, p in enumerate(['F2', 'G2', 'A2', 'B2']): n(at(6, 1 + i), 'piano', p, BEAT * 1.2, .34, -.15)
# bars 7–8 · Bloom: full and warm
for b, chord, mel, cel, vla, vln in [(7, ['C3', 'G3', 'C4', 'E4', 'G4'], ['G5', 'A5', 'G5', 'E5'], 'C3', 'G3', 'E5'),
                                     (8, ['F2', 'C3', 'F3', 'A3', 'C4'], ['F5', 'E5', 'C5', 'D5'], 'F3', 'A3', 'F5')]:
    for i, p in enumerate(chord): n(at(b) + i * .11, 'piano', p, BAR, .4, -.1)
    for i, p in enumerate(chord[2:]): n(at(b, 3) + i * .11, 'piano', p, BEAT * 2, .3, .1)
    n(at(b), 'cellos', cel, BAR, .4, .25, attack=.15)
    n(at(b), 'violas', vla, BAR, .34, -.15, attack=.2)
    n(at(b), 'violins', vln, BAR, .36, .3, attack=.2)
    for i, p in enumerate(mel): n(at(b, 1 + i), 'flute', p, BEAT * .95, .42, -.3)
n(at(7), 'glockenspiel', 'C6', 2.5, .5, .2); n(at(7) + .12, 'glockenspiel', 'E6', 2.5, .42, .3); n(at(7) + .24, 'glockenspiel', 'G6', 2.5, .4, .4)
for k in range(6): n(at(7, 2) + k * BEAT * .75 + rng.uniform(0, .05), 'glockenspiel', ['G6', 'E6', 'C7', 'A6', 'G6', 'E6'][k], 1.5, .22, rng.uniform(-.5, .5))
# bar 9 · Resolve on C major
for i, p in enumerate(['C3', 'E3', 'G3', 'C4', 'E4', 'G4']): n(at(9) + i * .1, 'piano', p, 3.3, .34, 0)
n(at(9), 'cellos', 'C3', 3.2, .3, .25, attack=.2); n(at(9), 'violas', 'G3', 3.2, .26, -.15, attack=.2); n(at(9), 'violins', 'E5', 3.2, .28, .3, attack=.2)
n(at(9, 3), 'glockenspiel', 'C6', 2.5, .3, .1)
score = S.render(sc, dur=DUR)
score = S.room(score, size=.5, mix=.2)
fo = int(1.2 * SR); score[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
sf.write(os.path.join(HERE, 'out', 'score.wav'), score, SR)

# ---------------- foley (sound design table in TREATMENT.md §7) ----------------
fx = np.zeros((N, 2))
def pink(d):
    m = int(round(d * SR)); w = np.fft.rfft(rng.standard_normal(m)); f = np.arange(len(w)); f[0] = 1
    return np.fft.irfft(w / np.sqrt(f), m)
def rain_bed():
    x = lp(hp(pink(DUR), 400), 7000) * 6
    drops = np.zeros(N); idx = rng.integers(0, N, int(DUR * 90)); drops[idx] = rng.uniform(.2, 1, len(idx))
    x += bp(drops, 2500, 9000) * 1.8
    t = tt(DUR); g = 1 - np.clip((t - 17.7) / (25.5 - 17.7), 0, 1); g = g * g * (3 - 2 * g)
    g *= np.minimum(1, t / .8)
    y = norm(x * g, .16)
    return np.stack([y, np.roll(y, 480)], 1)
fx += rain_bed()
def drip():
    t = tt(.35); f = rng.uniform(1700, 3000)
    return np.sin(2 * np.pi * f * t * (1 + .25 * np.exp(-t * 40))) * np.exp(-t * 22) * .5 + bp(noise(.35), 3000, 8000) * np.exp(-t * 90) * .3
def pencil(d):
    t = tt(d); jit = np.repeat(rng.uniform(.2, 1, int(d * 34) + 1), int(SR / 34) + 1)[:len(t)]
    return bp(noise(d), 2200, 6500) * jit * np.sin(np.pi * np.clip(t / d, 0, 1)) ** .5
def brush(d):
    t = tt(d)
    x = bp(noise(d), 1500, 7000) * (.6 + .4 * np.abs(np.sin(t * 2 * np.pi * 9))) + bp(pink(d), 300, 1500) * 4
    return norm(x * np.sin(np.pi * np.clip(t / d, 0, 1)) ** .8, .5)
def bloom(d):
    t = tt(d); e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    x = lp(pink(d), 900) * 3 + sum(np.sin(2 * np.pi * f * t) * a for f, a in [(261.6, .3), (392, .2), (523.3, .12)])
    return norm(x * e, .5)
def sweep(d):
    t = tt(d); return norm(bp(noise(d), 800, 5000) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.2, .5)
def petal():
    t = tt(.18); return bp(noise(.18), 3000, 9000) * np.exp(-t * 30)
def mist(d):
    t = tt(d); return norm(lp(pink(d), 2500) * np.sin(np.pi * np.clip(t / d, 0, 1)), .5)
def chirp():
    d = rng.uniform(.08, .16); t = tt(d); f0 = rng.uniform(3200, 4600)
    return np.sin(2 * np.pi * np.cumsum(f0 + 900 * np.sin(np.pi * t / d)) / SR) * np.sin(np.pi * t / d)
def put(x, t, g, pan=0.0):
    if t < DUR: add(fx, x, t, g, pan)
for e in EV:
    k, t, p = e['type'], e['t'], e.get('pan', 0)
    if k == 'drip': put(drip(), t, .2, p)
    elif k == 'pencil': put(pencil(e['d']), t, .1, p)
    elif k == 'brush': put(brush(e['d']), t, .14, p)
    elif k == 'bloom': put(bloom(e['d']), t, .18 if e['d'] > 2 else .1)
    elif k == 'sweep': put(sweep(e['d']), t, .12)
    elif k == 'chime': put(ding(.5), t, .14, .1)
    elif k == 'petal': put(petal(), t, .06, p)
    elif k == 'mist': put(mist(e['d']), t, .12)
for i in range(16):                               # first birds after the bloom, then a light breeze
    t0 = 20.6 + i * .58 + rng.uniform(0, .3); pan = rng.uniform(-.7, .7)
    for j in range(rng.integers(1, 4)): put(chirp(), t0 + j * .12, .035, pan)
br = lp(pink(DUR), 600) * 2; g = np.clip((tt(DUR) - 22) / 4, 0, 1); br = norm(br * g, .06)
fx += np.stack([br, np.roll(br, 2400)], 1)

# ---------------- narration ----------------
vo = np.zeros((N, 2))
for e in EV:
    if e['type'] != 'vo': continue
    x, sr = sf.read(os.path.join(HERE, 'voices', e['id'] + '.wav'), dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    x = resample_poly(x, SR, sr)
    x = compress(x, thr=.2, ratio=3)
    add(vo, x, e['t'], 1.0, 0)
ir = rng.standard_normal((int(.6 * SR), 2)) * np.exp(-np.arange(int(.6 * SR)) / SR * 9)[:, None]
ir = np.stack([lp(ir[:, 0], 4000), lp(ir[:, 1], 4000)], 1); ir /= np.sqrt((ir ** 2).sum(0))
vo = vo + .1 * np.stack([fftconvolve(vo[:, 0], ir[:, 0])[:N], fftconvolve(vo[:, 1], ir[:, 1])[:N]], 1)
vo = limit(vo, .9)

# ---------------- balance: voice ~10 dB over the music, music ducked ~4 dB under voice ----------------
act = np.abs(vo).mean(1) > 1e-3
win = int(.25 * SR)
envv = np.convolve(act.astype(float), np.ones(win) / win, 'same')
duck = 10 ** (-4 * np.clip(envv * 1.6, 0, 1) / 20)
mus = score * duck[:, None]
vrms = dbfs(vo[act]) if act.any() else -20
mus *= 10 ** ((vrms - 10 - dbfs(mus[act] if act.any() else mus)) / 20)
fx *= 10 ** ((dbfs(mus) - 6 - dbfs(fx)) / 20)
mix = limit(vo + mus + fx, .95)
sf.write(os.path.join(HERE, 'out', 'mix.wav'), mix.astype(np.float32), SR)
print(f'mix: {DUR:.1f}s  voice {vrms:.1f} dBFS  music {dbfs(mus):.1f} dBFS  fx {dbfs(fx):.1f} dBFS')
