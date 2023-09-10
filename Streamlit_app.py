from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import locale
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import ssl
from urllib import request
import streamlit as st
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
import warnings
warnings.filterwarnings("ignore")
from webdriver_manager.chrome import ChromeDriverManager

def Hisse_Temel_Veriler():
    url1="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-1"
    context = ssl._create_unverified_context()
    response = request.urlopen(url1, context=context)
    url1 = response.read()
    df = pd.read_html(url1,decimal=',', thousands='.')                         #Tüm Hisselerin Tablolarını Aktar
    df1=df[2]                                                                  #Tüm Hisselerin Özet Tablosu
    df2=df[6]
    df2['Sektör']=df1[['Sektör']]
    return df2

st.set_page_config(
    page_title="Hisse Temel Analiz",
    layout="wide",
    initial_sidebar_state="expanded")
    
with st.sidebar:
    Hisse_Ozet=Hisse_Temel_Veriler()
    st.header('Hisse Arama')
    Hisse_Adı = st.selectbox('Hisse Adı',Hisse_Ozet['Kod'])
    Hisse_Adı=[Hisse_Adı]

options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--headless')
options.add_argument('--log-level=3')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version='116.0.5845.96').install()), options=options)
  
def Hisse_Temel_Veriler(Hisse):
    driver.get('https://analizim.halkyatirim.com.tr/Financial/ScoreCardDetail?hisseKod='+Hisse)
    driver.implicitly_wait(20)

    BlcDnm=driver.find_element(By.XPATH,'/html/body/div[2]/div[2]/div/div[1]/div[2]/div[2]/div/span[2]/strong').text            #Hissenin Bilanco Dönemi
    SnFyt=driver.find_element(By.XPATH,'/html/body/div[2]/div[2]/div/div[1]/div[2]/div[3]/div[1]/div/div[2]/div[1]').text
    SnFyt=float(SnFyt)

    soup = BeautifulSoup(driver.page_source,"lxml")
    PzrEnd=pd.read_html(str(soup.find(id='pazar-endeskleri')))[0]
    FytPrf=pd.read_html(str(soup.find(id='fiyat-performansi')))[0]
    PysDgr=pd.read_html(str(soup.find(id='piyasa-degeri')))[0]
    TknVrl=pd.read_html(str(soup.find(id='teknik-veriler')))[0]
    TmlVrl=pd.read_html(str(soup.find(id='temel-veri-analizleri')))[0]
    FytOzt=pd.read_html(str(soup.find(id='fiyat-ozeti')))[0]

    Finansallar=pd.read_html(str(soup.find("table",id="TBLFINANSALVERİLER1")))               #Finansallar
    Karlılık=pd.read_html(str(soup.find("table",id="TBLFINANSALVERİLER2")))                  #Karlılık
    Carpanlar=pd.read_html(str(soup.find("table",id="TBLFINANSALVERİLER3")) )                #Carpanlar

    Finansallar=Finansallar[0].iloc[:-2]
    Karlılık=Karlılık[0].iloc[:-2]
    Carpanlar=Carpanlar[0].iloc[:-2]

    PysDgr=float(PysDgr.iat[0,1])
    OdnSrm=float(PzrEnd.iat[2,1][:-3].replace(',', ''))/1000000
    OzSrm=float(Finansallar.iat[0,12])
    Y_NetKar=float(Finansallar.iat[0,8])
    Y_NetSat=float(Finansallar.iat[0,2])
    NtBrc=float(Finansallar.iat[0,10])

    #Cari Piyasa Çarpanlarının Hesaplanması
    CariFK=TmlVrl.iat[0,1]
    CariPDDD=TmlVrl.iat[1,1]
    CariFDFV=TmlVrl.iat[2,1]
    CariFDST=round((PysDgr+NtBrc)/(Y_NetSat+0.001),2)

    #Tarihsel Ortalamaların Hesaplanması
    TarFK=round(np.nanmean(Carpanlar['F/K'].to_numpy(dtype='float')),2)
    TarPDDD=round(np.nanmean(Carpanlar['PD/DD'].to_numpy(dtype='float')),2)
    TarFDFV=round(np.nanmean(Carpanlar['FD/FAVÖK'].to_numpy(dtype='float')),2)
    TarFDST=round(np.nanmean(Carpanlar['FD/Satışlar'].to_numpy(dtype='float')),2)

    #Bist Ortalamalarının Hesaplanması
    BstVri = pd.read_html('https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-1',decimal=',', thousands='.')
    BstVri1=BstVri[6]
    BstVri1.replace('A/D', np.nan, inplace=True)

    BstFK=round(np.nanmean(BstVri1['F/K'].to_numpy(dtype='float')),2)
    BstPDDD=round(np.nanmean(BstVri1['PD/DD'].to_numpy(dtype='float')),2)
    BstFDFV=round(np.nanmean(BstVri1['FD/FAVÖK'].to_numpy(dtype='float')),2)
    BstFDST=round(np.nanmean(BstVri1['FD/Satışlar'].to_numpy(dtype='float')),2)

    #Sektör Ortalamalarının Hesaplanması
    BstVri2=BstVri[2]
    Sktr=BstVri2.loc[BstVri2['Kod'] == Hisse, 'Sektör'].iloc[0]
    SktrHsslr=BstVri1[BstVri2['Sektör'] == Sktr]

    SktrFK=round(np.nanmean(SktrHsslr['F/K'].to_numpy(dtype='float')),2)
    SktrPDDD=round(np.nanmean(SktrHsslr['PD/DD'].to_numpy(dtype='float')),2)
    SktrFDFV=round(np.nanmean(SktrHsslr['FD/FAVÖK'].to_numpy(dtype='float')),2)
    SktrFDST=round(np.nanmean(SktrHsslr['FD/Satışlar'].to_numpy(dtype='float')),2)

    #Geçmişe Göre Gelecek Değerler
    GlckFk=round(PysDgr/(Y_NetKar+0.0001),2)
    PotPD=round(Y_NetKar*7+OzSrm*0.5,2)
    NKarMarj=round(Y_NetKar/(Y_NetSat+0.0001),2)
    PD_NS=round(PysDgr/(Y_NetSat+0.0001),2)

    #tahmini Gelecek Değerler
    C_NetKar=Finansallar['Net Kâr Çeyrek (Mln TL)'].to_numpy(dtype='float')                       #Çeyreklik Net Kâr Değerleri
    C_NetSat=Finansallar['Net Satışlar Çeyrek (Mln TL)'].to_numpy(dtype='float')                  #Çeyreklik Net Satışlar Değerleri

    Donem=BlcDnm[-2:]
    if Donem == '03':
        T_NetKar = C_NetKar[0]*4
        T_NetSat = C_NetSat[0]*4

    if Donem == '06':
        T_NetKar = (C_NetKar[0]+C_NetKar[1])*2
        T_NetSat = (C_NetSat[0]+C_NetSat[1])*2

    if Donem == '09':
        T_NetKar = (C_NetKar[0]+C_NetKar[1]+C_NetKar[2])*4/3
        T_NetSat = (C_NetSat[0]+C_NetSat[1]+C_NetSat[2])*4/3

    if Donem == '12':
        T_NetKar = (C_NetKar[0]+C_NetKar[1]+C_NetKar[2]+C_NetKar[3])
        T_NetSat = (C_NetSat[0]+C_NetSat[1]+C_NetSat[2]+C_NetSat[3])

    T_NetKar=round(T_NetKar,2)
    T_NetSat=round(T_NetSat,2)

    T_Fk=round(PysDgr/(T_NetKar+0.0001),2)
    T_PotPD=round(T_NetKar*7+OzSrm*0.5,2)
    T_NKarMarj=round(Y_NetKar/(T_NetSat+0.0001),2)
    T_PD_NS=round(PysDgr/(T_NetSat+0.0001),2)

    Basliklar_1=['Hisse Adı','Sektör','Dönem',
            'Piyasa Değeri','Ödenmiş Sermaye','Öz Sermaye',
            'Yıllık Kar','Yıllık Satış','Fiyat',
            'Cari F/K','Cari PD/DD','Cari FD/FAVÖK','Cari FD/SATIŞLAR',
            'Gelecek F/K','Potansiyel PD','Net Kar Marjı','PD/NS',
            'Tarihsel F/K','Tarihsel PD/DD','Tarihsel FD/FAVÖK','Tarihsel FD/SATIŞLAR',
            'Sektör F/K','Sektör PD/DD','Sektör FD/FAVÖK','Sektör FD/SATIŞLAR',
            'BIST F/K','BIST PD/DD','BIST FD/FAVÖK','BIST FD/SATIŞLAR']

    Basliklar_2=['Hisse Adı','Sektör','Dönem',
            'Piyasa Değeri','Ödenmiş Sermaye','Öz Sermaye',
            'Tahmini Yıllık Kar','Tahmini Yıllık Satış','Fiyat',
            'Cari F/K','Cari PD/DD','Cari FD/FAVÖK','Cari FD/SATIŞLAR',
            'Tahmini Gelecek F/K','Tahmini Potansiyel PD','Tahmini Net Kar Marjı','Tahmini PD/NS',
            'Tarihsel F/K','Tarihsel PD/DD','Tarihsel FD/FAVÖK','Tarihsel FD/SATIŞLAR',
            'Sektör F/K','Sektör PD/DD','Sektör FD/FAVÖK','Sektör FD/SATIŞLAR',
            'BIST F/K','BIST PD/DD','BIST FD/FAVÖK','BIST FD/SATIŞLAR']

    Temel_Veriler_1=[Hisse,Sktr,BlcDnm,
                   PysDgr,OdnSrm,OzSrm,
                   Y_NetKar,Y_NetSat,SnFyt,
                   CariFK,CariPDDD,CariFDFV,CariFDST,
                   GlckFk,PotPD,NKarMarj,PD_NS,
                   TarFK,TarPDDD,TarFDFV,TarFDST,
                   SktrFK,SktrPDDD,SktrFDFV,SktrFDST,
                   BstFK,BstPDDD,BstFDFV,BstFDST]
    Temel_Veriler_2=[Hisse,Sktr,BlcDnm,
                   PysDgr,OdnSrm,OzSrm,
                   T_NetKar,T_NetSat,SnFyt,
                   CariFK,CariPDDD,CariFDFV,CariFDST,
                   T_Fk,T_PotPD,T_NKarMarj,T_PD_NS,
                   TarFK,TarPDDD,TarFDFV,TarFDST,
                   SktrFK,SktrPDDD,SktrFDFV,SktrFDST,
                   BstFK,BstPDDD,BstFDFV,BstFDST]

    Temel_Veriler_1=pd.DataFrame([Temel_Veriler_1],columns=Basliklar_1)
    Temel_Veriler_2=pd.DataFrame([Temel_Veriler_2],columns=Basliklar_2)
    driver.quit()
    return Temel_Veriler_1 , Temel_Veriler_2

def Degerleme(Temel_Veriler_1,Temel_Veriler_2):
    Degerleme_1=Temel_Veriler_1
    Degerleme_2=Temel_Veriler_2
    #Model 1 = Hisse_Fiyatıx(Sektör_FK/Şirket_FK) ve Hisse_Fiyatıx(Sektör_PDDD/Şirket_PDDD) 'nin ortalaması
    Degerleme_1['Degerleme 1'] = (Degerleme_1['Fiyat']*(Degerleme_1['Sektör F/K']/Degerleme_1['Cari F/K'])+Degerleme_1['Fiyat']*(Degerleme_1['Sektör PD/DD']/Degerleme_1['Cari PD/DD']))/2
    Degerleme_1['Degerleme 1'] = Degerleme_1['Degerleme 1'].apply(lambda x: round(x, 2))

    Degerleme_2['Degerleme 1'] = (Degerleme_2['Fiyat']*(Degerleme_2['Sektör F/K']/Degerleme_2['Cari F/K'])+Degerleme_1['Fiyat']*(Degerleme_2['Sektör PD/DD']/Degerleme_2['Cari PD/DD']))/2
    Degerleme_2['Degerleme 1'] = Degerleme_2['Degerleme 1'].apply(lambda x: round(x, 2))

    #Model 2 = (Hisse Fiyatı/Şirket_FK)xSektör_FK ve (Hisse Fiyatı/Şirket_FK)xBist_FK 'nın ortalaması
    Degerleme_1['Degerleme 2'] = ((Degerleme_1['Fiyat']/Degerleme_1['Cari F/K'])*Degerleme_1['Sektör F/K']+(Degerleme_1['Fiyat']/Degerleme_1['Cari F/K'])*Degerleme_1['BIST F/K'])/2
    Degerleme_1['Degerleme 2'] = Degerleme_1['Degerleme 2'].apply(lambda x: round(x, 2))

    Degerleme_2['Degerleme 2'] = ((Degerleme_2['Fiyat']/Degerleme_2['Cari F/K'])*Degerleme_2['Sektör F/K']+(Degerleme_2['Fiyat']/Degerleme_2['Cari F/K'])*Degerleme_2['BIST F/K'])/2
    Degerleme_2['Degerleme 2'] = Degerleme_2['Degerleme 2'].apply(lambda x: round(x, 2))

    #Model 3 = Gelecek_FK=(Piyasa Değeri / Yıllıklandırılmış Net Kâr) olmak üzere  (Hisse Fiyatı/Gelecek FK)xBist_FK ve (Hisse Fiyatı/Gelecek FK)xSektör_FK 'nın ortalaması
    Degerleme_1['Degerleme 3'] = ((Degerleme_1['Fiyat']/Degerleme_1['Gelecek F/K'])*Degerleme_1['Sektör F/K']+(Degerleme_1['Fiyat']/Degerleme_1['Gelecek F/K'])*Degerleme_1['BIST F/K'])/2
    Degerleme_1['Degerleme 3'] = Degerleme_1['Degerleme 3'].apply(lambda x: round(x, 2))

    Degerleme_2['Degerleme 3'] = ((Degerleme_2['Fiyat']/Degerleme_2['Tahmini Gelecek F/K'])*Degerleme_2['Sektör F/K']+(Degerleme_2['Fiyat']/Degerleme_2['Tahmini Gelecek F/K'])*Degerleme_2['BIST F/K'])/2
    Degerleme_2['Degerleme 3'] = Degerleme_2['Degerleme 3'].apply(lambda x: round(x, 2))

    #Model 4 = Şirket Sermayesi Kadar Kâr Elde Ederse 10 TL değeri vardır.
    Degerleme_1['Degerleme 4'] = (Degerleme_1['Yıllık Kar']/Degerleme_1['Ödenmiş Sermaye'])*10
    Degerleme_1['Degerleme 4'] = Degerleme_1['Degerleme 4'].apply(lambda x: round(x, 2))

    Degerleme_2['Degerleme 4'] = (Degerleme_2['Tahmini Yıllık Kar']/Degerleme_2['Ödenmiş Sermaye'])*10
    Degerleme_2['Degerleme 4'] = Degerleme_2['Degerleme 4'].apply(lambda x: round(x, 2))

    #Model 5 = PD/DD Öz Sermayenin 10 Katı olmalı. (Öz Sermaye Kârlılığı x10/(PD/DD))xHisse_Fiyatı
    Degerleme_1['Degerleme 5'] = (10*(Degerleme_1['Yıllık Kar']/Degerleme_1['Öz Sermaye'])/Degerleme_1['Cari PD/DD'])*Degerleme_1['Fiyat']
    Degerleme_1['Degerleme 5'] = Degerleme_1['Degerleme 5'].apply(lambda x: round(x, 2))

    Degerleme_2['Degerleme 5'] = (10*(Degerleme_2['Tahmini Yıllık Kar']/Degerleme_2['Öz Sermaye'])/Degerleme_2['Cari PD/DD'])*Degerleme_2['Fiyat']
    Degerleme_2['Degerleme 5'] = Degerleme_2['Degerleme 5'].apply(lambda x: round(x, 2))

    #Model 6 = Potansiyel PD/Özsermaye
    Degerleme_1['Degerleme 6'] = Degerleme_1['Potansiyel PD']/Degerleme_1['Ödenmiş Sermaye']
    Degerleme_1['Degerleme 6'] = Degerleme_1['Degerleme 6'].apply(lambda x: round(x, 2))

    Degerleme_2['Degerleme 6'] = Degerleme_2['Tahmini Potansiyel PD']/Degerleme_2['Ödenmiş Sermaye']
    Degerleme_2['Degerleme 6'] = Degerleme_2['Degerleme 6'].apply(lambda x: round(x, 2))

    #Model 7 = 100*(Net Kar Marjı / PD_NS )*Hisse_Fiyatı
    Degerleme_1['Degerleme 7'] = 10*(Degerleme_1['Net Kar Marjı']/Degerleme_1['PD/NS'])*Degerleme_1['Fiyat']
    Degerleme_1['Degerleme 7'] = Degerleme_1['Degerleme 7'].apply(lambda x: round(x, 2))

    Degerleme_2['Degerleme 7'] = 10*(Degerleme_2['Tahmini Net Kar Marjı']/Degerleme_2['Tahmini PD/NS'])*Degerleme_2['Fiyat']
    Degerleme_2['Degerleme 7'] = Degerleme_2['Degerleme 7'].apply(lambda x: round(x, 2))

    #Model 8 = Hisse_Fiyatı/(Sirket_PDDD)*Sektör_PDDD ve Hisse_Fiyatı/(Sirket_PDDD)*Bist_PDDD
    Degerleme_1['Degerleme 8'] = (Degerleme_1['Fiyat']/Degerleme_1['Cari PD/DD'])*Degerleme_1['Sektör PD/DD']+(Degerleme_1['Fiyat']/Degerleme_1['Cari PD/DD']*Degerleme_1['BIST PD/DD'])/2
    Degerleme_1['Degerleme 8'] = Degerleme_1['Degerleme 8'].apply(lambda x: round(x, 2))

    Degerleme_2['Degerleme 8'] = (Degerleme_2['Fiyat']/Degerleme_2['Cari PD/DD'])*Degerleme_2['Sektör PD/DD']+(Degerleme_2['Fiyat']/Degerleme_2['Cari PD/DD']*Degerleme_2['BIST PD/DD'])/2
    Degerleme_2['Degerleme 8'] = Degerleme_2['Degerleme 8'].apply(lambda x: round(x, 2))

    #Model 9 = Hisse_Fiyatı/(Şirket_FK)*Tarihsel_FK
    Degerleme_1['Degerleme 9'] =  (Degerleme_1['Fiyat']/Degerleme_1['Cari F/K'])*Degerleme_1['Tarihsel F/K']
    Degerleme_1['Degerleme 9'] = Degerleme_1['Degerleme 9'].apply(lambda x: round(x, 2))

    Degerleme_2['Degerleme 9'] =  (Degerleme_2['Fiyat']/Degerleme_2['Cari F/K'])*Degerleme_2['Tarihsel F/K']
    Degerleme_2['Degerleme 9'] = Degerleme_2['Degerleme 9'].apply(lambda x: round(x, 2))

    #Model 10 = Öz Sermayenin 3 yada 4 katı kadar piyasa değeri olması
    Degerleme_1['Degerleme 10'] = ((3*Degerleme_1['Piyasa Değeri'])/Degerleme_1['Cari PD/DD'])/Degerleme_1['Ödenmiş Sermaye']
    Degerleme_1['Degerleme 10'] = Degerleme_1['Degerleme 10'].apply(lambda x: round(x, 2))

    Degerleme_2['Degerleme 10'] = ((3*Degerleme_2['Piyasa Değeri'])/Degerleme_2['Cari PD/DD'])/Degerleme_2['Ödenmiş Sermaye']
    Degerleme_2['Degerleme 10'] = Degerleme_2['Degerleme 10'].apply(lambda x: round(x, 2))

    Degerleme_1['İçsel Değer']=Degerleme_1[['Degerleme 1', 'Degerleme 2','Degerleme 3','Degerleme 4','Degerleme 5','Degerleme 6','Degerleme 7','Degerleme 8','Degerleme 9','Degerleme 10']].mean(axis=1,skipna=True)
    Degerleme_1['İçsel Değer'] = Degerleme_1['İçsel Değer'].apply(lambda x: round(x, 2))
    Degerleme_1['Marj']=((Degerleme_1['İçsel Değer']-Degerleme_1['Fiyat'])/(Degerleme_1['Fiyat']+0.001))*100
    Degerleme_1['Marj'] = Degerleme_1['Marj'].apply(lambda x: round(x, 2))
    Degerleme_1=Degerleme_1.T

    Degerleme_2['İçsel Değer']=Degerleme_2[['Degerleme 1', 'Degerleme 2','Degerleme 3','Degerleme 4','Degerleme 5','Degerleme 6','Degerleme 7','Degerleme 8','Degerleme 9','Degerleme 10']].mean(axis=1,skipna=True)
    Degerleme_2['İçsel Değer'] = Degerleme_2['İçsel Değer'].apply(lambda x: round(x, 2))
    Degerleme_2['Marj']=((Degerleme_2['İçsel Değer']-Degerleme_2['Fiyat'])/(Degerleme_2['Fiyat']+0.001))*100
    Degerleme_2['Marj'] = Degerleme_2['Marj'].apply(lambda x: round(x, 2))
    Degerleme_2=Degerleme_2.T

    return Degerleme_1, Degerleme_2

Temel_Veriler_1, Temel_Veriler_2=Hisse_Temel_Veriler(Hisse_Adı[0])
Degerleme_1,Degerleme_2 = Degerleme(Temel_Veriler_1, Temel_Veriler_2)
col1, col2 = st.columns(2)
with col1:
    st.subheader('Yıllıklandırılmış Verilere Göre')
    st.dataframe(Degerleme_1,use_container_width=True,height=1500)
with col2:
   st.subheader('Tahmini Yıl Sonu Verilerine Göre')
   st.dataframe(Degerleme_2,use_container_width=True,height=1500)
