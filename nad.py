#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Ett litet script för att hämta data på Arkivnivå från den Nationella Arkivdatabasen (NAD)

Användning:
$ python nad.py --hk <huvudkategori> --p <antal sidor att iterer> --a <Arkivinstitution> --f <filnamn>

ex.
$ python nad.py --hk 7 --p 20 --a Landsakrivet+i+Lund --f utfil.csv
$ python nad.py --hk 6 --p 30 --a Region+och+Stadsarkivet+Göteborg --f utfil.csv
Huvudkategorier:
0 = Ej fastställt
1 = Statlig myndighet
2 = Kommunal myndighet
3 = Person (släkt, samlare)
4 = Gård
5 = By
6 = Förening
7 = Företag
9 = Övriga
'''

import requests
import codecs
from bs4 import BeautifulSoup
from time import sleep
import optparse
import sys
if (sys.version_info < (3, 0)):
    reload(sys)  # Reload does the trick!
    sys.setdefaultencoding('UTF8')


op = optparse.OptionParser()
op.add_option('--hk', dest="hk", choices=['0', '1', '2', '3', '4','5','6','7','9'], default='6')
op.add_option('--p', dest="p", default=20)
op.add_option('--a', dest="a", default=u'Landsarkivet+i+Göteborg')
op.add_option('--f', dest="f", default=u'output.csv')
opts, args = op.parse_args()
headers = u'no; arkiv; datering; omfång; villkor; villkorsanm; tillståndsgivare; sökmedel; länk'

with codecs.open(opts.f,'a', 'utf-8') as f:
    f.write(headers)
    f.write('\n')
    for page in range(1,int(opts.p)):

        print (opts.p)
        r = requests.get(u'https://sok.riksarkivet.se/nad?EndastDigitaliserat=false&BegransaPaTitelEllerNamn=false&Arkivinstitution={}&Typ=Arkiv&Huvudkategori={}&AvanceradSok=true&typAvLista=Standard&page={}&FacettState=undefined%3Ac%7C#tab'.format(opts.a,opts.hk,page))

        soup = BeautifulSoup(r.content, 'html.parser' )

        data = {}

        for div in soup.find_all('div',{"class": "span12"}):
            for divx in div.find_all('div'):
                if divx.string:
                    print (divx.string)
                    data[u'no'] = divx.string.replace('. Arkiv','')
                for href in divx.find_all('a', href=True):
                    print (href.string)
                    data['arkiv'] = (href.string)
                    r = requests.get('https://sok.riksarkivet.se/{}'.format(href['href']))
                    if r.status_code != 200:
                        sleep(120)
                        r = requests.get('https://sok.riksarkivet.se/{}'.format(href['href']))


                    soup = BeautifulSoup(r.content, 'html.parser')
                    table = soup.find('table', attrs={'class': 'cssTabViewDisplay'})
                    for tr in table.find_all('tr'):
                        td = tr.find('td', attrs={'class': 'subTblCellLabel'})
                        td2 = tr.find('td', attrs={'class': 'subTblGridCell'})
                        td3 = tr.find('td', attrs={'class': 'subTblCell'})
                        if td  and td3:
                            if u"Tillståndsgivare" in td.string:
                                data[u'tillståndsgivare'] = td3.string

                            elif u"Datering" in td.string:
                                data[u'datering'] = td3.string

                            elif u"Villkor" in td.string:
                                data[u'villkor'] = td3.string

                            elif u"Sökmedel" in td.string:
                                data[u'sökmedel'] = td3.string

                            elif u"Villkorsanm" in td.string:
                                data[u'villkorsanm'] = td3.string



                        if td and td2:
                                if u"Tillståndsgivare" in td.string:
                                    data[u'tillståndsgivare'] = td2.string

                                elif u"Datering" in td.string:
                                    dateValue = u''
                                    for v in td3.find_all('td', attrs={'class': 'subTblGridCell'}):
                                        if v.string:
                                            dateValue = dateValue + v.string
                                    #print dateValue
                                    data[u'datering'] = dateValue

                                elif u"Villkor" in td.string:
                                    data[u'villkor'] = td2.string

                                elif u"Sökmedel" in td.string:
                                    data[u'sökmedel'] = td2.string
                                elif u"Omfång" in td.string:
                                    data[u'omfång'] = td2.string

                                elif u"Villkorsanm" in td.string:
                                    data[u'villkorsanm'] = td2.string


                    data[u'länk'] = (href['href'])

                    output =  u'{};{};{};{};{};{};{};{};{}'.format(data[u'no'],data[u'arkiv'],
                                                                data[u'datering'] if u'datering' in data else '',
                                                                data[u'omfång'] if u'omfång' in data else '',
                                                                data[u'villkor'] if u'villkor' in data else '',
                                                                data[u'villkorsanm'] if u'villkorsanm' in data else '',
                                                                data[u'tillståndsgivare'] if u'tillståndsgivare' in data else '',
                                                                data[u'sökmedel'] if u'sökmedel' in data else '',
                                                                data[u'länk'] )
                    f.write(output)
                    f.write('\n')
                    data ={}
