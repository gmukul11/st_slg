import streamlit as st
import pandas as pd
import st_hist_insight_gen
import openai
openai.api_key=st.secrets['openai_api_key']

def generate_response(prompt):
    completion = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],temperature=0)
    return completion.choices[0].message.content

def ctr_prediction(inpt,channel):
    prompt="Channel: " + channel + " Subject line: "+ inpt +  " -->"
    prompt=prompt.strip()
    res=float(openai.Completion.create(model="davinci:ft-netcore-cloud:travel-industry-ctr-pred-model-2023-04-04-19-33-44", prompt=prompt,max_tokens=5)['choices'][0]['text'].strip())
    return res

if __name__=="__main__":
    st.write(
        """
        ### Marketing Campaign Subject Line Generator

        Takes input of channel and suggestion regarding new campaign
        """
    )

    col1, col2 = st.columns(2)

    channel = col1.selectbox("Select Channel",["App Push", "Email", "Web Push"])
    client_input=col2.text_input("Give input","For e.g. Travel with us - get exciting offers")
    data=pd.read_csv("travel_industry_campaign_data.csv")
    featli=['tonality','title_isupper','number of emojis','title length bucket','number of words bucket','discount tag','personlisation tag','new tag']
    data=st_hist_insight_gen.preprocessing(data,channel)
    hist_res=st_hist_insight_gen.insight_prep(data,featli)

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

