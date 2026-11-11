# "Rainy Window" — lo-fi hip hop, MIDI keys (FluidSynth) + DSP drums/bass/pad/vinyl
"""Exact reference track (fixed composition). Reproduces the approved sample bit-for-bit
modulo FluidSynth version. Use as the quality bar / A-B reference."""
import random
import engine as E
from engine import *  # noqa: F401,F403
LUFS = -14


def plan(seed=None):
    return dict(seed=5, fixed=True)


def render(p, out_path):
    E.seed(11)  # the original engine's module-level RNG seed
    random.seed(5)
    BPM=74; b=60/BPM; SW=0.07  # swing in beats
    # C major ii-V-I-vi with colour: Dm9 G13 Cmaj9 Am9 | Fmaj9 E7#9 Am9 Gm9-C9
    prog=[([50,53,57,60,64],38),([53,57,59,64],43),([52,55,59,62],36),([55,60,64,67],45),
          ([52,57,60,64,67],41),([52,56,59,62,67],40),([55,60,64,67],45),([53,57,58,62,65],43)]
    # sections in bars: intro4, A8, B8, break4, A'8, outro4 = 36 bars
    sect=['intro']*4+['A']*8+['B']*8+['brk']*4+['A2']*8+['out']*4
    bars=len(sect); L=int((bars*4*b+6)*SR)
    def T(bar,beat): sw=SW if (round(beat*2)%2==1) else 0; return (bar*4+beat+sw)*b
    keys=[];mel=[];
    for i,sc in enumerate(sect):
        ch,root=prog[i%8]
        # keys comp: rootless voicing, strum, push on "and of 4" into next bar sometimes
        hits=[(0,1.6,60),(2.5,1.2,50)] if sc!='brk' else [(0,3.8,52)]
        for pos,l,v in hits:
            for k,p in enumerate(ch[1:]):
                keys.append((p,T(i,pos)+k*0.018+random.uniform(0,0.01),l*b,v+random.randint(-6,6)))
        # melody (B & A2): pentatonic phrases, sparse, call & response
        if sc in('B','A2'):
            phr=[[(0,76,1),(1,74,.5),(1.5,72,1),(3,69,1)],
                 [(0.5,72,.5),(1,74,.5),(1.5,76,1.5),(3.5,79,.5)],
                 [(0,81,1.5),(1.5,79,.5),(2,76,1),(3,74,1)],
                 [(0,72,3)]][i%4]
            if sc=='A2' and i%4==1: phr=[(0,79,.5),(.5,76,.5),(1,74,1),(2,72,.5),(2.5,69,1.5)]
            for o,p,l in phr: mel.append((p,T(i,o),l*b*0.95,70+random.randint(-8,8)))
    end=bars*4*b
    keys+= [(p,end,4,48) for p in prog[0][0][1:]]
    K=render_midi(keys,4,L,BPM,gain=0.55)          # Rhodes-ish EP
    M=render_midi(mel,0,L,BPM,gain=0.45)           # piano melody
    # lo-fi treatment on keys/melody: band-limit, tape wow, saturation
    K=wow_flutter(saturate(lp(hp(K,120),4200),1.8),1.6,0.45)
    M=wow_flutter(saturate(lp(M,5000),1.4),1.2,0.5)
    drums=np.zeros((L,2)); bass=np.zeros((L,2)); pad=np.zeros((L,2)); kicks=[]
    for i,sc in enumerate(sect):
        ch,root=prog[i%8]
        if sc in('A','B','A2'):
            for pos in ([0,1.75,2.5] if i%2==0 else [0,2.5,3.25]):
                place(drums,lofi_kick(),T(i,pos),0.9); kicks.append(T(i,pos))
            for pos in (1,3): place(drums,lofi_snare(),T(i,pos)+0.012,0.55,0.52)
            for e in range(8):
                if random.random()<0.92: place(drums,lofi_hat(),T(i,e/2),0.35+0.15*(e%2==0),0.62)
            if i%4==3: place(drums,lofi_hat(True),T(i,3.5),0.35,0.62)
            # bass: root on 1, 5th/approach later
            for pos,iv,l in [(0,0,1.4),(2.5,7 if i%2 else 0,0.6),(3.5,12 if i%2 else -2,0.4)]:
                place(bass,sub_bass(root-12+iv+12,l*b),T(i,pos),0.9)
        if sc!='intro':
            for p in ch[1:4]: place(pad,pad_voice(p+12,4*b,bright=900,a=1.0,r=2.0),i*4*b,0.07,0.3+0.4*random.random())
        else:
            for p in ch[1:4]: place(pad,pad_voice(p+12,4*b,bright=500,a=1.5,r=2.0),i*4*b,0.05,0.5)
    drums=lp(drums,7500); drums=saturate(drums,2.0)
    # glue
    sc_gain=sidechain(L,kicks,0.35,0.3)
    K=to_db(K,-21); M=to_db(M,-23); drums=to_db(drums,-19.5); bass=to_db(bass,-21); pad=to_db(pad,-29)
    dry=K*sc_gain+M+drums+bass+pad*sc_gain
    wet=reverb(K*0.5+M*0.7+pad*0.8+drums*0.12,decay=2.2,tone=4000)
    mix=dry+wet*0.28+to_db(st(vinyl(L,5)),-42)+st(lp(rng.standard_normal(L),1500)*0.0)  
    # intro & outro: whole-mix lowpass sweep (the "telephone" lo-fi opening/closing)
    t=np.arange(L)/SR; intro_end=4*4*b; out_start=32*4*b
    filt=lp(mix,900,2); w=np.clip(t/intro_end,0,1)**2
    w=np.where(t>out_start,np.clip(1-(t-out_start)/(4*4*b),0,1),w)[:,None]
    mix=mix*w+filt*(1-w)
    fade=np.clip((L/SR-t)/5,0,1)[:,None]; mix*=fade
    master(mix,out_path,lufs=-14)
    return dict(lufs_target=LUFS, chords=None, melody=None, bars=bars)
