from files.flow_blueprints.scripts.external.fakturoid import Fakturoid

from google.cloud.bigquery.schema import SchemaField
## source:https://github.com/farin/python-fakturoid
bq_schema_mapping={"expenses":[SchemaField('_loaded_lines', 'RECORD', 'REPEATED', None,
                                           (SchemaField('id', 'INTEGER', 'NULLABLE', None, (), None),
                                             SchemaField('name', 'STRING', 'NULLABLE', None, (), None),
                                             SchemaField('quantity', 'FLOAT', 'NULLABLE', None, (), None),
                                             SchemaField('unit_name', 'STRING', 'NULLABLE', None, (), None),
                                             SchemaField('unit_price', 'FLOAT', 'NULLABLE', None, (), None),
                                             SchemaField('unit_price_with_vat', 'FLOAT', 'NULLABLE', None, (), None),
                                             SchemaField('unit_price_without_vat', 'FLOAT', 'NULLABLE', None, (), None),
                                             SchemaField('vat_rate', 'INTEGER', 'NULLABLE', None, (), None)), None),
                               SchemaField('attachment', 'RECORD', 'NULLABLE', None,
                                           (SchemaField('content_type', 'STRING', 'NULLABLE', None, (), None),
                                    SchemaField('download_url', 'STRING', 'NULLABLE', None, (), None),
                                    SchemaField('file_name', 'STRING', 'NULLABLE', None, (), None)), None),
                               SchemaField('bank_account', 'STRING', 'NULLABLE', None, (), None),
                               SchemaField('created_at', 'TIMESTAMP', 'NULLABLE', None, (), None),
                               SchemaField('currency', 'STRING', 'NULLABLE', None, (), None),
                               SchemaField('custom_id', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('description', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('document_type', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('due_on', 'DATE', 'NULLABLE', None, (), None),
                                SchemaField('exchange_rate', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('html_url', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('iban', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('id', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('issued_on', 'DATE', 'NULLABLE', None, (), None),
                                SchemaField('native_subtotal', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('native_total', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('number', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('original_number', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('paid_amount', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('paid_on', 'DATE', 'NULLABLE', None, (), None),
                                SchemaField('payment_method', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('private_note', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('proportional_vat_deduction', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('received_on', 'DATE', 'NULLABLE', None, (), None),
                                SchemaField('status', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('subject_id', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('subject_url', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('subtotal', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('supplier_city', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('supplier_country', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('supplier_name', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('supplier_registration_no', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('supplier_street', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('supplier_vat_no', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('supplier_zip', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('supply_code', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('swift_bic', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('tags', 'STRING', 'REPEATED', None, (), None),
                                SchemaField('tax_deductible', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('taxable_fulfillment_due', 'DATE', 'NULLABLE', None, (), None),
                                SchemaField('total', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('transferred_tax_liability', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('updated_at', 'TIMESTAMP', 'NULLABLE', None, (), None),
                                SchemaField('url', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('variable_symbol', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('vat_price_mode', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('extraction_timestamp', 'TIMESTAMP', 'NULLABLE', None, (), None)],
                   "invoices":[SchemaField('_loaded_lines', 'RECORD', 'REPEATED', None,
                                (SchemaField('id', 'INTEGER', 'NULLABLE', None, (), None),
                     SchemaField('name', 'STRING', 'NULLABLE', None, (), None),
                     SchemaField('quantity', 'FLOAT', 'NULLABLE', None, (), None),
                     SchemaField('unit_name', 'STRING', 'NULLABLE', None, (), None),
                     SchemaField('unit_price', 'FLOAT', 'NULLABLE', None, (), None),
                     SchemaField('unit_price_with_vat', 'FLOAT', 'NULLABLE', None, (), None),
                     SchemaField('unit_price_without_vat', 'FLOAT', 'NULLABLE', None, (), None),
                     SchemaField('vat_rate', 'INTEGER', 'NULLABLE', None, (), None)), None),
                                SchemaField('accepted_at', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('attachment', 'RECORD', 'NULLABLE', None,
                                            (SchemaField('content_type', 'STRING', 'NULLABLE', None, (), None),
                                             SchemaField('download_url', 'STRING', 'NULLABLE', None, (), None),
                                             SchemaField('file_name', 'STRING', 'NULLABLE', None, (), None)), None),
                                SchemaField('bank_account', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('cancelled_at', 'TIMESTAMP', 'NULLABLE', None, (), None),
                                SchemaField('client_city', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('client_country', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('client_local_vat_no', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('client_name', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('client_registration_no', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('client_street', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('client_street2', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('client_vat_no', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('client_zip', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('correction', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('correction_id', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('created_at', 'TIMESTAMP', 'NULLABLE', None, (), None),
                                SchemaField('currency', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('custom_id', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('due', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('due_on', 'DATE', 'NULLABLE', None, (), None),
                                SchemaField('eet', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('eet_cash_register', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('eet_records', 'STRING', 'REPEATED', None, (), None),
                                SchemaField('eet_store', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('eu_electronic_service', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('exchange_rate', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('extraction_timestamp', 'TIMESTAMP', 'NULLABLE', None, (), None),
                                SchemaField('footer_note', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('generator_id', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('gopay', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('hide_bank_account', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('html_url', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('iban', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('id', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('issued_on', 'DATE', 'NULLABLE', None, (), None),
                                SchemaField('language', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('native_subtotal', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('native_total', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('note', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('number', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('number_format_id', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('order_number', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('oss', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('paid_amount', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('paid_at', 'TIMESTAMP', 'NULLABLE', None, (), None),
                                SchemaField('partial_proforma', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('payment_method', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('paypal', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('pdf_url', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('private_note', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('proforma', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('public_html_url', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('related_id', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('remaining_amount', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('remaining_native_amount', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('reminder_sent_at', 'TIMESTAMP', 'NULLABLE', None, (), None),
                                SchemaField('sent_at', 'TIMESTAMP', 'NULLABLE', None, (), None),
                                SchemaField('show_already_paid_note_in_pdf', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('status', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('subject_custom_id', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('subject_id', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('subject_url', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('subtotal', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('supply_code', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('swift_bic', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('tags', 'STRING', 'REPEATED', None, (), None),
                                SchemaField('taxable_fulfillment_due', 'DATE', 'NULLABLE', None, (), None),
                                SchemaField('token', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('total', 'FLOAT', 'NULLABLE', None, (), None),
                                SchemaField('transferred_tax_liability', 'BOOLEAN', 'NULLABLE', None, (), None),
                                SchemaField('updated_at', 'TIMESTAMP', 'NULLABLE', None, (), None),
                                SchemaField('url', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('variable_symbol', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('vat_price_mode', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('webinvoice_seen_at', 'TIMESTAMP', 'NULLABLE', None, (), None),
                                SchemaField('your_city', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('your_country', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('your_local_vat_no', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('your_name', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('your_registration_no', 'INTEGER', 'NULLABLE', None, (), None),
                                SchemaField('your_street', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('your_street2', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('your_vat_no', 'STRING', 'NULLABLE', None, (), None),
                                SchemaField('your_zip', 'INTEGER', 'NULLABLE', None, (), None)]}
class instance(Fakturoid):

    def get(self,endpoint="invoices",bq_prep=False,**kwargs):

        if endpoint == 'invoices':
            model=self.invoices(**kwargs)
        elif endpoint == 'expenses':
            model=self.expenses(**kwargs)
        if bq_prep:
            import decimal
            import datetime
            record_list=[]
            model.bq_schema = bq_schema_mapping[endpoint]
            for record in model:
                record_dict=vars(record)
                record_dict.pop("lines")
                for k, v in record_dict.items():
                    import datetime
                    if type(v) == datetime.date or isinstance(v, datetime.datetime):
                        record_dict[k] = str(record_dict[k])
                    elif type(v) == decimal.Decimal:
                        record_dict[k] = float(record_dict[k])
                record_list.append(record_dict)
            output = record_list
        else:
            output = model
        return output















