from .invoice import generate

invoice.generate("invoices", "output",
                 "product_id", "product_name", "amount_purchased",
                 "price_per_unit", "total_price")