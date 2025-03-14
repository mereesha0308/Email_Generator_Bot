import streamlit as st
import openai
import pandas as pd
from openai import OpenAI
import io
from contextlib import redirect_stdout
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

# Retrieve the Kluster API key and base URL securely from Streamlit secrets
kluster_api_key = st.secrets["kluster"]["api_key"]
base_url = st.secrets["kluster"]["base_url"]

# Set up DeepSeek API via Kluster AI
client = OpenAI(
    api_key=kluster_api_key,  # Use the API key from secrets
    base_url=base_url  # Use the base URL from secrets
)

# Update the parsing logic for the response


def parse_email_response(response_text):
    try:
        # Initialize variables for email components
        to_email, subject, body = None, None, None
        
        # Extract 'To' email address if available
        to_email_match = re.search(r"To:\s*([^\n]+)", response_text)
        if to_email_match:
            to_email = to_email_match.group(1).strip()
        
        # Extract 'Subject' if present
        subject_match = re.search(r"Subject:\s*([^\n]+)", response_text)
        if subject_match:
            subject = subject_match.group(1).strip()
        
        # Extract the body content of the email, everything after 'Hi'
        body_match = re.search(r"Hi\s+[^\n]+([\s\S]*)", response_text)
        if body_match:
            body = body_match.group(1).strip()

        # Check if any components are missing and provide specific error messages
        missing_components = []
        if not to_email:
            missing_components.append("To Email")
        if not subject:
            missing_components.append("Subject")
        if not body:
            missing_components.append("Body")
        
        if missing_components:
            print(f"Error: Missing the following email components: {', '.join(missing_components)}")
            return None, None, None
        
        # Return the parsed email components
        return to_email, subject, body
    
    except Exception as e:
        print(f"Error during email parsing: {str(e)}")
        return None, None, None




# Email Agent (for email generation)
class EmailAgent:
    def __init__(self, client):
        self.client = client

        # Modify your generate_email function to use the updated parsing logic
    def generate_email(self, merchant_details, your_name, your_position, your_email, your_phone):
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

        Please generate a full and detailed email that includes a proper closing and call to action, ensuring the email does not get cut off at any point.
        """

        try:
            response = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=[
                    {"role": "system", "content": "Assume yourself as a lead Marketing Lead, with years of experience working for leading merchant sourcing and acquiring companies such as Wirecard, Cardlytics, and Fave, helping connect small to medium merchants to source an offer."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=1500,
                temperature=0.7,
            )
            response_text = response.choices[0].message.content

            # Use the new parsing logic to extract the components
            to_email, subject, body = parse_email_response(response_text)
            
            return to_email, subject, body
        except Exception as e:
            st.error(f"Error generating email: {str(e)}")
            return None, None, None


# Function to generate emails for all merchants
def generate_emails_with_agent(merchants, agent):
    emails = []
    your_name = "Sumit"
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
            **Strictly return only Python code.** Do NOT include `<think>` tags, explanations, comments, or any other meta-content. 
            Generate only valid and executable Python code. Do not include any markdown or code block formatting (` ```python` or ` ``` `). 
            Just give the Python code directly.

            The Python code should:
            1. Use the pandas library to process the dataset.
            2. Display the result using Streamlit functions (`st.write()`, `st.dataframe()`, etc.).
            3. Store the result in the variable 'output_data' after displaying it.
            4. Ensure the dataset file name is 'merchants_sg_emails.csv'.

            **Important:** 
            - Return only the Python code. 
            - Do not include any additional text, explanations, or tags.
            - Skip all reasoning steps. Do not include `<think>` or any other meta-content.
            """

            try:
                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1",
                    messages=[
                        {"role": "system", "content": "You are a helpful data assistant that generates Python code."},
                        {"role": "user", "content": openai_prompt}
                    ]
                )
                python_code = response.choices[0].message.content.strip()
                raw_output = response.choices[0].message.content.strip()

                #st.write("Generated Python Code:")
                #st.code(python_code)


                # Remove <think>...</think> section
                cleaned_output = re.sub(r"<think>.*?</think>", "", raw_output, flags=re.DOTALL).strip()
                python_code = cleaned_output
                #st.write("Generated Python Code:")
                #st.code(cleaned_output)

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
            email_agent = EmailAgent(client=client)  # Initialize the agent
            generated_emails_df = generate_emails_with_agent(merchants, email_agent)
            
            st.write("Generated Emails:")
            for _, row in generated_emails_df.iterrows():
                st.write(f"### Email for {row['Merchant Name']}")
                st.write(row['Email'])
                st.write("---")
            
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
