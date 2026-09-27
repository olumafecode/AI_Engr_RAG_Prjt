from app.lexical import BM25, tokenize


def test_tokenize_drops_stopwords_and_folds_plurals():
    assert tokenize("What are the policies for passwords?") == ["policy", "password"]


def test_bm25_ranks_matching_documents_first():
    documents = [
        "Annual leave entitlement by band.",
        "Report a lost or stolen card to the Fraud Desk.",
        "CCTV footage is kept for 90 days.",
    ]
    top = BM25(documents).top("my card was stolen", 3)
    assert top[0][0] == 1
    assert all(score > 0 for _, score in top)


def test_bm25_returns_nothing_when_no_words_match():
    assert BM25(["Annual leave entitlement."]).top("sourdough bread", 5) == []
