# Creat a streamlit app to use the predict_category function and take the input value from the user and display the predicted category and subcategory
import streamlit as st
import openai

# Setting the page config
st.set_page_config(page_title="Unify AI ")

openai.api_key = st.secrets["OPENAI_API_KEY"]
sheet_url = st.secrets["SHEET_URL"]

# Dictionary of categories and subcategories
categories_dict = {
    "Account Registration": ["Cannot Create Account", "Cannot Login to App", "Cannot Create Account"],
    "Connectivity Issue": ["3G Deprecation", "No Signal", "Weak Signal / Spotty Coverage", "Error 102"],
    "Customer Education": ["How to make purchase on APP and Portal", "How To Top Up"],
    "Device Registration": ["Cannot Pair the Device", "Cannot Use QR Scan", "Help Unpairing Account", "Cannot Pair the Device", "Help Unpairing Account"],
    "Hardware Issues": ["Cable / Adapter Issue", "Cannot Charge Hotspot", "LED Lights"],
    "Low Star Rating": [],
    "Order - Delivery Issue": ["Cancel Order", "Change Billing / Shipping Info", "Order Status Request", "Accidental Purchase", "Auto-reload", "Auto-renewal", "Credit on Amount Difference", "Overcharge", "Shipping", "Update On Refund Status", "Exchange::Other", "Defective Device", "Item Missing", "Replacement"],
    "Presale": ["Data Service Pricing", "Hotspot Availability", "Hotspot Pricing"],
    "Product Feature": ["Cannot Boot up Device Successfully", "Network SSID is Not Broadcasting", "Firmware", "Camera", "Signal Scan", "VPN"],
    "Question": ["Coverage", "Day Pass::How to Activate", "GoData", "One Hour Unlimited", "PPG", "Rental", "Skyroam VPN", "Solis 1", "Solis Lite", "Solis X", "USA Ums Inquiry","Follow up", "Homefi/account"],
    "Subscription - Purchase Related": [
        "Cannot Purchase WiFi Service DayPass",
        "Cannot Purchase WiFi Service GoData Monthly",
        "Cannot Purchase WiFi Service PPG - Pay Per GB",
        "Cannot Purchase WiFi Service Unlimited Monthly",
        "Cannot Redeem Coupon Code",
        "Cannot Start WiFi Service DayPass",
        "Cannot Start WiFi Service GoData Monthly",
        "Cannot Start WiFi Service Unlimited Monthly",
        "User Portal Cannot Purchase WiFi Service DayPass",
        "User Portal Cannot Redeem Coupon Code",
        "User Portal Cannot Start WiFi Service DayPass"
    ],
    "Speed": [
        "Data Speed is Slow (Not Throttled)",
        "Data Speed is Throttled"
    ],
    "Task": [
        "Help Customers Switch Plans",
        "Cancel Subscription GoData Unsubscribe / Cancel No Longer Using at This Time",
        "Cancel Subscription GoData Unsubscribe / Cancel Renewed Service",
        "Cancel Subscription UMS Unsubscribe / Cancel No Longer Using at This Time",
        "Cancel Subscription UMS Unsubscribe / Cancel Renewed Service",
        "Cancel Subscription UMS Unsubscribe / Cancel Switching Service",
        "Check Customer's Data Balance",
        "Invoice Request",
        "Password Reset",
        "Provide Guidance Finding WiFi Network Password",
        "Provide Guidance How To Add Multiple Hotspots",
        "Provide Guidance How To Make Payments",
        "Provide Guidance How To Use Skyroam",
        "Provide Guidance Provide Return Instructions",
        "Provide Guidance Resetting WiFi Network Password",
        "Refund Request Auto-Renewal Error",
        "Refund Request Duplicate Order",
        "Refund Request No Coverage In Location",
        "Refund Request Order Mistake",
        "Refund Request Others",
        "Refund Request Overcharged",
        "Sales Conversion",
        "Skyroam Rewards",
        "Transfer Data",
        "Update Account Information Both",
        "Update Account Information Email",
        "Update Account Information Phone Number"
    ], 
    "Other": ["Conversation with [ENTITY] "]
}

# Some html formatting of the background
html_temp = """
                <div style="background-color:{};padding:1px">
                
                </div>
                """

# Creating the sidebar for additional information
with st.sidebar:
    st.markdown("""
    # About the demo 🤓
    **Hacky v1 of the Intent Recognition Pipeline** built using GPT-3.5 
      that could be used by us for generating the training dataset 
      for the topic modeling module of the reasoning engine. 
    """)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    # More Info on the model 🤔
    - Using the **Skyroam Technical docs** sent over by Theja, I created mappings of the categories and subcategories using ChatGPT.
    - Combined with the **"subject" metadata** filled by the agents, this was used for checking the clustering approach.
    - I used **OpenAI's GPT-3.5** model to extract the customer complaint from the conversations in the dataset, and fed that into the model
    to predict the category and subcategory.
    - This would be **superhelpful as a starting point in generating the training dataset** for the topic modeling module where we could train **one of the 
    opensource LLMs** to be able to do this task eliminating our dependency on the ChatGPT model.
    """)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)

# A function to extract category from the input value
def predict_category(input_value):

    if input_value is None:
        return "Other"

    # Remove stop words
    stop_words = ["Solis App", "User Portal", "Device", "Other", "SIMO"]
    input_value = " ".join([word for word in input_value.split() if word not in stop_words])


    # Set up GPT-3 prompt
    prompt = f" From the following input, summarize the customer's problem in one-line. Using the given python dictionary called Categories, map the one-line summary to the corresponding category and subcategory and display them in json format \n\nCategories:\n{categories_dict} \n\n Example: \n Input: 'The consumer issue is the need for assistance in setting up a new unit' \n JSON Output: {{'Category':'Device Registration','Subcategory': 'Cannot Pair the Device'}} \n\n Input value: '{input_value}'  \n\nJSON Output:"

    

    # Generate response from gpt-3.5-turbo

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "You are a helpful assistant. Given below is a conversation between a contact centre agent and a customer. You are to help the agent by mapping the customer's issue to the corresponding category."},
            {"role": "user", "content": prompt}
        ],
    max_tokens=1000,
    n=1,
    stop=None,
    temperature=0.7
    )

    # Extract category from GPT-3 response
    result = response.choices[0].message.content.strip().strip("'").strip('"')

    return result

st.title("Intent Recognition Pipeline :balloon:")
st.markdown("""
    ##### Input a conversation or just a customer issue and get the predicted category and subcategory
    This of this as the first layer of processing on what the customer starts the chat with. You can try out 
    some of the conversations found in this [Google Sheet](%s) (I have hosted this privately within our workspace)
    """ % sheet_url, unsafe_allow_html=True)
# Take input value from the user
input_value = st.text_input("Enter the Input to try out the model:")
# Display the predicted category and subcategory
if st.button("Predict"):
    out_response = predict_category(input_value)
    # Convert string to json
    out_json= eval(out_response)
    # From the predicted json response, extract the category and subcategory
    category = out_json["Category"].strip().strip("'").strip('"')
    subcategory = out_json["Subcategory"].strip().strip("'").strip('"')
    st.write("**Category:** ", category)
    st.write("**Subcategory:** ", subcategory)
