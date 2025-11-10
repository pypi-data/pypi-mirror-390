import versalaw2

def test_basic():
    result = versalaw2.analyze_contract("test")
    assert 'risk_level' in result
