#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import socket
import requests
from dnspod import apicn
from pprint import pprint


config_file = os.path.join(os.path.dirname(__file__), 'config.json')
config = json.load(open(config_file))

domain = config['domain']
record_name = config['record_name']
login_token = config['login_token']


def getip():
    resp = requests.get('https://api.ipify.org?format=json')
    return resp.json()['ip']


def main():
    # please refer to:
    # https://support.dnspod.cn/Kb/showarticle/tsid/227/
    print("DomainId")
    api = apicn.DomainId(domain=domain, login_token=login_token)
    domain_info = api()
    domain_id = domain_info['domains']['id']
    print(domain_id)


    print("RecordList")
    api = apicn.RecordList(domain_id, login_token=login_token)
    record_list = api()

    record_id = None
    old_ip = None
    for rec in record_list['records']:
        name = rec['name']
        if name == record_name:
            record_id = rec['id']
            old_ip = rec['value']
            break

    ip = getip()
    if ip == old_ip:
        print('ip no change')
        return

    print(ip, record_id)

    if not record_id:
        print("RecordCreate")
        api = apicn.RecordCreate(record_name, "A", '默认'.encode("utf8"), ip, 600, domain_id=domain_id, login_token=login_token)
        record = api().get("record", {})
        record_id = record.get("id")
        print("Record id", record_id)
    else:
        print("RecordModify")
        api = apicn.RecordModify(
            record_id,
            sub_domain=record_name,
            record_type="A",
            record_line='默认'.encode("utf8"),
            value=ip,
            ttl=600,
            domain_id=domain_id,
            login_token=login_token)
        record = api().get("record", {})
        record_id = record.get("id")
        print("Record id", record_id)

if __name__ == '__main__':
    main()
