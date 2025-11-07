from odoo.tests.common import tagged
from odoo.tools import mute_logger
from odoo.tools.translate import load_language
from .common import CommonCase
from faker import Faker
from faker.providers import ssn
from datetime import date
import json

fake = Faker('es_ES')
fake.add_provider(ssn)

def gen_form_data(type_='individual', promotional_code=None):
    data = {
        'type': type_,

        'name': fake.first_name(),
        'surname': fake.last_name(),
        'vat': fake.nif(),
        'gender': fake.random.choice(['male', 'female', 'other']),
        'birthdate': fake.date(),

        'email': fake.email(),
        'phone': fake.phone_number(),

        'street': fake.street_address(),
        'street2': fake.random.choice([fake.secondary_address(), None]),
        'city': fake.city(),
        'state': fake.state(),
        'zip': fake.postcode().lstrip('0'),
        'country': 'España',

        'project': fake.sentence(2),
        'inversion': fake.random.randint(1, 10) * 1000,
        'promotional_code': promotional_code,

        'about_us': fake.random.choice(['Redes Sociales', 'Prensa', 'Búsqueda de internet', 'Amigo/Familia', 'Charla/Evento', 'Otro', None]),
        'participation_reason': fake.random.choice([None, fake.sentence()]),

        'personal_data_policy': fake.boolean(),
        'promotions': fake.boolean(),

        'tags': None
    }

    if type_ != 'individual':
        data.update({
            'name2': fake.first_name(),
            'surname2': fake.last_name(),
            'vat2': fake.nif(),
            'gender2': fake.random.choice(['male', 'female', 'other']),
            'birthdate2': fake.date(),
        })

        if type_ == 'partnership':
            data.update({
                'name': fake.company(),
                'surname': None,
                'gender': None,
                'birthdate': None,
            })

    return data


@tagged('post_install', '-at_install')
class TestInvestment(CommonCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        load_language(cls.cr, 'es_ES')

        cls.env['res.partner.type'].create({
            'name': 'Persona física'
        })


    def check_partner(self, form_data, vat2=False, is_company=False):
        partner = self.env['res.partner'].search([
            ('vat', '=', form_data['vat'] if not vat2 else form_data['vat2'])
        ]).ensure_one()

        country = self.env['res.country'].with_context(lang='es_ES').search([
            ('name', 'ilike', form_data['country'])
        ]).ensure_one()
        state = self.env['res.country.state'].with_context(lang='es_ES').search([
            ('name', 'ilike', form_data['state']),
            ('country_id', '=', country.id)
        ]).ensure_one()

        values = {
            'firstname':            form_data['name'],
            'lastname':             form_data['surname'],
            'vat':                  form_data['vat'],
            'gender_partner':       form_data['gender'],
            'birthday':             form_data['birthdate'],

            'email':                form_data['email'],
            'phone':                form_data['phone'],

            'street':               form_data['street'],
            'street2':              form_data['street2'],
            'city':                 form_data['city'],
            'state_id':             state.id,
            'zip':                  form_data['zip'],
            'country_id':           country.id,

            'about_us':             form_data['about_us'],
            'participation_reason': form_data['participation_reason'],

            'personal_data_policy': form_data['personal_data_policy'],
            'promotions':           form_data['promotions'],

            'participant':          True,
            'person_type':          self.env['res.partner.type'].search([('name', '=', 'Persona física')]).id,
        }
        if vat2:
            values.update({
                'firstname':      form_data['name2'],
                'lastname':       form_data['surname2'],
                'vat':            form_data['vat2'],
                'gender_partner': form_data['gender2'],
                'birthday':       form_data['birthdate2']
            })
        if is_company:
            values.update({
                'firstname':      False,
                'lastname':       form_data['name'],
                'gender_partner': False,
                'birthday':       False
            })

        self.assertRecordValues(partner, [values])
        self.assertEqual(partner.partner_mail_ids[0].mail, partner.email)
        self.assertEqual(partner.partner_phone_ids[0].phone, partner.phone)

        return partner


    def check_contract(self, contract, partner, form_data, partner2_id=None):
        self.assertRecordValues(contract, [{
            'name': 'Notificación Participación',
            'partner_id': partner.id,
            'inversion': form_data['inversion'],
            'contract_date': date.today(),
            'partner_relation': form_data['type'],
            'partner_id2': partner2_id,
        }])


@tagged('post_install', '-at_install')
class TestInvestmentIndividual(TestInvestment):

    @mute_logger('odoo.addons.base_rest.http', 'odoo.http')
    def test_investment_individual(self):
        form_data = gen_form_data()

        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat'])]), 0)

        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        partner = self.check_partner(form_data)
        self.assertFalse(partner.minor)
        self.assertFalse(partner.marriage)

        contract = self.env['contract.participation'].search([('partner_id', '=', partner.id)])
        self.check_contract(contract, partner, form_data)

        return partner, contract


    @mute_logger('odoo.addons.base_rest.http', 'odoo.http')
    def test_investment_individual_wrong_vat(self):
        vat = fake.numerify('########')
        form_data = gen_form_data() | { 'vat': vat }

        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 400)
        self.assertEqual(
            request.json()['description'],
            f'<p><br>The VAT number [{vat}] for partner [{form_data["name"]} {form_data["surname"]}] does not seem to be valid. <br>Note: the expected format is ESA12345674</p>'
        )
        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat'])]), 0)


    @mute_logger('odoo.addons.base_rest.http', 'odoo.http')
    def test_investment_individual_wrong_email(self):
        form_data = gen_form_data() | { 'email': fake.lexify('????????') }

        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 400)
        self.assertIn('email', request.json()['description'])
        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat'])]), 0)


    @mute_logger('odoo.addons.base_rest.http', 'odoo.http')
    def test_investment_individual_wrong_state(self):
        state = fake.lexify('????????')
        form_data = gen_form_data() | { 'state': state }

        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 400)
        self.assertEqual(
            request.json()['description'],
            f'<p>Provincia no encontrada: [{state}]</p>'
        )
        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat'])]), 0)


    @mute_logger('odoo.addons.base_rest.http', 'odoo.http')
    def test_investment_individual_wrong_country(self):
        country = fake.lexify('????????')
        form_data = gen_form_data() | { 'country': country }

        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 400)
        self.assertEqual(
            request.json()['description'],
            f'<p>País no encontrado: [{country}]</p>'
        )
        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat'])]), 0)


@tagged('post_install', '-at_install')
class TestInvestmentMinor(TestInvestment):

    @mute_logger('odoo.addons.base_rest.http')
    def test_investment_minor(self):
        form_data = gen_form_data('minor')

        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat'])]), 0)

        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 200)

        partner = self.check_partner(form_data)
        tutor = self.check_partner(form_data, vat2=True)

        self.assertTrue(partner.minor)
        self.assertEqual(partner.tutor.id, tutor.id)

        contract = self.env['contract.participation'].search([('partner_id', '=', partner.id)])
        self.check_contract(contract, partner, form_data, tutor.id)


    @mute_logger('odoo.addons.base_rest.http')
    def test_investment_minor_wrong(self):
        form_data = gen_form_data('minor') | { 'vat2': fake.numerify('########') }

        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat2'])]), 0)

        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 400)
        self.assertIn('The VAT number', request.json()['description'])
        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat2'])]), 0)


    @mute_logger('odoo.addons.base_rest.http')
    def test_investment_minor_same_vat(self):
        form_data = gen_form_data('minor')
        form_data.update(vat2=form_data['vat'])

        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat2'])]), 0)

        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 200)

        vat_minor = f'{form_data["vat"]}_menor_{form_data["name"]}'
        partner = self.check_partner(form_data | { 'vat': vat_minor })
        tutor = self.check_partner(form_data, vat2=True)

        self.assertTrue(partner.minor)
        self.assertEqual(partner.tutor.id, tutor.id)

        contract = self.env['contract.participation'].search([('partner_id', '=', partner.id)])
        self.check_contract(contract, partner, form_data, tutor.id)


@tagged('post_install', '-at_install')
class TestInvestmentMarriage(TestInvestment):

    @mute_logger('odoo.addons.base_rest.http')
    def test_investment_marriage(self):
        form_data = gen_form_data('marriage')

        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat'])]), 0)

        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 200)

        partner = self.check_partner(form_data)
        conyuge = self.check_partner(form_data, vat2=True)

        self.assertEqual(partner.marriage.id, conyuge.id)
        self.assertEqual(conyuge.marriage.id, partner.id)

        contract = self.env['contract.participation'].search([('partner_id', '=', partner.id)])
        self.check_contract(contract, partner, form_data, conyuge.id)


    @mute_logger('odoo.addons.base_rest.http')
    def test_investment_marriage_same_vat(self):
        form_data = gen_form_data('marriage')
        form_data.update(vat2=form_data['vat'])

        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat'])]), 0)

        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 400)
        self.assertEqual(
            request.json()['description'],
            f'<p>Los dos DNI/NIE no pueden ser iguales: [{form_data["vat"]}]</p>'
        )
        self.assertEqual(self.env['res.partner'].search_count([('vat', '=', form_data['vat'])]), 0)


@tagged('post_install', '-at_install')
class TestInvestmentDiscount(TestInvestmentIndividual):

    @mute_logger('odoo.addons.base_rest.http')
    def test_investment_discount(self):
        inviter, inviter_contract = super().test_investment_individual()

        form_data = gen_form_data(promotional_code=fake.lexify('????????'))

        # random promotional code
        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 400)

        # valid promotional code but no active contracts
        form_data = gen_form_data(promotional_code=inviter.promotional_code)
        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 400)

        # valid promotional code and active contract
        stage_active = (self.env['contract.participation.stage']
            .with_context(lang='en_US')
            .search([('name', '=', 'Active')]))
        inviter_contract.write({ 'stage_id': stage_active.id })
        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 200)
        self.assertTrue(json.loads(request.json()['detail'])['discount'])

        partner = self.check_partner(form_data)
        self.assertEqual(partner.inviter_id.id, inviter.id)
        self.assertEqual(len(inviter.friend_ids), 1)
        self.assertEqual(inviter.friend_ids[0].friend_id.id, partner.id)

        contract = self.env['contract.participation'].search([('partner_id', '=', partner.id)])
        self.check_contract(contract, partner, form_data)

        # existing participant
        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 400)
        self.assertEqual(
            request.json()['description'],
            f'<p>Código promocional sólo válido para nuevos participantes: [{form_data["promotional_code"]}]</p>'
        )

        return inviter, partner, form_data


    @mute_logger('odoo.addons.base_rest.http')
    def test_investment_discount_cancelled(self):
        inviter, partner, form_data = self.test_investment_discount()

        # with cancelled contracts
        stage_inactive = (self.env['contract.participation.stage']
            .with_context(lang='en_US')
            .search([('name', '=', 'Inactive - Cancel')]))
        partner.contract_ids.write({ 'stage_id': stage_inactive.id })

        request = self.http('POST', '/api/investments', form_data, { 'api_key': self.api_key })
        self.assertEqual(request.status_code, 200)
        self.assertTrue(json.loads(request.json()['detail'])['discount'])

        contract = self.env['contract.participation'].search([
            ('partner_id', '=', partner.id),
            ('stage_id', '!=', stage_inactive.id)
        ])
        self.check_contract(contract, partner, form_data)


# TODO test if existing partner doesn't update data
# TODO test with type = partnership
