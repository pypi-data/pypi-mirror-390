from pipeline import normalize, tokenize_simple, clean_tokens

def test_normalize():
    assert normalize("Árbol\n NUEVO\t") == "arbol nuevo"

def test_tokenize_and_clean():
    toks = clean_tokens(tokenize_simple("hola, 2024 mundo y el la de"), remove_digits=True, remove_sw=True)
    assert "hola" in toks and "mundo" in toks
    assert "2024" not in toks
