import requests

class zedlineAPI:
    def __init__(self, base_url="https://zedline.ir/api/v2/"):
        self.base_url = base_url

    def create(self, api, password, data, key):
        return self._send_request(api, password, data, key, method="CREATE")

    def update(self, api, password, data, key):
        return self._send_request(api, password, data, key, method="UPDATE")

    def delete(self, api, password, data, key):
        return self._send_request(api, password, data, key, method="DELETE")

    def _send_request(self, api, password, data, key, method):
        try:
            payload = {
                "api": api,
                "password": password,
                "data": data,
                "Key": key,
                "Method": method
            }
            response = requests.post(self.base_url, data=payload)
            response.raise_for_status()
            json_response = response.json()
            return self._analyze_response(json_response)
        except Exception as e:
            return {"Status": "ERROR", "Message": str(e)}

    def _analyze_response(self, response: dict) -> dict:
        status = response.get("Status-det", "")
        message = response.get("Message", "")

        if status == "OK":
            return {"Status": "OK", "Message": "Request completed successfully"}

        errors = {
            "Invalid input!": "Input values are invalid",
            "User not_found": "User key not found",
            "user_blocked!": "User is blocked by the system",
            "api not_found!": "API not found",
            "illegal access!": "You do not have access to this API",
            "api_blocked!": "API is blocked by the system",
            "Invalid password!": "API password is invalid",
            "api_userblocked!": "API is blocked by the user",
            "api found!": "This API already exists",
            "Invalid character!": "Used characters are not allowed [a-z 0-9]",
            "email invalid!": "Destination email is invalid",
            "Too_Request!": "Request count exceeds the allowed limit",
            "The system is being updated!": "The system is being updated",
            "Method is invalid!": "Invalid method",
            "Invalid Key!": "Access key is invalid",
            "NOTSUB!": "You do not have a subscription to send emails"
        }

        return {"Status": "ERROR", "Message": errors.get(message, f"Unknown error: {message}")}