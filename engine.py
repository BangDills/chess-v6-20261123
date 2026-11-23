import json, os, sys, urllib.request
sys.setrecursionlimit(10000)
U = os.environ.get("MAKEFUN_ENV_URL")
V = (0, 100, 320, 330, 500, 900, 0)
KN = (14, 18, 31, 33, -14, -18, -31, -33)
KI = (1, -1, 16, -16, 15, 17, -15, -17)
BI = (15, 17, -15, -17)
RO = (1, -1, 16, -16)
START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
BUD = 60000
MATE = 100000
T = [[0] * 128 for _ in range(7)]
KE = [0] * 128
for _r in range(8):
    for _f in range(8):
        _s = _r * 16 + _f
        _d = _r if _r < 4 else 7 - _r
        _c = (_f if _f < 4 else 7 - _f) + _d
        T[1][_s] = (0, 0, 6, 12, 20, 32, 50, 0)[_r] + (4 if _f in (3, 4) and 1 < _r < 6 else 0)
        T[2][_s] = 6 * _c - 18 + (12 if _r > 1 and _r < 6 and _f > 0 and _f < 7 else 0)
        T[3][_s] = 4 * _c - 8 + (12 if _r > 0 and _r < 7 and _f > 0 and _f < 7 else 0)
        T[4][_s] = 18 if _r == 6 else (4 if _r == 1 else 0)
        T[5][_s] = 3 * _c - 8
        T[6][_s] = (22, 26, 12, 0, 0, 12, 26, 22)[_f] - 16 * _r if _r < 2 else -12 * _r - 8
        KE[_s] = 10 * _c - 28
B = [0] * 128
S = [1, 15, -1, 0]
KP = [4, 116]
N = [0]
H = []
TT = {}
KL = [[0, 0] for _ in range(64)]
class TO(Exception):
    pass

def setup(f):
    global B
    B = [0] * 128
    pl, sd, ca, ep, ha, fu = f.split()
    r, fl = 7, 0
    for ch in pl:
        if ch == "/":
            r -= 1
            fl = 0
        elif ch.isdigit():
            fl += int(ch)
        else:
            t = "pnbrqk".index(ch.lower()) + 1
            q = r * 16 + fl
            B[q] = t if ch.isupper() else t + 8
            if t == 6:
                KP[0 if ch.isupper() else 1] = q
            fl += 1
    S[0] = 1 if sd == "w" else 0
    S[1] = (1 if "K" in ca else 0) | (2 if "Q" in ca else 0) | (4 if "k" in ca else 0) | (8 if "q" in ca else 0)
    S[2] = -1 if ep == "-" else "abcdefgh".index(ep[0]) + (int(ep[1]) - 1) * 16
    S[3] = int(ha)

def nm(s):
    return "abcdefgh"[s & 7] + str((s >> 4) + 1)

def uci(m):
    return nm(m[0]) + nm(m[1]) + ("", "", "n", "b", "r", "q")[m[2]]

def key():
    return (bytes(B), S[0], S[1], S[2])

def atk(s, w):
    if w:
        a = s - 15
        if not a & 136 and B[a] == 1:
            return 1
        a = s - 17
        if not a & 136 and B[a] == 1:
            return 1
    else:
        a = s + 15
        if not a & 136 and B[a] == 9:
            return 1
        a = s + 17
        if not a & 136 and B[a] == 9:
            return 1
    q = 2 if w else 10
    for d in KN:
        a = s + d
        if not a & 136 and B[a] == q:
            return 1
    q = 6 if w else 14
    for d in KI:
        a = s + d
        if not a & 136 and B[a] == q:
            return 1
    for d in BI:
        a = s + d
        while not a & 136:
            c = B[a]
            if c:
                if (c < 8) == w and (c & 7 == 3 or c & 7 == 5):
                    return 1
                break
            a += d
    for d in RO:
        a = s + d
        while not a & 136:
            c = B[a]
            if c:
                if (c < 8) == w and (c & 7 == 4 or c & 7 == 5):
                    return 1
                break
            a += d
    return 0

def gen(cp=0):
    ms = []
    w = S[0] == 1
    ep = S[2]
    for fr in range(128):
        if fr & 136:
            continue
        p = B[fr]
        if p == 0 or (p < 8) != w:
            continue
        t = p & 7
        if t == 1:
            if w:
                dr, sr, lr = 16, 1, 6
            else:
                dr, sr, lr = -16, 6, 1
            r = fr >> 4
            if (cp == 0 or r == lr) and B[fr + dr] == 0:
                if r == lr:
                    for pr in (5, 4, 3, 2):
                        ms.append((fr, fr + dr, pr))
                else:
                    ms.append((fr, fr + dr, 0))
                    if r == sr and B[fr + 2 * dr] == 0:
                        ms.append((fr, fr + 2 * dr, 0))
            for to in (fr + dr - 1, fr + dr + 1):
                if to & 136:
                    continue
                c = B[to]
                if c != 0 and (c < 8) != w and c & 7 != 6:
                    if r == lr:
                        for pr in (5, 4, 3, 2):
                            ms.append((fr, to, pr))
                    else:
                        ms.append((fr, to, 0))
                elif to == ep and c == 0:
                    ms.append((fr, to, 0))
        elif t == 2 or t == 6:
            for d in KN if t == 2 else KI:
                to = fr + d
                if to & 136:
                    continue
                c = B[to]
                if c == 0:
                    if cp == 0:
                        ms.append((fr, to, 0))
                elif (c < 8) != w and c & 7 != 6:
                    ms.append((fr, to, 0))
        else:
            for d in BI if t == 3 else RO if t == 4 else KI:
                to = fr + d
                while not to & 136:
                    c = B[to]
                    if c == 0:
                        if cp == 0:
                            ms.append((fr, to, 0))
                    else:
                        if (c < 8) != w and c & 7 != 6:
                            ms.append((fr, to, 0))
                        break
                    to += d
    if cp == 0:
        if w:
            if S[1] & 1 and B[5] == 0 and B[6] == 0 and B[4] == 6 and B[7] == 4 and not atk(4, 0) and not atk(5, 0) and not atk(6, 0):
                ms.append((4, 6, 0))
            if S[1] & 2 and B[3] == 0 and B[2] == 0 and B[1] == 0 and B[4] == 6 and B[0] == 4 and not atk(4, 0) and not atk(3, 0) and not atk(2, 0):
                ms.append((4, 2, 0))
        else:
            if S[1] & 4 and B[117] == 0 and B[118] == 0 and B[116] == 14 and B[119] == 12 and not atk(116, 1) and not atk(117, 1) and not atk(118, 1):
                ms.append((116, 118, 0))
            if S[1] & 8 and B[115] == 0 and B[114] == 0 and B[113] == 0 and B[116] == 14 and B[112] == 12 and not atk(116, 1) and not atk(115, 1) and not atk(114, 1):
                ms.append((116, 114, 0))
    return ms

def make(m):
    fr, to, pr = m
    pc = B[fr]
    cap = B[to]
    w = pc < 8
    u = [cap, S[1], S[2], S[3], 0, 0]
    S[3] += 1
    B[fr] = 0
    B[to] = pc
    if pc & 7 == 1:
        S[3] = 0
        if to == S[2]:
            cs = to - 16 if w else to + 16
            u[4] = cs
            u[5] = B[cs]
            B[cs] = 0
        elif to - fr == 32 or fr - to == 32:
            S[2] = fr + 16 if w else fr - 16
        else:
            S[2] = -1
        if pr:
            B[to] = pr if w else pr + 8
    else:
        S[2] = -1
        if cap:
            S[3] = 0
        t = pc & 7
        if t == 6:
            KP[0 if w else 1] = to
            S[1] &= ~(3 if w else 12)
            if to - fr == 2:
                B[fr + 1] = B[fr + 3]
                B[fr + 3] = 0
            elif fr - to == 2:
                B[fr - 1] = B[fr - 4]
                B[fr - 4] = 0
        elif t == 4:
            if fr == (7 if w else 119):
                S[1] &= ~(1 if w else 4)
            elif fr == (0 if w else 112):
                S[1] &= ~(2 if w else 8)
        if cap and cap & 7 == 4:
            if to == 7:
                S[1] &= ~1
            elif to == 0:
                S[1] &= ~2
            elif to == 119:
                S[1] &= ~4
            elif to == 112:
                S[1] &= ~8
    S[0] = 1 - S[0]
    return u

def unmake(m, u):
    fr, to, pr = m
    cap, c, e, h, es, ec = u
    S[0] = 1 - S[0]
    S[1] = c
    S[2] = e
    S[3] = h
    w = S[0] == 1
    pc = B[to]
    B[fr] = pc
    if pr:
        B[fr] = 1 if w else 9
    B[to] = cap
    if es:
        B[es] = ec
    if pc & 7 == 6:
        KP[0 if w else 1] = fr
        if to - fr == 2:
            B[fr + 3] = B[fr + 1]
            B[fr + 1] = 0
        elif fr - to == 2:
            B[fr - 4] = B[fr - 1]
            B[fr - 1] = 0

def legal(cp=0):
    r = []
    w = S[0] == 1
    for m in gen(cp):
        u = make(m)
        if not atk(KP[0 if w else 1], S[0] == 1):
            r.append(m)
        unmake(m, u)
    return r

def E():
    s = ph = wk = bk = bb = mn = bc = np = 0
    for q in range(128):
        if q & 136:
            continue
        p = B[q]
        if p == 0:
            continue
        t = p & 7
        w = p < 8
        if t == 6:
            if w:
                wk = q
            else:
                bk = q
            continue
        v = V[t] + T[t][q if w else q ^ 112]
        if w:
            s += v
        else:
            s -= v
        if t == 1 or t > 3:
            np = 1
        else:
            ph += V[t]
            mn += 1
            if t == 3:
                bb += 1 if w else -1
                bc |= 1 << (((q >> 4) + (q & 7)) & 1)
    if np == 0:
        if mn < 2:
            return 0
        if (bb == mn or bb == -mn) and bc != 3:
            return 0
    if ph > 6400:
        ph = 6400
    s += (T[6][wk] - T[6][bk ^ 112]) * ph // 6400 + (KE[wk] - KE[bk ^ 112]) * (6400 - ph) // 6400
    if bb > 1:
        s += 30
    elif bb < -1:
        s -= 30
    return s if S[0] == 1 else -s

def order(ms, pl, tm):
    if pl < 64:
        k0, k1 = KL[pl]
    else:
        k0 = k1 = 0
    def sc(m):
        fr, to, pr = m
        if m == tm:
            return 10000000
        c = B[to]
        x = 0
        if c:
            x = 10000 + 10 * V[c & 7] - V[B[fr] & 7]
        if pr:
            x += 9000 + 10 * V[pr]
        elif m == k0 or m == k1:
            x = 5000
        return x
    return sorted(ms, key=sc, reverse=True)

def C(m, F, d, a, b, pl):
    u = make(m)
    H.append(key())
    try:
        t = F(d, -b, -a, pl + 1)
    except TO:
        H.pop()
        unmake(m, u)
        raise
    H.pop()
    unmake(m, u)
    return -t

def Q(d, a, b, pl):
    N[0] += 1
    if N[0] > BUD:
        raise TO
    w = S[0] == 1
    if atk(KP[0 if w else 1], not w):
        ms = legal(0)
        if not ms:
            return -MATE + pl
        bs = -MATE - 1
        for m in order(ms, pl, 0):
            s = C(m, Q, 0, a, b, pl)
            if s > bs:
                bs = s
            if s > a:
                a = s
            if a >= b:
                break
        return bs
    if pl > 60:
        return E()
    st = E()
    if st >= b:
        return st
    if st > a:
        a = st
    for m in order(legal(1), pl, 0):
        s = C(m, Q, 0, a, b, pl)
        if s >= b:
            return s
        if s > a:
            a = s
    return a

def A(d, a, b, pl):
    N[0] += 1
    if N[0] > BUD:
        raise TO
    if S[3] >= 100:
        return 0
    k = key()
    if len(H) > 6 and H[max(0, len(H) - S[3] - 1):].count(k) > 2:
        return 0
    w = S[0] == 1
    ksq = KP[0 if w else 1]
    ic = atk(ksq, not w)
    if d <= 0:
        return Q(0, a, b, pl)
    if not ic and d > 2:
        e0 = S[2]
        S[0] = 1 - S[0]
        S[2] = -1
        S[3] += 1
        H.append(key())
        try:
            v = -A(d - 3, -b, 1 - b, pl + 1)
        except TO:
            S[0] = 1 - S[0]
            S[2] = e0
            S[3] -= 1
            H.pop()
            raise
        S[0] = 1 - S[0]
        S[2] = e0
        S[3] -= 1
        H.pop()
        if v >= b:
            return v
    tm = 0
    e = TT.get(k)
    if e and e[0] >= d:
        es = e[1]
        if es > 90000:
            es -= pl
        elif es < -90000:
            es += pl
        if e[2] == 0:
            return es
        if e[2] == 1 and es >= b:
            return es
        if e[2] == 2 and es <= a:
            return es
        tm = e[3]
    ms = legal(0)
    if not ms:
        return -MATE + pl if ic else 0
    bs = -MATE - 1
    bm = ms[0]
    a0 = a
    for j, m in enumerate(order(ms, pl, tm)):
        r = d - 1
        if j > 3 and d > 2 and not ic and B[m[1]] == 0 and m[2] == 0:
            r = d - 2
        s = C(m, A, r, a, b, pl)
        if r < d - 1 and s > a:
            s = C(m, A, d - 1, a, b, pl)
        if s > bs:
            bs = s
            bm = m
        if s > a:
            a = s
        if a >= b:
            if B[m[1]] == 0 and m[2] == 0 and pl < 64:
                if KL[pl][0] != m:
                    KL[pl][1] = KL[pl][0]
                    KL[pl][0] = m
            break
    sc = bs
    if sc > 90000:
        sc += pl
    elif sc < -90000:
        sc -= pl
    TT[k] = (d, sc, 0 if bs > a0 and bs < b else (1 if bs >= b else 2), bm)
    return bs

def choose(f, lg, hs):
    try:
        setup(START)
        del H[:]
        H.append(key())
        for u in hs:
            for m in legal(0):
                if uci(m) == u:
                    make(m)
                    H.append(key())
                    break
        L = set(lg)
        ms = [m for m in legal(0) if uci(m) in L]
        ms.sort(key=uci)
        if len(ms) == 1:
            return uci(ms[0])
        TT.clear()
        for i in range(64):
            KL[i] = [0, 0]
        N[0] = 0
        bs = [0] * len(ms)
        best = uci(ms[0])
        d = 1
        while 1:
            pb, ob, om = best, bs[:], ms[:]
            try:
                a = -MATE - 1
                for i, m in enumerate(ms):
                    s = C(m, A, d - 1, a, MATE + 1, 0)
                    bs[i] = s
                    if s > a:
                        a = s
                        best = uci(m)
            except TO:
                best, bs, ms = pb, ob, om
                break
            z = sorted(range(len(ms)), key=lambda i: -bs[i])
            ms = [ms[i] for i in z]
            bs = [bs[i] for i in z]
            if a > 90000 or d >= 64:
                break
            d += 1
        return best
    except Exception:
        return lg[0]

def post(p, b):
    r = urllib.request.Request(U + p, data=json.dumps(b).encode(), headers={"content-type": "application/json"})
    with urllib.request.urlopen(r) as x:
        return json.load(x)

if U:
    while 1:
        g = post("/game", {})
        if g["status"] == "done":
            break
        while g["status"] == "your_move":
            g = post("/move", {"game": g["game"], "move": choose(g["fen"], g["legal_moves"], g["moves"])})
        print("game %d: %s by %s" % (g["game"], g["outcome"], g["reason"]), file=sys.stderr)
    print("done: %d won, %d drawn, %d lost" % (g.get("wins"), g.get("draws"), g.get("losses")), file=sys.stderr)
