from breadify.breadify import bread, toast, repeat, donut

def test_bread():
    assert "🍞" in bread("test")

def test_toast():
    assert "TEST" in toast("test")

def test_repeat():
    assert "🥖" in repeat("test", 2)

def test_donut():
    assert "🍩" in donut("apple")
