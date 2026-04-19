def test_wrapper_instantiation():
    from classes.vrchat_api import VRChatAPI

    # basic smoke test: instantiate without credentials and check attributes
    client = VRChatAPI()
    assert hasattr(client, "get_current_user")
    assert hasattr(client, "get_user")
    assert hasattr(client, "get_world")
