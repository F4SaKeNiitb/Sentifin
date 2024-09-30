import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import string
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import re

data=pd.read_excel('Input.xlsx')

def remove_characters_after_pipe(text):
    if '|' in text:
        return text.split('|')[0]  
    else:
        return text    
    
def stopwords_finder():
    files_data = []
    for file_name in os.listdir('StopWords'):
        file_path = os.path.join('StopWords', file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'r',encoding='latin-1') as file:
                for line in file.readlines():
                    files_data.append(remove_characters_after_pipe(line).strip().lower())
    return files_data

stpwords=stopwords_finder()

def pos():
    positive=[]
    with open('positive-words.txt', 'r',encoding='latin-1') as file:
                for line in file.readlines():
                    line=remove_characters_after_pipe(line).strip().lower()
                    if line not in stpwords:
                        positive.append(line)
    return positive

def neg():
    negative=[]
    with open('negative-words.txt', 'r',encoding='latin-1') as file:
                for line in file.readlines():
                    line=remove_characters_after_pipe(line).strip().lower()
                    if line not in stpwords:
                        negative.append(line)
    return negative

positive_words=pos()
negative_words=neg()

def create_files():
    for index,rows in data.iterrows():
        try:
            response=requests.get(rows['URL'])
            soup = BeautifulSoup(response.text, 'html.parser')
            content=soup.find('div',class_='td-post-content')
            for tag in content.find_all(['pre']):
                tag.extract()
            txt=''
            for i in soup.find('div',class_='td-post-content').strings :
                txt+=i
            with open('Articles/{}'.format(rows['URL_ID']), 'w', encoding='utf-8') as file:
                    file.write(txt)
        except :
            print('Error 404 for {}'.format(rows['URL']))

def count_syllables(word):
    vowels = 'aeiou'
    if word.endswith(('es', 'ed')):
        return sum(word.count(vowel) for vowel in vowels) - 1
    else:
        return sum(word.count(vowel) for vowel in vowels)
    
def sentimental_analysis():
    lst=[]
    for file_name in os.listdir('Articles'):
        file_path = os.path.join('Articles', file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'r',encoding='latin-1') as file:
                article=file.read()
                text=article.lower().translate(str.maketrans('','',string.punctuation))
                tokenized_words=nltk.word_tokenize(text)
                words=[]
                for i in tokenized_words:
                     if i not in stpwords:
                          words.append(i)
                positive=0
                negative=0
                for i in words:
                     if i in positive_words:
                          positive+=1
                     if i in negative_words:
                          negative+=1
                polarity=(positive-negative)/((positive+negative) + 0.000001)
                subjectivity=(positive+negative)/(len(words) + 0.000001)
                num_sentences=len(nltk.sent_tokenize(article))
                avg_sentence_length=len(tokenized_words)/num_sentences
                complex_words=[]
                for i in tokenized_words:
                     if count_syllables(i) >2:
                          complex_words.append(i)
                per_of_complex_words=len(complex_words)/len(tokenized_words)
                fog_index=0.4*(avg_sentence_length+per_of_complex_words)
                stopwords_english = stopwords.words('english')
                filtered_tokens = [word for word in tokenized_words if word not in stopwords_english]
                word_count=len(filtered_tokens)
                sum=0
                for i in tokenized_words:
                     sum+=len(i)
                avg_word_length=sum/len(tokenized_words)
                pattern = re.compile(r'\b(I|we|my|ours)\b', flags=re.IGNORECASE)
                matches = pattern.findall(text)
                pattern=re.compile(r'us|Us|uS')
                matches += pattern.findall(text)
                pronoun_count=len(matches)
                sum=0
                for i in tokenized_words:
                     sum+=count_syllables(i)
                sum/=len(tokenized_words)
                lst.append({'URL_ID':file_name,'URL':list(data[data['URL_ID']==file_name]['URL'])[0],'POSITIVE SCORE':positive,'NEGATIVE SCORE':negative,'POLARITY SCORE':polarity,'SUBJECTIVITY SCORE':subjectivity,'AVERAGE SENTENCE LENGTH':avg_sentence_length,'PERCENTAGE OF COMPLEX WORDS':per_of_complex_words,'FOG INDEX':fog_index,'AVERAGE NUMBER OF WORDS PER SENTENCE':avg_sentence_length,'COMPLEX WORD COUNT':len(complex_words),'WORD COUNT':word_count,'SYLLABLE PER WORD':sum,'PERSONAL PRONOUN':pronoun_count,'AVERAGE WORD LENGTH':avg_word_length})
    pd.DataFrame(lst).set_index('URL_ID').to_excel('Output.xlsx')

if __name__=='__main__':
     create_files()
     sentimental_analysis()