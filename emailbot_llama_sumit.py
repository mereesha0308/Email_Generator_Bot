import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import re


# Load data
@st.cache_data
def load_data():
    try:
        return pd.read_csv("merchants_sg_emails.csv")
    except FileNotFoundError:
        st.error("The file 'merchants_sg_emails.csv' was not found.")
        return pd.DataFrame()  # Return an empty DataFrame

df = load_data()

# Set your Groq API endpoint and API key securely
# Set your Groq API endpoint and API key securely
groq_api_url = "https://api.groq.com/openai/v1/chat/completions"  # Correct endpoint
groq_api_key = st.secrets["groq"]["api_key"]  # Make sure to securely fetch the API key from environment variables

headers = {
    "Authorization": f"Bearer {groq_api_key}",
    "Content-Type": "application/json"
}

# Email Agent (for email generation)
class EmailAgent:
    def __init__(self):
        pass

    def generate_email(self, merchant_details, your_name, your_position, your_email, your_phone):
        merchant_name = merchant_details.get('merchant_name', 'Merchant')  # Extract the merchant name from the details
        prompt = f"""
        Use {merchant_details} and the Prompt Suggested for Email Generating Bot
        Please refer to the below instructions first
        INTRODUCTION & FLOW INSTRUCTIONS
        Follow the sections below in order (Role, Objectives, Examples, Tone & Style, Key Points to Cover, References, Output Format).
        Use the details in each section to craft a concise, ~200-word outreach email that strongly encourages the merchant to sign up for Pulse iD.
        The final output must be exactly in the 'To | Subject | Body' format (including the signature block), ensuring the email does not get cut off.
        ----------------------------------------------------
        SECTION 1: ROLE
        ----------------------------------------------------
        You are an advanced AI embodying:
        • A seasoned Marketing Lead for merchant sourcing & acquiring (e.g., Wirecard, Cardlytics, Fave)
        • A Loyalty & Merchant Relationship Specialist (e.g., Pulse iD, Giift, Entertainer)
        ----------------------------------------------------
        SECTION 2: OBJECTIVES
        ----------------------------------------------------
        • Persuade merchants to partner with Pulse iD, emphasizing:
        - Zero upfront costs (“pay only for redeemed offers” model).
        - Measurable ROI and trackable campaign performance.
        - Flexibility to pause, modify, or opt out anytime.
        • Demonstrate how Pulse iD uniquely leverages high-intent bank/telco channels, contrasting generic social media blasts.
        • Provide a clear call-to-action to sign up or inquire further.
        ----------------------------------------------------
        SECTION 3: EXAMPLES
        ----------------------------------------------------
        Use or adapt snippets like:
        • “A similar merchant recently boosted foot traffic by 25% with a 20% discount—this could be you!”
        • “We’ve noticed growing demand for 'merchant_category' in 'merchant_location', making this the perfect time to stand out.”
        • “Pulse iD’s data-driven loyalty programs can help 'merchant_name' maintain (or regain) a competitive edge in the market.”
        ----------------------------------------------------
        SECTION 4: TONE & STYLE
        ----------------------------------------------------
        • Professional yet conversational; avoid overly formal or robotic language.
        • Warm, human-crafted feel: this should read like a personal email from an experienced marketing lead.
        • Keep it concise—around 150 words total—to hold the recipient’s attention.
        • Maintain a positive, solution-focused narrative, even if some data is absent.
        ----------------------------------------------------
        SECTION 5: KEY POINTS TO COVER
        ----------------------------------------------------
        1. No Upfront Cost & ROI:
        - Mention the “no fees until redemption” model (or “pay-for-performance” approach).
        - Highlight potential lift in footfall, brand visibility, or revenue.
        2. Rating-Based Personalization (only if merchant rating is provided):
        - If rating < market average: Show how Pulse iD can improve visibility and loyalty via targeted campaigns.
        - If rating > market average: Reinforce how Pulse iD helps them sustain leadership and expand market share.
        - If rating is unavailable, omit any mention of ratings.
        3. High-Intent Channels:
        - Explain how Pulse iD harnesses bank/telco audiences—trusted sources that differ from typical social media.
        4. Offer Example:
        - Give a short, relevant example of a personalized offer.
        - E.g., “Did you know a nearby 'merchant_category' is offering 20% off and seeing double the traffic? This could be you.”
        5. CTA & Next Steps:
        - Invite them to sign up or schedule a conversation.
        - Underscore the flexibility and straightforward onboarding.
        6. Focus on Pulse iD Use Cases (Optional but Encouraged):
        - Briefly mention an online resource or success story link to illustrate credibility (e.g., “Learn more here: <Pulse iD link>”).
        ----------------------------------------------------
        SECTION 6: REFERENCES (FOR INTERNAL AI CONTEXT)
        ----------------------------------------------------
        Use insights from the appended frameworks:
        • Merchant Sourcing Framework
        • Tiering approach (market presence, location count) if needed, but keep the email concise.
        • Relevant case studies:
        - Zions Bank’s merchant-funded rewards success
        - Mastercard’s merchant-funded offers platform
        - Access Development’s approach to discounts
        …(and more in the provided references)
        Focus on short real-world results or quotes if desired (e.g., “Merchants see up to a +XX% revenue lift with card-linked offers.”)
        ----------------------------------------------------
        SECTION 7: OUTPUT FORMAT
        ----------------------------------------------------
        Insert the placeholders below where relevant to personalize your message:
        'merchant_name'
        'merchant_email'
        'merchant_rating'
        'market_average_rating'
        'your_name'
        'your_position'
        'your_email'
        'your_phone'
        The final email MUST follow this template exactly:
        To: <merchant_email>
        Subject: <subject_line>
        Body: <email_body>
        Include a professional closing, e.g.:
        Best regards,
        Sumit Uttamchandani
        Marketing Manager, Pulse iD
        sumit@pulseid.com
        Ensure the email flows naturally and doesn’t exceed ~150 words total.
        No part of the email should be cut off prematurely.
        Avoid disclaimers such as “data not available” or “no rating found.”
        ----------------------------------------------------
        NOW, GENERATE THE FINAL EMAIL ACCORDING TO THESE INSTRUCTIONS.

        Merchant Details:
        {merchant_details}


        Always include the sender's details:
        Name: {your_name}
        Position: {your_position}
        Email: {your_email}
        Phone: {your_phone}

        """

        payload = {
            "model": "llama-3.3-70b-versatile",  # Correct model name
            "messages": [
                {"role": "system", "content": "You are a lead marketing manager with extensive experience."},
                {"role": "user", "content": prompt}
            ]
        }
        
        import re

        try:
            response = requests.post(groq_api_url, json=payload, headers=headers)
            if response.status_code == 200:
                response_text = response.json()['choices'][0]['message']['content']
                # Debugging step: print raw response
                print(response.json())

                # Print the raw API response for debugging
                #st.write("### Raw API Response")

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
                    
                    # Simply return the response body as is (already includes the sender's details)
                    return to_email, subject, body
                else:
                    raise ValueError("Parsing error: Missing 'Subject' or 'Body'.")
            else:
                raise Exception(f"API request failed with status code {response.status_code}")
        
        except Exception as e:
            print("Error occurred:", str(e))  # Log the error for better debugging
            return "Error", "Error generating email", str(e)


# Function to generate emails for all merchants
def generate_emails_with_agent(merchants, agent):
    emails = []
    your_name = "Sumit Uttamachandani"
    your_position = "Marketing Manager"
    your_email = "sumit@pulseid.com"
    your_phone = "+971504959576"
    
    for _, row in merchants.iterrows():
        merchant_details = row.to_dict()
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
