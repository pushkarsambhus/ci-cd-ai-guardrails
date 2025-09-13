from app.scanner import scan_diff

def test_secrets_detection():
    diff = "+ API_KEY='abcdefghijklmnop1234'\n"
    res = scan_diff('repo', diff)
    assert any('secrets:' in f for f in res['findings'])

def test_dep_downgrade_detection():
    diff = """-requests==2.31.0
+requests==2.20.0
"""
    res = scan_diff('repo', diff)
    assert any('dependency_downgrade' in f for f in res['findings'])

def test_missing_tests_smell():
    diff = "+ def new_function():\n+    pass\n"
    res = scan_diff('repo', diff)
    assert 'code_changed_no_tests_changed' in res['findings']
