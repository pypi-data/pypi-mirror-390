from spellcure import SpellCure

def test_small_mode_basic():
    model = SpellCure(mode="small")
    output = model.correct("thsi is a tset")
    assert isinstance(output, str)
    assert output.strip() != ""
