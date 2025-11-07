def test_import_and_basic_class():
    from longformer_embedder import LongformerEmbedder
    assert hasattr(LongformerEmbedder, "get_embedding")
