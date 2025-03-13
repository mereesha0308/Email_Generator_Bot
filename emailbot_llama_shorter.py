import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import re
import time
import random


#### Load data
@st.cache_data
def load_data():
    try:
        return pd.read_csv("merchants_sg_emails.csv")
        #return pd.read_csv("burpple_data_with_emails.csv")
    except FileNotFoundError:
        st.error("The file 'merchants_sg_emails.csv' was not found.")
        #st.error("The file 'burpple_data_with_emails.csv' was not found.")
        return pd.DataFrame()  # Return an empty DataFrame


df = load_data()

# Set your Groq API endpoint and API key securely
groq_api_url = "https://api.groq.com/openai/v1/chat/completions"  # Correct endpoint
groq_api_key = st.secrets["groq"]["api_key"]  # Make sure to securely fetch the API key from environment variables  # Make sure to securely fetch the API key from environment variables

headers = {
    "Authorization": f"Bearer {groq_api_key}",
    "Content-Type": "application/json"
}

# Email Agent (for email generation)
class EmailAgent:
    def __init__(self, max_retries=10, base_delay=10):
        self.max_retries = max_retries  # Maximum retry attempts
        self.base_delay = base_delay  # Initial delay in seconds

    def generate_email(self, merchant_details, your_name, your_position, your_email, your_phone):
        merchant_name = merchant_details.get('merchant_name', 'Merchant')  # Extract the merchant name from the details
        prompt = f"""
        Assume yourself as a lead Marketing Lead, with years of experiences working for leading merchant sourcing and acquiring companies such as wirecard, cardlytics, fave that has helped to connect with small to medium merchants to source an offer. 
        Generate a personalized email for <merchant_name> with a compelling and curiosity-piquing subject line that feels authentic and human-crafted, ensuring the recipient does not perceive it as spam or automated. 

        Make the email feel as if it was personally written by a human, with natural language, warmth, and genuine engagement tailored to the merchant.
        And also Since this email will be read by a human, it’s important to keep it concise—around 150 words in the email. A shorter email ensures it holds their attention, as overly lengthy emails can discourage interest.

        The email should feature a warm and professional greeting, maintaining a conversational yet professional tone to captivate the reader. 
        Incorporate the following: 
        The Google rating of the merchant's category (e.g., burger shops) and its comparison to the average market rating. If the rating is below the market average: Present actionable ways PulseID can help the recipient improve their position, draw more foot traffic, and build stronger customer loyalty.
        If the rating is above the market average: Highlight how PulseID can reinforce their leadership position and expand their market share through increased foot traffic in a friendly way. 
        Ways Pulse iD can help to reach an audience otherwise very difficult to reach, through banks and telcos where customers trust the traffic source. Very different to posting a generic social media post with an offer. 
        But if the score rating is not available do not say this way or similarly “Whether your current rating leads or lags behind the market, there’s an opportunity to maximize impact.
        If there’s room to improve: PulseID can help strengthen your position with personalized loyalty programs and actionable insights designed to attract more customers and foster loyalty.
        If you’re already excelling: Let’s keep that momentum going by leveraging PulseID’s targeted campaigns to sustain your leadership position, reaching new audiences while ensuring your existing ones keep coming back”.

        But mention the idea in a professional supporting and friendly manner how PulseID can support or you can give a generated example how they support merchants like these but not mentioning names. ”Seamlessly integrate specific use cases relevant to the recipient's goals, using insights available online. 

        Based on the merchant and merchant's category/sub category, suggest or recommend a personalize offer for the merchant such as "Did you know the <merchant category> show similar to you that sells <food items(eg.burger, platter, steak etc. ) is giving away an offer for 20% with and is promoting to attract customers while serving the service? This can be you"

        Provide a call-to-action that aligns with the recipient’s objectives, offering actionable steps on how PulseID can support their growth. Ensure the narrative flows naturally, avoiding generic phrases such as "data not available", "no score ratings can be found" etc. 

        Maintain a focus on positive outcomes and actionable insights even if full data is not present. Also give some summary of PulseID use cases from its site and add a link. 

        This email should feel like it was written with directly targeting the recipient in mind, sparking curiosity and motivating engagement. 

        It has avoid too generic statements such as and example "At Pulse iD, we specialize in creating targeted, cost-effective campaigns that bring high-value customers to your doorstep. Here’s how our program can benefit your business: - Increased Customer Footfall: Targeted campaigns bring high-value customers to your location. 📍 - No Upfront Costs: You only fund the discount or offer provided— no hidden fees, no surprises. 👍 - Flexibility: You’re in control of your offers and can adjust or opt out anytime. 🔁". 

        But you can use similar making it tailor made written for the email sender making more personalized and emotionally engage answering a problem and pain of a merchant

        Pulse iD Website Link: https://www.pulseid.com
        
        Merchant Details:
        {merchant_details}


        Always include the sender's details:
        Name: {your_name}
        Position: {your_position}
        Email: {your_email}
        Phone: {your_phone}

        Respond in the following format:
        To: <merchant_email>
        Subject: <subject_line>
        Body: <email_body>
        """

        payload = {
            "model": "llama-3.3-70b-versatile",  # Correct model name
            "messages": [
                {"role": "system", "content": "You are a lead marketing manager with extensive experience."},
                {"role": "user", "content": prompt}
            ]
        }
        
        retries = 0

        while retries < self.max_retries:
            try:
                response = requests.post(groq_api_url, json=payload, headers=headers)
                if response.status_code == 200:
                    response_text = response.json()['choices'][0]['message']['content']
                    
                    # Debugging step: print raw response
                    print(response.json())

                    # Display email content for a specific merchant
                    st.write(f"****************************************")
                    st.write(f"### Email for: {merchant_name}")
                    st.text(response_text)  # Display the raw response text
                    
                    # Check if response_text is a string and not empty
                    if not response_text.strip():
                        raise ValueError("Empty response text received from API.")

                    # Use regex to capture the Subject and Body directly
                    subject_match = re.search(r"Subject:\s*(.*)", response_text)
                    body_match = re.search(r"(Dear\s*\w+|Hello\s*\w+|Hi\s*\w+)[\s\S]*", response_text)

                    # Check if Subject and Body were found
                    if subject_match and body_match:
                        subject = subject_match.group(1).strip()
                        body = body_match.group(0).strip()

                        # Extract 'To' directly
                        to_match = re.search(r"To:\s*(\S+@\S+)", response_text)
                        to_email = to_match.group(1).strip() if to_match else "Error: No email found"

                        # Fix: Add line breaks to sender details
                        body = body.replace(
                            f"{your_name} {your_position} {your_email} {your_phone}",
                            f"{your_name}\n\n{your_position}\n\n{your_email}\n\n{your_phone}"
                        )
                        
                        return to_email, subject, body
                    else:
                        raise ValueError("Parsing error: Missing 'Subject' or 'Body'.")
                
                elif response.status_code == 429:  # Rate Limit Exceeded
                    retries += 1
                    wait_time = 2 ** retries + random.uniform(0, 1)  # Exponential backoff with jitter
                    print(f"Rate limit hit. Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                
                else:
                    raise Exception(f"API request failed with status code {response.status_code}")

            except Exception as e:
                print("Error occurred:", str(e))  # Log the error for better debugging
                retries += 1
                wait_time = 2 ** retries + random.uniform(0, 1)  # Exponential backoff
                print(f"Retrying ({retries}/{self.max_retries}) in {wait_time:.2f} seconds...")
                time.sleep(wait_time)

        return "Error", "Error generating email", "Max retries exceeded."

# Function to generate emails for all merchants
def generate_emails_with_agent(merchants, agent):
    emails = []
    your_name = "Rasika Galhena"
    your_position = "Marketing Manager"
    your_email = "rasika@pulseid.net"
    your_phone = "+94775052158"
    
    for _, row in merchants.iterrows():
        merchant_details = row.to_dict()
        
        # Add a delay before making the request
        time.sleep(random.uniform(1.5, 3.0))  # Random delay between 1.5 to 3 seconds
        
        to_email, subject, body = agent.generate_email(
            merchant_details, your_name, your_position, your_email, your_phone
        )
        emails.append({
            "Merchant Name": row["merchant_name"],
            "Email": f"To: {to_email}\n\nSubject: {subject}\n\n{body}",
        })
    
    return pd.DataFrame(emails)



def main():
    # Streamlit app starts here
    st.title("Merchant Bot")
    st.write("Interact with your Email Generator Bot!")

    # Show dataset preview
    st.subheader("Dataset Preview")
    st.dataframe(df.head(3))  # Display the first 5 rows

    # User Input
    query = st.text_input("Which kind of merchants are you seeking? (e.g., Who are the top merchants in Singapore)")

    if "output_data" not in st.session_state:
        st.session_state.output_data = pd.DataFrame()

    if st.button("Submit"):
        if query:
            st.write(f"Your query: **{query}**")
            
            openai_prompt = f"""
            You are a helpful assistant that generates Python code for data analysis. The dataset contains the following columns:
            {', '.join(df.columns)}

            The user has requested the following:
            {query}

            Generate Python code that can process this request and provide the answer.
            The Python code should use the pandas library to process the dataset.
            Return only the Python code, no explanations or extra text.
            Please generate Python code that can process this request and provide the answer. Do **not include** any markdown or code block formatting (` ```python` or ` ``` `). Just give the Python code directly.
            my dataset file name is: merchants_sg_emails.csv
            when generate Python code that first displays the result using Streamlit functions (`st.write()`, `st.dataframe()`, etc.). Once the result is displayed, store it in the variable 'output_data' in last line of the code. Ensure that the result is properly displayed **before** being assigned to the 'output_data' variable.
            """
            
            try:
                # Use Llama API to generate Python code
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are a helpful data assistant that generates Python code."},
                        {"role": "user", "content": openai_prompt},
                    ]
                }

                response = requests.post(groq_api_url, json=payload, headers=headers)
                if response.status_code == 200:
                    python_code = response.json()['choices'][0]['message']['content'].strip()

                    # Execute the code
                    exec_globals = {"df": df, "pd": pd, "px": px, "st": st}
                    exec(python_code, exec_globals)
                    st.session_state.output_data = exec_globals.get('output_data', pd.DataFrame())
            
            except Exception as e:
                st.error(f"Error: {e}")

    # Generate emails
    if not st.session_state.output_data.empty:
        merchants = st.session_state.output_data
        st.write("### Extracted Merchants")
        st.dataframe(st.session_state.output_data)  # Display merchant data
        
        # Display the extracted merchants count
        #st.write(f"Extracted merchants count: {len(merchants)}")

        if st.button("Generate Emails"):
            email_agent = EmailAgent()
            generated_emails_df = generate_emails_with_agent(merchants, email_agent)

            
            # Allow user to download the generated emails as CSV
            csv_buffer = io.StringIO()
            generated_emails_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download Emails as CSV",
                data=csv_buffer.getvalue(),
                file_name="generated_emails.csv",
                mime="text/csv",
            )
    else:
        st.write("No merchant data available.")


# Run the app
if __name__ == "__main__":
    main()
