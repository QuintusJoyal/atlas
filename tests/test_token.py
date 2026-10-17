from atlas_runtime import token_budget

def test_token_count():
    tc = token_budget.TokenCounter()
    assert tc.count("hello world") > 0
    assert tc.count("") == 0
