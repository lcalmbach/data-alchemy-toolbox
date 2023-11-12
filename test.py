from openai import OpenAI
import pandas as pd
import streamlit as st


images = pd.read_csv("./data/demo/images.csv")
images.columns = ["url"]
client = OpenAI()

url_root = "https://images-datbx.s3.eu-central-1.amazonaws.com/"
url = f"{url_root}{images.iloc[0]['url']}"
print(url)
response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": url,
                    },
                },
            ],
        }
    ],
    max_tokens=300,
)
st.write(response.choices[0].message.content)
