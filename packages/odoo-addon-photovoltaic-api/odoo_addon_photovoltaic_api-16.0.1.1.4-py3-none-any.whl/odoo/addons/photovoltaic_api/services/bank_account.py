from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.fields import Command

from ..pydantic_models.bank_account import BankAccountIn, BankAccountOut


class BankAccountService(Component):
    _inherit = 'base.rest.service'
    _name = 'bank_account.service'
    _usage = 'bank_account'
    _collection = 'photovoltaic_api.services'


    @restapi.method(
        [(['/<int:_id>'], 'GET')],
        output_param=restapi.PydanticModel(BankAccountOut)
    )
    def get(self, _id):
        try:
            account = self.env['res.partner.bank'].browse(_id)
            return BankAccountOut(id=account.id, acc_number=account.acc_number)

        except AccessError:
            # Return 404 even if it is from a different user
            # to not leak information
            raise MissingError('Access error')


    @restapi.method(
        [(['/'], 'GET')],
        output_param=restapi.PydanticModelList(BankAccountOut)
    )
    def search(self):
        accounts = self.env.user.partner_id.bank_ids
        # Contracts with 'Crece Solar' activated have a placeholder account (with 'CRECE SOLAR as it's acc number)
        # that shouldn't be shown to the user
        return [BankAccountOut.model_validate(a) for a in accounts if 'CRECE SOLAR' not in a.acc_number]


    @restapi.method(
        [(['/<int:_id>'], 'PUT')],
        input_param=restapi.PydanticModel(BankAccountIn),
        output_param=restapi.PydanticModel(BankAccountOut)
    )
    def update(self, _id, account_in):
        try:
            account = self.env['res.partner.bank'].browse(_id)
            self.env.user.partner_id.message_post(body=f'Cuenta bancaria: {account.acc_number} ➔ {account_in.acc_number}')
            account.write(account_in.model_dump())
            return BankAccountOut(id=account.id, acc_number=account.acc_number)

        except AccessError:
            # Return 404 even if it is from a different user
            # to not leak information
            raise MissingError('Access error')


    @restapi.method(
        [(['/'], 'POST')],
        input_param=restapi.PydanticModel(BankAccountIn),
        output_param=restapi.PydanticModel(BankAccountOut)
    )
    def create(self, account_in):
        params = {
            'partner_id': self.env.user.partner_id.id,
            **account_in.model_dump()
        }

        account = self.env['res.partner.bank'].create(params)
        self.env.user.partner_id.message_post(body=f'Cuenta bancaria {account.acc_number} creada')
        return BankAccountOut(id=account.id, acc_number=account.acc_number)


    @restapi.method(
        [(['/<int:_id>'], 'DELETE')],
    )
    def delete(self, _id):
        try:
            account = self.env['res.partner.bank'].browse(_id)
            if self.env['contract.participation'].search_count([('bank_account_id', '=', _id)]) > 0:
                # Account is used by at least 1 contract
                raise UserError('Bad request')
            else:
                self.env.user.partner_id.message_post(body=f'Cuenta bancaria {account.acc_number} eliminada')
                account.unlink()
                return {}

        except AccessError:
            # Return 404 even if it is from a different user
            # to not leak information
            raise MissingError('Access error')
