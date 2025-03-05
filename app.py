import streamlit as st
import importlib

# Mapping of dropdown options to file names
model_mapping = {
    "Email Generator Bot - OpenAI": "emailbot_openai",
    "Email Generator Bot - OpenAI(Shorter)": "emailbot_openai_shorter",
    "Email Generator Bot - OpenAI(Sumit)": "emailbot_openai_sumit",
    "Email Generator Bot - LLaMA": "emailbot_llama",
    "Email Generator Bot - LLaMA(Shorter)": "emailbot_llama_shorter",
    "Email Generator Bot - LLaMa(Sumit)": "emailbot_llama_sumit",
    "Email Generator Bot - DeepSeek": "emailbot_deepseek",
    "Email Generator Bot - DeepSeek(Shorter)": "emailbot_deepseek_shorter",
    "Email Generator Bot - DeepSeek(Sumit)": "emailbot_deepseek_sumit",

    
}

# Set default model on first run
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Email Generator Bot - OpenAI"  # Default selection

# Sidebar dropdown for model selection
selected_option = st.sidebar.selectbox(
    "Select Email Bot Model:", 
    list(model_mapping.keys()), 
    index=list(model_mapping.keys()).index(st.session_state.selected_model)
)

# Update session state
st.session_state.selected_model = selected_option

# Get the corresponding script name
script_name = model_mapping[selected_option]

# Display the running model
st.write(f"🔹 Running: `{script_name}.py`")

# Import and run the selected script
try:
    module = importlib.import_module(script_name)
    module.main()  # Ensure each script has a `main()` function
except Exception as e:
    st.error(f"⚠️ Error running `{script_name}.py`: {e}")
