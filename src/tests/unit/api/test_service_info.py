from deps_cloud_native_extraction import constants


class TestServiceInfo:
    endpoint = constants.BASE_API_PREFIX + "/service-info"

    def test_version(self, client):
        response = client.get(f"{self.endpoint}/version")

        assert response.status_code == 200
