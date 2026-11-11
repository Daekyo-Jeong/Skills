# "Tidewater" — new age / ambient piano. MIDI piano+strings (FluidSynth) + DSP shimmer pad, FM bells, ocean wind, drone
"""Exact reference track (fixed composition). Reproduces the approved sample bit-for-bit
modulo FluidSynth version. Use as the quality bar / A-B reference."""
import random
import engine as E
from engine import *  # noqa: F401,F403
LUFS = -16


def plan(seed=None):
    return dict(seed=21, fixed=True)


def render(p, out_path):
    E.seed(11)  # the original engine's module-level RNG seed
    random.seed(21)
    BPM=66; b=60/BPM
    # (root, arpeggio tones low->high, chord tones for pads)
    P1=[(38,[38,45,52,54,57],[62,64,66,69]),   # Dmaj9 (add9)
        (35,[35,42,49,50,54],[59,62,64,66]),   # Bm11
        (31,[31,38,45,47,54],[59,62,66,69]),   # Gmaj9#11-ish
        (33,[33,40,45,47,52],[57,61,64,69])]   # Asus2 -> A
    P2=[(40,[40,47,54,55,59],[59,62,66,67]),   # Em9
        (42,[42,49,52,57,61],[61,64,66,69]),   # F#m7
        (31,[31,38,43,50,54],[59,62,66,67]),   # Gmaj7
        (33,[33,40,45,47,52],[57,61,64,69])]   # Asus
    sect=['intro']*4+['A']*8+['B']*8+['C']*8+['out']*4
    bars=len(sect); L=int((bars*4*b+9)*SR)
    def T(bar,beat): return (bar*4+beat)*b
    piano=[]; strings=[]; mel=[]
    arp_pat=[0,1,2,3,4,3,2,1]  # 8ths up-down
    for i,sc in enumerate(sect):
        chs=P1 if (i//4)%2==0 or sc in('intro','A') else P2
        root,arp,tones=chs[i%4]
        if sc=='intro':
            if i>=2: piano.append((root+12,T(i,0),4*b,38))
            continue
        dens = 8 if sc in('B','C') else (4 if sc=='A' and i<6 else 8)
        for e in range(dens):
            k=arp_pat[e*(8//dens)]; p=arp[k]
            v=46+10*(e==0)+(8 if sc=='C' else 0)+random.randint(-5,5)
            piano.append((p,T(i,e*(4/dens))+random.uniform(0,0.015),(4/dens)*b*1.8,v))
        if sc in('B','C','out'):
            for p in tones: strings.append((p-12 if sc=='out' else p,T(i,0),4*b+0.3,50 if sc=='C' else 40))
        if sc=='out': piano.append((root,T(i,0),4*b,40))
    # melody: long, singing, D major pentatonic; B states theme, C answers higher
    theme=[[(0,74,1.5),(1.5,76,.5),(2,78,2)],[(0,81,2),(2,78,1),(3,76,1)],
           [(0,74,3),(3,71,1)],[(0,73,1.5),(1.5,76,2.5)],
           [(0,71,1.5),(1.5,74,.5),(2,76,2)],[(0,78,2),(2,81,1),(3,78,1)],
           [(0,79,1.5),(1.5,78,.5),(2,74,2)],[(0,76,4)]]
    for i,sc in enumerate(sect):
        if sc in('B','C'):
            ph=theme[(i-12)%8]
            for o,p,l in ph:
                p2=p+12 if sc=='C' and (i-20)>=4 else p
                mel.append((p2,T(i,o)+random.uniform(0,0.02),l*b*1.05,62+random.randint(-6,6)+(6 if sc=='C' else 0)))
    end=bars*4*b
    piano.append((50,end,6,34)); piano.append((57,end,6,30)); piano.append((66,end+0.05,6,30)); piano.append((76,end+0.1,6,28))
    PIA=render_midi(piano+mel,0,L,BPM,gain=0.6)
    STR=render_midi(strings,49,L,BPM,gain=0.5)
    PIA=lp(PIA,9000)
    # DSP layers
    shimmer=np.zeros((L,2)); bells=np.zeros((L,2)); drone=np.zeros((L,2))
    for i,sc in enumerate(sect):
        chs=P1 if (i//4)%2==0 or sc in('intro','A') else P2
        root,arp,tones=chs[i%4]
        for p in tones[:3]:
            place(shimmer,sine_pad(p+12,4*b,a=2.5,r=4),T(i,0),0.25,0.25+0.5*random.random())
        if i%2==0: place(drone,sine_pad(26,8*b,a=4,r=5),T(i,0),0.5,0.5)
        if sc in('intro','A','C','out'):
            for _ in range(2 if sc!='C' else 3):
                p=random.choice([74,76,78,81,83,86,88])
                place(bells,fm_bell(p,5,idx=2.5,ratio=3.5),T(i,random.choice([0.5,1.5,2.5,3,3.5])),0.12,random.random())
    ocean=st(wind(L,150,700))
    t=np.arange(L)/SR
    swell=(0.55+0.45*np.sin(2*np.pi*t/(8*b)-np.pi/2))[:,None]   # wave-like swell
    ocean=ocean*swell
    # levels
    PIA=to_db(PIA,-19); STR=to_db(STR,-29); shimmer=to_db(shimmer,-30); bells=to_db(bells,-30)
    drone=to_db(drone,-32); ocean=to_db(ocean,-36)
    dry=PIA+STR+shimmer+bells+drone+ocean
    wet=reverb(PIA*0.8+STR+shimmer+bells*1.2,decay=5.5,tone=6000,predelay=0.04)
    mix=dry+wet*0.45
    fadein=np.clip(t/6,0,1)[:,None]; fadeout=np.clip((L/SR-t)/8,0,1)[:,None]
    master(mix*fadein*fadeout,out_path,lufs=-16)
    return dict(lufs_target=LUFS, chords=None, melody=None, bars=bars)
