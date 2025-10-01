import streamlit as st
from js_text_monitor import text_monitor
#import shared_project_functions as spf
import requests

# --- Use st_autorefresh for periodic polling ---
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=1000, key="refresh")

# Set a custom background colour using CSS

page_background_colour = "#F7F9FB"
js_input_colour = "#222E3C"
js_suggestion_colour = "#1976D2"
js_spacing_colour = "#F7F9FB"
js_font_size = "1.4em"
js_box_bg_colour = "#FFFFFF"
toolbar_bg_colour = page_background_colour

st.markdown(
    f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
        /* ...your existing styles... */

    /* Hide Streamlit header and footer */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Remove default Streamlit padding */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }}
    
    .stApp {{
        background-color: {page_background_colour};
    }}

    h1, .stMarkdown h1, .stHeading, .stMarkdownContainer h1 {{
        color: {js_input_colour} !important;
    }}

    label, .stTextInput label, .stTextInput input {{
        color: {js_input_colour} !important;
    }}
    .stTextInput input {{
        background-color: #fff !important;
        color: {js_input_colour} !important;
        font-size: 1.3em !important;
        border-radius: 8px !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: #fff !important;
        border-radius: 8px !important;
        margin-bottom: 8px;
        color: {js_input_colour} !important;
    }}

    label[for="selected_model"] {{
        color: {js_input_colour} !important;
        font-weight: 500;
        font-size: 1.1em;
    }}

    /* Popover inner wrapper (removes black bar) */
    div[data-baseweb="popover"] div.st-dy,
    div[data-baseweb="popover"] div.st-dh {{
        background: #fff !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
        padding: 0 !important;
    }}

    /* Dropdown menu (the popup) */
    div[data-baseweb="popover"] ul[data-testid="stSelectboxVirtualDropdown"] {{
        background-color: #fff !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        color: {js_input_colour} !important;
        padding: 0 !important;
        min-width: 100% !important;
        margin-left: 0 !important;
        left: 0 !important;
        right: auto !important;
        transform: none !important;
    }}

    div[data-baseweb="popover"] ul[data-testid="stSelectboxVirtualDropdown"] > li[role="option"] {{
        background-color: #fff !important;
        color: {js_input_colour} !important;
        border-radius: 6px !important;
        margin: 2px 4px !important;
        padding: 6px 12px !important;
        width: auto !important;
        max-width: 100% !important;
    }}
    div[data-baseweb="popover"] ul[data-testid="stSelectboxVirtualDropdown"] > li[role="option"][aria-selected="true"] {{
        background-color: #e3eaf2 !important;
        color: #1976D2 !important;
    }}

    div[data-baseweb="popover"] ul[data-testid="stSelectboxVirtualDropdown"] div {{
        color: {js_input_colour} !important;
    }}

    .toolbar {{
        background: {toolbar_bg_colour};
        padding: 8px;
        border-radius: 6px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([1,5])
with col1:
    st.markdown('<div style="text-align: right; color: #222E3C; font-size: 1.4em; font-weight: 500;">To:</div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 22px"></div>', unsafe_allow_html=True)  # Spacer
    st.markdown('<div style="text-align: right; color: #222E3C; font-size: 1.4em; font-weight: 500;">Subject:</div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 20px"></div>', unsafe_allow_html=True)  # Spacer
    st.markdown('<div style="text-align: right; color: #222E3C; font-size: 1.4em; font-weight: 500;">Model:</div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 28px"></div>', unsafe_allow_html=True)  # Spacer
    st.markdown('<div style="text-align: right; color: #222E3C; font-size: 1.4em; font-weight: 500;">Words:</div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 20px"></div>', unsafe_allow_html=True)  # Spacer
    st.markdown('<div style="text-align: right; color: #222E3C; font-size: 1.4em; font-weight: 500;">Body:</div>', unsafe_allow_html=True)

# Call inference server for autocomplete suggestions
# Return JSON with suggestions and model list
def get_suggestions(text, selected_model) -> dict:
    try:
        print(f"DEBUG: Sending request to server with text: '{text}' and model: '{selected_model}'")
        response = requests.post(
            "http://localhost:5000/autocomplete",
            json={"model": selected_model,
                  "text": text},
            timeout=2
        )
        if response.status_code == 200: # Successful response
            return {"suggestions": response.json().get("suggestions", []),
                    "model_list": response.json().get("model_list", [])
            }
        else:
            return {"suggestions": ["error1"], "model_list": ["error1"]}
    except Exception as e:
        return {"suggestions": ["error2"], "model_list": ["error2"]}

# Get current text from the custom component (initially empty)
if 'body_text' not in st.session_state:
    st.session_state['body_text'] = ""
    

selected_model = "shakespeare"  # Placeholder for model selection
model_list = ['initial']  # Placeholder for model list

#Initialize model list
@st.cache_data
def get_models_from_server():
    response = get_suggestions("init", selected_model)  # Empty text to get model list
    model_list = response.get("model_list", ['error in get_model_from_server'])
    return model_list
model_list = get_models_from_server()

with col2:
    to = st.text_input("To", key="to", label_visibility="collapsed")
    subject = st.text_input("Subject", key="subject", label_visibility="collapsed")
    
    # Model selection dropdown
    selected_model = st.selectbox(
        "choose model",
        model_list,
        index=0 if "shakespeare" not in model_list else model_list.index("shakespeare"),
        key="selected_model",
        label_visibility="collapsed"
    )
    
    n_words = st.text_input("Number of Words", key="n_words", label_visibility="collapsed")
    
    # Get suggestions from inference server based on current text
    suggestions = []
    if st.session_state['body_text']:
        # get last sentence of body text only
        last_sentence = st.session_state['body_text'].strip().split('.')[-1]  # [-1]: last sentence
        suggestions_response = get_suggestions(last_sentence, selected_model)
        #print(f"DEBUG: suggestions from server: {suggestions_response}")
        
        suggestion_list = suggestions_response.get('suggestions', []) if isinstance(suggestions_response, dict) else []
        suggestion_to_show = suggestion_list[0] 
        if suggestion_list:
            #Show only the first "n_words" words of the suggestion
            if n_words.isdigit() and int(n_words) > 0:
                n = int(n_words) + 1
                words = suggestion_to_show.split(' ')
                suggestion_to_show = ' '.join(words[:n]) if len(words) >= n else suggestion_to_show
        else: suggestion_to_show = ""
    else:
        suggestion_to_show = ""

    # Debug prints
    print("DEBUG: model_list =", model_list)
    print("DEBUG: selected_model (from selectbox) =", selected_model)
    print("DEBUG: st.session_state['selected_model'] =", st.session_state.get("selected_model"))
    
    
    
    # Show the text monitor with the first suggestion
    text = text_monitor(
        suggestion=suggestion_to_show,
        input_color=js_input_colour,
        suggestion_color=js_suggestion_colour,
        spacing_color=js_spacing_colour,
        font_size=js_font_size,
        box_bg_color=js_box_bg_colour,
        height=300,
        key="body_text"
    )
    st.markdown(f"""
    <div class="toolbar" style="background: {toolbar_bg_colour}; padding: 8px; border-radius: 6px;">
        <button style="width:40px; height:40px; font-size: 1.2em;">B</button>
        <button style="width:40px; height:40px; font-size: 1.2em;">I</button>
        <button style="width:40px; height:40px; font-size: 1.2em;">U</button>
        <button style="width:40px; height:40px; font-size: 1.2em;">&#10554;</button>
        <button style="width:40px; height:40px; font-size: 1.2em;">&#10555;</button>
        <button style="width:40px; height:40px; font-size: 1.2em;">&#43;</button>
        <button style="width:40px; height:40px; font-size: 1.2em;">&#9786;</button>

    </div>
    """, unsafe_allow_html=True)