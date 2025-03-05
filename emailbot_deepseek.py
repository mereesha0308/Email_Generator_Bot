import streamlit as st
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

# Initialize DeepSeek LLM API
client = OpenAI(
    #api_key="54ac69c8-55f7-473b-9d00-d8e498b06a3e", #My Key
    api_key="7556ec59-95e1-4ede-b6cf-b8d25dc54339",  # Replace with your actual Kluster API key #Shadeer's api key   
    base_url="https://api.kluster.ai/v1"
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
        Assume yourself as a lead Marketing Lead, with years of experiences working for leading merchant sourcing and acquiring companies such as wirecard, cardlytics, fave that has helped to connect with small to medium merchants to source an offer. 
        Generate a personalized email for <merchant_name> with a compelling and curiosity-piquing subject line that feels authentic and human-crafted, ensuring the recipient does not perceive it as spam or automated. 

        Make the email feel as if it was personally written by a human, with natural language, warmth, and genuine engagement tailored to the merchant.

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
            'merchant_name', 'merchant_category', 'merchant_address',
        'nearest_city', 'merchant_street', 'city', 'merchant_postal_code',
        'country_code', 'merchant_phone_number', 'google_review_score',
        'google_review_count', 'url', 'merchant_website', 'merchant_email',
        'merchant_social_media', 'source', 'Recent review', 'Cuisine Type',
        'Menu', 'Cost per two', 'Operating Hours', 'Storelocations'

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