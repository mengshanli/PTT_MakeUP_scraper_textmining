# -*- coding: utf-8 -*-
#%%
'''
scraper-PPT 美妝版
2018/1/1~12/29
makeup 2821~3182 page
https://www.ptt.cc/bbs/MakeUp/index3171.html
'''

import requests 
from bs4 import BeautifulSoup
import pandas as pd
       
ptt_url='https://www.ptt.cc'

all_push=[]
all_content=[]
all_date=[]
all_title=[]

for i in range(3182,2821,-1):# change
    all_url = 'https://www.ptt.cc/bbs/MakeUp/index%d.html' % i # change
    resp = requests.get(all_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    article_url=[]
    uu=soup.select('a[href^="/bbs/MakeUp/M"]') #首頁文章標題連結 # change
    for uuu in uu:
        a=ptt_url+uuu['href']
        article_url.append(a)
    
    article_push=[]
    pp=soup.select(".nrec") #首頁文章推文數
    for ppp in pp:
        text=ppp.get_text()
        article_push.append(text)
    all_push.append(article_push)
    
    article_date=[]
    dd=soup.select(".date") #首頁文章日期
    for ddd in dd:
        text=ddd.get_text()
        article_date.append(text)
    all_date.append(article_date)
    
    article_title=[]
    tt=soup.select(".title") #首頁文章標題
    for ttt in tt:
        text=ttt.get_text()
        article_title.append(text)
    all_title.append(article_title)
    
    if i == 3182: # change
        #article_url=article_url[:20]  # change     
        del article_url[4:] # change
    else:
        article_url=article_url
        
    contents=[]
    for i in range(len(article_url)): #抓各文章的資訊        
        url=article_url[i]
        resp2 = requests.get(url)
        soup2 = BeautifulSoup(resp2.text, 'html.parser')
        
        try:    
            time=soup2.select(".article-meta-value")[3].get_text()
            author=soup2.select(".article-meta-value")[0].get_text()
            board=soup2.select(".article-meta-value")[1].get_text()
            title=soup2.select(".article-meta-value")[2].get_text()
            
            '''
            # 文章內文
            article=soup2.select("#main-content")                            
            article=str(article)
            #t1=article.split("</span></div>")
                
            t1=article.split("2018</span></div>")
            t2=t1[1].split("""<span class="f2">※ 發信站""")
            article=t2[0]
            '''
            
            content={'board':board, 'author':author, 'title':title, 'time':time}
            contents.append(content)        
        except:
            print("error")                                    
    all_content.append(contents)

# each article info  
all_contents=[]
for c in all_content:
    for cc in c:
        all_contents.append(cc)
all_contents1=pd.DataFrame(all_contents)

# homepage info     
all_pushs=[]
for p in all_push:
    for pp in p:
        all_pushs.append(pp)
all_pushs1=pd.DataFrame(all_pushs, columns=['push'])
        
all_dates=[]
for d in all_date:
    for dd in d:
        all_dates.append(dd)       
all_dates1=pd.DataFrame(all_dates, columns=['date'])

all_titles=[]
for t in all_title:
    for tt in t:
        all_titles.append(tt)       
all_titles1=pd.DataFrame(all_titles, columns=['title'])

tems=pd.concat([all_titles1,all_dates1],axis=1)
homepage=pd.concat([tems,all_pushs1],axis=1)
homepage['title']=homepage['title'].str.strip('\n')
      
# merge
final_result=pd.merge(all_contents1,homepage, on='title')
final_result=pd.DataFrame(final_result, columns=['board','title','author','date','push'])

# split topic
title=final_result["title"]

titles=[]
for t in range(len(title)):
    try:
        topic=title.iloc[t].split("]")
        topic=topic[0].split("[")
        topic=topic[1]
    except:
        print('error')
        topic=''
    titles.append(topic)
    
titles=pd.DataFrame(titles, columns=['topic'])
final_result['topic']=titles

final_result.to_csv("makeup_0101-1229.csv", encoding='utf_8_sig')  # change   

#%%
'''
=========================================================================
jieba-split words

https://blog.csdn.net/HHTNAN/article/details/76586693
https://www.jianshu.com/p/e8b5d01ca073
https://cloud.tencent.com/developer/article/1010859
https://github.com/fxsjy/jieba #簡體
https://github.com/ldkrsi/jieba-zh_TW #繁體
=========================================================================
'''
import requests 
from bs4 import BeautifulSoup
import pandas as pd
#import numpy as np
import jieba

makeup=pd.read_csv("makeup_0101-1229.csv",encoding='utf_8_sig')

'''
# only 爆
makeup=makeup[makeup['push'] == '爆']
makeup=makeup.reset_index(drop=True)
'''

# transform string into int
makeup_new=makeup.sort_values(by = "push")
makeup_new=makeup_new.reset_index()
makeup_new_other=makeup_new.iloc[:6196] # 爆 以外

makeup_new_high=makeup_new.iloc[6200:6416] # 爆 

aa=makeup_new_other['push']
pushs=[]
for a in aa:    
    tem=int(a)
    pushs.append(tem)

pushs=pd.DataFrame(pushs, columns=['push1'])
makeup_new_other['push1']=pushs
 
#stds=makeup_new_other[makeup_new_other['push1'] >= 30] # set standard

makeup=pd.concat([makeup_new_other,makeup_new_high], axis=0) # new raw data
#makeup=pd.concat([stds,makeup_new_high], axis=0) # new raw data
makeup=makeup.reset_index(drop=True)

# 標題去topic
title=makeup['title'] 

titles=[]
for t in range(len(title)):
    
    try:
        topic=title.iloc[t].split("]")
        topic=topic[1]
    except:
        print('error')
        topic=''
    titles.append(topic)
    
titles=pd.DataFrame(titles, columns=['title_1'])
makeup['title_1']=titles

#makeup.to_csv('MDS_makeup_title1_1229new.csv', encoding='utf-8-sig')

#%%
'''
# cut(dict of key words and stop words)
https://blog.csdn.net/u012052268/article/details/77825981#52-%E8%BD%BD%E5%85%A5%E5%81%9C%E7%94%A8%E8%AF%8D%E8%A1%A8
'''
jieba.load_userdict("dict_words.txt") # load words dict

jieba.add_word('水桶名單')
jieba.add_word('總裁系列')
jieba.add_word('內有選手')
jieba.add_word('MAC')
jieba.add_word('眼影盤')
jieba.add_word('倩碧小花')
jieba.add_word('絕對完美')
jieba.add_word('粉持久')
jieba.add_word('訂製')
jieba.add_word('超持久')
jieba.add_word('MAC唇膏')
jieba.add_word('試色分享')
jieba.add_word('唇膏分享')
jieba.add_word('簡單分享')
jieba.add_word('蘭蔻零粉感')
jieba.add_word('蘭蔻絕對完美')
jieba.add_word('唇膏色')
jieba.add_word('霧面唇膏')
jieba.add_word('色號選擇')
jieba.add_word('選擇色號')
jieba.add_word('蜜粉餅')
jieba.add_word('凹凹賞')
jieba.add_word('有人用過')
jieba.add_word('單眼皮')
jieba.add_word('求推薦')
jieba.add_word('晃祐堂')
jieba.add_word('BobbiBrown')
jieba.add_word('妝前乳')
jieba.add_word('混合肌')
jieba.add_word('Dior唇膏')   
jieba.add_word('鬼打牆')
jieba.add_word('色唇膏')
jieba.add_word('心得分享')
jieba.add_word('訂製唇膏')
jieba.add_word('液態唇膏')
jieba.add_word('櫃姐流動率')
jieba.add_word('水粉底')

#add stop words to this file
def stopwordslist(filepath):  # load stop words dict
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8-sig').readlines()]  
    return stopwords

stopwords = stopwordslist('dict_stops.txt')  # 匯入停用詞

def seg_sentence(sentence, stopwords):  
    sentence_seged = list(jieba.cut(sentence.strip()))
    
    #count=word_frequency(sentence_seged)
    
    outstr =[]
    for word in sentence_seged:
        if word not in stopwords:  
            if word != '\t':  
                outstr.append(word) 
    
    while ' ' in outstr:
        outstr.remove(' ')        
    
    return outstr

    
'''
term frequency
'''    
from collections import Counter
    
def word_frequency(seg_list):
    c = Counter()
    for x in seg_list:
        #print(x)
        if len(x)>1 and x != '\r\n':
            c[x] += 1 
    return c
#%%
'''
=====================================================================
'''  
# combine all articles to one article
''' 
title=makeup["title_1"]
#content=makeup["content"] 

all_title='' # combine all titles
for row in range(len(title)):
    each=title[row]
    all_title += each
    
all_content='' # combine all contents
for row in range(len(content)):
    each=content[row]
    all_content += each  
    
count_title=seg_sentence(all_title, stopwords)[1] #詞頻
#count_content=seg_sentence(all_content, stopwords)[1] #詞頻

count_title1=pd.DataFrame.from_dict(count_title, orient='index',columns=['count']).reset_index()
#count_content1=pd.DataFrame.from_dict(count_content, orient='index',columns=['count']).reset_index() 
'''
#%%     
# each article 

each_result=[]
title_result=[]
content_result=[]
for row in range(len(makeup)):
    title=makeup["title_1"][row]  
    #content=makeup["content"][row]  

    each_title=seg_sentence(title, stopwords) #切詞
    #each_content=seg_sentence(content, stopwords) #切詞 
    
    title_result.append(each_title)
    #content_result.append(each_content)

#title_result1=pd.DataFrame(title_result)
#title_result1.to_csv("data_for_tableau.csv", encoding="utf-8-sig", index=False)

#%%
'''
============================================================================
scatter plot
跟眉毛有關的文章中，求批與非求批文章的比例
'''    
results=[]
#test_data=makeup['title_1']
for i in range(len(title_result)):
    if '眉毛' in title_result[i]:
        results.append(i)  
        print(title_result[i])

final=[]
for i in results:         
    word=title_result[i]
    push=makeup.get_value(i, 'push1')
    date=makeup.get_value(i, 'date')
    topic=makeup.get_value(i, 'topic')
    author=makeup.get_value(i, 'author')
    title=makeup.get_value(i, 'title')
    #split=makeup.get_value(i, 'split_title')
    
    alls=title, word, push, date, topic, author   
    final.append(alls)

final_df=pd.DataFrame(final)

#final_df.to_csv("mds_analysis4.csv", encoding="utf-8-sig")
       
'''
scatter plot
分享文中，唇膏、唇彩、眼妝各自的比例
'''
title=final_df.iloc[:,1]

answers=[]
for i in range(len(title)):
    if str('唇膏') in title[i]:
        ans=i,'唇膏'
        answers.append(ans)
    elif str('唇彩') in title[i]:
        ans=i,'唇彩'
        answers.append(ans)
    elif str('眼妝') in title[i]:
        ans=i,'眼妝'
        answers.append(ans)
    else:
        ans=i,'other'
        answers.append(ans)
            
        
import seaborn as sns
sns.set(style="whitegrid")   
import pandas as pd
import matplotlib.pyplot as plt

final_df=pd.read_csv("mds_analysis4_2.csv", encoding="utf-8")

sns.jointplot(x = "month", y = "push", data = final_df)
fig=sns.swarmplot(x = "month", y = "push", data = final_df, hue='type')
fig.figure.savefig("ask_share.png",dpi=400)

#%%
'''
word cloud
'''
rows=pd.read_csv('MDS_makeup_title1_1229new.csv', header=0 ,encoding='utf-8',dtype=str)

title=rows["title_1"]

all_title='' # combine all titles
for row in range(len(title)):
    try:        
        each=title[row]
        all_title += each
    except:
        print('error')

#rows["title_1"] = rows["title_1"].astype(str)

words = jieba.analyse.extract_tags(all_title,topK=100,withWeight=True,allowPOS=('ns', 'n', 'vn', 'v'))
    #print(words)

for item in words:
    keyword=item[0]
    count=item[1]

words_df=pd.DataFrame(words)
words_df[1]=words_df[1] * 1000

#words_df.to_csv('text for wordcloud_1229new.csv', encoding='utf-8-sig')


from wordcloud import WordCloud
import matplotlib.pyplot as plt
from wordcloud import WordCloud,ImageColorGenerator

with open('text for wordcloud.csv', "r",encoding="utf-8") as f:
    words_df = f.read()

font = r'msjh.ttc'

wc = WordCloud(collocations=False, font_path = font, background_color="white", width=1800, height=1800, margin=2, prefer_horizontal=1).generate(words_df)

plt.imshow(wc)
plt.axis("off")
plt.show()

wc.to_file('wordcloud_1229_1.png')  

#%%    
'''
=============================================================================
TF-IDF
https://blog.csdn.net/bozhanggu2239/article/details/80157305
'''
import jieba.analyse

keywords_title= jieba.analyse.extract_tags(count_title, topK=50)
#keywords_content= jieba.analyse.extract_tags(all_content, topK=20, withWeight=True, allowPOS=('n','nr','ns'))

#for item in keywords_title:
#    print(item[0],item[1])

#%%
'''
=============================================================================
associative rule (apyori)
'''
from apyori import apriori
def apriori_result(data):
    #association_rules = apriori(data, min_support=0, min_confidence=0, min_lift=3, max_length=2) 

    association_rules = apriori(data, min_support=0.9, min_confidence=0.6) 
    #association_results = list(association_rules)
        
    results=[]
    for item in association_rules:    
       pair = item[0]   
       #print(pair)
       items = [x for x in pair]
       print(items)
       print(item[2][0][2])
       print('=========')
       
       try:
           rule1, rule2=items[0], items[1]
           support=str(item[1])
           confidence=str(item[2][0][2])
           lift=str(item[2][0][3])
           
           result=rule1, rule2, support, confidence, lift
           results.append(result)
       except:
           print("error")
       
       print("Rule: " + items[0] + " -> " + items[1])
       print("Support: " + str(item[1]))
       print("Confidence: " + str(item[2][0][2]))
       print("Lift: " + str(item[2][0][3]))
       print("=====================================")
       
    return results       

data=content_result
test=apriori_result(data)