# -*- coding: utf-8 -*-
"""Existing handle-number/fixed-sigma probit preview from the local project.

This is a legacy entry-feedback convention, separate from the external Force +
Exact reference output selected for final project reporting. The inherited k
lookup is retained for traceability, without a new equivalence claim.
See docs/CALCULATION.md. No experimental records are embedded in this module.
"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize_scalar

# 官方 Aesthesio 套件全表：力值(g) → 官方 Xf 标号（用户提供的厂商标定）
AESTHESIO = [
    (0.008, 1.65, 'Green'), (0.02, 2.36, 'Green'), (0.04, 2.44, 'Green'),
    (0.07, 2.83, 'Green'), (0.16, 3.22, 'Light Blue'), (0.40, 3.61, 'Light Blue'),
    (0.60, 3.84, 'Purple'), (1.00, 4.08, 'Purple'), (1.40, 4.17, 'Purple'),
    (2.00, 4.31, 'Purple'), (4.00, 4.56, 'Orange'), (6.00, 4.74, 'Orange'),
    (8.00, 4.93, 'Orange'), (10.0, 5.07, 'Orange'), (15.0, 5.18, 'Orange'),
    (60.0, 5.88, 'Orange'), (100.0, 6.10, 'Orange'), (180.0, 6.45, 'Orange'),
    (300.0, 6.65, 'Orange'),
]
LOGS = {g: xf for g, xf, _ in AESTHESIO}

# 本实验实际用到的纤维丝（0.07–2.0 g，共 7 种）
KIT = [0.07, 0.16, 0.4, 0.6, 1.0, 1.4, 2.0]
# δ = (4.31 − 2.83) / 6
SIGMA = (LOGS[KIT[-1]] - LOGS[KIT[0]]) / (len(KIT) - 1)


def pwt(trials, sigma=SIGMA, logs=LOGS):
    """trials: [(力值g, 'O'/'X'), ...] → (PWT_g, mu)；只依赖各力值的 O/X 计数，与顺序无关"""
    xs = np.array([logs[g] for g, _ in trials])
    o = np.array([r.upper() == 'O' for _, r in trials])

    def nll(mu):
        p = np.where(o, norm.cdf(mu - xs, scale=sigma), norm.cdf(xs - mu, scale=sigma))
        return -np.log(p).sum()

    res = minimize_scalar(nll, bounds=(xs.min() - 1, xs.max() + 1), method='bounded')
    return 10 ** res.x / 10000, res.x


# ── k 查表法（用户 2026-08-13 提供，Chaplan 1994 k 值表；原文 0/O 混用为 OCR 噪音）──
K_TABLE_RAW = {
    "OX": -0.5, "0X": -0.5, "XO": 0.5, "X0": 0.5,
    "OOX": -0.378, "00X": -0.378, "XXO": 0.378,
    "OOOX": -0.377, "000X": -0.377, "XXXO": 0.377,
    "OXO": 0.842, "0X0": 0.842, "XOX": -0.842,
    "OOXO": 0.89, "00XO": 0.89, "XXOX": -0.89,
    "OOOXO": 0.894, "000XO": 0.894, "XXXOX": -0.894,
    "OOOOXO": 0.894, "0000XO": 0.894, "XXXXOX": -0.894,
    "OXX": -0.178, "0XX": -0.178, "XOO": 0.178, "X00": 0.178,
    "OOXX": 0.0, "00XX": 0.0, "XXOO": 0.0,
    "OOOXX": 0.026, "000XX": 0.026, "XXXOO": -0.026,
    "OOOOXX": 0.028, "0000XX": 0.028, "XXXXOO": -0.028,
    "OXOO": 0.299, "0X00": 0.299, "XOXX": -0.299,
    "OOXOO": 0.314, "00X00": 0.314, "XXOXX": -0.314,
    "OOOXOO": 0.315, "000X00": 0.315, "XXXOXX": -0.315,
    "OOOOXOO": 0.315, "0000X00": 0.315, "XXXXOXX": -0.315,
    "OXOX": -0.5, "0X0X": -0.5, "XOXO": 0.5,
    "OOXOX": -0.439, "00X0X": -0.439, "XXOXO": 0.439,
    "OOOXOX": -0.432, "000X0X": -0.432, "XXXOXO": 0.432,
    "OOOOXOX": -0.432, "0000X0X": -0.432, "XXXXOXO": 0.432,
    "OXXO": 1.0, "0XX0": 1.0, "XOOX": -1.0, "X00X": -1.0,
    "OOXXO": 1.122, "00XX0": 1.122, "XXOOX": -1.122,
    "OOOXXO": 1.139, "000XX0": 1.139, "XXXOOX": -1.139,
    "OOOOXXO": 1.14, "0000XX0": 1.14, "XXXXOOX": -1.14,
    "OXXX": 0.194, "0XXX": 0.194, "XOOO": -0.194, "X000": -0.194,
    "OOXXX": 0.449, "00XXX": 0.449, "XXOOO": -0.449,
    "OOOXXX": 0.5, "000XXX": 0.5, "XXXOOO": -0.5,
    "OOOOXXX": 0.506, "0000XXX": 0.506, "XXXXOOO": -0.506,
    "OXOOO": -0.157, "0X000": -0.157, "XOXXX": 0.157,
    "OOXOOO": -0.154, "00X000": -0.154, "XXOXXX": 0.154,
    "OOOXOOO": -0.154, "000X000": -0.154, "XXXOXXX": 0.154,
    "OOOOXOOO": -0.154, "0000X000": -0.154, "XXXXOXXX": 0.154,
    "OXOOX": -0.878, "0X00X": -0.878, "XOXXO": 0.878,
    "OOXOOX": -0.861, "00X00X": -0.861, "XXOXXO": 0.861,
    "OOOXOOX": -0.86, "000X00X": -0.86, "XXXOXXO": 0.86,
    "OOOOXOOX": -0.86, "0000X00X": -0.86, "XXXXOXXO": 0.86,
    "OXOXO": 0.701, "0X0X0": 0.701, "XOXOX": -0.701,
    "OOXOXO": 0.737, "00XOX0": 0.737, "XXOXOX": -0.737,
    "OOOXOXO": 0.741, "000XOX0": 0.741, "XXXOXOX": -0.741,
    "OOOOXOXO": 0.741, "0000XOX0": 0.741, "XXXXOXOX": -0.741,
    "OXOXX": 0.084, "0XOXX": 0.084, "XOXOO": -0.084, "X0X00": -0.084,
    "OOXOXX": 0.169, "00XOXX": 0.169, "XXOXOO": -0.169, "XX0X00": -0.169,
    "OOOXOXX": 0.181, "000XOXX": 0.181, "XXXOXOO": -0.181, "XXX0X00": -0.181,
    "OOOOXOXX": 0.182, "0000XOXX": 0.182, "XXXXOXOO": -0.182, "XXXX0X00": -0.182,
    "OXXOO": 0.305, "0XX00": 0.305, "XOOXX": -0.305, "X00XX": -0.305,
    "OOXXOO": 0.372, "00XX00": 0.372, "XXOOXX": -0.372,
    "OOOXXOO": 0.38, "000XX00": 0.38, "XXXOOXX": -0.38,
    "OOOOXXOO": 0.381, "0000XX00": 0.381, "XXXXOOXX": -0.381,
    "OXXOX": -0.305, "0XX0X": -0.305, "XOOXO": 0.305, "X00X0": 0.305,
    "OOXXOX": -0.169, "00XX0X": -0.169, "XXOOXO": 0.169, "XX00X0": 0.169,
    "OOOXXOX": -0.144, "000XX0X": -0.144, "XXXOOXO": 0.144, "XXX00X0": 0.144,
    "OOOOXXOX": -0.142, "0000XX0X": -0.142, "XXXXOOXO": 0.142, "XXXX00X0": 0.142,
    "OXXXO": 1.288, "0XXX0": 1.288, "XOOOX": -1.288, "X000X": -1.288,
    "OOXXXO": 1.5, "00XXX0": 1.5, "XXOOOX": -1.5, "XX000X": -1.5,
    "OOOXXXO": 1.544, "000XXX0": 1.544, "XXXOOOX": -1.544, "XXX000X": -1.544,
    "OOOOXXXO": 1.549, "0000XXX0": 1.549, "XXXXOOOX": -1.549, "XXXX000X": -1.549,
    "OXXXX": 0.555, "0XXXX": 0.555, "XOOOO": -0.555, "X0000": -0.555,
    "OOXXXX": 0.897, "00XXXX": 0.897, "XXOOOO": -0.897, "XX0000": -0.897,
    "OOOXXXX": 0.985, "000XXXX": 0.985, "XXXOOOO": -0.895, "XXX0000": -0.895,
    "OOOOXXXX": 1.0, "0000XXXX": 1.0, "XXXXOOOO": -1.0, "XXXX0000": -1.0,
    "OXOOOO": -0.547, "0X0000": -0.547, "XOXXXX": 0.547,
    "OOXOOOO": -0.547, "00X0000": -0.547, "XXOXXXX": 0.547,
    "OOOXOOOO": -0.547, "000X0000": -0.547, "XXXOXXXX": -0.547,
    "OOOOXOOOO": -0.547, "0000X0000": -0.547, "XXXXOXXXX": -0.547,
    "OOXXOXOX": 0.022, "00XX0X0X": 0.022,
    "OOOXXOXOX": 0.039, "000XX0X0X": 0.039,
    "OOOOXXOXOX": 0.04, "0000XX0X0X": 0.04,
    "OXOXOX": -0.458, "0X0X0X": -0.458,
    "OOXOXOX": -0.453, "00X0X0X": -0.453,
    "OOOXOXOX": -0.453, "000X0X0X": -0.453,
    "OOOOXOXOX": -0.453, "0000X0X0X": -0.453,
    "OXXOXX": 1.169, "0XX0XX": 1.169,
    "OOXXOXX": 1.237, "00XX0XX": 1.237,
    "OOOXXOXX": 1.247, "000XX0XX": 1.247,
    "OOOOXXOXX": 1.248, "0000XX0XX": 1.248,
    "OXXXXO": 0.611, "0XXXX0": 0.611,
    "OOXXXXO": 0.732, "00XXXX0": 0.732,
    "OOOXXXXO": 0.756, "000XXXX0": 0.756,
    "OOOOXXXXO": 0.758, "0000XXXX0": 0.758,
    "OXXOOO": -0.296, "0XX000": -0.296,
    "OOXXOOO": -0.266, "00XX000": -0.266,
    "OOOXXOOO": -0.263, "000XX000": -0.263,
    "OOOOXXOOO": -0.263, "0000XX000": -0.263,
    "OXXOOX": -0.831, "0XX00X": -0.831,
    "OOXXOOX": -0.763, "00XX00X": -0.763,
    "OOOXXOOX": -0.753, "000XX00X": -0.753,
    "OOOOXXOOX": -0.752, "0000XX00X": -0.752,
    "OXXOXO": 0.831, "0XX0X0": 0.831,
    "OOXXOXO": 0.935, "00XX0X0": 0.935,
    "OOOXXOXO": 0.952, "000XX0X0": 0.952,
    "OOOOXXOXO": 0.954, "0000XX0X0": 0.954,
    "OXXXOO": 0.296, "0XXX00": 0.296,
    "OOXXXOO": 0.463, "00XXX00": 0.463,
    "OOOXXXOO": 0.5, "000XXX00": 0.5,
    "OOOOXXXOO": 0.504, "0000XXX00": 0.504,
    "OXXXOX": 0.648, "0XXX0X": 0.648,
    "OOXXXOX": 0.678, "00XXX0X": 0.678,
    "OOOXXXOX": 0.681, "000XXX0X": 0.681,
    "OXXXXX": 0.244, "0XXXXX": 0.244,
    "OOXXXXX": 0.252, "00XXXXX": 0.252,
    "OXXXXXO": 1.603, "0XXXXX0": 1.603,
    "OOXXXXXO": 1.917, "00XXXXX0": 1.917,
    "OOOXXXXXO": 2.0, "000XXXXX0": 2.0,
    "OOOOXXXXXO": 2.014, "0000XXXXX0": 2.014,
    "OXXXXXX": 0.893, "0XXXXXX": 0.893,
    "OOXXXXXX": 1.329, "00XXXXXX": 1.329,
    "OOOXXXXXX": 1.465, "000XXXXXX": 1.465,
    "OOOOXXXXXX": 1.496, "0000XXXXXX": 1.496,
}
# 0 ≡ O（OCR 噪音），归一化
K_TABLE = {}
for _k, _v in K_TABLE_RAW.items():
    K_TABLE[_k.upper().replace('0', 'O')] = _v
# 补全镜像模式：O↔X 互换则 k 取相反数（原表 OCR 不全，如 XOXOXO 缺失 → +0.458）
for _k, _v in list(K_TABLE.items()):
    _mir = _k.replace('O', 'T').replace('X', 'O').replace('T', 'X')
    K_TABLE.setdefault(_mir, -_v)


def k_lookup(seq):
    """按'第一次 OX/XO 后连测 4 次'规则取 6 位序列查 k；序列不足 6 位或无对应模式返回 None"""
    s = seq.upper().replace('0', 'O')
    for i in range(len(s) - 1):
        if s[i] != s[i + 1]:  # 第一次转折
            pat = s[i:i + 6]
            if len(pat) < 6:
                return None
            return K_TABLE.get(pat)
    return None


def pwt_k_table(seq, last_g, sigma=SIGMA):
    """k 查表法：50% Threshold = 10^(Xf + k·δ)/10000；不适用时返回 None"""
    k = k_lookup(seq)
    if k is None:
        return None
    return 10 ** (LOGS[last_g] + k * sigma) / 10000
