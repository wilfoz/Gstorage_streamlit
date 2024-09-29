import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account


def load_credentials():
    gcs_credentials = dict(st.secrets["gcloud"])
    credentials = service_account.Credentials.from_service_account_info(gcs_credentials)
    return credentials


@st.cache_resource()
def init_bucket():
    try:
        credentials = load_credentials()
        client = storage.Client(credentials=credentials)
        bucket_name = 'streamlit-chatlt'
        bucket = client.get_bucket(bucket_name)
        return bucket
    except Exception as e:
        st.error(f"Erro ao inicializar Storage: {str(e)}")
        return None
