# WORLD3 2003 updated equations, in pydynamo syntax.
# Population sector
pop.k = p1.k + p2.k + p3.k + p4.k
p1.k = p1.j + dt*(b.j - d1.j - mat1.j)
p1.i = p1i
p1i = 65e7
d1.k = p1.k * m1.k
m1.k = tabhl(m1t, le.k, 20, 80, 10)
m1t = [0.0567, 0.0366, 0.0243, 0.0155, 0.0082, 0.0023, 0.001]
mat1.k = p1.k*(1 - m1.k)/15
p2.k = p2.j + dt*(mat1.j - d2.j - mat2.j)
p2.i = p2i
p2i = 70e7
d2.k = p2.k * m2.k
m2.k = tabhl(m2t, le.k, 20, 80, 10)
m2t = [0.0266, 0.0171, 0.0110, 0.0065, 0.0040, 0.0016, 0.0008]
mat2.k = p2.k*(1 - m2.k)/30
p3.k = p3.j + dt*(mat2.j-d3.j-mat3.j)
p3.i = p3i
p3i = 19e7
d3.k = p3.k * m3.k
m3.k = tabhl(m3t, le.k, 20, 80, 10)
m3t = [0.0562, 0.0373, 0.0252, 0.0171, 0.0118, 0.0083, 0.006]
mat3.k = p3.k*(1 - m3.k)/20
p4.k = p4.j + dt*(mat3.j - d4.j)
p4.i = p4i
p4i = 6e7
d4.k = p4.k * m4.k
m4.k = tabhl(m4t, le.k, 20, 80, 10)
m4t = [0.13, 0.11, 0.09, 0.07, 0.06, 0.05, 0.04]

# Death rate subsector
d.k = d1.j + d2.j + d3.j + d4.j
cdr.k = 1000*d.k/pop.k # death rate
le.k = len*lmf.k*lmhs.k*lmp.k*lmc.k
len = 28
lmf.k = tabhl(lmft, fpc.k/sfpc, 0, 5, 1)
lmft = [0, 1, 1.43, 1.5, 1.5, 1.5]
hsapc.k = tabhl(hsapct, sopc.k, 0, 2000, 250)
hsapct = [0, 20, 50, 95, 140, 175, 200, 220, 230]
ehspc.k = smooth(hsapc.j, hsid)
hsid = 20
lmhs.k = clip(lmhs1.k, lmhs2.k, 1940, time.k)
lmhs1.k = tabhl(lmhs1t, ehspc.k, 0, 100, 20)
lmhs1t = [1, 1.1, 1.4, 1.6, 1.7, 1.8]
lmhs2.k = tabhl(lmhs2t, ehspc.k, 0, 100, 20)
lmhs2t = [1, 1.5, 1.9, 2, 2, 2]
fpu.k = tabhl(fput, pop.k, 0, 16e9, 2e9)
fput = [0, 0.2, 0.4, 0.5, 0.58, 0.65, 0.72, 0.78, 0.80]
cmi.k = tabhl(cmit, iopc.k, 0, 1600, 200)
cmit = [0.5, 0.05, -0.1, -0.08, -0.02, 0.05, 0.1, 0.15, 0.2]
lmc.k = 1 - (cmi.k*fpu.k)
lmp.k = tabhl(lmpt, ppolx.k, 0, 100, 10)
lmpt = [1, 0.99, 0.97, 0.95, 0.90, 0.85, 0.75, 0.65, 0.55, 0.40, 0.20]

# Birth rate subsector
b.k = clip((tf.k*p2.k*0.5/rlt), d.k, pet, time.k)
cbr.k = 1000*b.k/pop.k # birth rate 
rlt = 30
pet = 4000
cbr.k = 1000*b.j/pop.k
tf.k = min(mtf.k, (mtf.k*(1-fce.k) + dtf.k*fce.k))
mtf.k = mtfn * fm.k
mtfn = 12
fm.k = tabhl(fmt, le.k, 0, 80, 10)
fmt = [0, 0.2, 0.4, 0.6, 0.7, 0.75, 0.79, 0.84, 0.87]
dtf.k = dcfs.k*cmple.k
cmple.k = tabhl(cmplet, ple.k, 0, 80, 10)
cmplet = [3, 2.1, 1.6, 1.4, 1.3, 1.2, 1.1, 1.05, 1]
ple.k = dlinf3(le.k, lpd)
lpd = 20
dcfs.k = clip(dcfsn*frsn.k*sfsn.k, 2.0, zpgt, time.k)
zpgt = 4000
dcfsn = 3.8
sfsn.k = tabhl(sfsnt, diopc.k, 0, 800, 200)
sfsnt =  [1.25, 0.94, 0.715, 0.59, 0.5] # Changed from Vensim. Before it was  [1.25, 1, 0.9, 0.8, 0.75]
diopc.k = dlinf3(iopc.k, sad) 
sad = 20
frsn.k = tabhl(frsnt, fie.k, -0.2, 0.2, 0.1)
frsnt = [0.5, 0.6, 0.7, 0.85, 1]
# frsn.i = 0.82 # Removed from Vensim 
fie.k = (iopc.k - aiopc.k)/aiopc.k
aiopc.k = smooth(iopc.j, ieat)
ieat = 3
nfc.k = (mtf.k / dtf.k) - 1
fce.k = clip(tabhl(fcet, fcfpc.k, 0, 3, 0.5), 1.0, fcest, time.k)
fcest = 4000
fcet = [0.75, 0.85, 0.9, 0.95, 0.98, 0.99, 1]
fcfpc.k = dlinf3(fcapc.k, hsid)
fcapc.k = fsafc.k*sopc.k
fsafc.k = tabhl(fsafct, nfc.k, 0, 10, 2)
fsafct = [0, 0.005, 0.015, 0.025, 0.03, 0.035]

# Capital sector
## Industrial subsector
iopc.k = io.k/pop.k
io.k = ic.k*(1-fcaor.k)*cuf.k/icor.k
icor.k = clip(icor1, icor2.k, pyear, time.k)
icor1 = 3
icor2.k = icormrrct.k*icormlyt.k*icormpt.k
icormrrct.k = tabhl(icormrrctt, nruf.j,0, 1, 0.1) # industrial capital output ratio multiplier from resource conservation technology
icormrrctt = [3.75, 3.6, 3.47, 3.36, 3.25, 3.16, 3.1, 3.06, 3.02, 3.01, 3] # industrial capital output ratio multiplier from resource table
icormlyt.k = tabhl(icormlytt, lymt.j, 1, 2, 0.2) # industrial capital output ratio multiplier from land yield technology
# Note: Weird stuff in Vensim file (1,0.8)-(2,2)],
icormlytt = [1, 1.05, 1.12, 1.25, 1.35, 1.5] # industrial capital output ratio multiplier table
icormpt.k = tabhl(icormptt, ppgf.j, 0, 1, 0.1) # industrial capital output ratio multiplier from pollution technology
icormptt = [1.25, 1.2, 1.15, 1.11, 1.08, 1.05, 1.03, 1.02, 1.01, 1, 1] # industrial capital output ratio multiplier from pollution table
ic.k = ic.j + dt*(icir.j-icdr.j)
ic.i = ici
ici = 2.1e11
icdr.k = ic.k/alic.k
alic.k = clip(alic1, alic2, pyear, time.k)
alic1 = 14
alic2 = 14
icir.k = io.k*fioai.k
fioai.k = 1- fioaa.k - fioas.k - fioac.k
fioac.k = clip(fioacc.k, fioacv.k, iet, time.k)
iet = 4000
fioacc.k = clip(fioac1, fioac2, pyear, time.k)
fioac1 = 0.43
fioac2 = 0.43
fioacv.k = tabhl(fioacvt, iopc.k/iopcd, 0, 2, 0.2)
fioacvt = [0.3, 0.32, 0.34, 0.36, 0.38, 0.43, 0.73, 0.77, 0.81, 0.82, 0.83]
iopcd = 400

## Service subsector
isopc.k = clip(isopc1.k, isopc2.k, pyear, time.k)
isopc1.k = tabhl(isopc1t, iopc.k, 0, 1600, 200)
isopc1t = [40, 300, 640, 1000, 1220, 1450, 1650, 1800, 2000]
isopc2.k = tabhl(isopc2t, iopc.k, 0, 1600, 200)
isopc2t = [40, 300, 640, 1000, 1220, 1450, 1650, 1800, 2000]
fioas.k = clip(fioas1.k, fioas2.k, pyear, time.k)
fioas1.k = tabhl(fioas1t, sopc.k/isopc.k, 0, 2, 0.5)
fioas1t = [0.3, 0.2, 0.1, 0.05, 0]
fioas2.k = tabhl(fioas2t, sopc.k/isopc.k, 0, 2, 0.5)
fioas2t = [0.3, 0.2, 0.1, 0.05, 0]
scir.k = io.k*fioas.k
sc.k = sc.j + dt*(scir.j-scdr.j)
sc.i = sci
sci = 1.44e11
scdr.k = sc.k/alsc.k
alsc.k = clip(alsc1, alsc2, pyear, time.k)
alsc1 = 20
alsc2 = 20
so.k = (sc.k*cuf.k)/scor.k
sopc.k = so.k/pop.k
scor.k = clip(scor1, scor2, pyear, time.k)
scor1 = 1
scor2 = 1

## Job subsector
j.k = pjis.k + pjas.k +pjss.k
pjis.k = ic.k*jpicu.k
jpicu.k = tabhl(jpicut, iopc.k, 50, 800, 150)*1e-3
jpicut = [0.37, 0.18, 0.12, 0.09, 0.07, 0.06]
pjss.k = sc.k*jpscu.k
jpscu.k = tabhl(jpscut, sopc.k, 50, 800, 150)*1e-3
jpscut = [1.1, 0.6, 0.35, 0.2, 0.15, 0.15]
pjas.k = jph.k*al.k
jph.k = tabhl(jpht, aiph.k, 2, 30, 4)
jpht = [2, 0.5, 0.4, 0.3, 0.27, 0.24, 0.2, 0.2]
lf.k = (p2.k + p3.k)*lfpf
lfpf = 0.75
luf.k = j.k/lf.k
lufdi.k = clip(1, luf.j, initial_time, time.k) # helper for luf
lufd.k = smooth(lufdi.k, lufdt) # Added from  Vensim
lufdt = 2
cuf.k = tabhl(cuft, lufd.k, 1, 11, 2)
cuf.i = 1
cuft = [1, 0.9, 0.7, 0.3, 0.1, 0.1]

# Agricultural sector
## Loop1: food from investment in land development
lfc.k = al.k/palt
palt = 3.2e9
al.k = al.j + dt*(ldr.j - ler.j - lrui.j)
al.i = ali
ali = 0.9e9
pal.k = pal.j + dt*(-ldr.j)
pal.i = pali
pali = 2.3e9
f.k = ly.k*al.k*lfh*(1-pl)
lfh = 0.7
pl = 0.1
fpc.k = f.k/pop.k
ifpc.k = clip(ifpc1.k, ifpc2.k, pyear, time.k)
ifpc1.k = tabhl(ifpc1t, iopc.k, 0, 1600, 200)
ifpc1t = [230, 480, 690, 850, 970, 1070, 1150, 1210, 1250]
ifpc2.k = tabhl(ifpc2t, iopc.k, 0, 1600, 200)
ifpc2t = [230, 480, 690, 850, 970, 1070, 1150, 1210, 1250]
tai.k = io.k*fioaa.k
fioaa.k = clip(fioaa1.k, fioaa2.k, pyear, time.k)
fioaa1.k = tabhl(fioaa1t, fpc.k/ifpc.k, 0, 2.5, 0.5)
fioaa1t = [0.4, 0.2, 0.1, 0.025, 0, 0]
fioaa2.k = tabhl(fioaa2t, fpc.k/ifpc.k, 0, 2.5, 0.5)
fioaa2t = [0.4, 0.2, 0.1, 0.025, 0, 0]
ldr.k = tai.k*fiald.k/dcph.k
dcph.k = tabhl(dcpht, pal.k/palt, 0, 1, 0.1)
dcpht = [1e5, 7400, 5200, 3500, 2400, 1500, 750, 300, 150, 75, 50]

## Loop2: food from investment in agricultural inputs
cai.k = tai.k * (1 - fiald.k)
ai.k = smooth(cai.j, alai.k)
ai.i = 5e9
alai.k = clip(alai1, alai2, pyear, time.k)
alai1 = 2
alai2 = 2
aiph.k = ai.k*(1 - falm.k)/al.k
lymc.k = tabhl(lymct, aiph.k, 0, 1000, 40)
lymct = [1, 3, 4.5, 5.0, 5.3, 5.6, 5.9, 6.1, 6.35, 6.6, 6.9, 7.2, 7.4, 7.6, 7.8, 8, 8.2, 8.4, 8.6, 8.8, 9, 9.2, 9.4, 9.6, 9.8, 10]
ly.k = lymt.k*lfert.k*lymc.k*lymap.k
lymt.k = clip(lyf1, lyf2.k, pyear, time.k) # land yield multiplier from technology
lyf1 = 1
lyf2.k = smooth(lyt.k, tdd)
lyt.k = lyt.j + dt*(lytcr.k) # land yield technology
lyt.i = 1
lytcr.k = clip(0, lyt.j*lytcrm.j, pyear, time.k)# land yield technology change rate
lytcrm.k = tabhl(lytcrmt, drf - fr.k, 0, 1, 1)# land yield technology change rate multiplier
lytcrmt = [0, 0] # land yield technology change rate multiplier table
drf = 2 # desired food ratio
lymap.k = clip(lymap1.k, lymap2.k, appyear, time.k)
appyear = 4000 # air pollution policy implementation time
lymap1.k = tabhl(lymap1t, io.k/io70, 0, 30, 10)
lymap1t = [1, 1, 0.7, 0.4]
lymap2.k = tabhl(lymap2t, io.k/io70, 0, 30, 10)
lymap2t = [1, 1, 0.98, 0.95] # Seen in wrld3+03.mdl
io70 = 7.9e11

## Loop 1 & 2: the investment allocation decision
fiald.k = tabhl(fialdt, mpld.k/mpai.k, 0, 2, 0.25)
fialdt = [0, 0.05, 0.15, 0.30, 0.50, 0.70, 0.85, 0.95, 1]
mpld.k = ly.k/(dcph.k*sd)
sd = 0.07
mpai.k = alai.k*ly.k*mlymc.k/lymc.k
mlymc.k = tabhl(mlymct, aiph.k, 0, 600, 40)
mlymct = [0.075, 0.03, 0.015, 0.011, 0.009, 0.008, 0.007, 0.006, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005]

## Loop 3: land erosion and urban-industrial use
all.k = alln*llmy.k
alln = 1000
llmy.k = clip(llmy1.k, 0.95**((time.k - llmytm)/oy)*llmy1.k + (1 - 0.95**((time.k - llmytm)/oy))*llmy2.k, llmytm, time.k) 
llmy1.k = tabhl(llmy1t, ly.k/ilf, 0, 9, 1)
llmy1t = [1.2, 1, 0.63, 0.36, 0.16, 0.055, 0.04, 0.025, 0.015, 0.01]
llmy2.k = tabhl(llmy2t, ly.k/ilf, 0, 9, 1)
llmy2t = [1.2, 1, 0.63, 0.36, 0.29, 0.26, 0.24, 0.22, 0.21, 0.2] # Note: added from Vensim
ler.k = al.k/all.k
uilpc.k = tabhl(uilpct, iopc.k, 0, 1600, 200)
uilpct = [0.005, 0.008, 0.015, 0.025, 0.04, 0.055, 0.07, 0.08, 0.09]
uilr.k = uilpc.k*pop.k
lrui.k = max(0, (uilr.k - uil.k)/uildt)
uildt = 10
uil.k = uil.j + dt*(lrui.j)
uil.i = uili
uili = 8.2e6

## Loop 4: land fertility degradation
lfert.k = lfert.j + dt*(lfr.j-lfd.j)
lfert.i = lferti
lferti = 600
lfdr.k = tabhl(lfdrt, ppolx.k, 0, 30, 10)
lfdrt = [0, 0.1, 0.3, 0.5]
lfd.k = lfert.k*lfdr.k

## Loop 5: land fertility regeneration
lfr.k = (ilf-lfert.k)/lfrt.k
ilf = 600
lfrt.k = tabhl(lfrtt, falm.k, 0, 0.10, 0.02)
lfrtt = [20.0, 13.0, 8.0, 4.0, 2.0, 2.0]

## Loop 6: Discontinuing land maintinance
falm.k = tabhl(falmt, pfr.k, 0, 4, 1)
falmt = [0.0, 0.04, 0.07, 0.09, 0.1]
fr.k = fpc.k/sfpc
sfpc = 230
pfr.k = smooth(fr.j, fspd)
pfr.i = 1
fspd = 2

# Nonrenewable resource sector
nr.k = nr.j + dt*(-nrur.j)
nr.i = nri
nri = 1e12
nrur.k = pop.k * pcrum.k * nruf.k
nruf.k = clip(nruf1, nruf2.k, pyear, time.k)
nruf1 = 1
nruf2.k = smooth(rct.k, tdd)
rct.k = rct.j - dt*(rctcr.k)# resource conservation technology
rct.i = 1
rctcr.k = clip(0, rct.j*rtcm.j, pyear, time.k) # resource technology change rate
rtcm.k = tabhl(rtcmt,1-nrur.j/drur, -1, 0, 1) # resource technology change rate multiplier
drur = 4.8e09 # desired resource use rate
rtcmt = [0, 0]# resource technology change mult table
pcrum.k = tabhl(pcrumt, iopc.k, 0, 1600, 200)
pcrumt = [0, 0.85, 2.6, 3.4, 3.8, 4.1, 4.4, 4.7, 5]
nrfr.k = nr.k/nri
fcaor.k = clip(fcaor1.k, fcaor2.k, fcaortm, time.k)
fcaor1.k = tabhl(fcaor1t, nrfr.k, 0, 1, 0.1)
fcaor1t = [1.0, 0.9, 0.7, 0.5, 0.2, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05]
fcaor2.k = tabhl(fcaor2t, nrfr.k, 0, 1, 0.1)
fcaor2t = [1.0, 0.2, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]


# Persistent pollution sector
ppgr.k = (ppgio.k + ppgao.k)*ppgf.k
ppgf.k = clip(ppgf1, ppgf2.k, pyear, time.k)
ppgf1 = 1
ppgf2.k = smooth(ppt.k, tdd)
tdd = 20 # technology development delay
ppt.k = ppt.j + dt*pptcr.k # persistent pollution technology
ppti = 1 # Initial persistent pollution technology
ppt.i = ppti
pptcr.k = clip(0, ppt.j*pptcm.j, pyear, time.k) # persistent pollution technology change rate
pptcm.k = tabhl(pptcmt, 1 - ppolx.k/dppolx, -1, 0, 1)# persistent pollution technology change multiplier
pptcmt = [0, 0] # persistent pollution technology change mult table
dppolx = 1.2 # desired persistent pollution index
# Note: industrial capital output ratio multiplier from persistent pollution technology is not implemented in Vensim while on the schemas
ppgio.k = pcrum.k * pop.k * frpm*imef*imti
frpm = 0.02
imef = 0.1
imti = 10
ppgao.k = aiph.k*al.k*fipm*amti
fipm = 0.001
amti = 1
ppapr.k = delay3(ppgr.j, pptd) # Delay3i ??
pptd = 20
ppol.k = ppol.j + dt*(ppapr.j-ppasr.j)
ppol.i = ppoli
ppoli = 2.5e7
ppolx.k = ppol.k/ppol70
ppol70 = 1.36e8
ppasr.k = ppol.k/(ahl.k*1.4)
ahlm.k = tabhl(ahlmt, ppolx.k, 1, 1001, 250)
ahlmt = [1.0, 11.0, 21.0, 31.0, 41.0]
ahl.k = ahl70*ahlm.k
ahl70 = 1.5

# World3 03 supplementary equations sector
cio.k = io.k*fioacc.k # consumed industrial output
ciopc.k = cio.k/pop.k # consumed industrial output per capita
fao.k = pof * f.k/(pof*f.k + so.k + io.k) # fraction of output in agriculture
fos.k = so.k/(pof*f.k + so.k + io.k) # fraction of output in services
foi.k = io.k/(pof*f.k + so.k + io.k) # fraction of output in industry
llmytm = 4000 # land life policy implementation time
pof = 0.22 # price of food
fcaortm = 4000# fraction of industrial capital allocated to obtaining resources switch time
plinid.k = ppgio.k*ppgf.k/io.k  # persistent pollution intensity industry
resint.k = nrur.k/io.k # resource use intensity
thousand = 1000 # THOUSAND

# World3 03 indicators sector
ugdp = 1 # GDP pc unit
uai = 1 # unit agricultural input
up = 1 # unit population
ablgha.k = ppgr.k*hpup/hpgha # "Absorption Land (GHA)"
ei.k = tabhl(eit, gdppc.k/ugdp, 0, 7000, 1000) # Education Index
eit = [0, 0.81, 0.88, 0.92, 0.95, 0.98, 0.99, 1] # Education Index LOOKUP
gdpi.k = log(gdppc.k/rlgdp, 10)/log(rhgdp/rlgdp, 10) # GDP index
gdppc.k = tabhl(gdppct, iopc.k/ugdp, 0, 1000, 200) # GDP per capita
gdppct = [120, 600, 1200, 1800, 2500, 3200] # GDP per capita LOOKUP
hpgha = 1e9 # ha per gha
hpup = 4 # ha per unit of pollution
hef.k = (algha.k + ulgha.k + ablgha.k)/tl # Human Ecological Footprint
hwi.k = (lei.k + ei.k + gdpi.k)/3 # Human Welfare Index
lei.k = tabhl(leit, le.k/oy, 25, 85, 10) # Life Expectancy Index
leit = [0, 0.16, 0.33, 0.5, 0.67, 0.84, 1]#  Life Expectancy Index LOOKUP
oy = 1 # one year
rhgdp = 9508 # Ref Hi GDP
rlgdp = 24 # Ref Lo GDP
tl = 1.91 # Total land
ulgha.k = uil.k/hpgha # "Urban Land (GHA)"
algha.k = al.k/hpgha # "Arable Land in Gigahectares (GHA)"

# Control card for simulation
pyear = 1975
initial_time = 1900

# Take care to keep the last line :)
