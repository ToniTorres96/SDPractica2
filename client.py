# importem llibreries
import tweepy
import csv
from textblob import TextBlob
from wordcloud import WordCloud
import pandas as pd
import numpy as np
import re
import string
import matplotlib.pyplot as plt
from sentiment_analysis_spanish import sentiment_analysis
import lithops
from lithops import Storage
import unicodedata
storage=Storage()

plt.style.use('fivethirtyeight')

# Insertamos la información de usuario (Login)

consumerKey = ''
consumerSecret = ''
accessToken = ''
accessTokenSecret = ''



def sentiment(numTweets):
    llista=[]   #llista on emmagatzemem el resultat del sentiment analysis
    sentiment = sentiment_analysis.SentimentAnalysisSpanish()
    cont=0
    while(cont<int(numTweets)): #iterem entre tots els tweets
        name="tweet"+str(cont)+".txt"
        text=storage.get_object(bucket='practica2sd', key=name)
        if(text[0:4]!="RT @" ): #eliminem retweets
            result=sentiment.sentiment(text)    #calculem sentiment analysis

            if(result>=0.65):
                llista.append("El sentimiento es positivo con un valor de: "+str(result)+"\n") #afegim a la llista
            elif(result<=0.35):
                llista.append("El sentimiento es negativo con un valor de: "+str(result)+"\n")
            else:
                llista.append("El sentimiento es neutro/indeterminado con un valor de: "+str(result)+"\n")
        cont+=1
    return(llista)

def dataCrawler(totalTweets, hashtag):
    # creem authentification object
    autenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
    autenticate.set_access_token(accessToken, accessTokenSecret)
    # creem API object
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(autenticate, wait_on_rate_limit = True)

    fullHashtag='#'+hashtag # per buscar
    printable = set(string.printable) #ens ajuda a esborrar caracters no imprimibles dels tweets(emojis, altres)
 
    cont=0
    for tweet in tweepy.Cursor(api.search,q=fullHashtag,count=int(totalTweets),
                            lang="es",
                            since="2021-01-01").items(int(totalTweets)):
        aux=str(tweet.text)
        nfkd_form = unicodedata.normalize('NFKD', aux)
        aux = nfkd_form.encode('ASCII', 'ignore')
        #''.join(filter(lambda x: x in printable, aux))        
        storage.put_object(bucket='practica2sd', key="tweet"+str(cont)+".txt", body=aux) #pujem el tweet al COS
        cont=cont+1 


if __name__ == "__main__":

    print("Sobre que hashtag quiere hacer el sentiment analysis(no ponga '#')?")
    hashtag = input()

    print("Cual es el total de tweets que se quiere analizar?")
    numTweets = input()

    fexec = lithops.FunctionExecutor()

    fexec.call_async(dataCrawler, (numTweets, hashtag))#
    
    fexec.call_async(sentiment, numTweets)
    result=fexec.get_result() #obtenim la llista resultant
    for x in range(len(result)):
        print (result[x])
