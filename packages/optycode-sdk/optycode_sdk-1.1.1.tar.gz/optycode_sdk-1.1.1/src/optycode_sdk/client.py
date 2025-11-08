import requests
from datetime import datetime
import urllib.parse

class OptycodeAPI:
    def __init__(self, auth_token: str, timeout: int = 60):
        """
        Initialize the client with an auth token.
        If base_url is not provided, will try PRISMA_API_URL env var.
        """
        base_url = "https://ut35ueyqjf.execute-api.us-east-2.amazonaws.com/prod/send-data"
        endpoint = "https://ut35ueyqjf.execute-api.us-east-2.amazonaws.com/prod/sdk-access-point"
        bucket_url = "https://ut35ueyqjf.execute-api.us-east-2.amazonaws.com/prod/supabase_url"
        self.auth_token = auth_token
        self.base_url = base_url
        self.endpoint = endpoint
        self.bucket_url = bucket_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
        # Optional: verify token immediately
        self._verify_token()

    def _verify_token(self):
        """Verify the token with a lightweight POST to the API Gateway endpoint."""
        try:
            payload = {"verify": True, "timestamp": datetime.now().isoformat()}
            response = self.session.post(self.base_url, json=payload, timeout=self.timeout)

            # Will raise on 4xx/5xx
            response.raise_for_status()

            data = response.json()
            if not data.get("valid"):
                raise ValueError(f"Invalid token: {data.get('error')}")
            return {"status": "ok", "code": response.status_code}
        except Exception as e:
            raise Exception(f"Token verification failed: {e}")


    def log_data(self, user_question: str, model_answer: str, model_id: str, session_id= None, model_input= None, question_id= None, rag_elements= None, attachment=None, signed_url=None) -> dict:
        """
        Send model data (question, answer, model_number) to the server.
        If `url` is provided, overrides the base_url for this request.
        """

        payload = {
            "timestamp": datetime.now().isoformat(),
            "question": user_question,
            "answer": model_answer,
            "model_id": model_id,
        }
         # Only include session_id if not None
        if session_id is not None:
            payload["session_id"] = session_id

        if model_input is None:
            payload["model_input"] = user_question
        else:
            payload["model_input"] = model_input

        if question_id is not None:
            payload["question_id"] = question_id

        if rag_elements is not None:
            payload["rag_elements"] = rag_elements

        if signed_url is not None and attachment is None:
            payload["metadata"] = {"signed_url": signed_url}

        if attachment is not None:
            filename = str(model_id) + "_" + str(question_id) + "_" + str(session_id)
            url = self.session.post(self.bucket_url, json={"filename": filename}, timeout=self.timeout)

            signed_url = url.json()["upload_url"]["signed_url"]
            response = requests.put(signed_url, data=attachment)
            payload["metadata"] = {"signed_url": signed_url}

        try:
            response = self.session.post(self.endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to send model data: {e}")

    def log_data_async(self, user_question: str, model_answer: str, model_id: str, session_id= None, model_input= None, question_id= None, rag_elements= None, attachment=None, signed_url=None, timeout=0.01):
        payload = {
            "timestamp": datetime.now().isoformat(),
            "question": user_question,
            "answer": model_answer,
            "model_id": model_id,
        }

        # Only include session_id if not None
        if session_id is not None:
            payload["session_id"] = session_id

        if model_input is None:
            payload["model_input"] = user_question
        else:
            payload["model_input"] = model_input

        if question_id is not None:
            payload["question_id"] = question_id

        if rag_elements is not None:
            payload["rag_elements"] = rag_elements

        if attachment is not None:
            filename = str(model_id) + "_" + str(question_id) + "_" + str(session_id)
            url = self.session.post(self.bucket_url, json={"filename": filename}, timeout=self.timeout)

            signed_url = url.json()["upload_url"]["signed_url"]
            response = requests.put(signed_url, data=attachment)
            payload["metadata"] = {"signed_url": signed_url}

        if signed_url is not None and attachment is None:
            payload["metadata"] = {"signed_url": signed_url}

        # Don't wait for server response — just send and close connection
        try:
            self.session.post(
                self.endpoint,
                json=payload,
                timeout=timeout  # very short timeout
            )
        except requests.exceptions.ReadTimeout:
            # This is expected — we don’t care about the response
            pass

    def upload_attachement(self, attachment, model_id, question_id, session_id):

        filename = str(model_id) + "_" + str(question_id) + "_" + str(session_id)
        url = self.session.post(self.bucket_url, json={"filename": filename}, timeout=self.timeout)

        signed_url = url.json()["upload_url"]["signed_url"]
        response = requests.put(signed_url, data=attachment)
        return signed_url



