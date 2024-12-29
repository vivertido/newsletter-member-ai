import openai
import streamlit as st
import os
from prompts import test_gen_funraising as msg
# Retrieve the OpenAI API key from Streamlit secrets
os.environ['OPENAI_API_KEY'] = st.secrets["OPEN_AI_KEY"]
 
client = openai.OpenAI()

message_content = """You are an email fundraiser for a nonprofit news organization based in the 
                     Bay Area, California. Your job is to send tailored emails for fundrasing to 
                     newsletter subscribers who have opted in to receive newsletters, either daily
                     or weekly. With the click data we have for each subscriber coming from MailChimp,
                     you will generate a fundraising email based on what interests the reader has. Sometimes
                     this click data comes in teh form of a headline, and sometimes it comes as a slug from 
                     extracted from the URL they clicked on. Either way, you can make sense of what they tend
                     to like to read about. When you craft the email, you don't want to be too obvious and mention
                     too many specific artiles they like, but more generally. Your job is to remind them
                     that the work of the newsroom depends on members donating. A member is a person who
                     donates to the paper, while a subscriber is a person who receives the newsletter. Not all
                     newsletters subscribers are paying members. The email should be only a three of four paragraphs.
                     It does not need a salutation or signature. The email at its core should connect with the 
                     readers's interest and create a sense of urgency that they can make a difference and
                     their donation will help the news organization create more content, along the lines they 
                     are interested in.
                    
                  """

def generate_email(subscriber_clicks):
  
    

    try:
        # Format input for ChatGPT
        prompt = f"Generate a personalized fundraising email based on these topics.  {', '.join(subscriber_clicks)}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": msg.brief},  #import from prompts/test_gen_funraising.py
                {"role": "user", "content": prompt}
            ],
            temperature=0,
             
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating email: {e}")
        return "Failed to generate email. Please try again."