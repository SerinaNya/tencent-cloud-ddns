from os import getenv
from typing import Tuple

import netifaces
import requests
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.dnspod.v20210323 import dnspod_client, models

secret_id = getenv('TENCENT_CLOUD_SECRET_ID')
secret_key = getenv('TENCENT_CLOUD_SECRET_KEY')

cred = credential.Credential(secret_id, secret_key)
httpProfile = HttpProfile()
httpProfile.endpoint = 'dnspod.tencentcloudapi.com'

clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile
client = dnspod_client.DnspodClient(cred, '', clientProfile)


def getRecordInfo(domain: str, subdomain: str, record_type: str) -> Tuple[str, int, str]:
    req = models.DescribeRecordListRequest()
    req._deserialize(
        {'Domain': domain, 'Subdomain': subdomain, 'RecordType': record_type})
    resp = client.DescribeRecordList(req)
    record: models.RecordListItem = resp.RecordList[0]
    return record.Value, record.RecordId, record.Line


def modifyRecord(domain, record_id, record_line, subdomain, record_type, record_value):
    req = models.ModifyRecordRequest()
    params = {
        'Domain': domain,
        'RecordId': record_id,
        'RecordLine': record_line,
        'SubDomain': subdomain,
        'RecordType': record_type,
        'Value': record_value
    }
    req._deserialize(params)
    resp = client.ModifyRecord(req)
    print(
        f'DNS was updated successfully! Tencent Cloud API RequestId: {resp.RequestId}')


def getPublicIPv4Addr():
    ip_addr = requests.get('https://checkip.amazonaws.com/').text.strip()
    print(f'Your public IPv4 address is {ip_addr}')
    return ip_addr


def getIPv6Addr():
    interface = getenv('INTERFACE', 'eth0')
    ip_addr = netifaces.ifaddresses(
        interface)[netifaces.AF_INET6][0]['addr']
    print(f'Your IPv6 address is {ip_addr}')
    return ip_addr


def main():
    domain = getenv('DOMAIN')
    subdomain = getenv('SUBDOMAIN')
    record_type = getenv('RECORD_TYPE')

    if record_type == 'A':
        ip_addr = getPublicIPv4Addr()
    elif record_type == 'AAAA':
        ip_addr = getIPv6Addr()
    else:
        raise ValueError(
            'RECORD_TYPE only supports A and AAAA, must be upcase')

    record_value, record_id, record_line = getRecordInfo(
        domain, subdomain, record_type)

    if record_value != ip_addr:
        modifyRecord(domain, record_id, record_line,
                     subdomain, record_type, ip_addr)
    else:
        print('DNS has already been set correctly.')


if __name__ == '__main__':
    main()
