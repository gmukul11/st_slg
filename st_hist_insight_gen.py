import pandas as pd
import numpy as np
import emoji
import re

def preprocessing(data,channel):
    data['Subject line or Title']=data['Subject line or Title'].astype(str)
    data['Subject line or Title']=data['Subject line or Title'].apply(lambda x : x.strip())
    data=data[(data['Delivered']>1200) & (data['Status']=='Sent') & (data['Channel']==channel)]
    data.reset_index(inplace=True,drop=True)
    if data.shape[0]>0:
        data=data.groupby(['Subject line or Title','Channel']).agg({'Delivered':sum,'Unique Clicked':sum}).reset_index()
        data['clicked_perc']=(data['Unique Clicked']*100)/data['Delivered']
        data['Subject line or Title_v2']=data['Subject line or Title'].apply(lambda x : emoji.replace_emoji(x, replace=''))
        data['Subject line or Title_v2']=data['Subject line or Title_v2'].apply(lambda x : x.strip())
        data['last_letter']=data['Subject line or Title_v2'].apply(lambda x : x[-1] if len(x)>0 else '.')
        data['tonality']=np.where(data['last_letter']=='!','surprise',np.where(data['last_letter']=='?','curious','simple'))
        data['title_isupper']=data['Subject line or Title'].apply(lambda x : x.isupper())
        data['no_of_words']=data['Subject line or Title_v2'].apply(lambda x : len(x.split()))
        data['number of emojis']=data['Subject line or Title'].apply(lambda x : emoji.emoji_count(x))
        data['title_len']=data['Subject line or Title_v2'].apply(lambda x : len(x))
        data['title_len']=data['title_len']+data['number of emojis']
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

def insight_prep(data,channel,featli):
        hist_insight=""
        j=0
        for i in featli:
            temp=pd.DataFrame(data.groupby(i).agg({'Delivered':'sum','Unique Clicked':'sum','Channel':'count'})).reset_index()
            if temp.shape[0]>0:
                temp.rename({'Channel':'cnt'},axis=1,inplace=True)
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
