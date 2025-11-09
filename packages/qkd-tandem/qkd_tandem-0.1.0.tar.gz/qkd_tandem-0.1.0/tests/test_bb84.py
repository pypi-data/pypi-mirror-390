from qkd_tandem.cli.run import simulate

def test_clean_low_qber():
    out = simulate(n_bits=200, attack_rate=0.0, seed=1)
    assert out['bb84_qber'] < 0.05
    assert abs(out['bb84_qber'] - out['ks_qber']) < 0.02

def test_tampered_ks_higher_qber():
    out = simulate(n_bits=500, attack_rate=0.5, seed=2)
    assert out['ks_qber'] > out['bb84_qber']
    assert out['ks_qber'] > 0.3

