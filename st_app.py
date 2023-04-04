import streamlit as st
import st_hist_insight_gen
import openai
openai.api_key=st.secrets['openai_api_key']

def generate_response(prompt):
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}])
    return completion.choices[0].message.content

def ctr_prediction(inpt,channel):
    prompt="Channel: " + channel + " Subject line: "+ inpt +  " -->"
    prompt=prompt.strip()
    res=float(openai.Completion.create(model="davinci:ft-netcore-cloud-2023-04-04-01-15-42", prompt=prompt,max_tokens=5)['choices'][0]['text'].strip())
    return res

st.write(
    """
    ### Marketing Campaign Subject Line Generator

    Takes input of channel and suggestion regarding new campaign
    """
)

col1, col2 = st.columns(2)

channel = col1.selectbox("Select Channel",["App Push", "Email", "Web Push"])
client_input=col2.text_input("Give input","For e.g. Travel with us - get exciting offers")
hist_res=st_hist_insight_gen.insight_prep(channel)

prompt=f"""

Based on historical client marketing campaign subject line and click rate data insights :
{hist_res}
and client input for new campaign :
{client_input}
generate 5 suggestions of new marketing campaign subject line which will result in higher click rate

"""
input_scr=ctr_prediction(client_input,channel)
st.text("")
st.markdown(f"**Client input** : {client_input}") 
st.markdown(f"**Client input click rate prediction** : {input_scr:.02f}%")
slg =generate_response(prompt) 
slg_li=slg.split('\n')
slg_scr_li=[]
for i in range(len(slg_li)):
    slg_scr_li.append(ctr_prediction(slg_li[i][2:].strip(),channel))
st.subheader("Suggested Market campaign title based on historical insight and client input :")
for i in range(len(slg_li)):
    st.markdown(f"Suggestion: {slg_li[i]} and expected click rate: {slg_scr_li[i]:.02f}%")
st.subheader("Historical market campaign title insights :")
st.text(hist_res)

