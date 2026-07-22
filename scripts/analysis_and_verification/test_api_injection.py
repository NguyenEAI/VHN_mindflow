import json

api_call_product_data = """[
  {
    "status": "success",
    "data": [
      {
        "name": "Christina - Unstress - Harmonizing Night Cream - 50ml (Kem phục hồi, đổi mới và làm sáng da ban đêm)",
        "price": "2860000",
        "link_image": "https://vhndistribution.com/wp-content/uploads/2023/06/Unstress-Harmonizing-night-cream-50.png"
      }
    ]
  }
]"""

# If Handlebars renders {{api_raw_product_data[0].data}}, it will inject it as a literal.
# Let's see what happens if the data contains quotes.

import json
data = json.loads(api_call_product_data)

# Mindflow injects using {{api_raw_product_data[0].data}}
# If data is a list of dicts, it gets injected as string representation of a Python list/dict!
injected_str = str(data[0]['data'])
print("Injected string would be:")
print(injected_str)

# When the Python node runs:
# PRODUCTS = {{api_raw_product_data[0].data}}
# This becomes:
# PRODUCTS = [{'name': 'Christina - Unstress...', 'price': '2860000', ...}]
