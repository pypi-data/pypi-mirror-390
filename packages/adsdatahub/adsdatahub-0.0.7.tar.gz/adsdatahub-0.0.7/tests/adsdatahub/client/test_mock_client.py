import adsdatahub


class TestMockClient:
    def test_constructor_type(self):
        assert isinstance(adsdatahub.MockClient(), adsdatahub.MockClient)
