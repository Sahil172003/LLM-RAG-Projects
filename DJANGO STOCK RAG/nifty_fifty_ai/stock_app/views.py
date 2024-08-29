from django.shortcuts import render, redirect
from django.http import JsonResponse
import requests
import csv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpld3
from mpld3 import plugins
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import urllib.parse
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_anthropic import ChatAnthropic
from langchain.schema import SystemMessage, HumanMessage

nifty_fifty_urls = {
    "ADANIENT": {"url": "https://www.bseindia.com/stock-share-price/adani-enterprises-ltd/ADANIENT/512599/", 'name': 'Adani Enterprises', 'symbol': 'ADANIENT.BSE'},
    "HDFCBANK": {"url": "https://www.bseindia.com/stock-share-price/hdfc-bank-ltd/HDFCBANK/500180/", 'name': 'HDFC Bank', 'symbol': 'HDFCBANK.BSE'},
    "RELIANCE": {"url": "https://www.bseindia.com/stock-share-price/reliance-industries-ltd/RELIANCE/500325/", 'name': 'Reliance Industries', 'symbol': 'RELIANCE.BSE'},
    "ASIANPAINT": {"url": "https://www.bseindia.com/stock-share-price/asian-paints-ltd/ASIANPAINT/500820/", 'name': 'Asian Paints', 'symbol': 'ASIANPAINT.BSE'},
    "AXISBANK": {"url": "https://www.bseindia.com/stock-share-price/axis-bank-ltd/AXISBANK/532215/", 'name': 'Axis Bank', 'symbol': 'AXISBANK.BSE'},
    "BAJAJ-AUTO": {"url": "https://www.bseindia.com/stock-share-price/bajaj-auto-ltd/BAJAJ-AUTO/532977/", 'name': 'Bajaj Auto', 'symbol': 'BAJAJ-AUTO.BSE'},
    "BAJAJFINSV": {"url": "https://www.bseindia.com/stock-share-price/bajaj-finserv-ltd/BAJAJFINSV/532978/", 'name': 'Bajaj Finserv', 'symbol': 'BAJAJFINSV.BSE'},
    "BAJFINANCE": {"url": "https://www.bseindia.com/stock-share-price/bajaj-finance-ltd/BAJFINANCE/500034/", 'name': 'Bajaj Finance', 'symbol': 'BAJFINANCE.BSE'},
    "BHARTIARTL": {"url": "https://www.bseindia.com/stock-share-price/bharti-airtel-ltd/BHARTIARTL/532454/", 'name': 'Bharti Airtel', 'symbol': 'BHARTIARTL.BSE'},
    "BPCL": {"url": "https://www.bseindia.com/stock-share-price/bharat-petroleum-corporation-ltd/BPCL/500547/", 'name': 'Bharat Petroleum', 'symbol': 'BPCL.BSE'},
    "BRITANNIA": {"url": "https://www.bseindia.com/stock-share-price/britannia-industries-ltd/BRITANNIA/500825/", 'name': 'Britannia Industries', 'symbol': 'BRITANNIA.BSE'},
    "CIPLA": {"url": "https://www.bseindia.com/stock-share-price/cipla-ltd/CIPLA/500087/", 'name': 'Cipla', 'symbol': 'CIPLA.BSE'},
    "COALINDIA": {"url": "https://www.bseindia.com/stock-share-price/coal-india-ltd/COALINDIA/533278/", 'name': 'Coal India', 'symbol': 'COALINDIA.BSE'},
    "DIVISLAB": {"url": "https://www.bseindia.com/stock-share-price/divis-laboratories-ltd/DIVISLAB/532488/", 'name': 'Divi’s Laboratories', 'symbol': 'DIVISLAB.BSE'},
    "DRREDDY": {"url": "https://www.bseindia.com/stock-share-price/dr-reddy-s-laboratories-ltd/DRREDDY/500124/", 'name': 'Dr. Reddy\'s Laboratories', 'symbol': 'DRREDDY.BSE'},
    "EICHERMOT": {"url": "https://www.bseindia.com/stock-share-price/eicher-motors-ltd/EICHERMOT/505200/", 'name': 'Eicher Motors', 'symbol': 'EICHERMOT.BSE'},
    "GRASIM": {"url": "https://www.bseindia.com/stock-share-price/grasim-industries-ltd/GRASIM/500300/", 'name': 'Grasim Industries', 'symbol': 'GRASIM.BSE'},
    "HCLTECH": {"url": "https://www.bseindia.com/stock-share-price/hcl-technologies-ltd/HCLTECH/532281/", 'name': 'HCL Technologies', 'symbol': 'HCLTECH.BSE'},
    "HDFC": {"url": "https://www.bseindia.com/stock-share-price/housing-development-finance-corporation-ltd/HDFC/500010/", 'name': 'Housing Development Finance Corporation', 'symbol': 'HDFC.BSE'},
    "HEROMOTOCO": {"url": "https://www.bseindia.com/stock-share-price/hero-motocorp-ltd/HEROMOTOCO/500182/", 'name': 'Hero MotoCorp', 'symbol': 'HEROMOTOCO.BSE'},
    "HINDALCO": {"url": "https://www.bseindia.com/stock-share-price/hindalco-industries-ltd/HINDALCO/500440/", 'name': 'Hindalco Industries', 'symbol': 'HINDALCO.BSE'},
    "HINDUNILVR": {"url": "https://www.bseindia.com/stock-share-price/hindustan-unilever-ltd/HINDUNILVR/500696/", 'name': 'Hindustan Unilever', 'symbol': 'HINDUNILVR.BSE'},
    "ICICIBANK": {"url": "https://www.bseindia.com/stock-share-price/icici-bank-ltd/ICICIBANK/532174/", 'name': 'ICICI Bank', 'symbol': 'ICICIBANK.BSE'},
    "INDUSINDBK": {"url": "https://www.bseindia.com/stock-share-price/indusind-bank-ltd/INDUSINDBK/532187/", 'name': 'IndusInd Bank', 'symbol': 'INDUSINDBK.BSE'},
    "INFY": {"url": "https://www.bseindia.com/stock-share-price/infosys-ltd/INFY/500209/", 'name': 'Infosys', 'symbol': 'INFY.BSE'},
    "ITC": {"url": "https://www.bseindia.com/stock-share-price/itc-ltd/ITC/500875/", 'name': 'ITC', 'symbol': 'ITC.BSE'},
    "JSWSTEEL": {"url": "https://www.bseindia.com/stock-share-price/jsw-steel-ltd/JSWSTEEL/500228/", 'name': 'JSW Steel', 'symbol': 'JSWSTEEL.BSE'},
    "KOTAKBANK": {"url": "https://www.bseindia.com/stock-share-price/kotak-mahindra-bank-ltd/KOTAKBANK/500247/", 'name': 'Kotak Mahindra Bank', 'symbol': 'KOTAKBANK.BSE'},
    "LT": {"url": "https://www.bseindia.com/stock-share-price/larsen---toubro-ltd/LT/500510/", 'name': 'Larsen & Toubro', 'symbol': 'LT.BSE'},
    "M&M": {"url": "https://www.bseindia.com/stock-share-price/mahindra---mahindra-ltd/M%26M/500520/", 'name': 'Mahindra & Mahindra', 'symbol': 'M&M.BSE'},
    "MARUTI": {"url": "https://www.bseindia.com/stock-share-price/maruti-suzuki-india-ltd/MARUTI/532500/", 'name': 'Maruti Suzuki', 'symbol': 'MARUTI.BSE'},
    "NESTLEIND": {"url": "https://www.bseindia.com/stock-share-price/nestle-india-ltd/NESTLEIND/500790/", 'name': 'Nestlé India', 'symbol': 'NESTLEIND.BSE'},
    "NTPC": {"url": "https://www.bseindia.com/stock-share-price/ntpc-ltd/NTPC/532555/", 'name': 'NTPC', 'symbol': 'NTPC.BSE'},
    "ONGC": {"url": "https://www.bseindia.com/stock-share-price/oil---natural-gas-corporation-ltd/ONGC/500312/", 'name': 'Oil & Natural Gas Corporation', 'symbol': 'ONGC.BSE'},
    "POWERGRID": {"url": "https://www.bseindia.com/stock-share-price/power-grid-corporation-of-india-ltd/POWERGRID/532898/", 'name': 'Power Grid Corporation', 'symbol': 'POWERGRID.BSE'},
    "SBILIFE": {"url": "https://www.bseindia.com/stock-share-price/sbi-life-insurance-company-ltd/SBILIFE/540719/", 'name': 'SBI Life Insurance', 'symbol': 'SBILIFE.BSE'},
    "SBIN": {"url": "https://www.bseindia.com/stock-share-price/state-bank-of-india/SBIN/500112/", 'name': 'State Bank of India', 'symbol': 'SBIN.BSE'},
    "SUNPHARMA": {"url": "https://www.bseindia.com/stock-share-price/sun-pharmaceutical-industries-ltd/SUNPHARMA/524715/", 'name': 'Sun Pharmaceutical Industries', 'symbol': 'SUNPHARMA.BSE'},
    "TATACONSUM": {"url": "https://www.bseindia.com/stock-share-price/tata-consumer-products-ltd/TATACONSUM/500800/", 'name': 'Tata Consumer Products', 'symbol': 'TATACONSUM.BSE'},
    "TATAMOTORS": {"url": "https://www.bseindia.com/stock-share-price/tata-motors-ltd/TATAMOTORS/500570/", 'name': 'Tata Motors', 'symbol': 'TATAMOTORS.BSE'},
    "TATASTEEL": {"url": "https://www.bseindia.com/stock-share-price/tata-steel-ltd/TATASTEEL/500470/", 'name': 'Tata Steel', 'symbol': 'TATASTEEL.BSE'},
    "TCS": {"url": "https://www.bseindia.com/stock-share-price/tata-consultancy-services-ltd/TCS/532540/", 'name': 'Tata Consultancy Services', 'symbol': 'TCS.BSE'},
    "TECHM": {"url": "https://www.bseindia.com/stock-share-price/tech-mahindra-ltd/TECHM/532755/", 'name': 'Tech Mahindra', 'symbol': 'TECHM.BSE'},
    "TITAN": {"url": "https://www.bseindia.com/stock-share-price/titan-company-ltd/TITAN/500114/", 'name': 'Titan Company', 'symbol': 'TITAN.BSE'},
    "ULTRACEMCO": {"url": "https://www.bseindia.com/stock-share-price/ultratech-cement-ltd/ULTRACEMCO/532538/", 'name': 'UltraTech Cement', 'symbol': 'ULTRACEMCO.BSE'},
    "UPL": {"url": "https://www.bseindia.com/stock-share-price/upl-ltd/UPL/512070/", 'name': 'UPL', 'symbol': 'UPL.BSE'},
    "WIPRO": {"url": "https://www.bseindia.com/stock-share-price/wipro-ltd/WIPRO/507685/", 'name': 'Wipro', 'symbol': 'WIPRO.BSE'},
}


def find_company_details(company_name):
    for key, value in nifty_fifty_urls.items():
        if value['name'].lower() == company_name.lower():
            return value
    return None

def get_stock_data(symbol, api_key):
    base_url = "https://www.alphavantage.co/query"
    function = "TIME_SERIES_DAILY"
    
    params = {
        "function": function,
        "symbol": symbol,
        "outputsize": "full",
        "apikey": api_key,
        "datatype": "csv"
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error fetching data: {response.status_code}")

def filter_last_3_years(csv_data):
    lines = csv_data.strip().split('\n')
    reader = csv.reader(lines)
    headers = next(reader)
    
    three_years_ago = datetime.now() - relativedelta(years=3)
    
    filtered_data = [headers]
    for row in reader:
        date = datetime.strptime(row[0], "%Y-%m-%d")
        if date >= three_years_ago:
            filtered_data.append(row)
    
    return filtered_data

def get_share_price(url, company):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        
        price_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "idcrval"))
        )
        
        share_price = price_element.text
        return share_price
    
    except Exception as e:
        print(f"An error occurred while fetching {company}'s share price: {e}")
        return None
    
    finally:
        driver.quit()

def get_google_news_links(query, num_results=3):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}&tbm=nws"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch results. Status code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    links = []
    articles = soup.find_all('div', class_='SoaBEf')
    
    for article in articles:
        link_element = article.find('a')
        title_element = article.find('div', class_='n0jPhd')
        source_element = article.find('div', class_='NUnG9d')
        
        if link_element and title_element:
            link = link_element.get('href', '')
            title = title_element.get_text(strip=True)
            source = source_element.get_text(strip=True) if source_element else "Unknown Source"
            
            links.append({
                'title': title,
                'source': source,
                'link': link
            })
        
        if len(links) >= num_results:
            break
    
    return links

def news_summary(url, api_key):
    loader = WebBaseLoader(url)
    documents = loader.load()
    
    text_splitter = CharacterTextSplitter(chunk_size=6000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    
    llm = ChatAnthropic(model="claude-3-sonnet-20240229", anthropic_api_key=api_key)
    
    chain = load_summarize_chain(llm, chain_type="stuff")
    summary = chain.invoke(texts)
    summary = summary['output_text']
    
    messages = [
        SystemMessage(content="Summarize the following in 60 words and also tell me the sentiment."),
        HumanMessage(content=summary)
    ]
    
    final_summary = llm.invoke(messages)
    return final_summary.content

def home(request):
    if request.method == 'POST':
        api_key = request.POST.get('api_key')
        request.session['api_key'] = api_key
        return redirect('company_input')
    return render(request, 'home.html')

def company_input(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        company_details = find_company_details(company_name)
        if company_details:
            request.session['company_details'] = company_details
            return redirect('company_data')
        else:
            error = "Invalid company name. Try again."
            return render(request, 'company_input.html', {'error': error})
    return render(request, 'company_input.html')

def company_data(request):
    company_details = request.session.get('company_details')
    api_key = request.session.get('api_key')

    if not company_details or not api_key:
        return redirect('home')

    # Fetch and process stock data
    csv_data = get_stock_data(company_details['symbol'], api_key)
    filtered_data = filter_last_3_years(csv_data)
    
    # Save data to CSV file
    SAVE_FOLDER = "company_stocks"
    os.makedirs(SAVE_FOLDER, exist_ok=True)
    output_filename = f"{company_details['symbol']}_last_3_years.csv"
    full_path = os.path.join(SAVE_FOLDER, output_filename)
    
    with open(full_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(filtered_data)

    # Create graph
    df = pd.read_csv(full_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[['timestamp', 'close']]
    df = df.iloc[::-1]

    fig, ax = plt.subplots(figsize=(8, 4))
    line, = ax.plot(df['timestamp'], df['close'], '-o', label='Close Price', markersize=2)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
    plt.setp(ax.get_xticklabels(), rotation=90, ha='center')

    tooltip = plugins.PointHTMLTooltip(line, 
                                       labels=[f'Date: {d.strftime("%Y-%m-%d")}<br>Close: {c:.2f}' 
                                               for d, c in zip(df['timestamp'], df['close'])],
                                       voffset=10, hoffset=10)
    plugins.connect(fig, tooltip)
    plt.title('Stock Close Prices')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    plt.tight_layout()

    # Get current share price
    share_price = get_share_price(company_details['url'], company_details['name'])

    return render(request, 'company_data.html', {
        'company_details': company_details,
        'graph': mpld3.fig_to_html(fig),
        'share_price': share_price
    })

def news(request):
    company_details = request.session.get('company_details')
    api_key = request.session.get('api_key')
    if not company_details or not api_key:
        return redirect('home')

    # Fetch news and generate summaries
    news_links = get_google_news_links(company_details['name'])
    news_data = []
    for news_item in news_links:
        summary = news_summary(news_item['link'], api_key)
        news_data.append({
            'title': news_item['title'],
            'source': news_item['source'],
            'link': news_item['link'],
            'summary': summary
        })

    return render(request, 'news.html', {'news_data': news_data})