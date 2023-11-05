try:
    __import__('pysqlite3')
    import sys

    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except:
    print("running locally!")

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from ibm_cloud_sdk_core import IAMTokenManager
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator, BearerTokenAuthenticator
import os

from utils import (
    embed_docs_chroma,
    get_sources_v2,
    parse_docx,
    parse_pdf_v2,
    parse_txt,
    search_docs_chroma,
    text_to_docs,
    wrap_text_in_html,
    parse_pdf_v3
)
from prompts import get_model_output, get_model_output_rag, generate_prompt_rag, get_model_output_rag_qa
from urllib.parse import quote
from common import set_page_container_style

st.set_page_config(page_title="watsonxai", page_icon="⚛", layout="wide")
st.write("#")
st.image("header.png")


set_page_container_style(
        max_width = 1100, max_width_100_percent = True,
        padding_top = 0, padding_right = 1, padding_left = 1, padding_bottom = 10
)

load_dotenv()

try:
    api_key = st.secrets["api_key"]
    project_id = st.secrets["project_id"]
except:
    api_key = os.environ.get("api_key")
    project_id = os.environ.get("project_id")

try:
    access_token = IAMTokenManager(
        apikey=api_key,
        url="https://iam.cloud.ibm.com/identity/token"
    ).get_token()
except:
    raise ValueError("Authentication failed!")


def redirect_button(url: str, text: str = None, color="#FD504D"):
    stringMessage = url + "?body=" + text
    st.markdown(
        f"""
    <a href={stringMessage} target="_self">
        <div style="
                display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 400;
    padding: 0.25rem 0.75rem;
    border-radius: 0.5rem;
    min-height: 38.4px;
    margin: 0px;
    line-height: 1.6;
    color: inherit;
    width: auto;
    user-select: none;
    background-color: rgb(255, 255, 255);
    border: 1px solid rgba(49, 51, 63, 0.2);">
            Send Email
        </div>
    </a>
    """,
        unsafe_allow_html=True
    )

st.header("Customer: Watsonx/AI Analysis")
st.title("")

def clear_submit():
    st.session_state["submit"] = False


if 'summary_output' not in st.session_state:
    st.session_state['summary_output'] = ''

from chromadb.config import Settings
import chromadb

chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))

##############################################################################################

pred_output_col_1, pred_output_col_2 = st.columns(2)

with pred_output_col_1:
    st.subheader("Recent customer interaction:")
with pred_output_col_2:
    st.subheader("Interaction Summary:")

pred_output_img_col, pred_output_chart_col = st.columns(2)

with pred_output_img_col:
    text_input = st.text_area(label="", value="""[Customer Service Representative]: Thank you for calling [Company Name], my name is John. How can I assist you today?

[Customer]: Hi John, I'm calling because I'm really frustrated with the service, and I'm considering canceling it.

[Customer Service Representative]: I'm sorry to hear that you're feeling this way. Can you please share more about the issue you're facing so that I can try to help resolve it for you?

[Customer]: The problem is that the price of my service is just too high, and I can't afford it anymore. It's been increasing steadily, and it's become a financial burden for me.

[Customer Service Representative]: I understand your concern about the pricing. Let me see if I can assist you in finding a more cost-effective solution. Can you please provide me with your account number or the phone number associated with your account so I can look into your billing history?

[Customer]: Sure, it's [Account Number/Phone Number].

[Customer Service Representative]: Thank you for providing that information. Let me review your account.

[Customer]: Take your time.

[Customer Service Representative]: I've reviewed your account, and I can see that your monthly charges have indeed increased over time. I can understand how that can be frustrating. Can you tell me which specific services or features are causing the price increase?

[Customer]: Well, I initially had a basic package, but I added a few premium channels and upgraded my internet speed. While I understand that these additions come with an extra cost, I just didn't expect the overall price to go up so much.

[Customer Service Representative]: I appreciate your explanation, and I can see how those additions can affect the cost. Let me see if there are any promotions or packages available that could better suit your needs.

[Customer]: That would be great. If we can find a more affordable option, I'd be willing to stay with the company.

[Customer Service Representative]: I appreciate your willingness to explore alternatives. Let me check for available packages. Please hold for a moment while I do that.

[Customer]: Okay, I'll wait.

[Customer Service Representative]: Thank you for waiting. I've searched for alternative packages, but it appears that there are no available promotions or plans that would significantly reduce your monthly bill while maintaining the services you want.

[Customer]: I see. That's disappointing.

[Customer Service Representative]: I understand how you feel, and I'm sorry that I couldn't provide a more cost-effective solution in this case. I know that the price increase can be frustrating. If there's anything else you'd like to discuss or if you're still considering canceling, please let me know how you'd like to proceed.

[Customer]: Well, I appreciate your help, but it seems like I have no other option at this point. I'd like to go ahead and cancel the service.

[Customer Service Representative]: I understand your decision, and I'm sorry that we couldn't find a more suitable solution. I'll process your cancellation request for you. Please keep in mind that any equipment returns or final bills will be part of the cancellation process. Thank you for being a customer, and I wish you the best in your future service needs.

[Customer]: Thank you for your assistance, John. I hope I can find a more affordable option elsewhere.

[Customer Service Representative]: You're welcome, and I appreciate your understanding. If you ever decide to return in the future or have any questions, don't hesitate to reach out. Have a good day.
""",
                              height=400, on_change=clear_submit)
    summarize_button = st.button("Summarize!")

with pred_output_chart_col:
    if summarize_button:
        prompt_input = "summarize this customer review in 50 words: " + text_input + "\n" + "Summary: "
        output = get_model_output(access_token, prompt_input, 50, 20, project_id)
        prompt_input_2 = "Classify this review as positive or negative. " + text_input + "\n" + "Summary: "
        output_2 = get_model_output(access_token, prompt_input_2, 1, 1, project_id)
        st.write(output)
        st.session_state['summary_output'] = output
    st.subheader("Interaction Sentiment:")
    if summarize_button:
        if output_2 == "negative":
            st.write(output_2 + "🙁")
        if output_2 == "positive":
            st.write(output_2 + "😃")

st.markdown("___")

ask_questions_row, = st.columns(1)
with ask_questions_row:
    st.subheader("Knowledge Assistant/Offer Recommendations:")

#####
index = None
doc = []

upload_yes = st.checkbox("Upload your own documents?")
if upload_yes:
    uploaded_files = st.file_uploader("Upload a pdf, docx, or txt file",
                                      type=["pdf", "docx", "txt"],
                                      accept_multiple_files=True,
                                      help="Scanned documents are not supported yet!",
                                      on_change=clear_submit, )

    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith(".pdf"):
                doc.append(parse_pdf_v2(uploaded_file))
            elif uploaded_file.name.endswith(".docx"):
                doc.append(parse_docx(uploaded_file))
            elif uploaded_file.name.endswith(".txt"):
                doc.append(parse_txt(uploaded_file))
            else:
                raise ValueError("File type not supported!")
        # print(doc)
        text = text_to_docs(doc)
        index = embed_docs_chroma(chroma_client, text)
else:
    file_path = "./data/Customer Retention Offers.docx"
    doc.append(parse_docx(file_path))
    text = text_to_docs(doc)
    with st.spinner("Indexing document... This may take a while⏳"):
        index = embed_docs_chroma(chroma_client, text)

with st.expander("Document"):
    # Hack to get around st.markdown rendering LaTeX
    st.markdown(f"<p>{wrap_text_in_html(doc)}</p>", unsafe_allow_html=True)

query = st.text_area("Ask a question about the document", on_change=clear_submit,
                     value="Generate an email to a customer with a few offers he is qualified for. " + st.session_state[
                         'summary_output'])

button = st.button("Submit")

if button:
    # if not index:
    #    st.error("Please upload a document!")

    if not query:
        st.error("Please enter a question!")
    else:
        st.session_state["submit"] = True
        # Output Columns
        answer_col, sources_col = st.columns(2)
        sources = search_docs_chroma(index, query)
        print("***********")
        print(sources)

        try:
            prompt_input = generate_prompt_rag(query, sources)
            print("***prompts***")
            print(prompt_input)

            answer_col, sources_col = st.columns(2)
            # Get the sources for the answer
            answer = ""
            with answer_col:
                st.markdown("#### Answer")
                if "email" in query:
                    answer = get_model_output_rag(access_token, prompt_input, 500, 0, 7, project_id)
                    answer = answer.replace(":", ": ")
                    st.markdown(answer)
                    redirect_button("mailto:", quote(answer))
                else:
                    answer = get_model_output_rag_qa(access_token, prompt_input, 100, 50, 1482679647, project_id)
                    print(answer)
                    st.markdown(answer)
                    redirect_button("mailto:", quote(answer))
                    # print(len(answer.split(" ")))

            with sources_col:
                st.markdown("#### Sources")
                for source in sources:
                    st.markdown(source)
                    st.markdown("---")
        except:
            print("generate_prompt_rag error!")
