from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import ssl
from urllib import request
import streamlit as st
from urllib import request
import requests
from tvDatafeed import TvDatafeed, Interval
from webdriver_manager.chrome import ChromeDriverManager

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
driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version='120.0.6099.224').install()), options=options)
Temel_Veriler_1=pd.DataFrame()
Temel_Veriler_2=pd.DataFrame()
Finansallar=pd.DataFrame()
Karlılık=pd.DataFrame()
Topics=[]                                                                   #Başlıklar İçin boş Liste
Tarihler=[]                                                                 #Tüm Bilanço Tarihleri
Yillar=[]                                                                   #Tüm Bİlanço Yılları
Donemler=[]                                                                 #Tüm Bilanço Tarihleri
Hisse=[]                                                                    #Analiz Edilecek Hisse Kodu
Fiyat=[]                                                                    #Analiz Edilecek Hissenin Güncel Fiyatı
Firma=[]                                                                    #Analiz Edilecek Firma Adı

Aylar=['Yıllar','Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
Çeyrekler=['Yıllar','Q1','Q2','Q3','Q4']

def Hisse_İsimleri():
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
    page_title="Hisse Değerleme",
    layout="wide",
    initial_sidebar_state="expanded")

with st.sidebar:
    Hisse_Ozet=Hisse_İsimleri()
    st.header('Hisse Arama')
    Hisse_Adı = st.selectbox('Hisse Adı',Hisse_Ozet['Kod'])
    Hisse_Adı=[Hisse_Adı]

def Hisse_Temel_Veriler(Hisse):
    driver.get('https://analizim.halkyatirim.com.tr/Financial/ScoreCardDetail?hisseKod='+Hisse)
    driver.implicitly_wait(20)
    
    BlcDnm=driver.find_element(By.XPATH,'/html/body/div[2]/div[2]/div/div[1]/div[2]/div[2]/div/span[2]/strong').text            #Hissenin Bilanco Dönemi
    SnFyt=driver.find_element(By.XPATH,'/html/body/div[2]/div[2]/div/div[1]/div[2]/div[3]/div[1]/div/div[2]/div[1]').text
    SnFyt=float(SnFyt.replace(',', ''))

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
    if np.isnan(CariFK):
      Temel_Veriler_1=pd.DataFrame()
      Temel_Veriler_2=pd.DataFrame()
      return Temel_Veriler_1, Temel_Veriler_2

    #Tarihsel Ortalamaların Hesaplanması
    TarFK=round(np.nanmean(Carpanlar['F/K'].to_numpy(dtype='float')),2)
    TarPDDD=round(np.nanmean(Carpanlar['PD/DD'].to_numpy(dtype='float')),2)
    TarFDFV=round(np.nanmean(Carpanlar['FD/FAVÖK'].to_numpy(dtype='float')),2)
    TarFDST=round(np.nanmean(Carpanlar['FD/Satışlar'].to_numpy(dtype='float')),2)

    if np.isnan(TarFK):
      TarFK=CariFK

    if np.isnan(TarPDDD):
      TarPDDD=CariPDDD

    if np.isnan(TarFDFV):
      TarFDFV=CariFDFV

    if np.isnan(TarFDST):
      TarFDST=CariFDST

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
    
    if np.isnan(SktrFK):
      SktrFK=CariFK

    if np.isnan(SktrPDDD):
      SktrPDDD=CariPDDD

    if np.isnan(SktrFDFV):
      SktrFDFV=CariFDFV

    if np.isnan(SktrFDST):
      SktrFDST=CariFDST

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
    if (Temel_Veriler_1.isnull().any().any() or Temel_Veriler_2.isnull().any().any())==True:
      Temel_Veriler_1=pd.DataFrame()
      Temel_Veriler_2=pd.DataFrame()
      return Temel_Veriler_1, Temel_Veriler_2

    driver.quit()
    return Temel_Veriler_1 , Temel_Veriler_2 ,Finansallar, Karlılık,BlcDnm

def Hisse_Karne(Hisse,Finansallar,Karlılık,BlcDnm):
   #Karlılık Karnesi
  
    C_BurKarMarj=round(float(Karlılık.iat[0,1])*100-float(Karlılık.iat[1,1])*100,0)
    C_FavKarMarj=round(float(Karlılık.iat[0,5])*100-float(Karlılık.iat[1,5])*100,0)
    C_NetKarMarj=round(float(Karlılık.iat[0,7])*100-float(Karlılık.iat[1,7])*100,0)

    Y_BurKarMarj=round(float(Karlılık.iat[0,2])*100-float(Karlılık.iat[4,2])*100,0)
    Y_FavKarMarj=round(float(Karlılık.iat[0,6])*100-float(Karlılık.iat[4,6])*100,0) 
    Y_NetKarMarj=round(float(Karlılık.iat[0,8])*100-float(Karlılık.iat[4,8])*100,0)

    Karlılık_Basliklar=['Hisse Adı',
              'Çeyreklik Brüt Kâr Marjı Değişimi',
              'Çeyreklik FAVÖK Marjı Değişimi',
              'Çeyreklik Net Marjı Değişimi',
              'Yıllık Brüt Kâr Marjı Değişimi',
              'Yıllık FAVÖK Marjı Değişimi',
              'Yıllık Net Marjı Değişimi']


    if C_BurKarMarj>0:
       Check_1='Pozitif'
    else:
       Check_1='Negatif'

    if C_FavKarMarj>0:
       Check_2='Pozitif'
    else:
       Check_2='Negatif'

    if C_NetKarMarj>0:
       Check_3='Pozitif'
    else:
       Check_3='Negatif' 

    if Y_BurKarMarj>0:
       Check_4='Pozitif'
    else:
       Check_4='Negatif' 

    if Y_FavKarMarj>0:
       Check_5='Pozitif'
    else:
       Check_5='Negatif'  

    if Y_NetKarMarj>0:
       Check_6='Pozitif'
    else:
       Check_6='Negatif' 
    Karlılık=[Hisse,Check_1,Check_2,Check_3,Check_4,Check_5,Check_6] 
    Karlılık=pd.DataFrame([Karlılık],columns=Karlılık_Basliklar)
    Karlılık=Karlılık.T
      
    #Büyüme Karnesi
    NetKar=Finansallar['Net Kâr Çeyrek (Mln TL)'].to_numpy(dtype='float')                       #Çeyreklik Net Kâr Değerleri
    NetSat=Finansallar['Net Satışlar Çeyrek (Mln TL)'].to_numpy(dtype='float')                  #Çeyreklik Net Satışlar Değerleri
    FAVOK=Finansallar['FAVÖK (Çeyrek) (Mln TL)'].to_numpy(dtype='float')                        #Çeyreklik FAVÖK değerleri
    if len(NetKar)<8:
      return

    C_NetKarDeg=((NetKar[0]/(NetKar[1]+0.001))-1)*100
    C_NetSatDeg=((NetSat[0]/(NetSat[1]+0.001))-1)*100
    C_FAVOKDeg=((FAVOK[0]/(FAVOK[1]+0.001))-1)*100

    Donem=BlcDnm[-2:]
    if Donem == '03':
        Y_NetKarDeg = ((NetKar[0]/(NetKar[4]+0.001)-1))*100
        Y_NetSatDeg = ((NetSat[0]/(NetSat[4]+0.001))-1)*100
        Y_FAVOKDeg = ((FAVOK[0]/(FAVOK[4]+0.001))-1)*100


    if Donem == '06':
        Y_NetKarDeg = (((NetKar[0]+NetKar[1])/(NetKar[4]+NetKar[5]+0.001)-1))*100
        Y_NetSatDeg = (((NetSat[0]+NetSat[1])/(NetSat[4]+NetSat[5]+0.001)-1))*100
        Y_FAVOKDeg = (((FAVOK[0]+FAVOK[1])/(FAVOK[4]+FAVOK[5])-1)+0.001)*100

    if Donem == '09':
        Y_NetKarDeg = (((NetKar[0]+NetKar[1]+NetKar[2])/(NetKar[4]+NetKar[5]+NetKar[6]+0.001)-1))*100
        Y_NetSatDeg = (((NetSat[0]+NetSat[1]+NetSat[2])/(NetSat[4]+NetSat[5]+NetSat[6]+0.001)-1))*100
        Y_FAVOKDeg = (((FAVOK[0]+FAVOK[1]+FAVOK[2])/(FAVOK[4]+FAVOK[5]+FAVOK[6]+0.001)-1))*100


    if Donem == '12':
        Y_NetKarDeg = (((NetKar[0]+NetKar[1]+NetKar[2]+NetKar[3])/(NetKar[4]+NetKar[5]+NetKar[6]+NetKar[7]+0.001)-1))*100
        Y_NetSatDeg = (((NetSat[0]+NetSat[1]+NetSat[2]+NetSat[3])/(NetSat[4]+NetSat[5]+NetSat[6]+NetSat[7]+0.001)-1))*100
        Y_FAVOKDeg = (((FAVOK[0]+FAVOK[1]+FAVOK[2]+FAVOK[3])/(FAVOK[4]+FAVOK[5]+FAVOK[6]+FAVOK[7]+0.001)-1))*100


    C_NetKarDeg=round(C_NetKarDeg,2)
    C_NetSatDeg=round(C_NetSatDeg,2)
    C_FAVOKDeg=round(C_FAVOKDeg,2)
    Y_NetKarDeg=round(Y_NetKarDeg,2)
    Y_NetSatDeg=round(Y_NetSatDeg,2)
    Y_FAVOKDeg=round(Y_FAVOKDeg,2)
    
    Büyüme_Basliklar=['Hisse Adı',
              'Satışlar Çeyreklik Değişim',
              'FAVÖK Çeyreklik Değişim',
              'Net Kâr Çeyreklik Değişim',
              'Satışlar Yıllık Değişim',
              'FAVÖK Yıllık  Değişim',
              'Net Kâr Yıllık Değişim']

    if C_NetSatDeg>0:
       Check_1='Pozitif'
    else:
       Check_1='Negatif'

    if C_FAVOKDeg>0:
       Check_2='Pozitif'
    else:
       Check_2='Negatif'

    if C_NetKarDeg>0:
       Check_3='Pozitif'
    else:
       Check_3='Negatif' 

    if Y_NetSatDeg>0:
       Check_4='Pozitif'
    else:
       Check_4='Negatif' 

    if Y_FAVOKDeg>0:
       Check_5='Pozitif'
    else:
       Check_5='Negatif'  

    if Y_NetKarDeg>0:
       Check_6='Pozitif'
    else:
       Check_6='Negatif'

    Büyüme=[Hisse,Check_1,Check_2,Check_3,Check_4,Check_5,Check_6] 
    Büyüme=pd.DataFrame([Büyüme],columns=Büyüme_Basliklar)
    Büyüme=Büyüme.T

    #Borçluluk Karnesi
    url1="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse="+Hisse
    r1=requests.get(url1,verify=False)                                          #Web Sitesine Talepte Bulun
    soup=BeautifulSoup(r1.text,"html.parser")                                   #Web Sitesinin Sayfa Kaynağını Görüntüle
    FinGrp=soup.find("select",id="ddlMaliTabloGroup").find("option")["value"]   #Finansal Grubu Çek
    TarGrp=soup.find("select", id="ddlMaliTabloFirst").findChildren("option")   #Tarih Gruplarını Çek
    for j in TarGrp:
        Tarihler.append(j.string.rsplit("/"))                                    #Yilları ve Dönemleri Ayır
    for k in Tarihler:
        Yillar.append(k[0])                                                      #Yilları Tarihlerden Çek
        Donemler.append(k[1])                                                    #Dönemleri Tarihlerden Çek
 
    url1="https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"
        
    Parametreler=(
        ("companyCode",Hisse),                                               #Hisse Kodunu Parametre Olarak Tanımla
        ("exchange","TRY"),                                                  #Türk Lirasını Parametre Olarak Tanımla
        ("financialGroup",FinGrp),                                           #Finansal Grubu Parametre Olarak Tanımla
        ("year1",Yillar[0]),                                                 #Yılları Parametre Olarak Tanımla
        ("period1",Donemler[0]),                                             #Dönemleri Parametre Olarak Tanımla
        ("year2",Yillar[1]),                                                 #Yılları Parametre Olarak Tanımla
        ("period2",Donemler[1]),                                             #Dönemleri Parametre Olarak Tanımla
        ("year3",Yillar[2]),                                                 #Yılları Parametre Olarak Tanıml
        ("period3",Donemler[2]),                                             #Dönemleri Parametre Olarak Tanımla
        ("year4",Yillar[3]),                                                 #Yılları Değişken Parametre Olarak Tanıml
        ("period4",Donemler[3]))                                             #Dönemleri Değişken Parametre Olarak Tanımla
        
    r1=requests.get(url1,params=Parametreler,verify=False).json()["value"]                  #JSON formatında Sayfa Verisine Ulaş
    Borcluluk=pd.DataFrame.from_dict(r1)                                                    #Sayfa Verisini Oku
    Borcluluk = Borcluluk.drop(Borcluluk.columns[[0,2,4,5,6]],axis = 1)                     #Sayfa Verisini Ayıkla  
    
    Borcluluk.columns.values[0] = Hisse                                                      #Ana Verinin Başlıklarını Yeniden İsimlendir
    Borcluluk.columns.values[1] = 'Son Veri'                                                 #Ana Verinin Başlıklarını Yeniden İsimlendir
    Borcluluk[Borcluluk.columns] = Borcluluk.apply(lambda x: x.str.strip())                  #Ana Verideki Gereksiz Boşlukları Sil

    DonVar=Borcluluk[Borcluluk[Hisse].isin(['Dönen Varlıklar'])].reset_index(drop=True)                       #Dönen Varlıklar
    DonVar=DonVar.drop(DonVar.columns[[0]],axis = 1).to_numpy(dtype='float')                                  #Dönen Varlıklar

    DurVar=Borcluluk[Borcluluk[Hisse].isin(['Duran Varlıklar'])].reset_index(drop=True)                       #Dönen Varlıklar
    DurVar=DurVar.drop(DurVar.columns[[0]],axis = 1).to_numpy(dtype='float')                                  #Dönen Varlıklar

    KVY=Borcluluk[Borcluluk[Hisse].isin(['Kısa Vadeli Yükümlülükler'])].reset_index(drop=True)                #Kısa Vadeli Yükümlülükler
    KVY=KVY.drop(KVY.columns[[0]],axis = 1).to_numpy(dtype='float')                                           #Kısa Vadeli Yükümlülükler

    UVY=Borcluluk[Borcluluk[Hisse].isin(['Uzun Vadeli Yükümlülükler'])].reset_index(drop=True)                #Uzun Vadeli Yükümlülükler
    UVY=UVY.drop(UVY.columns[[0]],axis = 1).to_numpy(dtype='float')                                           #Uzun Vadeli Yükümlülükler

    FinBorc=Borcluluk[Borcluluk[Hisse].isin(['Finansal Borçlar'])].reset_index(drop=True)                                           #Finansal Borçlar
    
    FinBorc_1=FinBorc.drop([1], axis=0).reset_index(drop=True)                                                                      #Kısa Vadeli Finansal Borçlar
    FinBorc_1=FinBorc_1.drop(FinBorc_1.columns[[0]],axis = 1).to_numpy(dtype='float')                                               #Kısa Vadeli Finansal Borçlar
    FinBorc_2=FinBorc.drop([0], axis=0).reset_index(drop=True)                                                                      #Uzun Vadeli Finansal Borçlar
    FinBorc_2=FinBorc_2.drop(FinBorc_2.columns[[0]],axis = 1).to_numpy(dtype='float')                                               #Uzun Vadeli Finansal Borçlar

    NetSer=Borcluluk[Borcluluk[Hisse].isin(['İşletme Faaliyetlerinden Kaynaklanan Net Nakit'])].reset_index(drop=True)            #Net İşletme Sermayesi
    NetSer=NetSer.drop(NetSer.columns[[0]],axis = 1).to_numpy(dtype='float')                                          #Uzun Vadeli Yükümlülükler
    NetBorc=float(Finansallar.iat[0,10])
    Cari_Oran=DonVar/KVY

    Fin_Borc=FinBorc_1+FinBorc_2
    Fin_Borc_Rat=((FinBorc_1+FinBorc_2)/(DonVar+DurVar+0.0001))*100

    NetFinGid=float(Finansallar.iat[0,5])
    FAVOK=float(Finansallar.iat[0,3])

    if Cari_Oran[0]>1.5:
       Check_1='Pozitif'
    else:
       Check_1='Negatif'

    if Fin_Borc_Rat[0]<50:
       Check_2='Pozitif'
    else:
       Check_2='Negatif'

    if NetSer[0]>0:
       Check_3='Pozitif'
    else:
       Check_3='Negatif' 

    if NetBorc<0:
       Check_4='Pozitif'
    else:
       Check_4='Negatif' 

    if DonVar>Fin_Borc[0]:
       Check_5='Pozitif'
    else:
       Check_5='Negatif'  

    if NetFinGid<(FAVOK/5):
       Check_6='Pozitif'
    else:
       Check_6='Negatif'              

    Borcluluk_Basliklar=['Hisse Adı',
              'Cari Oran > 1.5',
              'Finansal Borçluluk < 50%',
              'Net İşletme Sermayesi > 0',
              'Net Borç < 0',
              'Dönen Varlıklar > Finansal Borç',
              'Net Finansal Gider < FAVÖK /5']
    
    Borcluluk=[Hisse,Check_1,Check_2,Check_3,Check_4,Check_5,Check_6] 
    Borcluluk=pd.DataFrame([Borcluluk],columns=Borcluluk_Basliklar)
    Borcluluk=Borcluluk.T
    return Karlılık, Büyüme, Borcluluk

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
    Degerleme_1['Degerleme 8'] = ((Degerleme_1['Fiyat']/Degerleme_1['Cari PD/DD'])*Degerleme_1['Sektör PD/DD']+(Degerleme_1['Fiyat']/Degerleme_1['Cari PD/DD']*Degerleme_1['BIST PD/DD']))/2
    Degerleme_1['Degerleme 8'] = Degerleme_1['Degerleme 8'].apply(lambda x: round(x, 2))

    Degerleme_2['Degerleme 8'] = ((Degerleme_2['Fiyat']/Degerleme_2['Cari PD/DD'])*Degerleme_2['Sektör PD/DD']+(Degerleme_2['Fiyat']/Degerleme_2['Cari PD/DD']*Degerleme_2['BIST PD/DD']))/2
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

def Hisse_Tarihsel(Hisse):
    tv = TvDatafeed()
    Hisse = tv.get_hist(symbol=Hisse,exchange='BIST',interval=Interval.in_monthly,n_bars=(1000))
    Hisse.index=pd.to_datetime(Hisse.index).to_period('M')

    Hisse = Hisse.drop(columns=['high', 'low','volume'])
    Hisse['Yüzde']=((Hisse['close']-Hisse['open'])/Hisse['open'])*100
    Hisse['Yüzde']=round(Hisse['Yüzde'],2)
    Yıllar=Hisse.index.year.drop_duplicates()

    Ocak = list(Hisse[Hisse.index.month == 1]['Yüzde'])[::-1]
    Subat = list(Hisse[Hisse.index.month == 2]['Yüzde'])[::-1]
    Mart = list(Hisse[Hisse.index.month == 3]['Yüzde'])[::-1]
    Nisan = list(Hisse[Hisse.index.month == 4]['Yüzde'])[::-1]
    Mayıs = list(Hisse[Hisse.index.month == 5]['Yüzde'])[::-1]
    Haziran = list(Hisse[Hisse.index.month == 6]['Yüzde'])[::-1]
    Temmuz = list(Hisse[Hisse.index.month == 7]['Yüzde'])[::-1]
    Agustos = list(Hisse[Hisse.index.month == 8]['Yüzde'])[::-1]
    Eylül = list(Hisse[Hisse.index.month == 9]['Yüzde'])[::-1]
    Ekim = list(Hisse[Hisse.index.month == 10]['Yüzde'])[::-1]
    Kasım = list(Hisse[Hisse.index.month == 11]['Yüzde'])[::-1]
    Aralık = list(Hisse[Hisse.index.month == 12]['Yüzde'])[::-1]
    Aralık.insert(0, np.nan)

    Hisse_Ozet = pd.DataFrame(columns=Aylar)
    Hisse_Ozet['Yıllar']=Yıllar[::-1]  
    Hisse_Ozet['Ocak']=pd.Series(Ocak)
    Hisse_Ozet['Şubat']=pd.Series(Subat)
    Hisse_Ozet['Mart']=pd.Series(Mart)
    Hisse_Ozet['Nisan']=pd.Series(Nisan)
    Hisse_Ozet['Mayıs']=pd.Series(Mayıs)
    Hisse_Ozet['Haziran']=pd.Series(Haziran)
    Hisse_Ozet['Temmuz']=pd.Series(Temmuz)
    Hisse_Ozet['Ağustos']=pd.Series(Agustos)
    Hisse_Ozet['Eylül']=pd.Series(Eylül)
    Hisse_Ozet['Ekim']=pd.Series(Ekim)
    Hisse_Ozet['Kasım']=pd.Series(Kasım)
    Hisse_Ozet['Aralık']=pd.Series(Aralık)
    
    Hisse_Ozet.loc['Ortalama Değer'] = Hisse_Ozet.mean()
    Hisse_Ozet.loc['Medyan Değer'] = Hisse_Ozet.median()
    Hisse_Ozet.loc['Standart Sapma'] = Hisse_Ozet.std()


    Hisse_Ozet_2 = pd.DataFrame(columns=Çeyrekler)
    Hisse_Ozet_2['Yıllar']=Yıllar[::-1]
    Hisse_Ozet_2['Q1']=100*(100+Hisse_Ozet['Ocak'])/100
    Hisse_Ozet_2['Q1']=Hisse_Ozet_2['Q1']*(100+Hisse_Ozet['Şubat'])/100
    Hisse_Ozet_2['Q1']=Hisse_Ozet_2['Q1']*(100+Hisse_Ozet['Mart'])/100-100

    Hisse_Ozet_2['Q2']=100*(100+Hisse_Ozet['Nisan'])/100
    Hisse_Ozet_2['Q2']=Hisse_Ozet_2['Q2']*(100+Hisse_Ozet['Mayıs'])/100
    Hisse_Ozet_2['Q2']=Hisse_Ozet_2['Q2']*(100+Hisse_Ozet['Haziran'])/100-100

    Hisse_Ozet_2['Q3']=100*(100+Hisse_Ozet['Temmuz'])/100
    Hisse_Ozet_2['Q3']=Hisse_Ozet_2['Q3']*(100+Hisse_Ozet['Ağustos'])/100
    Hisse_Ozet_2['Q3']=Hisse_Ozet_2['Q3']*(100+Hisse_Ozet['Eylül'])/100-100

    Hisse_Ozet_2['Q4']=100*(100+Hisse_Ozet['Ekim'])/100
    Hisse_Ozet_2['Q4']=Hisse_Ozet_2['Q4']*(100+Hisse_Ozet['Kasım'])/100
    Hisse_Ozet_2['Q4']=Hisse_Ozet_2['Q4']*(100+Hisse_Ozet['Aralık'])/100-100

    Hisse_Ozet_2.loc['Ortalama Değer'] = Hisse_Ozet_2.mean()
    Hisse_Ozet_2.loc['Medyan Değer'] = Hisse_Ozet_2.median()
    Hisse_Ozet_2.loc['Standart Sapma'] = Hisse_Ozet_2.std()
    
    return Hisse_Ozet, Hisse_Ozet_2

def cooling_highlight_1(val):
    color = '#ff3300' if val<0  else '#00ff00'
    return f'background-color: {color}'

def cooling_highlight_2(val):
    color = '#ff3300' if val=='Negatif'  else '#00ff00'
    return f'background-color: {color}'

Temel_Veriler_1, Temel_Veriler_2, Finansallar, Karlılık, BlcDnm=Hisse_Temel_Veriler(Hisse_Adı[0])
Karlılık, Büyüme, Borcluluk,=Hisse_Karne(Hisse_Adı[0],Finansallar,Karlılık,BlcDnm)
Degerleme_1, Degerleme_2 =Degerleme(Temel_Veriler_1,Temel_Veriler_2)
Hisse_Ozet_Aylık,Hisse_Ozet_Ceyrek=Hisse_Tarihsel(Hisse_Adı[0])

Headers = Karlılık.iloc[0]
Karlılık = Karlılık[1:]
Karlılık.columns = Headers

Büyüme = Büyüme[1:]
Büyüme.columns = Headers

Borcluluk = Borcluluk[1:]
Borcluluk.columns = Headers

Degerleme_1=Degerleme_1[1:]
Degerleme_1.columns = Headers

Degerleme_2=Degerleme_2[1:]
Degerleme_2.columns = Headers

Sapmalar=Hisse_Ozet_Aylık.tail(3).drop(['Yıllar'],axis=1)
Sapmalar=Sapmalar.head(2)
Ortalama=Sapmalar.head(1)

Sapmalar_2=Hisse_Ozet_Ceyrek.tail(3).drop(['Yıllar'],axis=1)
Sapmalar_2=Sapmalar_2.head(2)
Ortalama_2=Sapmalar_2.head(1)

st.header(str(Hisse_Adı[0])+' Dönem: '+str(BlcDnm)+' Temel Analiz Değerlendirmesi')
col1, col2 ,col3=st.columns(3)
with col1:
    st.metric(label="Güncel Fiyat", value=Degerleme_1.iat[7,0])

with col2:
    st.metric(label="Yıllıklandırılmış Verilere Göre Değerleme", value=Degerleme_1.iat[38,0], delta=Degerleme_1.iat[39,0])

with col3:
    st.metric(label="Tahmini Yıl Sonu Verilerine Göre Değerleme", value=Degerleme_2.iat[38,0], delta=Degerleme_2.iat[39,0])
    
st.header('Hisse Karnesi')
col1, col2 , col3= st.columns(3)
with col1:
    st.subheader('Karlılık')
    st.dataframe(Karlılık.style.applymap(cooling_highlight_2,subset=[Hisse_Adı[0]]),use_container_width=True)

with col2:
   st.subheader('Büyüme')
   st.dataframe(Büyüme.style.applymap(cooling_highlight_2,subset=[Hisse_Adı[0]]),use_container_width=True)

with col3:
   st.subheader('Borçluluk')
   st.dataframe(Borcluluk.style.applymap(cooling_highlight_2,subset=[Hisse_Adı[0]]),use_container_width=True)   


st.header('Hisse Geçmiş Yıllar Aylık Bazlı Ortalama Getiri')
st.dataframe(Hisse_Ozet_Aylık[:-3].style.applymap(cooling_highlight_1, subset=['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']),use_container_width=True)

st.header('Hisse Geçmiş Yıllar Hisse Aylık Ortalamalar')
st.dataframe(Sapmalar.style.applymap(cooling_highlight_1, subset=['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']),use_container_width=True)

st.header('Hisse Geçmiş Yıllar Çeyreklik Bazlı Ortalama Getiri')
st.dataframe(Hisse_Ozet_Ceyrek[:-3].style.applymap(cooling_highlight_1, subset=['Q1','Q2','Q3','Q4']),use_container_width=True)

st.header('Hisse Geçmiş Yıllar Çeyreklik Ortalamalar')
st.dataframe(Sapmalar_2.style.applymap(cooling_highlight_1, subset=['Q1','Q2','Q3','Q4']),use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader('Yıllıklandırılmış Verilere Göre')
    st.dataframe(Degerleme_1.iloc[2:].style.applymap(cooling_highlight_2,subset=[Hisse_Adı[0]]),use_container_width=True,height=1500)
with col2:
   st.subheader('Tahmini Yıl Sonu Verilerine Göre')
   st.dataframe(Degerleme_2.iloc[2:].style.applymap(cooling_highlight_2,subset=[Hisse_Adı[0]]),use_container_width=True,height=1500)
