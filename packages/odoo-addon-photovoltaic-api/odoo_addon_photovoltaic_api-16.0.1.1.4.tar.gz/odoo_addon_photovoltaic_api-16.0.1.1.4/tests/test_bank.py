from odoo.tests.common import tagged
from odoo.tools import mute_logger
from .test_account import TestLogin, VAT
from faker import Faker
import re

fake = Faker('es_ES')

@tagged('post_install', '-at_install')
class TestBankAccount(TestLogin):

    @mute_logger('odoo.addons.base_rest.http')
    def test_bank_accounts(self):
        super().test_login_correct()

        request = self.http('GET', '/api/bank_account/', {}, { 'Authorization': f'Bearer {self.jwt_token}' })
        self.assertTrue(request.ok)
        self.assertEqual(request.json(), [])

        iban = fake.iban()
        iban_formatted = ' '.join(re.findall('....', iban))
        request = self.http('POST', '/api/bank_account/', { 'acc_number': iban }, { 'Authorization': f'Bearer {self.jwt_token}' })
        self.assertTrue(request.ok)
        bank_account = request.json()
        self.assertEqual(bank_account['acc_number'], iban_formatted)

        request = self.http('GET', f'/api/bank_account/{bank_account["id"]}', {}, { 'Authorization': f'Bearer {self.jwt_token}' })
        self.assertTrue(request.ok)
        self.assertEqual(request.json(), { 'id': bank_account['id'], 'acc_number': iban_formatted })

        new_iban = fake.iban()
        new_iban_formatted = ' '.join(re.findall('....', new_iban))
        request = self.http('PUT', f'/api/bank_account/{bank_account["id"]}', { 'acc_number': new_iban }, { 'Authorization': f'Bearer {self.jwt_token}' })
        self.assertTrue(request.ok)
        self.assertEqual(request.json()['acc_number'], new_iban_formatted)

        request = self.http('GET', '/api/bank_account/', {}, { 'Authorization': f'Bearer {self.jwt_token}' })
        self.assertTrue(request.ok)
        self.assertEqual(request.json(), [{ 'id': bank_account['id'], 'acc_number': new_iban_formatted }])

        request = self.http('DELETE', f'/api/bank_account/{bank_account["id"]}', {}, { 'Authorization': f'Bearer {self.jwt_token}' })
        self.assertTrue(request.ok)
        self.assertEqual(request.json(), {})

        request = self.http('GET', '/api/bank_account/', {}, { 'Authorization': f'Bearer {self.jwt_token}' })
        self.assertTrue(request.ok)
        self.assertEqual(request.json(), [])

        request = self.http('DELETE', f'/api/bank_account/{bank_account["id"]}', {}, { 'Authorization': f'Bearer {self.jwt_token}' })
        self.assertEqual(request.status_code, 404)
        self.assertEqual(request.json(), {'code': 404, 'name': 'Not Found'})

        # TODO check deleting bank account used in a contracts
