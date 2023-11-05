import streamlit as st

@st.cache_data
def generate_prompt_rag(query, sources): 
    return "Answer the question based on the context below.\n\n```\n" + "\n".join(sources) + "\n```\n\nQuestion:\n\n" + query + "\nAnswer:"

@st.cache_data
def get_model_output(access_token, prompt_input, max_new_tokens, min_new_tokens, project_id):
    import requests, json
    prompt_input = prompt_input.replace("\n", "\\n")
    url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(access_token)
    }

    data = {
        "model_id": "google/flan-ul2",
        "input": prompt_input,
        "parameters": {
            "decoding_method": "sample",
            "max_new_tokens": max_new_tokens,
            "min_new_tokens": min_new_tokens,
            "random_seed": 17,"stop_sequences": [],
            "temperature": 1.01,
            "top_k": 50,
            "top_p": 1,
            "repetition_penalty": 2
        },
        "project_id": project_id
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    output = response.json()['results'][0]['generated_text']
    #print(output)
    return output

@st.cache_data
def get_model_output_rag(access_token, prompt_input, max_new_tokens, min_new_tokens, random_seed, project_id):
    import requests, json
    #prompt_input = prompt_input.replace("\n", "\\n")
    #prompt_input = prompt_input.replace("\n", "")
    #print(prompt_input)
    url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-28"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(access_token)
    }

    data = {
        "model_id": "meta-llama/llama-2-70b-chat",
        "input": prompt_input,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": max_new_tokens,
            #"min_new_tokens": min_new_tokens,
            #"random_seed": random_seed,
            #"stop_sequences": ["."],
            #"temperature": 0.8,
            #"top_k": 50,
            #"top_p": ,
            "repetition_penalty": 1
        },
        "project_id": project_id
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    output = response.json()['results'][0]['generated_text']
    #print(output)
    return output
# todo: combine this with the one above, and add control for stop_seq

@st.cache_data
def get_model_output_rag_qa(access_token, prompt_input, max_new_tokens, min_new_tokens, random_seed, project_id):
    import requests, json
    #prompt_input = prompt_input.replace("\n", "\\n")
    #prompt_input = prompt_input.replace("\n", "")
    #print(prompt_input)
    url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(access_token)
    }

    data = {
        "model_id": "meta-llama/llama-2-70b-chat",
        "input": prompt_input,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": max_new_tokens,
            "min_new_tokens": min_new_tokens,
            #"random_seed": random_seed,
            "stop_sequences": ["\n"],
            #"temperature": 0.7,
            #"top_k": 50,
            #"top_p": 1 ,
            "repetition_penalty": 1
        },
        "project_id": project_id
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    output = response.json()['results'][0]['generated_text']
    #print(output)
    return output