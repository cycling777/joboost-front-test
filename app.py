import streamlit as st
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_file_to_server(
    file_buffer,
    tenant_id,
    tenant_user_id,
    service_user_id,
    service_user_companies,
    extension,
):
    url = "https://fvoeg1cu56.execute-api.ap-northeast-1.amazonaws.com/prod/upload"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            url=url,
            data=json.dumps(
                {
                    "tenant_id": tenant_id,
                    "tenant_user_id": tenant_user_id,
                    "service_user_id": service_user_id,
                    "service_user_companies": service_user_companies,
                    "extension": extension,
                }
            ),
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        logger.error(f"Something went wrong: {err}")
        return None

    response_data = response.json()

    files = {"file": (response_data["fields"]["key"], file_buffer)}
    try:
        http_response = requests.post(
            response_data["url"],
            data=response_data["fields"],
            files=files,
            verify=True,
        )
        http_response.raise_for_status()
    except requests.exceptions.RequestException as err:
        logger.error(f"Something went wrong: {err}")
        return None

    return http_response.status_code


# Streamlit UI
st.title("File Upload API Trigger")

tenant_id = st.text_input("Tenant ID", "株式会社デザイナー")
tenant_user_id = st.text_input("Tenant User ID", "吉田彰吾")
service_user_id = st.text_input("Service User ID", "嶋田蓮大")

# Dynamic input fields for Service User Companies
service_user_companies = []
add_button = st.button("Add Company")
num_companies = st.session_state.get("num_companies", 0)

if add_button:
    num_companies += 1
    st.session_state.num_companies = num_companies

for i in range(num_companies):
    company = st.text_input(f"Service User Company #{i + 1}", key=f"company_{i}")
    service_user_companies.append(company)

extension = st.text_input("File Extension", ".mp4")

uploaded_file = st.file_uploader("Choose a file", type=["mp4"])

if uploaded_file is not None:
    if st.button("Upload"):
        status_code = upload_file_to_server(
            uploaded_file,
            tenant_id,
            tenant_user_id,
            service_user_id,
            service_user_companies,
            extension,
        )
        if status_code is not None:
            st.success(f"File uploaded successfully with status code {status_code}")
        else:
            st.error("File upload failed")