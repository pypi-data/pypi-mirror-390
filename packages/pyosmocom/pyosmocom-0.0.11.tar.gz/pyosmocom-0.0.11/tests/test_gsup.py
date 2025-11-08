#!/usr/bin/env python3

import unittest
from pprint import pprint as pp

from osmocom.utils import b2h, h2b
from osmocom.gsup.message import *


class Test_GSUP(unittest.TestCase):
    testdatasets = [
        {
            'desc': 'SendAuthInfo Req (osmo-msc)',
            'encoded': h2b('08010800010100000000f1'),
        }, {
            'desc': 'SendAuthInfo Req (dia2gsup)',
            'encoded': h2b('08010862420200000000f12901032a0103'),
        }, {
            'desc': 'SendAuthInfo Req (epdg, resync)',
            'encoded': h2b('08010862424201495149f505121001001102f121120908696e7465726e6574260e95f371a6b471f222d65eabd25dec2010a8a4f119881035f3be2b72e2a09aea99'),
        }, {
            'desc': 'SendAuthInfo Res',
            'encoded': h2b('0a010800010100000000f10362201020080c3818183b522614162c07601d0d2104e91e477722083b0f999e42198874231011329aae8e8d2941bb226b2061137c582410740d62df9803eebde5120acf358433d02510f11b89a2a8be00001f9c526f3d75d44c27086a91970e838fd0790362201020080c3818183b522614162c07601d0d2104e91e477722083b0f999e42198874231011329aae8e8d2941bb226b2061137c582410740d62df9803eebde5120acf358433d02510f11b89a2a8bf0000bcbfa23f0496acc027086a91970e838fd0790362201020080c3818183b522614162c07601d0d2104e91e477722083b0f999e42198874231011329aae8e8d2941bb226b2061137c582410740d62df9803eebde5120acf358433d02510f11b89a2a8bc00009ce36667cb8de7b727086a91970e838fd0790362201020080c3818183b522614162c07601d0d2104e91e477722083b0f999e42198874231011329aae8e8d2941bb226b2061137c582410740d62df9803eebde5120acf358433d02510f11b89a2a8bd00007647a225559454bf27086a91970e838fd0790362201020080c3818183b522614162c07601d0d2104e91e477722083b0f999e42198874231011329aae8e8d2941bb226b2061137c582410740d62df9803eebde5120acf358433d02510f11b89a2a8ba00005ca737b9b66e8f9227086a91970e838fd079')
        }, {
            'desc': 'SendAuthInfo Err',
            'encoded': h2b('09010862021131107541f2020102'),
        }, {
            'desc': 'UpdateLocation Req',
            'encoded': h2b('04010800010100000000f1280101'),
        }, {
            'desc': 'InsertSubscriberData Req PS',
            'encoded': h2b('10010800010100000000f10804039900f105071001011202012a280101'),
        }, {
            'desc': 'InsertSubscriberData Req CS',
            'encoded': h2b('10010809710000004107f50803020110280102'),
        }, {
            'desc': 'InsertSubscriberData Res',
            'encoded': h2b('12010800010100000000f1'),
        }, {
            'desc': 'Check IMEI Req',
            'encoded': h2b('30010809710000004107f550090853897760820568f00a0101'),
        }, {
            'desc': 'Check IMEI Res',
            'encoded': h2b('32010809710000004107f5510100'),
        }, {
            'desc': 'UpdateLocation Res',
            'encoded': h2b('06010800010100000000f1'),
        }, {
            'desc': 'SS Req',
            'encoded': h2b('20010809711195876385f83004200000013101013515a11302010502013b300b04010f0406aa510c061b01'),
        }, {
            'desc': 'E Close',
            'encoded': h2b('47010809710000004107f50a0104600c6d73632d3236322d34322d30610c6d73632d3930312d37302d30'),
        }, {
            'desc': 'Purge MS Req',
            'encoded': h2b('0c010862424201495149f5280101'),
        }, {
            'desc': 'Purge MS Res',
            'encoded': h2b('0e010862424201495149f50700'),
        }, {
            'desc': 'ePDG tunnel request',
            'encoded': h2b('50010862424201495149f5280101150780000d00000c000a0105'),
        }, {
            'desc': 'ePDG tunnel response',
            'encoded': h2b('52010862424201495149f50400051f1001001106f121c0a80002120908696e7465726e65741303000000140200000a0105150f80000d0401020304000c0405060708'),
        },

    ]

    def test_gsup_encdec(self):
        for t in Test_GSUP.testdatasets:
            with self.subTest(desc=t['desc']):
                encoded_bin = t['encoded']
                parsed = GsupMessage.from_bytes(encoded_bin)
                parsed_d = parsed.to_dict()
                pp(parsed_d)
                msg2 = GsupMessage.from_dict(parsed_d)
                #print(msg2.to_dict())
                #self.assertEqual(parsed, msg2)
                re_encoded = msg2.to_bytes()
                self.assertEqual(b2h(encoded_bin), b2h(re_encoded))


if __name__ == '__main__':
    unittest.main()
