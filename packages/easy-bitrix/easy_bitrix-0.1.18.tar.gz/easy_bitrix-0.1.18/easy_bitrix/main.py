import asyncio
import pprint
import json

from .bitrix import Bitrix24
from .options import RequestOptions
from .bitrix_objects import Deal, Contact, Item
from .operations import FilterOperation, OrderOperations, Logic
from .parameters import Fields
from .oauth import OAuth

site_name = 'site_name'
user_id = 1
webhook = 'webhook'
client_id = 'app.zzz'
client_secret = 'LJSl0lNB76B5YY6u0YVQ3AW0DrVADcRTwVr4y99PXU1BWQybWK'
code = 'avmocpghblyi01m3h42bljvqtyd19sw1'

def main():
    options = RequestOptions(user_id=user_id, webhook_url=webhook, high_level_domain='ru')
    bitrix = Bitrix24(bitrix_address=site_name)
    response = bitrix.request(param=Item.get_list(type_id=140,
                                                  select=[Item.SET_UF_KEY('CRM_8_1739771708'),
                                                          Item.SET_UF_KEY('CRM_8_1629390426202'),
                                                          Item.SET_UF_KEY('CRM_8_1629390449135'),
                                                          Item.SET_UF_KEY('CRM_8_1629390470080'),
                                                          Item.SET_UF_KEY('CRM_8_1723706718320')],
                                                  filter=[FilterOperation.IN(Item.SET_UF_KEY_VALUE('CRM_8_1739771708', [55238]))],
                                                  use_original_uf_names=True),
                              options=options)
    # response = bitrix.request(param=Item.get(type_id=140, id=38, use_original_uf_names=True), options=options)
    # with open('result_select_1.json', mode='w', encoding='utf-8') as fp:
    #     fp.write(response.raw_data)


main()
