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
  
def Yıllıklandirilmiş_Veriler(Hisse):
    print(Hisse)
    driver.implicitly_wait(5)
    driver.get("https://halkyatirim.com.tr/skorkart/"+Hisse)
    driver.implicitly_wait(20)
    L00=driver.find_element(By.XPATH,'//*[@id="TBLFINANSALVERİLER3"]/tbody/tr[1]/td[1]').text            #Hissenin Bilanco Donemi
    L01=driver.find_element(By.XPATH,'//*[@id="TBLPIYASADEGER"]/tbody/tr[1]/td[2]').text                 #Hissenin Son Piyasa Değeri
    L02=driver.find_element(By.XPATH,'//*[@id="TBLPAZARENDEKSLERI"]/tbody/tr[3]/td[2]').text[:-3]        #Hissenin Ödenmiş Sermayesi
    L03=driver.find_element(By.XPATH,'//*[@id="TBLFINANSALVERİLER3"]/tbody/tr[1]/td[13]').text           #Hissenin Özkaynakları
    L04=driver.find_element(By.XPATH,'//*[@id="TBLFINANSALVERİLER3"]/tbody/tr[1]/td[9]').text            #Hissenin Yıllıklandırılmış Net Kârı
    L05=driver.find_element(By.XPATH,'//*[@id="TBLFINANSALVERİLER3"]/tbody/tr[1]/td[3]').text            #Hissenin Yıllıklandırılmış Net Satışları


    L01=locale.atof(L01)            #Hissenin Son Piyasa Değeri
    L02=locale.atof(L02)/1000000    #Hissenin Ödenmiş Sermayesi
    L03=locale.atof(L03)            #Hissenin Özkaynakları
    L04=locale.atof(L04)            #Hissenin Yıllıklandırılmış Net Kârı
    L05=locale.atof(L05)            #Hissenin Yıllıklandırılmış Net Satışları

    soup = BeautifulSoup(driver.page_source,"lxml")
    Carpanlar=soup.find("table",id="TBLFINANSALVERİLER1")                   #Carpanlar
    Carpanlar = pd.read_html(str(Carpanlar))                                #Temel Teknik Verileri Dataframe'e dönüştü
    Carpanlar=pd.DataFrame(Carpanlar[0])
    Carpanlar = Carpanlar.iloc[:-5]
    Carpanlar.replace('-', np.nan, inplace=True)
    Carpanlar.replace('a.d.', np.nan, inplace=True)
    soup = BeautifulSoup(driver.page_source,"lxml")
    Finansallar=soup.find("table",id="TBLFINANSALVERİLER3")
    Finansallar = pd.read_html(str(Finansallar))
    Finansallar = pd.DataFrame(Finansallar[0])
    Finansallar = Finansallar.iloc[:-2]
    Finansallar.replace('-', np.nan, inplace=True)
    Finansallar.replace('a.d.', np.nan, inplace=True)

    driver.quit()

    NetKar=Finansallar['Net Kâr Çeyrek (Mln TL)'].to_numpy(dtype='float')                       #Çeyreklik Net Kâr Değerleri
    NetSat=Finansallar['Net Satışlar Çeyrek (Mln TL)'].to_numpy(dtype='float')                  #Çeyreklik Net Satışlar Değerleri

    Donem=L00[-2:]
    if Donem == '03':
        Y_NetKar = NetKar[0]*4
        Y_NetSat = NetSat[0]*4

    if Donem == '06':
        Y_NetKar = (NetKar[0]+NetKar[1])*2
        Y_NetSat = (NetSat[0]+NetSat[1])*2

    if Donem == '09':
        Y_NetKar = (NetKar[0]+NetKar[1]+NetKar[2])*4/3
        Y_NetSat = (NetSat[0]+NetSat[1]+NetSat[2])*4/3

    if Donem == '12':
        Y_NetKar = (NetKar[0]+NetKar[1]+NetKar[2]+NetKar[3])
        Y_NetSat = (NetSat[0]+NetSat[1]+NetSat[2]+NetSat[3])

    NetKar=round(Y_NetKar,2)
    NetSat=round(Y_NetSat,2)


    return L01,L02,L03,L04,L05,Carpanlar,NetKar,NetSat

Hisse_Ozet.replace('A/D', np.nan, inplace=True)                                           #Anlamsız Verileri NA ya çevir

Ortalama_Basliklar=['Hisse Adı','Sektör','Dönem','Piyasa Değeri','Ödenmiş Sermaye','Öz Sermaye','YILLIK KAR','YILLIK SATIŞ','Fiyat',
                    'F/K','PD/DD','FD/FAVÖK','FD/SATIŞLAR',
                    'Tarihsel F/K','Tarihsel PD/DD','Tarihsel FD/FAVÖK','Tarihsel FD/SATIŞLAR',
                    'GELECEK FK','POTASİYEL PD','NET KAR MARJI','PD/NS',
                    'BIST F/K','BIST PD/DD','BIST FD/FAVÖK','BIST FD/SATIŞLAR',
                    'SEKTÖR F/K','SEKTÖR PD/DD','SEKTÖR FD/FAVÖK','SEKTÖR FD/SATIŞLAR']

Ortalama_Basliklar_2=['Hisse Adı','Sektör','Dönem','Piyasa Değeri','Ödenmiş Sermaye','Öz Sermaye','TAHMİNİ YILLIK KAR','TAHMİNİ YILLIK SATIŞ','Fiyat',
                    'F/K','PD/DD','FD/FAVÖK','FD/SATIŞLAR',
                    'Tarihsel F/K','Tarihsel PD/DD','Tarihsel FD/FAVÖK','Tarihsel FD/SATIŞLAR',
                    'TAHMİNİ GELECEK FK','TAHMİNİ POTASİYEL PD','TAHMİNİ NET KAR MARJI','TAHMİNİ PD/NS',
                    'BIST F/K','BIST PD/DD','BIST FD/FAVÖK','BIST FD/SATIŞLAR',
                    'SEKTÖR F/K','SEKTÖR PD/DD','SEKTÖR FD/FAVÖK','SEKTÖR FD/SATIŞLAR']

Tum_Carpanlar=pd.DataFrame(columns=Ortalama_Basliklar)             #Tüm Çarpan Ortalamalarının Birleştirilmesi
Tum_Carpanlar_2=pd.DataFrame(columns=Ortalama_Basliklar_2)         #Tüm Çarpan Ortalamalarının Birleştirilmesi
for i in range(len(Hisse_Adı)):

    Hisse_Fiyat=Hisse_Ozet.loc[Hisse_Ozet['Kod'] == Hisse_Adı[i], 'Kapanış (TL)'].iloc[0]     #Hissenin Kapanış Fiyatı
    Hisse_Dönem=Hisse_Ozet.loc[Hisse_Ozet['Kod'] == Hisse_Adı[i], 'Son Dönem'].iloc[0]        #Hissenin Bilanço Dönemi

    #Hisse Piyasa Çarpanları
    Hisse_Finansallar=Hisse_Ozet.loc[Hisse_Ozet['Kod'] == Hisse_Adı[i], 'Kod'].iloc[0]        #Hissenin Bulunması
    Filtre2=Hisse_Ozet[Hisse_Ozet['Kod'].str.contains(Hisse_Finansallar)]                     #Hisse Bazlı Filtreleme
    HISSE_FKX=Filtre2['F/K'].to_numpy(dtype='float')[0]                                       #Hisse F/K Oranı
    HISSE_PDDDX=Filtre2['PD/DD'].to_numpy(dtype='float')[0]                                   #Hisse PD/DD Oranı
    HISSE_FD_FAV=Filtre2['FD/FAVÖK'].to_numpy(dtype='float')[0]                               #Hisse FD/FAVÖK Oranı
    HISSE_FD_SAT=Filtre2['FD/Satışlar'].to_numpy(dtype='float')[0]                            #Hisse FD/SAT Oranı

    #BIST Piyasa Çarpanları Ortalaması
    BIST_FKX=Hisse_Ozet['F/K'].to_numpy(dtype='float')                                        #BIST F/K Oranı
    BIST_PDDDX=Hisse_Ozet['PD/DD'].to_numpy(dtype='float')                                    #BIST PD/DD Oranı
    BIST_FD_FAV=Hisse_Ozet['FD/FAVÖK'].to_numpy(dtype='float')                                #BIST FD/FAVÖK Oranı
    BIST_FD_SAT=Hisse_Ozet['FD/Satışlar'].to_numpy(dtype='float')                             #BIST FD/SAT Oranı
    BIST_FKX=round(np.nanmean(BIST_FKX),3)                                                    #BIST Ortalaması
    BIST_PDDDX=round(np.nanmean(BIST_PDDDX),3)                                                #BIST PD/DD Ortalaması
    BIST_FD_FAV=round(np.nanmean(BIST_FD_FAV),3)                                              #BIST FD/FAVÖK Ortalaması
    BIST_FD_SAT=round(np.nanmean(BIST_FD_SAT),3)                                              #BIST FD/SAT Ortalaması

    #Sektörel Piyasa Çarpanları Ortalamalası
    Sektor=Hisse_Ozet.loc[Hisse_Ozet['Kod'] == Hisse_Adı[i], 'Sektör'].iloc[0]                #Sektörün Bulunması
    Filtre=Hisse_Ozet[Hisse_Ozet['Sektör'].str.contains(Sektor)]                              #Sektörel Bazlı Filtreleme
    SEKTOR_FKX=Filtre['F/K'].to_numpy(dtype='float')                                          #Sektör F/K Oranı
    SEKTOR_PDDDX=Filtre['PD/DD'].to_numpy(dtype='float')                                      #Sektör PD/DD Oranı
    SEKTOR_FD_FAV=Filtre['FD/FAVÖK'].to_numpy(dtype='float')                                  #Sektör FD/FAVÖK Oranı
    SEKTOR_FD_SAT=Filtre['FD/Satışlar'].to_numpy(dtype='float')                               #Sektör FD/SAT Oranı
    SEKTOR_FKX=round(np.nanmean(SEKTOR_FKX),3)                                                #Sektör Ortalaması
    SEKTOR_PDDDX=round(np.nanmean(SEKTOR_PDDDX),3)                                            #Sektör PD/DD Ortalaması
    SEKTOR_FD_FAV=round(np.nanmean(SEKTOR_FD_FAV),3)                                          #Sektör FD/FAVÖK Ortalaması
    SEKTOR_FD_SAT=round(np.nanmean(SEKTOR_FD_SAT),3)                                          #Sektör FD/SAT Ortalaması

    LL01,LL02,LL03,LL04,LL05,Tarihsel_Carpanlar,Tah_NetKar,Tah_NetSat=Yıllıklandirilmiş_Veriler(Hisse_Adı[i])

    TarFK=Tarihsel_Carpanlar['F/K'].to_numpy(dtype='float')
    TarFK=round(np.nanmean(TarFK),2)

    TarPD_DD=Tarihsel_Carpanlar['PD/DD'].to_numpy(dtype='float')
    TarPD_DD=round(np.nanmean(TarPD_DD),2)

    TarFD_FAV=Tarihsel_Carpanlar['FD/FAVÖK'].to_numpy(dtype='float')
    TarFD_FAV=round(np.nanmean(TarFD_FAV),2)

    TarFD_SAT=Tarihsel_Carpanlar['FD/Satışlar'].to_numpy(dtype='float')
    TarFD_SAT=round(np.nanmean(TarFD_SAT),2)

    PiyDeg=LL01
    ÖdSer=LL02
    ÖzSer=LL03
    Yıllık_Kar=LL04
    Tah_Yıllık_Kar=Tah_NetKar
    
    Yıllık_Satıs=LL05
    Tah_Yıllık_Sat=Tah_NetSat

    Gelecek_FK=PiyDeg/(Yıllık_Kar+0.0001)
    Gelecek_FK_2=PiyDeg/(Tah_Yıllık_Kar+0.0001)
    
    Sermaye_Çarpanı=Yıllık_Kar/ÖdSer                               #Şirket Sermayesi kadar kâr elde ederse fiyatı 10 tl eder.
    Sermaye_Çarpanı_2=Tah_Yıllık_Kar/ÖdSer
    
    Potansiyel_PD=Yıllık_Kar*7+ÖzSer*0.5                           #Potansiyel Piyasa Değeri Yıllıklandırılmış Kâr x 7 + Özsermaye x 0.5
    Potansiyel_PD_2=Tah_Yıllık_Kar*7+ÖzSer*0.5
    
    NetKarMarjı=Yıllık_Kar/(Yıllık_Satıs+0.0001)                   #Net Kâr Marjı
    NetKarMarjı_2=Tah_Yıllık_Kar/(Tah_Yıllık_Sat+0.0001)
    
    PD_NS=PiyDeg/(Yıllık_Satıs +0.0001)                            #Piyasa Değeri / Net Satışlar
    PD_NS_2=PiyDeg/(Tah_Yıllık_Sat+0.0001)

    Carpanlar=[Hisse_Adı[i],Sektor,Hisse_Dönem,PiyDeg,ÖdSer,ÖzSer,Yıllık_Kar,Yıllık_Satıs,Hisse_Fiyat,
                HISSE_FKX,HISSE_PDDDX,HISSE_FD_FAV,HISSE_FD_SAT,
                TarFK,TarPD_DD,TarFD_FAV,TarFD_SAT,
                Gelecek_FK,Potansiyel_PD,NetKarMarjı,PD_NS,
                BIST_FKX,BIST_PDDDX,BIST_FD_FAV,BIST_FD_SAT,
                SEKTOR_FKX,SEKTOR_PDDDX,SEKTOR_FD_FAV,SEKTOR_FD_SAT]


    Carpanlar_2=[Hisse_Adı[i],Sektor,Hisse_Dönem,PiyDeg,ÖdSer,ÖzSer,Yıllık_Kar,Yıllık_Satıs,Hisse_Fiyat,
                HISSE_FKX,HISSE_PDDDX,HISSE_FD_FAV,HISSE_FD_SAT,
                TarFK,TarPD_DD,TarFD_FAV,TarFD_SAT,
                Gelecek_FK_2,Potansiyel_PD_2,NetKarMarjı_2,PD_NS_2,
                BIST_FKX,BIST_PDDDX,BIST_FD_FAV,BIST_FD_SAT,
                SEKTOR_FKX,SEKTOR_PDDDX,SEKTOR_FD_FAV,SEKTOR_FD_SAT]

    Carpanlar=pd.DataFrame([Carpanlar],columns=Ortalama_Basliklar)                            #Tüm Çarpanların Birleştirilmesi
    Carpanlar_2=pd.DataFrame([Carpanlar_2],columns=Ortalama_Basliklar_2)                      #Tüm Çarpanların Birleştirilmesi
    Tum_Carpanlar=Tum_Carpanlar.append(Carpanlar)
    Tum_Carpanlar_2=Tum_Carpanlar_2.append(Carpanlar_2)


Tum_Carpanlar['POTASİYEL PD'] = Tum_Carpanlar['POTASİYEL PD'].apply(lambda x: round(x, 2))
Tum_Carpanlar['NET KAR MARJI'] = Tum_Carpanlar['NET KAR MARJI'].apply(lambda x: round(x, 2))
Tum_Carpanlar['GELECEK FK'] = Tum_Carpanlar['GELECEK FK'].apply(lambda x: round(x, 2))
Tum_Carpanlar['PD/NS'] = Tum_Carpanlar['PD/NS'].apply(lambda x: round(x, 2))

Tum_Carpanlar_2['TAHMİNİ POTASİYEL PD'] = Tum_Carpanlar_2['TAHMİNİ POTASİYEL PD'].apply(lambda x: round(x, 2))
Tum_Carpanlar_2['TAHMİNİ NET KAR MARJI'] = Tum_Carpanlar_2['TAHMİNİ NET KAR MARJI'].apply(lambda x: round(x, 2))
Tum_Carpanlar_2['TAHMİNİ GELECEK FK'] = Tum_Carpanlar_2['TAHMİNİ GELECEK FK'].apply(lambda x: round(x, 2))
Tum_Carpanlar_2['TAHMİNİ PD/NS'] = Tum_Carpanlar_2['TAHMİNİ PD/NS'].apply(lambda x: round(x, 2))

#Değerleme 1 = Hisse_Fiyatıx(Sektör_FK/Şirket_FK) ve Hisse_Fiyatıx(Sektör_PDDD/Şirket_PDDD) 'nin ortalaması
Tum_Carpanlar['Degerleme 1']=(Tum_Carpanlar['Fiyat']*(Tum_Carpanlar['SEKTÖR F/K']/Tum_Carpanlar['F/K'])+Tum_Carpanlar['Fiyat']*(Tum_Carpanlar['SEKTÖR PD/DD']/Tum_Carpanlar['PD/DD']))/2
Tum_Carpanlar['Degerleme 1'] = Tum_Carpanlar['Degerleme 1'].apply(lambda x: round(x, 2))

Tum_Carpanlar_2['Degerleme 1']=(Tum_Carpanlar_2['Fiyat']*(Tum_Carpanlar_2['SEKTÖR F/K']/Tum_Carpanlar_2['F/K'])+Tum_Carpanlar_2['Fiyat']*(Tum_Carpanlar_2['SEKTÖR PD/DD']/Tum_Carpanlar_2['PD/DD']))/2
Tum_Carpanlar_2['Degerleme 1'] = Tum_Carpanlar_2['Degerleme 1'].apply(lambda x: round(x, 2))

#Değerleme 2 = (Hisse Fiyatı/Şirket_FK)xSektör_FK ve (Hisse Fiyatı/Şirket_FK)xBist_FK 'nın ortalaması
Tum_Carpanlar['Degerleme 2']=((Tum_Carpanlar['Fiyat']/Tum_Carpanlar['F/K'])*Tum_Carpanlar['SEKTÖR F/K']+(Tum_Carpanlar['Fiyat']/Tum_Carpanlar['F/K'])*Tum_Carpanlar['BIST F/K'])/2
Tum_Carpanlar['Degerleme 2'] = Tum_Carpanlar['Degerleme 2'].apply(lambda x: round(x, 2))

Tum_Carpanlar_2['Degerleme 2']=((Tum_Carpanlar_2['Fiyat']/Tum_Carpanlar_2['F/K'])*Tum_Carpanlar_2['SEKTÖR F/K']+(Tum_Carpanlar_2['Fiyat']/Tum_Carpanlar_2['F/K'])*Tum_Carpanlar_2['BIST F/K'])/2
Tum_Carpanlar_2['Degerleme 2'] = Tum_Carpanlar_2['Degerleme 2'].apply(lambda x: round(x, 2))

#Değerleme 3 = Gelecek_FK=(Piyasa Değeri / Yıllıklandırılmış Net Kâr) olmak üzere  (Hisse Fiyatı/Gelecek FK)xBist_FK ve (Hisse Fiyatı/Gelecek FK)xSektör_FK 'nın ortalaması
Tum_Carpanlar['Degerleme 3']=((Tum_Carpanlar['Fiyat']/Tum_Carpanlar['GELECEK FK'])*Tum_Carpanlar['SEKTÖR F/K']+(Tum_Carpanlar['Fiyat']/Tum_Carpanlar['GELECEK FK'])*Tum_Carpanlar['BIST F/K'])/2
Tum_Carpanlar['Degerleme 3'] = Tum_Carpanlar['Degerleme 3'].apply(lambda x: round(x, 2))

Tum_Carpanlar_2['Degerleme 3']=((Tum_Carpanlar_2['Fiyat']/Tum_Carpanlar_2['TAHMİNİ GELECEK FK'])*Tum_Carpanlar_2['SEKTÖR F/K']+(Tum_Carpanlar_2['Fiyat']/Tum_Carpanlar_2['TAHMİNİ GELECEK FK'])*Tum_Carpanlar_2['BIST F/K'])/2
Tum_Carpanlar_2['Degerleme 3'] = Tum_Carpanlar_2['Degerleme 3'].apply(lambda x: round(x, 2))

#Değerleme 4 = Şirket Sermayesi Kadar Kâr Elde Ederse 10 TL değeri vardır.
Tum_Carpanlar['Degerleme 4']=(Tum_Carpanlar['YILLIK KAR']/Tum_Carpanlar['Ödenmiş Sermaye'])*10
Tum_Carpanlar['Degerleme 4'] = Tum_Carpanlar['Degerleme 4'].apply(lambda x: round(x, 2))

Tum_Carpanlar_2['Degerleme 4']=(Tum_Carpanlar_2['TAHMİNİ YILLIK KAR']/Tum_Carpanlar_2['Ödenmiş Sermaye'])*10
Tum_Carpanlar_2['Degerleme 4'] = Tum_Carpanlar_2['Degerleme 4'].apply(lambda x: round(x, 2))

#Değerleme 5 = PD/DD Öz Sermayenin 10 Katı olmalı. (Öz Sermaye Kârlılığı x10/(PD/DD))xHisse_Fiyatı
Tum_Carpanlar['Degerleme 5']=(10*(Tum_Carpanlar['YILLIK KAR']/Tum_Carpanlar['Öz Sermaye'])/Tum_Carpanlar['PD/DD'])*Tum_Carpanlar['Fiyat']
Tum_Carpanlar['Degerleme 5'] = Tum_Carpanlar['Degerleme 5'].apply(lambda x: round(x, 2))

Tum_Carpanlar_2['Degerleme 5']=(10*(Tum_Carpanlar_2['TAHMİNİ YILLIK KAR']/Tum_Carpanlar_2['Öz Sermaye'])/Tum_Carpanlar_2['PD/DD'])*Tum_Carpanlar_2['Fiyat']
Tum_Carpanlar_2['Degerleme 5'] = Tum_Carpanlar_2['Degerleme 5'].apply(lambda x: round(x, 2))

#Değerleme 6 = Potansiyel PD/Özsermaye
Tum_Carpanlar['Degerleme 6']=Tum_Carpanlar['POTASİYEL PD']/Tum_Carpanlar['Ödenmiş Sermaye']
Tum_Carpanlar['Degerleme 6'] = Tum_Carpanlar['Degerleme 6'].apply(lambda x: round(x, 2))

Tum_Carpanlar_2['Degerleme 6']=Tum_Carpanlar_2['TAHMİNİ POTASİYEL PD']/Tum_Carpanlar_2['Ödenmiş Sermaye']
Tum_Carpanlar_2['Degerleme 6'] = Tum_Carpanlar_2['Degerleme 6'].apply(lambda x: round(x, 2))

#Değerleme 7 = 100*(Net Kar Marjı / PD_NS )*Hisse_Fiyatı
Tum_Carpanlar['Degerleme 7']=10*(Tum_Carpanlar['NET KAR MARJI']/Tum_Carpanlar['PD/NS'])*Tum_Carpanlar['Fiyat']
Tum_Carpanlar['Degerleme 7'] = Tum_Carpanlar['Degerleme 7'].apply(lambda x: round(x, 2))

Tum_Carpanlar_2['Degerleme 7']=10*(Tum_Carpanlar_2['TAHMİNİ NET KAR MARJI']/Tum_Carpanlar_2['TAHMİNİ PD/NS'])*Tum_Carpanlar_2['Fiyat']
Tum_Carpanlar_2['Degerleme 7'] = Tum_Carpanlar_2['Degerleme 7'].apply(lambda x: round(x, 2))


#Değerleme 8 = Hisse_Fiyatı/(Sirket_PDDD)*Sektör_PDDD ve Hisse_Fiyatı/(Sirket_PDDD)*Bist_PDDD
Tum_Carpanlar['Degerleme 8']=(Tum_Carpanlar['Fiyat']/Tum_Carpanlar['PD/DD'])*Tum_Carpanlar['SEKTÖR PD/DD']+(Tum_Carpanlar['Fiyat']/Tum_Carpanlar['PD/DD']*Tum_Carpanlar['BIST PD/DD'])/2
Tum_Carpanlar['Degerleme 8'] = Tum_Carpanlar['Degerleme 8'].apply(lambda x: round(x, 2))

Tum_Carpanlar_2['Degerleme 8']=(Tum_Carpanlar_2['Fiyat']/Tum_Carpanlar_2['PD/DD'])*Tum_Carpanlar_2['SEKTÖR PD/DD']+(Tum_Carpanlar_2['Fiyat']/Tum_Carpanlar_2['PD/DD']*Tum_Carpanlar_2['BIST PD/DD'])/2
Tum_Carpanlar_2['Degerleme 8'] = Tum_Carpanlar_2['Degerleme 8'].apply(lambda x: round(x, 2))

#Değerleme 9 = Hisse_Fİyatı/(Şirket_FK)*Tarihsel_FK
Tum_Carpanlar['Degerleme 9']=(Tum_Carpanlar['Fiyat']/Tum_Carpanlar['F/K'])*Tum_Carpanlar['Tarihsel F/K']
Tum_Carpanlar['Degerleme 9'] = Tum_Carpanlar['Degerleme 9'].apply(lambda x: round(x, 2))

Tum_Carpanlar_2['Degerleme 9']=(Tum_Carpanlar_2['Fiyat']/Tum_Carpanlar_2['F/K'])*Tum_Carpanlar_2['Tarihsel F/K']
Tum_Carpanlar_2['Degerleme 9'] = Tum_Carpanlar_2['Degerleme 9'].apply(lambda x: round(x, 2))

#Değerleme 10 =Öz Sermayenin 3 yada 4 katı kadar piyasa değeri olması
Tum_Carpanlar['Degerleme 10']=((3*Tum_Carpanlar['Piyasa Değeri'])/Tum_Carpanlar['PD/DD'])/Tum_Carpanlar['Ödenmiş Sermaye']
Tum_Carpanlar['Degerleme 10'] = Tum_Carpanlar['Degerleme 10'].apply(lambda x: round(x, 2))

Tum_Carpanlar_2['Degerleme 10']=((3*Tum_Carpanlar_2['Piyasa Değeri'])/Tum_Carpanlar_2['PD/DD'])/Tum_Carpanlar_2['Ödenmiş Sermaye']
Tum_Carpanlar_2['Degerleme 10'] = Tum_Carpanlar_2['Degerleme 10'].apply(lambda x: round(x, 2))

Tum_Carpanlar['İçsel Değer']=Tum_Carpanlar[['Degerleme 1', 'Degerleme 2','Degerleme 3','Degerleme 4','Degerleme 5','Degerleme 6','Degerleme 7','Degerleme 8','Degerleme 9','Degerleme 10']].mean(axis=1,skipna=True)
Tum_Carpanlar['İçsel Değer'] = Tum_Carpanlar['İçsel Değer'].apply(lambda x: round(x, 2))
Tum_Carpanlar['Marj']=((Tum_Carpanlar['İçsel Değer']-Tum_Carpanlar['Fiyat'])/(Tum_Carpanlar['Fiyat']+0.001))*100
Tum_Carpanlar['Marj'] = Tum_Carpanlar['Marj'].apply(lambda x: round(x, 2))
Tum_Carpanlar=Tum_Carpanlar.T

Tum_Carpanlar_2['İçsel Değer']=Tum_Carpanlar_2[['Degerleme 1', 'Degerleme 2','Degerleme 3','Degerleme 4','Degerleme 5','Degerleme 6','Degerleme 7','Degerleme 8','Degerleme 9','Degerleme 10']].mean(axis=1,skipna=True)
Tum_Carpanlar_2['İçsel Değer'] = Tum_Carpanlar_2['İçsel Değer'].apply(lambda x: round(x, 2))
Tum_Carpanlar_2['Marj']=((Tum_Carpanlar_2['İçsel Değer']-Tum_Carpanlar_2['Fiyat'])/(Tum_Carpanlar_2['Fiyat']+0.001))*100
Tum_Carpanlar_2['Marj'] = Tum_Carpanlar_2['Marj'].apply(lambda x: round(x, 2))
Tum_Carpanlar_2=Tum_Carpanlar_2.T
print(Tum_Carpanlar_2)
col1, col2 = st.columns(2)
with col1:
    st.subheader('Yıllıklandırılmış Verilere Göre')
    st.dataframe(Tum_Carpanlar,height=1500)
with col2:
   st.subheader('Tahmini Yıl Sonu Verilerine Göre')
   st.dataframe(Tum_Carpanlar_2,height=1500)
