#!/usr/bin/python3

import os
import sys
import re
import json
import time
import requests
import argparse
import tldextract
from colored import fg, bg, attr

w_blacklist = [ 'privacy', 'redacted', 'destination', 'dnstination', 'west', 'select request email', 'markmonitor', 'nameshield', 'service noms de domaine', 'technical manager' ]


# https://twitter.com/intigriti/status/1639610098954932225
def searchDomainBuiltwith( _domain ):
    global _verbose, t_data

    if _verbose:
        sys.stdout.write( '%s[+] calling builtwith targeting domain%s\n' % (fg('green'),attr(0)) )

    try:
        url = 'https://builtwith.com/relationships/'+_domain
        r = requests.get( url )
    except Exception as e:
        sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        return

    rgxp = r'("https://builtwith.com/relationships/[^"]+)'
    matches = re.findall( rgxp, r.text, re.IGNORECASE )

    if matches:
        for m in matches:
            if not '/tag/' in m:
                domain = m.replace('https://builtwith.com/relationships/','').replace('"','')
                domain = domain.lower()
                if not domain in t_data['domains']:
                    t_data['domains'].append( domain )
                    print( domain )


def searchDomainCrtsh( _domain ):
    global _verbose, t_data

    if _verbose:
        sys.stdout.write( '%s[+] calling crtsh targeting domain%s\n' % (fg('green'),attr(0)) )


    parse = tldextract.extract( _domain )
    # print(parse)
    url = 'https://crt.sh/?q=%25'+parse.domain+'%25&output=json'
    if _verbose:
        sys.stdout.write( '%s[+] %s%s\n' % (fg('white'),url,attr(0)) )

    try:
        r = requests.get( url )
        t_json = r.json()
        # print(t_json)
    except Exception as e:
        sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        return

    # f = open("crtsh.json")
    # t_json = json.load(f)
    # f.close()

    for item in t_json:
        if 'common_name' in item:
            try:
                parse = tldextract.extract( item['common_name'] )
                domain = parse.domain + '.' + parse.suffix
                domain = domain.lower()
                if not domain in t_data['domains']:
                    t_data['domains'].append( domain )
                    print( domain )
            except Exception as e:
                pass


def searchCompanyWhoxy( _whoxy_key ):
    global _verbose, t_data

    if _verbose:
        sys.stdout.write( '%s[+] whoxy key found, calling whoxy api targeting company%s\n' % (fg('green'),attr(0)) )

    for company in t_data['companies']:

        confirm = input("Grab domains registered with company \""+company+"\"? (y/n) ")
        if not confirm.lower() == "y":
            if _verbose:
                sys.stdout.write( '%s[-] skip company: %s%s\n' % (fg('red'),company,attr(0)) )
            continue

        new = 0
        page = 1
        company = company.replace( ' ', '+' )
        if _verbose:
            sys.stdout.write( '%s[+] search for company: %s%s\n' % (fg('green'),company,attr(0)) )

        while True:
            time.sleep(2)
            url = 'https://api.whoxy.com/?key='+_whoxy_key+'&reverse=whois&company='+company+'&mode=micro&page='+str(page)
            # url = 'https://api.whoxy.com/?key='+_whoxy_key+'&search_identifier=company&search_keyword='+company+'&mode=micro&page='+str(page)
            page = page + 1
            if _verbose:
                sys.stdout.write( '%s[+] %s%s\n' % (fg('white'),url,attr(0)) )

            try:
                r = requests.get( url )
                t_json = r.json()
                # print(t_json)
            except Exception as e:
                sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
                continue

            if 'search_result' in t_json and len(t_json['search_result']):
                for result in t_json['search_result']:
                    if not result['domain_name'] in t_data['domains']:
                        new = new + 1
                        t_data['domains'].append( result['domain_name'] )
                        print( result['domain_name'] )
            else:
                break

        if _verbose:
            sys.stdout.write( '%s[+] new domain for company %s: %d%s\n' % (fg('green'),company,new,attr(0)) )



def searchEmailWhoxy( _whoxy_key ):
    global _verbose, t_data

    if _verbose:
        sys.stdout.write( '%s[+] whoxy key found, calling whoxy api targeting email%s\n' % (fg('green'),attr(0)) )

    for email in t_data['emails']:

        confirm = input("Grab domains registered with email \""+email+"\"? (y/n) ")
        if not confirm.lower() == "y":
            if _verbose:
                sys.stdout.write( '%s[-] skip email: %s%s\n' % (fg('red'),email,attr(0)) )
            continue

        sys.stdout.write( '%s[+] search for email: %s%s\n' % (fg('green'),email,attr(0)) )

        new = 0
        page = 1
        if _verbose:
            sys.stdout.write( '%s[+] search for email: %s%s\n' % (fg('green'),email,attr(0)) )

        while True:
            time.sleep(2)
            url = 'https://api.whoxy.com/?key='+_whoxy_key+'&reverse=whois&email='+email+'&mode=micro&page='+str(page)
            # url = 'https://api.whoxy.com/?key='+_whoxy_key+'&search_identifier=email&search_keyword='+email+'&mode=micro&page='+str(page)
            page = page + 1
            if _verbose:
                sys.stdout.write( '%s[+] %s%s\n' % (fg('white'),url,attr(0)) )

            try:
                r = requests.get( url )
                t_json = r.json()
                # print(t_json)
            except Exception as e:
                sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
                continue

            if 'search_result' in t_json and len(t_json['search_result']):
                for result in t_json['search_result']:
                    if not result['domain_name'] in t_data['domains']:
                        new = new + 1
                        t_data['domains'].append( result['domain_name'] )
                        print( result['domain_name'] )
            else:
                break

        if _verbose:
            sys.stdout.write( '%s[+] new domain for email %s: %d%s\n' % (fg('green'),email,new,attr(0)) )


# https://www.whoxy.com/reverse-whois/demo.php
def searchDomainWhoxy( _domain, _whoxy_key ):
    global _verbose, t_data

    if _verbose:
        sys.stdout.write( '%s[+] whoxy key found, calling whoxy api targeting domain%s\n' % (fg('green'),attr(0)) )

    url = 'https://api.whoxy.com/?key='+_whoxy_key+'&whois='+_domain
    if _verbose:
        sys.stdout.write( '%s[+] %s%s\n' % (fg('white'),url,attr(0)) )

    try:
        r = requests.get( url )
        t_json = r.json()
        # print(t_json)
    except Exception as e:
        sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        return

    extractDatasWhoxy( t_json )
    if _verbose:
        print(t_data['companies'])
        print(t_data['emails'])


def is_blacklisted( str ):
    for wbl in w_blacklist:
        if wbl in str.lower():
            return True
    return False


def extractDatasWhoxy( t_json ):
    global _verbose, t_data

    for index in ['technical_contact','registrant_contact','administrative_contact']:
        if index in t_json:
            if index in t_json and len(t_json[index]):
                if 'company_name' in t_json[index] and not is_blacklisted(t_json[index]['company_name']) and not t_json[index]['company_name'] in t_data['companies']:
                    t_data['companies'].append( t_json[index]['company_name'] )
                if 'email_address' in t_json[index] and not is_blacklisted(t_json[index]['email_address']) and not t_json[index]['email_address'] in t_data['emails']:
                    t_data['emails'].append( t_json[index]['email_address'] )

    return


parser = argparse.ArgumentParser()
parser.add_argument( "-e","--email",help="email you are looking for (required or -d or -c)" )
parser.add_argument( "-b","--builtwith",help="use builtwith as an additional source", action="store_true" )
parser.add_argument( "-c","--company",help="company you are looking for (required or -d or -e)" )
parser.add_argument( "-d","--domain",help="domain you already know (required or -c)" )
parser.add_argument( "-k","--key",help="whoxy api key (required)" )
parser.add_argument( "-s","--source",help="list of sources separated by comma, available sources are: whoxy (default=whoxy)" )
# parser.add_argument( "-s","--source",help="list of sources separated by comma, available sources are: builtwith,crtsh,whoxy (default=whoxy)" )
parser.add_argument( "-v","--verbose",help="enable verbose mode, default off", action="store_true" )
parser.parse_args()
args = parser.parse_args()

t_data = { 'domains':[], 'companies':[], 'emails':[] }

if args.verbose:
    _verbose = True
else:
    _verbose = False

if args.company:
    t_data['companies'].append( args.company )

if args.email:
    t_data['emails'].append( args.email )

if args.domain:
    _domain = args.domain
else:
    _domain = False

if not _domain and not len(t_data['companies']) and not len(t_data['emails']):
    parser.error( 'domain or company or email required' )

if not args.source:
    t_sources = "whoxy"
else:
    t_sources = args.source.split(',')

if "whoxy" in t_sources:
    if args.key:
        _whoxy_key = args.key
    else:
        _whoxy_key =  os.getenv('WHOXY_KEY')
        if not _whoxy_key:
            _whoxy_key = ""

if _domain:
    if _verbose:
        sys.stdout.write( '%s[+] search for domain: %s%s\n' % (fg('green'),_domain,attr(0)) )

    # if "crtsh" in t_sources:
    #     searchDomainCrtsh( _domain )

    # if "builtwith" in t_sources:
    #     searchDomainBuiltwith( _domain )

    if "whoxy" in t_sources:
        if len(_whoxy_key):
            searchDomainWhoxy( _domain, _whoxy_key )


if "whoxy" in t_sources:
    if len(_whoxy_key) and len(t_data['companies']):
        searchCompanyWhoxy( _whoxy_key )

    if len(_whoxy_key) and len(t_data['emails']):
        searchEmailWhoxy( _whoxy_key )
