import pandas as pd 
import numpy as np 
import seaborn as sns
import re
import matplotlib.pyplot as plt
import difflib


def preprocess(x) :
    global df, df_user_words, df_monthly_analyze, df_time_analyze
    f=open(x, 'r',encoding='utf-8')
    data = f.read()
    chats = [c.strip() for c in re.split(r'(?=\[)', data) if c.strip()]
    df = pd.DataFrame(chats, columns=['chat'])
    df[['Date_Time','text']]=df['chat'].str.split('~',n=1,expand=True)
    df['Date_Time']=df['Date_Time'].str.strip()
    df=df.drop(['chat'],axis=1)
    df['text']=df['text'].str.strip()
    df=df.drop(df.index[:5]).reset_index(drop=True)
    pattern = 'joined using a group link|changed the group name|This message was deleted|created the username|was added|Waiting for this message'
    df=df[~df['text'].str.contains(pattern,na=False)].reset_index(drop=True)
    df=df.dropna().reset_index(drop=True)
    df[['Date', 'Time']] = df['Date_Time'].str.split(',', n=1, expand=True)
    df['Date'] = df['Date'].str.replace('[', '', regex=False).str.strip()
    df['Time'] = df['Time'].str.replace(']', '', regex=False).str.strip()
    df=df.drop(['Date_Time'],axis=1)
    df = df.dropna().reset_index(drop=True)
    df[['time_hour','time_min','time_dust']]=df['Time'].str.split(':',expand=True)
    df['time_dust']=df['time_dust'].str.extract(r'(AM|PM)')
    df['time_hour']=df['time_hour'].astype(float)
    df['time_min']=df['time_min'].astype(float)
    df['Time_']=(df['time_hour']+df['time_min']/60).round(2)
    df=df.drop(['Time','time_hour','time_min'],axis=1)
    df.loc[((df['time_dust']== 'PM') & (df['Time_']<12.00)),'Time_']+=12.0
    df['Time_']=df['Time_'].astype(int)
    df=df.drop(['time_dust'],axis=1)
    df[['Day','Month','Year']]=df['Date'].str.split('/',n=False,expand=True)
    df=df.drop(['Date'],axis=1)
    n=df['Year'].mode()[0]
    df=df[df['Year']==n]
    df[['user','text']]=df['text'].str.split(':',n=1,expand=True)
    df['text'].replace('\n',' ')
    df=df.dropna().reset_index(drop=True)
    df['word_count']=df['text'].str.split().str.len()
    month_map = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    df['Month'] = df['Month'].astype(int).map(month_map)

    #OVERALL
    df_user_words=df.groupby('user')['word_count'].sum().sort_values(ascending=False).reset_index()
    df_monthly_analyze=df.groupby('Month')['word_count'].sum().sort_values(ascending=False).reset_index()
    df_time_analyze=df.groupby('Time_')['word_count'].sum().sort_values(ascending=False).reset_index()

    #INDIVIDUAL
    dfi=df[df['user']=='Mohammad Ibrahim Khalil']
    dfi_monthly_analyze=dfi.groupby('Month')['word_count'].sum().sort_values(ascending=False).reset_index()
    dfi_time_analyze=dfi.groupby('Time_')['word_count'].sum().sort_values(ascending=False).reset_index()
    daily_word_count = dfi.groupby(['Month', 'Day'])['word_count'].sum().reset_index()
    pivot_table = daily_word_count.pivot(index='Month',columns='Day',values='word_count').fillna(0)
    
    





def individual(x) :
    users = df['user'].unique()
    matches = [u for u in users if x.lower() in u.lower()] or difflib.get_close_matches(x, users, n=1, cutoff=0.1)
    x = matches[0]
    dfi = df[df['user'] == x]
    dfi_monthly_analyze = dfi.groupby('Month')['word_count'].sum().sort_values(ascending=False).reset_index()
    dfi_time_analyze = dfi.groupby('Time_')['word_count'].sum().sort_values(ascending=False).reset_index()
    daily_word_count = dfi.groupby(['Month', 'Day'])['word_count'].sum().reset_index()
    pivot_table = daily_word_count.pivot(index='Month', columns='Day', values='word_count').fillna(0)

  
    fig = plt.figure(figsize=(14, 11))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.2])

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])

    sns.barplot(data=dfi_monthly_analyze, x='Month', y='word_count', ax=ax1, palette='mako')
    ax1.set_title("Monthly Word Count", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Total Words")


    sns.lineplot(data=dfi_time_analyze.sort_values(by='Time_'), x='Time_', y='word_count', ax=ax2, marker='o', color='crimson')
    ax2.set_title("Word Count by Time of Day", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Time (24-Hour Decimal)")
    ax2.set_ylabel("Total Words")

    sns.heatmap(pivot_table, annot=True, fmt=".0f", linewidths=0.5, cmap='Blues', ax=ax3)
    ax3.set_title("Heatmap of Word Count by Day and Month", fontsize=12, fontweight='bold')
    ax3.set_xlabel("Day of Month")
    ax3.set_ylabel("Month")

    plt.tight_layout()
    plt.show()



def overall() :

    n = int(df_user_words.shape[0] / 3) if df_user_words.shape[0] > 10 else df_user_words.shape[0]
    sns.set_theme(style="whitegrid")


    fig, axes = plt.subplots(3, 1, figsize=(10, 15))

    sns.barplot(
        data=df_user_words.head(n), 
        x='word_count', 
        y='user', 
        ax=axes[0], 
        palette='Blues_r',
        hue='user',
        legend=False
    )
    axes[0].set_title('Top  Users by Word Count', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Total Words')
    axes[0].set_ylabel('User')

    sns.barplot(
        data=df_monthly_analyze, 
        x='Month', 
        y='word_count', 
        ax=axes[1], 
        palette='crest',
        hue='Month',
        legend=False
    )
    axes[1].set_title('Total Words by Month', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Month')
    axes[1].set_ylabel('Total Words')

    sns.lineplot(
        data=df_time_analyze.sort_values(by='Time_'), 
        x='Time_', 
        y='word_count', 
        ax=axes[2], 
        marker='o', 
        color='teal'
    )
    axes[2].set_title('Word Activity Throughout the Day (24-Hour Decimal)', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Time (Hour of the Day)')
    axes[2].set_ylabel('Total Words')

    plt.tight_layout()
    plt.show()

