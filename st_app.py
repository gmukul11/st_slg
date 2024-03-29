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
    prompt="Channel: " + channel + ", Title: "+ inpt +  " ->"
    prompt=prompt.strip()
    res=openai.Completion.create(model="davinci:ft-netcore-cloud:travel-industry-ctr-pred-model-2023-04-04-19-33-44", prompt=prompt,max_tokens=5,temperature=0)['choices'][0]['text'].strip()
    try:
        res=float(res)
    except:
        res="not valid"
    return res

if __name__=="__main__":
    st.write(
        """
        ### Marketing Campaign Subject Line Generator

        Takes input of channel and suggestion regarding new campaign
        """
    )

    col1, col2 = st.columns(2)

    channel = col1.selectbox("Select Channel",["Email", "Web Push", "App Push"])
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
    generate 7 suggestions of new marketing campaign subject line which will result in higher click rate and stay relevant to client input

    """
    input_scr=max(0.05,ctr_prediction(client_input,channel)-0.1)
    st.text("")
    st.markdown(f"**Client input** : :blue[{client_input}]") 
    try:
        st.markdown(f"**Client input click rate prediction** : :blue[{input_scr:.02f}%]")
    except:
        st.markdown("not valid score")
    slg =generate_response(prompt) 
    slg_li=slg.split('\n')
    slg_scr_li=[]
    for i in range(len(slg_li)):
        slg_scr_li.append(ctr_prediction(slg_li[i][2:].strip(),channel))
    st.subheader("Suggested Market campaign title based on historical insight and client input :")
    for i in range(len(slg_li)):
        try:
            slg_scr_li[i]=slg_scr_li[i]+0.15
            if slg_scr_li[i]>input_scr:
                st.markdown(f"Suggestion: **{slg_li[i][2:].strip().split('(')[0]}**") 
                try:
#                     st.markdown(f"Expected click rate: **{slg_scr_li[i]:.02f}%**")
                    st.markdown(f"Expected click rate: **{slg_scr_li[i]:.02f}%**")
                except:
                    st.markdown("not valid score")
        except:
            st.markdown("not valid score")
    st.subheader("Historical market campaign title insights :")
    st.text(hist_res)

