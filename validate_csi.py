#!/usr/bin/env python3
"""Dependency-free validation of a FeitCSI .dat capture.

Mirrors FeitCSI's own decoding (include/Csi.h RawHeaderData, src/Csi.cpp
format/width decode) using only the Python stdlib.
"""
import math
import struct
import sys

HDR = 272

MOD_TYPES = {0: "CCK", 1: "LEGACY_OFDM", 2: "HT", 3: "VHT", 4: "HE", 5: "EHT"}
WIDTHS = {0: 20, 1: 40, 2: 80, 3: 160, 4: 320}
HT20_PILOTS = {7, 21, 34, 48}


def parse(path):
    data = open(path, "rb").read()
    print(f"File: {path}")
    print(f"Size: {len(data)} bytes")

    records = []
    off = 0
    while off + HDR <= len(data):
        csi_size, _space4, ftm_clock = struct.unpack_from("<III", data, off)
        (timestamp,) = struct.unpack_from("<Q", data, off + 12)
        num_rx = data[off + 46]
        num_tx = data[off + 47]
        (num_sc,) = struct.unpack_from("<I", data, off + 52)
        (rssi1,) = struct.unpack_from("<I", data, off + 60)
        (rssi2,) = struct.unpack_from("<I", data, off + 64)
        src_mac = data[off + 68 : off + 74]
        (rate_n_flags,) = struct.unpack_from("<I", data, off + 92)

        payload = data[off + HDR : off + HDR + csi_size]
        records.append(
            dict(
                csi_size=csi_size,
                ftm_clock=ftm_clock,
                timestamp=timestamp,
                num_rx=num_rx,
                num_tx=num_tx,
                num_sc=num_sc,
                rssi1=rssi1,
                rssi2=rssi2,
                src_mac=src_mac,
                rate_n_flags=rate_n_flags,
                payload=payload,
            )
        )
        off += HDR + csi_size

    print(f"Records: {len(records)}, trailing bytes: {len(data) - off}")
    return records


def decode_rate(rnf):
    mod = (rnf >> 8) & 0x7
    width = (rnf >> 11) & 0x7
    mcs = rnf & 0xF
    nss = (rnf >> 4) & 0x1
    ldpc = bool(rnf & (1 << 27))
    return MOD_TYPES.get(mod, f"?{mod}"), WIDTHS.get(width, f"?{width}"), mcs, nss, ldpc


def samples(rec):
    """int16 re/im pairs, order rx -> tx -> subcarrier (per Csi.h comment)."""
    n = len(rec["payload"]) // 4
    vals = struct.unpack(f"<{n*2}h", rec["payload"])
    out = []
    for i in range(0, len(vals), 2):
        out.append(complex(vals[i], vals[i + 1]))
    return out


def bar(v, maxv, width=56):
    return "#" * max(0, min(width, round(v / maxv * width)))


def main(path):
    records = parse(path)
    for idx, rec in enumerate(records):
        fmt, width, mcs, nss, ldpc = decode_rate(rec["rate_n_flags"])
        mac = ":".join(f"{b:02x}" for b in rec["src_mac"])
        expected = rec["num_rx"] * rec["num_tx"] * rec["num_sc"] * 4
        print(f"\n--- Record {idx} ---")
        print(f"  srcMac          : {mac}")
        print(f"  timestamp       : {rec['timestamp']}")
        print(f"  numRx/numTx     : {rec['num_rx']} / {rec['num_tx']}")
        print(f"  numSubCarriers  : {rec['num_sc']}")
        print(f"  rssi1 / rssi2   : {rec['rssi1']} / {rec['rssi2']}")
        print(f"  rateNFlags      : 0x{rec['rate_n_flags']:08x}"
              f"  -> format={fmt} width={width}MHz mcs={mcs} nss={nss} ldpc={ldpc}")
        print(f"  csiDataSize     : {rec['csi_size']} bytes"
              f" (expected rx*tx*sc*4 = {expected}) -> "
              f"{'OK' if expected == rec['csi_size'] else 'MISMATCH'}")

        smp = samples(rec)
        mags = [abs(s) for s in smp]
        nonzero = [m for m in mags if m > 0]
        print(f"  samples         : {len(smp)} complex int16")
        print(f"  magnitude       : min={min(mags):.1f} max={max(mags):.1f} "
              f"mean={sum(mags)/len(mags):.1f} zero-samples={len(mags)-len(nonzero)}")
        if not nonzero:
            print("  !! all-zero CSI payload")
            continue

        # edge-null check: HT/VHT 20 MHz reports 56 subcarriers, indices 0-3 and
        # 52-55 are guard/DC nulls and should be ~0 in real channel data
        per_rx = rec["num_sc"]
        for rx in range(rec["num_rx"]):
            rxm = mags[rx * per_rx : (rx + 1) * per_rx]
            edge = rxm[:4] + rxm[-4:]
            core = rxm[4:-4]
            print(f"  rx{rx}: edge-null mean={sum(edge)/len(edge):.1f} "
                  f"core mean={sum(core)/len(core):.1f} "
                  f"({'edge < core: consistent with real HT-20 CSI' if sum(edge) < sum(core) else 'NO edge suppression'})")

        # ASCII magnitude plot per rx (normalised to that rx's max)
        for rx in range(rec["num_rx"]):
            rxm = mags[rx * per_rx : (rx + 1) * per_rx]
            mx = max(rxm) or 1
            print(f"\n  |H| rx{rx} (subcarrier 0..{per_rx-1}, '#'={mx:.0f})")
            for i, m in enumerate(rxm):
                mark = " P" if i in HT20_PILOTS and fmt == "HT" and per_rx == 56 else ""
                print(f"   {i:3d} |{bar(m, mx)}{mark}")

        # phase sanity: phases should be spread (real multipath), not constant
        for rx in range(rec["num_rx"]):
            rxp = [math.atan2(s.imag, s.real) for s in
                   smp[rx * per_rx : (rx + 1) * per_rx] if s != 0]
            if rxp:
                print(f"  rx{rx}: phase range {min(rxp):+.2f}..{max(rxp):+.2f} rad "
                      f"({len(rxp)} non-null)")

    print("\nDONE")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/feitcsi-smoke-20260919-205449.dat")
