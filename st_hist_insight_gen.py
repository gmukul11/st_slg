import pandas as pd
import numpy as np
import emoji
import regex
import glob
import re
import random

def simple_stats(data):
    print(f"Min date: {data['Published Time'].min()}")
    print("-----------------------------------------")
    print(f"Max date: {data['Published Time'].max()}")
    print("-----------------------------------------")
    print(f"Unique Titles: {data['Subject line or Title'].nunique()}")
    print("-----------------------------------------")
    print(f"Max length of title: {data['Subject line or Title'].apply(lambda x : len(x)).max()}")
    print("-----------------------------------------")
    print(f"Top titles by count: \n{data['Subject line or Title'].value_counts().head()}")
    print("-----------------------------------------")

def emoji_li(text):
    emoji_list = []
    data = regex.findall(r'\X', text)
    for word in data:
        if word in emoji.UNICODE_EMOJI['en']:
            emoji_list.append(word)
    return emoji_list

def rem_emoji(x):
    temp=[]
    for i in range(len(x)):
        if x[i] in emoji.UNICODE_EMOJI['en']:
            temp.append(i)
    ans=""
    for i in range(len(x)):
        if i not in temp:
            ans+=x[i]
    return " ".join(ans.split())

def preprocessing(data,channel):
    data['Subject line or Title']=data['Subject line or Title'].astype(str)
    data['Subject line or Title']=data['Subject line or Title'].apply(lambda x : x.strip())
    data=data[(data['Delivered']>1200) & (data['Status']=='Sent') & (data['Channel']==channel)]
    data.reset_index(inplace=True,drop=True)
    if data.shape[0]>0:
        data=data.groupby(['Subject line or Title','Channel']).agg({'Delivered':sum,'Unique Clicked':sum}).reset_index()
        data['clicked_perc']=(data['Unique Clicked']*100)/data['Delivered']
        data['emoji_list']=data['Subject line or Title'].apply(lambda x : emoji_li(x))
        data['title_list']=data['Subject line or Title'].apply(lambda x : regex.findall(r'\X', x))
        data['Subject line or Title_v2']=data['title_list'].apply(lambda x : rem_emoji(x))
        data['Subject line or Title_v2']=data['Subject line or Title_v2'].apply(lambda x : x.strip())
        data['last_letter']=data['Subject line or Title_v2'].apply(lambda x : x[-1] if len(x)>0 else '.')
        data['tonality']=np.where(data['last_letter']=='!','surprise',np.where(data['last_letter']=='?','curious','simple'))
        data['title_isupper']=data['Subject line or Title'].apply(lambda x : x.isupper())
        data['title_len']=data['title_list'].apply(lambda x : len(x))
        data['no_of_words']=data['Subject line or Title_v2'].apply(lambda x : len(x.split()))
        data['number of emojis']=data['emoji_list'].apply(lambda x : len(x))
        data['number of emojis']=np.where(data['number of emojis']>2,'2+',data['number of emojis'])
        data['title length bucket']=pd.qcut(data['title_len'],4)
        data['number of words bucket']=pd.qcut(data['no_of_words'],4)
        data['Subject line or Title_v2']=data['Subject line or Title_v2'].str.lower()
        disc_li=['eoss','sale','free','saving','% off','₹']
        new_li=['new']
        data['discount tag']=data['Subject line or Title_v2'].apply(lambda x: 1 if any(i in x for i in disc_li) else 0)
        data['personlisation tag']=data['Subject line or Title_v2'].apply(lambda x: 1 if len(re.findall("\[.*?\]", x))>0 else 0)
        data['new tag']=data['Subject line or Title_v2'].apply(lambda x: 1 if any(i in x for i in new_li) else 0)
        return data
    return None

# fileli=glob.glob("./data/Campaign_*")

channelli=['Email','Web Push','App Push']

# client=fileli[random.randint(0,len(fileli)-1)]
# channel=channelli[random.randint(0,len(channelli)-1)]

def insight_prep(channel):

    data=pd.read_csv("Campaign_Multi_Unified_Summary_20230403 (2).csv")
    data=preprocessing(data,channel)
    if data is None:
        return ""
    if data.shape[0]>0:
        featli=list(data.columns[9:])
        featli.remove('no_of_words')
        featli.remove('title_len')
        hist_insight=""
        j=0
        for i in featli:
            temp=pd.DataFrame(data.groupby(i).agg({'Delivered':'sum','Unique Clicked':'sum','title_list':'count'})).reset_index()
            if temp.shape[0]>0:
                temp.rename({'title_list':'cnt'},axis=1,inplace=True)
                temp['ctr']=(temp['Unique Clicked']*100)/temp['Delivered']
                total_val=(temp[temp['cnt']>5]['Unique Clicked'].sum()*100)/temp[temp['cnt']>10]['Delivered'].sum()
                high_cat=temp.iloc[temp[temp['cnt']>10][['ctr']].idxmax()][i].values[0]
                high_val=temp.iloc[temp[temp['cnt']>10][['ctr']].idxmax()]['ctr'].values[0]
                inc_val=(high_val-total_val)*100/total_val
                if inc_val>5 :
                    if ('tag' in i) and (high_cat==0):
                        continue
                    elif 'tag' in i:
                        j+=1
                        hist_insight=hist_insight+f"{j} subject line with {i} has {inc_val:.0f}% higher click rate than overall"+'\n'
                    else:
                        j+=1
                        hist_insight=hist_insight+f"{j} subject line with {high_cat} {i} has {inc_val:.0f}% higher click rate than overall"+'\n'
        return hist_insight
