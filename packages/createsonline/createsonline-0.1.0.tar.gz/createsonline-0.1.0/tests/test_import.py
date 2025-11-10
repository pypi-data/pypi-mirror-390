"""
Basic test to ensure test discovery works.
"""

def test_import():
    """Test that the createsonline package can be imported."""
    import createsonline
    assert createsonline.__name__ == "createsonline"
