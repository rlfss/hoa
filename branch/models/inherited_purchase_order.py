# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class purchase_order(models.Model):

    _inherit = 'purchase.order.line'


    @api.model
    def default_get(self, default_fields):
        res = super(purchase_order, self).default_get(default_fields)
        if self._context.get('branch_id'):
            res['branch_id'] = self._context.get('branch_id')
        elif self.env.user.branch_id and self.env.user.branch_id.company_id.id == self.env.company.id:
            res['branch_id'] = self.env.user.branch_id.id
        elif self.env.user.branch_ids.ids:
            for i in self.env.user.branch_ids:
                if self.env.company.id == i.company_id.id:
                    res['branch_id'] = i.id
                    break
        return res

    branch_id = fields.Many2one('res.branch', string='Branch', domain="[('company_id', '=', company_id)]")


    def _prepare_stock_moves(self, picking):
        result = super(purchase_order, self)._prepare_stock_moves(picking)

        branch_id = False
        if self.branch_id:
            branch_id = self.branch_id.id
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id

        for res in result:
            res.update({'branch_id' : branch_id})

        return result


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.model
    def default_get(self,fields):
        res = super(PurchaseOrder, self).default_get(fields)
        if self.env.user.branch_id and self.env.user.branch_id.company_id.id == self.env.company.id:
            res['branch_id'] = self.env.user.branch_id.id
        elif self.env.user.branch_ids.ids:
            for i in self.env.user.branch_ids:
                if self.env.company.id == i.company_id.id:
                    res['branch_id'] = i.id
                    break
        if res.get('branch_id'):
            branched_warehouse = self.env['stock.warehouse'].search([('branch_id','=',res.get('branch_id'))])
            if branched_warehouse:
                res['picking_type_id'] = branched_warehouse[0].in_type_id.id
        return res

    branch_id = fields.Many2one('res.branch', string='Branch')

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        branch_id = False
        if self.branch_id:
            branch_id = self.branch_id.id
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({
            'branch_id' : branch_id
        })
        return res


    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''

        result = super(PurchaseOrder, self).action_view_invoice()

        branch_id = False
        if self.branch_id:
            branch_id = self.branch_id.id
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id


        if 'context' in result:
            result['context'].update({
                'default_branch_id' : branch_id,
                'branch_id' : branch_id
            })

        return result
