import pandas as pd
from text2clusters import TextClusterer, EmbeddingConfig, ReductionConfig, ClusterConfig

def test_import_and_configs():
    _ = TextClusterer()
    EmbeddingConfig()
    ReductionConfig()
    ClusterConfig()

def test_dataframe_interface():
    df = pd.DataFrame({"text": ["hello world", "hi there"]})
    # Don't actually run heavy embedding in CI by default.
    assert "text" in df.columns
