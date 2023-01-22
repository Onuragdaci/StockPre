from tvDatafeed import TvDatafeed, Interval
import plotly.graph_objects as go
from plotly.subplots import make_subplots 
import streamlit as st
import pandas as pd
from pandas.tseries.offsets import CustomBusinessHour , BDay
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly ,plot_forecast_component_plotly 
import ssl
from urllib import request
#python -m streamlit run app.py
def Hisse_Temel_Veriler():
    url1="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-1"
    context = ssl._create_unverified_context()
    response = request.urlopen(url1, context=context)
    url1 = response.read()

    df1 = pd.read_html(url1,decimal=',', thousands='.')                         #Tüm Hisselerin Tablolarını Aktar
    df1=df1[2]                                                                  #Tüm Hisselerin Özet Tablosu
    return df1

st.set_page_config(
    page_title="Hisse Temel Analiz",                                            #Sayfa Başlığı
    layout="wide",                                                              #Sayfa Formatı
    initial_sidebar_state="expanded")

lstAll=['1-Minute','3-Minute','5-Minute','15-Minute','30-Minute','45-Minute','1-Hour','2-Hour','3-Hour','4-Hour','1 Day']      #Görsel Zaman Aralığı
lst1=['1','3','5','15','30','45','1H','2H','3H','4H','1D']                                                             #Alt Zaman Aralığı
lst2=['1T','3T','5T','15T','30T','45T','1H','2H','3H','4H','D']                                                        #Alt Zaman Aralığı
with st.sidebar:
    Hisse_Temel=Hisse_Temel_Veriler()                                                                                  #Hisse Başlıkları
    st.header('Hisse Arama')                                                                                           #Yan Pencere Adı
    dropdown1 = st.selectbox('Hisse Adı',Hisse_Temel['Kod'])                                                           #Hisse Seçiminin Belirtilmesi
    dropdown2 = st.selectbox('Zaman Aralığı',lstAll,index=10)                                                          #Hisse Zaman Aralığının Belirtilmesi - Varsayılan 1 Saat    
    dropdown3 = st.slider('Data Sayısı', 0, 10000, 1000, 100)                                                          #İncelenecek Data Sayısının Belirtilmesi - Varsayılan 5000 Birim
    dropdown4 = st.slider('Gün Tahmini', 0, 20, 5, 5)                                                                  #Tahmin Edilecek Gün Sayısının Belirtilmesi - Varsayılan 5 Gün

tv = TvDatafeed()                                                                                                      #Data Çekmek için Trading View Uygulaması
index=lstAll.index(dropdown2)                                                                                          #Zaman Aralığı İndeks'inin Bulunması
data = tv.get_hist(symbol=dropdown1,exchange='BIST',interval=Interval(lst1[index]),n_bars=dropdown3)                   #TradingView dan Hisseye Sit Datanın İlgili Zaman Aralığında Çekilmesi
df_train=pd.DataFrame({"ds":data.index.values,"y":data['close'].values})                                               #Eğitim Kümesinin Oluşturulması

st.header(dropdown1+' Analizi')                                                                                        #Hisseye Ait Ana Sayfa Başlığının Oluşturulması
fig1= go.Figure()                                                                                                      #Plotly 1 Görselinin Oluşturulması
fig1.add_trace(go.Scatter(x=data.index,y=data["close"],name="Hisse Fiyatı"))                                           #Plotly 1 Hisse Fiyat Görselinin Oluşturulması
st.plotly_chart(fig1)                                                                                                  #Plotly 1 Görselinin Sayfaya Yüklenmesi

m=Prophet()                                                                                                            #Makine Öğrenme Algoritmasının Çağırılması
m.fit(df_train)                                                                                                        #Eğitim Kümesinin Fit Edilmesi
cbh = pd.tseries.offsets.CustomBusinessHour(n = 1, weekmask = 'Mon Tue Wed Thu Fri', start ='10:00', end="18:00")      #BIST Çalışma Günlerinin ve Saatlerinin Belirlenmesi

startdate=data.index[-1]                                                                                               #Tahminin Yapılacağı Başlangıç Tarihinin Belirlenmesi
enddate=(startdate+BDay(n=dropdown4+1)).replace(hour=18, second=00,minute=00)                                          #Tahminin Yapılacağı Son Gün ve Kapanış Saatinin Belirlenmesi

future1=pd.DataFrame({"ds":df_train["ds"].values})                                                                     #Geçmiş Tarihli Tahmin Kümesinin Oluşturulması
future2=pd.bdate_range(start=startdate,end=enddate,freq=lst2[index])                                                   #Gelecek Tarihli Tahmin Kümesinin DatetimeIndex Olarak Oluşturulması
future2=pd.DataFrame({"ds":future2})                                                                                   #Gelecek Tahmin Kümesinin OLuşturulması
future2=future2[pd.to_datetime(future2["ds"]).map(cbh.is_on_offset)]                                                   #Gelecek Tahmin Kümesinin Çalışma Saatlerine Göre Filtrelenmesi

if index==10:
    startdate=data.index[-1]                                                                                           #Tahminin Yapılacağı Başlangıç Tarihinin Belirlenmesi
    enddate=(startdate+BDay(n=dropdown4))                                                                              #Tahminin Yapılacağı Son Gün ve Kapanış Saatinin Belirlenmesi
    future2=pd.bdate_range(start=data.index[-1],end=enddate,freq='B').strftime("%Y-%m-%d 10:00:00")
    future2=pd.DataFrame({"ds":future2})
futureAll=pd.concat([future1,future2],axis=0,ignore_index=True)                                                        #Geçmiş ve Gelecek Tahmin Kümelerinin Birleştirilmesi
forecast=m.predict(futureAll)                                                                                          #Tahminin Yapılması
st.write("Tahmin Grafikleri")                                                                                          #Sayfaya Tahmin Grafikleri Başlığının Yazılması
fig2=plot_plotly(m,forecast)                                                                                           #Plotly 2 Görselinin Oluşturulması
st.plotly_chart(fig2)                                                                                                  #Sayfaya Tahmin Grafiklerinin Yüklenmesi

st.write("Tahmin Bileşenleri")                                                                                         #Sayfaya Tahmin Bileşenleri Başlığının Yazılması
fig3=plot_components_plotly(m, forecast,figsize=(1600, 300))                                                           #Plotly 3 Görselinin Oluşturulması
st.write(fig3)                                                                                                         #Sayfaya Tahmin Bileşenlerinin Yüklenmesi                                 
