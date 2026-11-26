#!/usr/bin/env python3
"""News Image 20261125 — deterministic PNG renderer (stdlib only)."""
import os, struct, zlib

W = H = 1024
NAVY=(10,24,58); RED=(196,30,42); GOLD=(245,176,0); PAPER=(250,246,235); INK=(18,20,28)
BLUE=(22,92,180); TEAL=(0,150,150); GREEN=(24,140,70); ORANGE=(238,110,20); PURPLE=(112,60,180)
PINK=(215,60,110); SKY=(120,200,240); SAND=(240,205,120); GRAY=(95,100,110); WHITE=(255,255,255)

FONT={
'A':[".###.","#...#","#...#","#####","#...#","#...#","#...#"],'B':["####.","#...#","#...#","####.","#...#","#...#","####."],
'C':[".####","#....","#....","#....","#....","#....",".####"],'D':["####.","#...#","#...#","#...#","#...#","#...#","####."],
'E':["#####","#....","#....","####.","#....","#....","#####"],'F':["#####","#....","#....","####.","#....","#....","#...."],
'G':[".####","#....","#....","#.###","#...#","#...#",".###."],'H':["#...#","#...#","#...#","#####","#...#","#...#","#...#"],
'I':["#####","..#..","..#..","..#..","..#..","..#..","#####"],'J':["..###","...#.","...#.","...#.","...#.","#..#.",".##.."],
'K':["#...#","#..#.","#.#..","##...","#.#..","#..#.","#...#"],'L':["#....","#....","#....","#....","#....","#....","#####"],
'M':["#...#","##.##","#.#.#","#.#.#","#...#","#...#","#...#"],'N':["#...#","##..#","#.#.#","#..##","#...#","#...#","#...#"],
'O':[".###.","#...#","#...#","#...#","#...#","#...#",".###."],'P':["####.","#...#","#...#","####.","#....","#....","#...."],
'Q':[".###.","#...#","#...#","#...#","#.#.#","#..#.",".##.#"],'R':["####.","#...#","#...#","####.","#.#..","#..#.","#...#"],
'S':[".####","#....","#....",".###.","....#","....#","####."],'T':["#####","..#..","..#..","..#..","..#..","..#..","..#.."],
'U':["#...#","#...#","#...#","#...#","#...#","#...#",".###."],'V':["#...#","#...#","#...#","#...#","#...#",".#.#.","..#.."],
'W':["#...#","#...#","#...#","#.#.#","#.#.#","##.##","#...#"],'X':["#...#",".#.#.","..#..","..#..","..#..",".#.#.","#...#"],
'Y':["#...#","#...#",".#.#.","..#..","..#..","..#..","..#.."],'Z':["#####","....#","...#.","..#..",".#...","#....","#####"],
'0':[".###.","#..##","#.#.#","##..#","#...#","#...#",".###."],'1':["..#..",".##..","..#..","..#..","..#..","..#..","#####"],
'2':[".###.","#...#","....#","...#.","..#..",".#...","#####"],'3':["#####","...#.","..#..","...#.","....#","#...#",".###."],
'4':["...#.","..##.",".#.#.","#..#.","#####","...#.","...#."],'5':["#####","#....","####.","....#","....#","#...#",".###."],
'6':[".###.","#....","#....","####.","#...#","#...#",".###."],'7':["#####","....#","...#.","..#..","..#..","..#..","..#.."],
'8':[".###.","#...#","#...#",".###.","#...#","#...#",".###."],'9':[".###.","#...#","#...#",".####","....#","....#",".###."],
' ':["....."]*7,'.':[".....",".....",".....",".....",".....",".##..",".##.."],',':[".....",".....",".....",".....",".##..",".##..",".#..."],
':':[".....",".##..",".##..",".....",".##..",".##..","....."],';':[".....",".##..",".##..",".....",".##..",".##..",".#..."],
"'":["..#..","..#..",".#...",".....",".....",".....","....."],'"':[".#.#.",".#.#.",".....",".....",".....",".....","....."],
'-':[".....",".....",".....","#####",".....",".....","....."],'/':["....#","...#.","...#.","..#..",".#...",".#...","#...."],
'%':["##..#","##.#.","...#.","..#..",".#...",".#.##","#..##"],'$':["..#..",".####","#.#..",".###.","..#.#","####.","..#.."],
'+':[".....","..#..","..#..","#####","..#..","..#..","....."],'(':["...#.","..#..",".#...",".#...",".#...","..#..","...#."],
')':[".#...","..#..","...#.","...#.","...#.","..#..",".#..."],'!':["..#..","..#..","..#..","..#..","..#..",".....","..#.."],
'?':[".###.","#...#","....#","...#.","..#..",".....","..#.."],'&':[".##..","#..#.","#.#..",".#...","#.#.#","#..#.",".##.#"]}

class Canvas:
    def __init__(self): self.px=bytearray(W*H*3)
    def set(self,x,y,c):
        if 0<=x<W and 0<=y<H:
            i=(y*W+x)*3; self.px[i:i+3]=bytes(c)
    def rect(self,x,y,w,h,c):
        for yy in range(y,y+h):
            for xx in range(x,x+w): self.set(xx,yy,c)
    def circle(self,cx,cy,r,c):
        for yy in range(cy-r,cy+r+1):
            for xx in range(cx-r,cx+r+1):
                if (xx-cx)**2+(yy-cy)**2<=r*r: self.set(xx,yy,c)
    def ring(self,cx,cy,r,c,t=3):
        for yy in range(cy-r,cy+r+1):
            for xx in range(cx-r,cx+r+1):
                d=(xx-cx)**2+(yy-cy)**2
                if (r-t)**2<=d<=r*r: self.set(xx,yy,c)
    def line(self,x1,y1,x2,y2,c,t=3):
        steps=max(abs(x2-x1),abs(y2-y1),1)
        for i in range(steps+1):
            x=x1+(x2-x1)*i//steps; y=y1+(y2-y1)*i//steps
            self.rect(x-t//2,y-t//2,t,t,c)
    def poly(self,pts,c):
        ys=[p[1] for p in pts]
        for y in range(min(ys),max(ys)+1):
            xs=[]
            for i in range(len(pts)):
                x1,y1=pts[i]; x2,y2=pts[(i+1)%len(pts)]
                if (y1<=y<y2) or (y2<=y<y1): xs.append(x1+(y-y1)*(x2-x1)//(y2-y1))
            xs.sort()
            for i in range(0,len(xs)-1,2): self.rect(xs[i],y,xs[i+1]-xs[i]+1,1,c)
    def text(self,x,y,s,scale,c):
        cx=x
        for ch in s.upper():
            g=FONT.get(ch,FONT[' '])
            for ry,row in enumerate(g):
                for rx,v in enumerate(row):
                    if v=='#': self.rect(cx+rx*scale,y+ry*scale,scale,scale,c)
            cx+=6*scale
        return cx-x
    def tw(self,s,scale): return len(s)*6*scale-scale
    def ctext(self,cx,y,s,scale,c): self.text(cx-self.tw(s,scale)//2,y,s,scale,c)
    def png(self):
        raw=bytearray()
        for y in range(H): raw.append(0); raw+=self.px[y*W*3:(y+1)*W*3]
        def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
        ihdr=struct.pack('>IIBBBBB',W,H,8,2,0,0,0)
        return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',ihdr)+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b'')

def badge(cv,x,y,num,c=RED):
    cv.circle(x+16,y+16,16,c); s=str(num); cv.text(x+16-cv.tw(s,2)//2,y+9,s,2,WHITE)
def pill(cv,x,y,s,c):
    w=cv.tw(s,1)+12; cv.rect(x,y,w,16,c); cv.text(x+6,y+4,s,1,WHITE); return w
def pictogram(cv,sid,x,y,w,h):
    bg={1:NAVY,2:GOLD,3:TEAL,4:GREEN,5:SKY,6:ORANGE,7:RED,8:PURPLE,9:NAVY,10:BLUE,11:PINK,12:ORANGE,13:GREEN}[sid]
    cv.rect(x,y,w,h,bg); cx=x+w//2; cy=y+h//2; u=max(2,min(w,h)//18)
    if sid==1:
        cv.poly([(cx-8*u,cy-9*u),(cx+8*u,cy-9*u),(cx+8*u,cy+2*u),(cx,cy+10*u),(cx-8*u,cy+2*u)],SKY)
        cv.line(cx-5*u,cy-5*u,cx+4*u,cy+4*u,RED,3*u); cv.line(cx+5*u,cy-6*u,cx-3*u,cy+5*u,RED,3*u)
    elif sid==2:
        cv.rect(cx-2*u,cy-9*u,4*u,12*u,NAVY); cv.line(cx-9*u,cy-6*u,cx+9*u,cy-6*u,NAVY,3*u)
        cv.poly([(cx-10*u,cy+4*u),(cx-4*u,cy+4*u),(cx-7*u,cy-3*u)],RED); cv.poly([(cx+4*u,cy+4*u),(cx+10*u,cy+4*u),(cx+7*u,cy-3*u)],RED)
        cv.rect(cx-9*u,cy+7*u,18*u,3*u,NAVY)
    elif sid==3:
        cv.poly([(cx-10*u,cy+3*u),(cx+10*u,cy+3*u),(cx+6*u,cy+8*u),(cx-6*u,cy+8*u)],WHITE)
        cv.rect(cx-1*u,cy-8*u,2*u,11*u,WHITE); cv.poly([(cx+1*u,cy-8*u),(cx+1*u,cy+2*u),(cx+8*u,cy+2*u)],GOLD)
        for i in range(3): cv.line(x+6+i*4*u,cy+11*u,x+16+i*4*u,cy+9*u,WHITE,2*u)
    elif sid==4:
        cv.circle(cx,cy,7*u,WHITE); cv.circle(cx,cy,3*u,RED)
        for dx,dy in [(-9,-6),(9,-6),(-10,5),(10,5),(0,-11),(0,11)]: cv.circle(cx+dx*u,cy+dy*u,2*u,WHITE)
    elif sid==5:
        cv.rect(cx-8*u,cy-3*u,13*u,6*u,WHITE); cv.poly([(cx+5*u,cy-2*u),(cx+12*u,cy-5*u),(cx+12*u,cy+1*u),(cx+5*u,cy+2*u)],WHITE)
        cv.line(cx-11*u,cy-8*u,cx+11*u,cy-8*u,NAVY,2*u); cv.line(cx-4*u,cy+5*u,cx+6*u,cy+5*u,NAVY,2*u)
    elif sid==6:
        cv.rect(cx-9*u,cy-8*u,18*u,16*u,WHITE); cv.rect(cx-3*u,cy-2*u,6*u,10*u,TEAL); cv.rect(cx-9*u,cy-11*u,18*u,3*u,RED)
    elif sid==7:
        cv.rect(cx-8*u,cy-2*u,16*u,9*u,WHITE); cv.rect(cx-5*u,cy-8*u,4*u,6*u,WHITE); cv.rect(cx+2*u,cy-10*u,4*u,8*u,WHITE)
        cv.poly([(cx,cy-13*u),(cx+5*u,cy-4*u),(cx-5*u,cy-4*u)],GOLD)
    elif sid==8:
        cv.rect(cx-7*u,cy-10*u,14*u,20*u,WHITE)
        for i in range(4): cv.rect(cx-4*u,cy-6*u+i*4*u,8*u,2*u,PURPLE)
        cv.rect(cx-4*u,cy+6*u,8*u,3*u,RED)
    elif sid==9:
        cv.circle(cx-5*u,cy-3*u,4*u,GOLD); cv.circle(cx+5*u,cy-4*u,3*u,SKY); cv.circle(cx,cy+5*u,3*u,PINK)
        cv.ring(cx,cy,10*u,WHITE,2*u)
    elif sid==10:
        for i in range(3): cv.rect(cx-8*u,cy-8*u+i*6*u,16*u,4*u,WHITE); cv.circle(cx+5*u,cy-6*u+i*6*u,1*u,GREEN)
    elif sid==11:
        cv.line(cx-9*u,cy-6*u,cx-3*u,cy+1*u,WHITE,3*u); cv.line(cx-3*u,cy+1*u,cx+2*u,cy-3*u,WHITE,3*u); cv.line(cx+2*u,cy-3*u,cx+9*u,cy+7*u,WHITE,3*u)
        cv.poly([(cx+9*u,cy+8*u),(cx+4*u,cy+7*u),(cx+8*u,cy+3*u)],WHITE)
    elif sid==12:
        cv.circle(cx-5*u,cy,5*u,WHITE); cv.circle(cx+5*u,cy,5*u,TEAL); cv.rect(cx-2*u,cy-2*u,4*u,4*u,GOLD)
    else:
        cv.circle(cx,cy,9*u,WHITE); cv.poly([(cx,cy-4*u),(cx+4*u,cy),(cx,cy+4*u),(cx-4*u,cy)],INK)
        for dx,dy in [(-7,-6),(7,-6),(-7,6),(7,6)]: cv.circle(cx+dx*u,cy+dy*u,2*u,INK)

LEADS=[
(1,["CIA SYSTEM","BREACHED"],"ODNI ALSO HIT","NO SECRETS TAKEN","CIA","US INTEL","AP","CONFIRMED"),
(2,["HUAWEI GUILTY","10 OF 12 COUNTS"],"BROOKLYN COURT","CRIMINAL CASE","10/12","US COURTS","REUTERS","CONFIRMED"),
(3,["175 MIGRANTS","MISSING"],"BOAT LOST FROM DAKAR","CONTACT LOST","175","SENEGAL","REUTERS","CONFIRMED")]
MEDIUMS=[
(4,["CONGO REBELS HALT","EBOLA TEAM OUT"],"DR CONGO","BBC/WHO","CONFIRMED"),
(5,["TURKISH COPTER DOWN","5 SOLDIERS DEAD"],"TURKEY","REUTERS","CONFIRMED"),
(6,["CARTAGENA SIEGE ENDS","HOSTAGES FREE"],"COLOMBIA","AP","CONFIRMED"),
(7,["PUTIN VOWS REVENGE","REFINERY STRIKES"],"RUSSIA","WIRE","REPORTED"),
(8,["LEAKED RUSSIAN FILE","720,000 WAR DEAD"],"RUSSIA","LEAK","REPORTED"),
(9,["IMPOSSIBLE TRIPLE STAR","28 LIGHT YEARS"],"SPACE","IAC","CONFIRMED"),
(10,["DELL AI SALES DOUBLE","$25B BUYBACK"],"MARKETS","BARRON'S","CONFIRMED"),
(11,["NASDAQ -1.48%","NVIDIA +31.5% ERASED"],"MARKETS","REUTERS","CONFIRMED"),
(12,["BJP-AKALI REUNITE","PUNJAB ELECTION"],"INDIA","TIMES OF INDIA","CONFIRMED"),
(13,["REAL MADRID 5-1 PSV","FULL TIME"],"FOOTBALL","SCORE","CONFIRMED")]
ALSO=["ENGLAND WIN BY 8 WICKETS","TRUMP TEAM SPLIT ON IRAN","RIYADH TOWER HIT, 11 HURT","O'HARE TRAVEL CHAOS","MODI-MERZ: INDIA-GERMANY","MEDICINE SHORTAGES IN IRAN","NATO EARLY-WARNING JETS","VENEZUELA DEBT $237.5B"]
DATECHECK=["SOORYAVANSHI 204: 24 NOV","NEPAL QUAKE 5.3: 24 NOV","LANDMINE REPORT: 24 NOV","ALL EXCLUDED"]
PINS={1:(140,84),2:(160,100),3:(120,150),4:(152,182),5:(202,108),6:(74,154),7:(230,66),8:(244,86),9:(266,36),10:(126,116),11:(146,128),12:(226,146),13:(180,92)}

def draw():
    cv=Canvas(); cv.rect(0,0,W,H,PAPER)
    cv.rect(0,0,W,132,NAVY); cv.rect(0,132,W,30,RED)
    cv.text(24,14,"WEDNESDAY",3,GOLD); cv.text(24,44,"25 NOVEMBER 2026",7,WHITE)
    cv.text(760,22,"WORLD",4,WHITE); cv.text(760,58,"BRIEF",4,GOLD); cv.text(760,96,"ONE DAY",2,SKY)
    cv.text(24,140,"35 STORIES",3,WHITE); cv.rect(250,148,10,10,GOLD); cv.text(276,140,"15 MAP PINS",3,WHITE)
    cv.text(760,140,"13 NUMBERED",3,WHITE)
    for i,(sid,lines,sub,sub2,key,region,src,cert) in enumerate(LEADS):
        x=16+i*336; y=172; cv.rect(x,y,320,258,WHITE); cv.rect(x,y,320,6,RED)
        pictogram(cv,sid,x+10,y+12,190,104); badge(cv,x+8,y+8,sid)
        cv.text(x+(200 if len(key)>3 else 208),y+18,key,4 if len(key)>3 else 5,RED); cv.text(x+208,y+66,region,2,NAVY)
        yy=y+128
        for ln in lines: cv.text(x+12,yy,ln,3,INK); yy+=30
        cv.text(x+12,yy,sub,2,BLUE); cv.text(x+12,yy+24,sub2,2,GRAY)
        pill(cv,x+12,y+226,cert,GREEN if cert=="CONFIRMED" else ORANGE); cv.text(x+150,y+230,src,2,INK)
    for i,(sid,lines,region,src,cert) in enumerate(MEDIUMS):
        col=i//5; row=i%5; x=16+col*332; y=442+row*64
        cv.rect(x,y,324,58,WHITE); cv.rect(x,y,5,58,BLUE if cert=="CONFIRMED" else ORANGE)
        pictogram(cv,sid,x+8,y+4,50,50); badge(cv,x+4,y+2,sid,NAVY)
        cv.text(x+64,y+6,lines[0],2,INK); cv.text(x+64,y+26,lines[1],2,INK)
        cv.text(x+64,y+46,region+"  "+src,1,GRAY); pill(cv,x+246,y+40,cert,GREEN if cert=="CONFIRMED" else ORANGE)
    mx,my=688,442; cv.rect(mx,my,320,314,NAVY); cv.text(mx+14,my+10,"WORLD MAP",3,GOLD)
    cv.poly([(mx+28,my+96),(mx+96,my+70),(mx+132,my+96),(mx+104,my+142),(mx+52,my+150)],SKY)
    cv.poly([(mx+72,my+160),(mx+112,my+160),(mx+104,my+224),(mx+78,my+232)],SAND)
    cv.poly([(mx+142,my+86),(mx+238,my+62),(mx+292,my+92),(mx+252,my+150),(mx+176,my+146)],SKY)
    cv.poly([(mx+150,my+150),(mx+196,my+150),(mx+190,my+226),(mx+158,my+220)],SAND)
    cv.poly([(mx+238,my+170),(mx+282,my+176),(mx+276,my+214),(mx+244,my+208)],SKY)
    for sid,(px,py) in PINS.items():
        cv.circle(mx+px,my+py,11,RED); s=str(sid); cv.text(mx+px-cv.tw(s,1)//2,my+py-3,s,1,WHITE)
    cv.text(mx+14,my+282,"PINS MATCH STORY NUMBERS",2,WHITE)
    cv.rect(16,776,648,150,WHITE); cv.rect(16,776,648,30,NAVY); cv.text(28,784,"ALSO ON WEDNESDAY",3,GOLD)
    for i,s in enumerate(ALSO):
        col=i//4; row=i%4; cv.text(28+col*324,820+row*26,s,2,INK)
    cv.rect(680,776,328,150,(255,244,200)); cv.rect(680,776,328,30,RED); cv.text(692,784,"DATE CHECK",3,WHITE)
    for i,s in enumerate(DATECHECK): cv.text(692,820+i*30,s,2,INK)
    cv.rect(0,942,W,82,NAVY); cv.text(24,956,"SOURCES: AP  REUTERS  BBC/WHO  IAC",3,WHITE)
    cv.text(24,988,"BARRON'S  TIMES OF INDIA",3,GOLD); cv.text(700,970,"25 NOV 2026",4,WHITE)
    return cv.png()

def main():
    out=os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out,exist_ok=True)
    png_bytes=draw()
    with open(os.path.join(out,"entry.png"),"wb") as f: f.write(png_bytes)

if __name__=="__main__": main()
