from odoo import models, fields, api
from odoo.exceptions import UserError
import winsound
import base64
import xlrd

class SerialNumberWizard(models.TransientModel):
    _name = 'stock.picking.serial.number.wizard'

    serial_number = fields.Char(string='Serial Number')
    product_name = fields.Char(string='Product Name', compute='_compute_product_name', readonly=True, store=True)
    transfer_id = fields.Many2one('stock.picking')
    serial_number_count = fields.Integer(string='Serial Number Count', default=0)

    picking_type_id = fields.Many2one('stock.picking.type')
    control_button = fields.Boolean(related='picking_type_id.control_button', string='Import File')

    import_file = fields.Binary(string='Import File', filename='FileName.xlsx')

    def import_excel(self):
        if self.transfer_id.picking_type_id.control_button == False:
            raise UserError("check administrator to allow Import File")

        decoded_data = base64.b64decode(self.import_file)
        workbook = xlrd.open_workbook(file_contents=decoded_data)
        sheet = workbook.sheet_by_index(0)

        invalid_serial_numbers = []
        duplicate_serial_numbers = []
        valid_serial_numbers = []

        for row_index in range(sheet.nrows):
            if row_index > 0:  # Process all rows except the header row
                serial_number = sheet.cell_value(row_index, 0)

                # Check for invalid serial numbers
                try:
                    if isinstance(serial_number, float):
                        serial_number = str(int(serial_number))
                    else:
                        serial_number = str(serial_number)

                    xldate = xlrd.xldate.xldate_as_datetime(sheet.cell_value(row_index, 0), workbook.datemode)
                    if xldate == "Invalid":
                        invalid_serial_numbers.append(serial_number)
                        continue
                except (TypeError, ValueError):
                    invalid_serial_numbers.append(serial_number)
                    continue

                # Check for duplicate serial numbers
                if serial_number in valid_serial_numbers:
                    duplicate_serial_numbers.append(serial_number)
                    continue

                valid_serial_numbers.append(serial_number)

        # Raise errors for invalid and duplicate serial numbers
        if invalid_serial_numbers:
            self.play_error_sound()
            raise UserError(f"Please enter valid serial numbers: {invalid_serial_numbers}")

        if duplicate_serial_numbers:
            self.play_error_sound()
            raise UserError(f"Duplicate serial numbers found: {duplicate_serial_numbers}")

        # Process the valid serial numbers
        for serial_number in valid_serial_numbers:
            self._compute_product_name_values([serial_number])

        # Update the picking with the new move lines
        self.transfer_id.action_assign()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.transfer_id.id,
            'target': 'current',
        }

    def play_error_sound(self, times=2):
        # Define a function to play an error sound multiple times
        for _ in range(times):
            winsound.Beep(1000, 500)

    @api.depends('serial_number')
    def _compute_product_name(self):
        for record in self:
            if record.serial_number:
                serial_numbers = [record.serial_number]  # Convert single serial number to a list
                record._compute_product_name_values(serial_numbers)
            else:
                record.product_name = 'Product Name'

    def _compute_product_name_values(self, serial_numbers):
        self.transfer_id = self.env.context.get('active_id')
        invalid_serial_numbers = []

        for serial_number in serial_numbers:
            if serial_number:
                lot = self.env['stock.lot'].search([('name', '=', serial_number)])

                if lot:
                    # Check if a stock move has already been created
                    move = self.env['stock.move'].search([
                        ('picking_id', '=', self.transfer_id.id),
                        ('product_id', '=', lot[0].product_id.id)
                    ], limit=1)
                    if move == False:
                        move = self.env['stock.move'].create({
                            'name': lot[0].product_id.name,
                            'product_id': lot[0].product_id.id,
                            'product_uom': lot[0].product_id.uom_id.id,
                            'product_uom_qty': 1,
                            'location_id': self.transfer_id.location_id.id,
                            'location_dest_id': self.transfer_id.location_dest_id.id,
                            'picking_id': self.transfer_id.id
                        })
                    move_line = move.move_line_ids.search([
                        ('picking_id', '=', self.transfer_id.id),
                        ('product_id', '=', lot[0].product_id.id),
                        ('lot_id', '=', lot[0].id)
                    ], limit=1)
                    if move_line:
                        self.play_error_sound()
                        raise UserError(f"serial number added before '{serial_number}'")

                    move.write({'move_line_ids': [(0, 0, {
                        'picking_id': self.transfer_id.id,
                        'move_id': move.id,
                        'product_id': lot[0].product_id.id,
                        'lot_id': lot[0].id,
                        'qty_done': 1.0,
                    })]})
                    self.product_name = lot.product_id.name
                    # self.check_serial_numbers(move)
                    self.serial_number_count += 1
                else:
                    invalid_serial_numbers.append(serial_number)
                    self.play_error_sound()
                    raise UserError(f"'Please enter a valid serial number '{invalid_serial_numbers}")
            else:
                self.product_name = 'Product Name'
            self.serial_number = None
            continue

    @api.model
    def default_get(self, fields_list):
        # check if the state is waiting
        res = super(SerialNumberWizard, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            picking = self.env['stock.picking'].browse(active_id)
            if picking.state not in ['confirmed', 'assigned']:
                self.play_error_sound()
                raise UserError('The stock picking must be in Waiting or Ready state to open this wizard')
            res['transfer_id'] = active_id
        return res
