from rick_db import fieldmapper


@fieldmapper(tablename="customers", pk="customer_id")
class CustomerRecord:
    id = "customer_id"
    company_name = "company_name"
    contact_name = "contact_name"
    contact_title = "contact_title"
    address = "address"
    city = "city"
    region = "region"
    postal_code = "postal_code"
    country = "country"
    phone = "phone"
    fax = "fax"


@fieldmapper(tablename="categories", pk="category_id")
class CategoryRecord:
    id = "category_id"
    name = "category_name"
    description = "description"
    picture = "picture"


@fieldmapper(tablename="shippers", pk="shipper_id")
class ShipperRecord:
    id = "shipper_id"
    name = "company_name"
    phone = "phone"


@fieldmapper(tablename="us_states", pk="state_id")
class UsStatesRecord:
    id = "state_id"
    name = "state_name"
    abbr = "state_abbr"
    region = "state_region"


@fieldmapper(tablename="territories", pk="territory_id")
class TerritoriesRecord:
    id = "territory_id"
    territory_description = "territory_description"
    region_id = "region_id"
