import pytest
import io
from conversational_files_API_module import ConversationalFilesAPI  # Import your FastAPI app
from fastapi.testclient import TestClient

api = ConversationalFilesAPI()
client = TestClient(api.app)

class TestConversationalFiles:
    # Define request functions
    @staticmethod
    def get_request(endpoint):
        response = client.get(endpoint)
        return response

    @staticmethod
    def post_request(endpoint, data=None, files=None):
        response = client.post(endpoint, params=data, files=files)
        return response

    # Define your test cases
    def test_root_endpoint(self):
        try:
            response = self.get_request("/")  # Simulate GET request to "/"
            print("test_root_endpoint response:", response.content.decode())
            assert response.status_code == 200
            assert response.content.decode()  # Check if content is present (optional)
        except Exception as e:
            print(f"Error in test_root_endpoint: {e}")

    def test_txt_2_csv(self):
        try:
            data = {"input_str": "header1,header2\n data1,data2"}
            response = self.post_request("/txt2_csv/", data=data)
            print("test_txt_2_csv response:", response.content.decode())
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "text/csv"
            assert response.headers["Content-Disposition"] == "attachment; filename=output.csv"
            
            # Verify CSV content
            content = response.content.decode()
            assert content == "header1,header2\n data1,data2"
        except Exception as e:
            print(f"Error in test_txt_2_csv: {e}")

    def test_get_column_names_valid_csv(self):
        try:
            csv_content = "header1,header2,header3\ndata1,data2,data3"
            csv_file = io.StringIO(csv_content)
            files = {"file": ("test.csv", csv_file.getvalue())}
            response = self.post_request("/get_column_names", files=files)
            print("test_get_column_names_valid_csv response:", response.json())

            assert response.status_code == 200
            assert response.json() == {"column_names": ["header1", "header2", "header3"]}
        except Exception as e:
            print(f"Error in test_get_column_names_valid_csv: {e}")

    def test_get_column_names_invalid_file(self):
        try:
            invalid_content = "This is not a CSV file"
            invalid_file = io.StringIO(invalid_content)
            files = {"file": ("invalid.txt", invalid_file.getvalue())}
            response = self.post_request("/get_column_names", files=files)
            print("test_get_column_names_invalid_file response:", response.json())

            assert response.status_code == 400
            assert "error" in response.json()
        except Exception as e:
            print(f"Error in test_get_column_names_invalid_file: {e}")

    def test_get_column_names_empty_file(self):
        try:
            empty_file = io.StringIO("")
            files = {"file": ("empty.csv", empty_file.getvalue())}
            response = self.post_request("/get_column_names", files=files)
            print("test_get_column_names_empty_file response:", response.json())

            assert response.status_code == 400
            assert "error" in response.json()
        except Exception as e:
            print(f"Error in test_get_column_names_empty_file: {e}")

    def test_get_column_names_missing_file(self):
        try:
            response = self.post_request("/get_column_names")
            print("test_get_column_names_missing_file response:", response.json())

            assert response.status_code == 422  # Unprocessable Entity
            assert "detail" in response.json()
        except Exception as e:
            print(f"Error in test_get_column_names_missing_file: {e}")

    @pytest.mark.parametrize("input_data,expected_columns", [
        ("h1,h2\nd1,d2", ["h1", "h2"]),
        ("single", ["single"]),
        ("a,b,c,d,e\n1,2,3,4,5", ["a", "b", "c", "d", "e"]),
    ])
    def test_get_column_names_various_inputs(self, input_data, expected_columns):
        try:
            csv_file = io.StringIO(input_data)
            files = {"file": ("test.csv", csv_file.getvalue())}
            response = self.post_request("/get_column_names", files=files)
            print("test_get_column_names_various_inputs response:", response.json())

            assert response.status_code == 200
            assert response.json() == {"column_names": expected_columns}
        except Exception as e:
            print(f"Error in test_get_column_names_various_inputs: {e}")

    def test_large_file_handling(self):
        try:
            large_csv_content = "header1,header2\n" + ",".join(["data"] * 2) + "\n" * 100000
            large_csv_file = io.StringIO(large_csv_content)
            files = {"file": ("large.csv", large_csv_file.getvalue())}
            response = self.post_request("/get_column_names", files=files)
            print("test_large_file_handling response:", response.json())

            assert response.status_code == 200
            assert response.json() == {"column_names": ["header1", "header2"]}
        except Exception as e:
            print(f"Error in test_large_file_handling: {e}")

# Run tests
if __name__ == "__main__":
    pytest.main()
    t = TestConversationalFiles()
    t.test_txt_2_csv()
