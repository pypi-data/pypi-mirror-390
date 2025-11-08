import numpy as np
from numba import njit
# import warnings

IBM32_SIGN = np.uint32(0x80000000)
IBM32_EXPT = np.uint32(0x7f000000)
IBM32_FRAC = np.uint32(0x00ffffff)
IBM32_TOP  = np.uint32(0x00f00000)
IEEE32_MAXEXP = 254
IEEE32_INFINITY = np.uint32(0x7f800000)
BITCOUNT_MAGIC32 = np.uint32(0x000055af)  # 用于统计顶端 hex digit 前导零

IBM64_SIGN = np.uint64(0x8000000000000000)
IBM64_EXPT = np.uint64(0x7f00000000000000)
IBM64_FRAC = np.uint64(0x00ffffffffffffff)
IBM64_TOP  = np.uint64(0x00f0000000000000)
TIES_TO_EVEN_MASK32 = np.uint32(0xfffffffd)
TIES_TO_EVEN_MASK64 = np.uint64(0xfffffffffffffffd)
TIES_TO_EVEN_RSHIFT3  = np.uint64(0x000000000000000b)
TIES_TO_EVEN_RSHIFT32 = np.uint64(0x000000017fffffff)

@njit(cache=True)
def _ibm32_to_ieee32_bits(ibm_bits: np.uint32) -> np.uint32:
    ieee_sign = ibm_bits & IBM32_SIGN
    ibm_frac  = ibm_bits & IBM32_FRAC
    if ibm_frac == 0:
        return ieee_sign  # ±0

    ibm_expt = np.int32((ibm_bits & IBM32_EXPT) >> 22)  # >>24 再 *4 等价于 >>22
    top_digit = ibm_frac & IBM32_TOP
    while top_digit == 0:
        ibm_frac <<= np.uint32(4)
        ibm_expt -= 4
        top_digit = ibm_frac & IBM32_TOP
    leading_zeros = np.int32((BITCOUNT_MAGIC32 >> np.uint32(top_digit >> np.uint32(19))) & 3)
    ibm_frac <<= np.uint32(leading_zeros)

    ieee_expt = ibm_expt - 131 - leading_zeros  # C 实现中的 -131-leading_zeros
    if 0 <= ieee_expt < IEEE32_MAXEXP:
        ieee_frac = ibm_frac
        return ieee_sign + (np.uint32(ieee_expt) << np.uint32(23)) + ieee_frac
    elif ieee_expt >= IEEE32_MAXEXP:
        return ieee_sign + IEEE32_INFINITY
    elif ieee_expt >= -32:
        mask = ~(TIES_TO_EVEN_MASK32 << np.uint32(-1 - ieee_expt))
        round_up = np.uint32(1) if (ibm_frac & mask) > 0 else np.uint32(0)
        ieee_frac = ((ibm_frac >> np.uint32(-1 - ieee_expt)) + round_up) >> np.uint32(1)
        return ieee_sign + ieee_frac
    else:
        return ieee_sign  # 下溢到 0

@njit(cache=True)
def _ibm64_to_ieee32_bits(ibm_bits: np.uint64) -> np.uint32:
    ieee_sign = np.uint32((ibm_bits & IBM64_SIGN) >> np.uint64(32))
    ibm_frac  = ibm_bits & IBM64_FRAC
    if ibm_frac == 0:
        return ieee_sign

    ibm_expt = np.int32((ibm_bits & IBM64_EXPT) >> np.uint64(54))
    top_digit = ibm_frac & IBM64_TOP
    while top_digit == 0:
        ibm_frac <<= np.uint64(4)
        ibm_expt -= 4
        top_digit = ibm_frac & IBM64_TOP
    leading_zeros = np.int32((BITCOUNT_MAGIC32 >> np.uint32(top_digit >> np.uint64(51))) & 3)

    ibm_frac <<= np.uint64(leading_zeros)
    ieee_expt = ibm_expt - 131 - leading_zeros
    if 0 <= ieee_expt < IEEE32_MAXEXP:
        round_up = np.uint32(1) if (ibm_frac & TIES_TO_EVEN_RSHIFT32) > 0 else np.uint32(0)
        ieee_frac = ((np.uint32(ibm_frac >> np.uint64(31))) + round_up) >> np.uint32(1)
        return ieee_sign + (np.uint32(ieee_expt) << np.uint32(23)) + ieee_frac
    elif ieee_expt >= IEEE32_MAXEXP:
        return ieee_sign + IEEE32_INFINITY
    elif ieee_expt >= -32:
        mask = ~(TIES_TO_EVEN_MASK64 << np.uint64(31 - ieee_expt))
        round_up = np.uint32(1) if (ibm_frac & mask) > 0 else np.uint32(0)
        ieee_frac = ((np.uint32(ibm_frac >> np.uint64(31 - ieee_expt))) + round_up) >> np.uint32(1)
        return ieee_sign + ieee_frac
    else:
        return ieee_sign

@njit(cache=True)
def _ibm32_to_ieee64_bits(ibm_bits: np.uint32) -> np.uint64:
    ieee_sign = np.uint64(ibm_bits & IBM32_SIGN) << np.uint64(32)
    ibm_frac  = np.uint64(ibm_bits & IBM32_FRAC)
    if ibm_frac == 0:
        return ieee_sign
    ibm_expt = np.int32((ibm_bits & IBM32_EXPT) >> np.uint32(22))
    # 规范化应按 IBM32 的 24-bit 小数顶端掩码
    top_digit = ibm_frac & np.uint64(IBM32_TOP)
    while top_digit == 0:
        ibm_frac <<= np.uint64(4)
        ibm_expt -= 4
        top_digit = ibm_frac & np.uint64(IBM32_TOP)
    # 统计 32-bit 视角下顶端 hex digit 的前导 0 个数
    top_digit_u32 = np.uint32(top_digit)
    leading_zeros = np.int32((BITCOUNT_MAGIC32 >> np.uint32(top_digit_u32 >> np.uint32(19))) & 3)
    ibm_frac <<= np.uint64(leading_zeros)
    ieee_expt = ibm_expt + 765 - leading_zeros
    ieee_frac = ibm_frac << np.uint64(29)
    return ieee_sign + (np.uint64(ieee_expt) << np.uint64(52)) + ieee_frac

@njit(cache=True)
def _ibm64_to_ieee64_bits(ibm_bits: np.uint64) -> np.uint64:
    ieee_sign = ibm_bits & IBM64_SIGN
    ibm_frac  = ibm_bits & IBM64_FRAC
    if ibm_frac == 0:
        return ieee_sign
    ibm_expt = np.int32((ibm_bits & IBM64_EXPT) >> np.uint64(54))
    top_digit = ibm_frac & IBM64_TOP
    while top_digit == 0:
        ibm_frac <<= np.uint64(4)
        ibm_expt -= 4
        top_digit = ibm_frac & IBM64_TOP
    leading_zeros = np.int32((BITCOUNT_MAGIC32 >> np.uint32(top_digit >> np.uint64(51))) & 3)
    ibm_frac <<= np.uint64(leading_zeros)
    ieee_expt = ibm_expt + 765 - leading_zeros
    round_up = np.uint64(1) if (ibm_frac & TIES_TO_EVEN_RSHIFT3) > 0 else np.uint64(0)
    ieee_frac = ((ibm_frac >> np.uint64(2)) + round_up) >> np.uint64(1)
    return ieee_sign + (np.uint64(ieee_expt) << np.uint64(52)) + ieee_frac

# 向量封装（输入必须是 uint32/uint64 数组，返回 float32/float64）
@njit(cache=True)
def ibm2float32_numba_u32(x):
    out = np.empty(x.shape, dtype=np.float32)
    xf = x.ravel()
    of = out.view(np.uint32).ravel()
    for i in range(xf.size):
        of[i] = _ibm32_to_ieee32_bits(xf[i])
    return out

@njit(cache=True)
def ibm2float32_numba_u64(x):
    out = np.empty(x.shape, dtype=np.float32)
    xf = x.ravel()
    of = out.view(np.uint32).ravel()
    for i in range(xf.size):
        of[i] = _ibm64_to_ieee32_bits(xf[i])
    return out

@njit(cache=True)
def ibm2float64_numba_u32(x):
    out = np.empty(x.shape, dtype=np.float64)
    xf = x.ravel()
    of = out.view(np.uint64).ravel()
    for i in range(xf.size):
        of[i] = _ibm32_to_ieee64_bits(xf[i])
    return out

@njit(cache=True)
def ibm2float64_numba_u64(x):
    out = np.empty(x.shape, dtype=np.float64)
    xf = x.ravel()
    of = out.view(np.uint64).ravel()
    for i in range(xf.size):
        of[i] = _ibm64_to_ieee64_bits(xf[i])
    return out

# 便捷入口
def ibm2float32(a: np.ndarray) -> np.ndarray:
    """
    Convert IBM-format (uint32/uint64) to IEEE float32.

    Examples
    --------
    >>> ibm2float32(np.array([0x41100000], dtype=np.uint32))
    array([1.], dtype=float32)
    """
    a = np.asarray(a)
    if a.dtype not in (np.uint32, np.uint64):
        raise TypeError(f"ibm2float32: input must be uint32 or uint64, got {a.dtype}")
    if not a.flags.c_contiguous:
        a = np.ascontiguousarray(a)
    return ibm2float32_numba_u32(a) if a.dtype == np.uint32 else ibm2float32_numba_u64(a)

def ibm2float64(a: np.ndarray) -> np.ndarray:
    """
    Convert IBM-format (uint32/uint64) to IEEE float64.

    Examples
    --------
    >>> ibm2float64(np.array([0x4110000000000000], dtype=np.uint64))
    array([1.])
    """
    a = np.asarray(a)
    if a.dtype not in (np.uint32, np.uint64):
        raise TypeError(f"ibm2float64: input must be uint32 or uint64, got {a.dtype}")
    if not a.flags.c_contiguous:
        a = np.ascontiguousarray(a)
    return ibm2float64_numba_u32(a) if a.dtype == np.uint32 else ibm2float64_numba_u64(a)