from optycode_sdk import OptycodeAPI

# with open("img.png", "rb") as f:
#     image = f.read()

client = OptycodeAPI(auth_token="")
# client.OptycodeAPI(auth_token="")
client.log_data(user_question="NUOVO ID", model_answer="async2", model_id='', session_id=1234, model_input="aaa", question_id=2, rag_elements=None, attachment=None)
