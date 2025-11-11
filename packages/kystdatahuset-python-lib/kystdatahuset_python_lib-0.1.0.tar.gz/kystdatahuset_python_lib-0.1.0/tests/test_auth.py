from kystdatahuset.auth import login
import os

def test_login_success():
    response = login(os.getenv("TEST_USERNAME"), os.getenv("TEST_PASSWORD"))
    assert response is not None, "Expected a response, got None"
    assert response.data is not None, "Response does not contain 'data'"
    assert response.data.JWT is not None, "Response 'data' does not contain 'JWT'"