from usdm4.api.study import Study
from usdm4.api.address import Address
from usdm4.api.organization import Organization
from usdm4_excel.export.base.collection_panel import CollectionPanel


class OrganizationsPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        for version in study.versions:
            for org in version.organizations:
                self._add_org(collection, org)
        return super().execute(
            collection,
            ["identifierScheme", "identifier", "name", "label", "type", "address"],
        )

    def _add_org(self, collection: list, org: Organization):
        data = org.model_dump()
        data["type"] = self._pt_from_code(org.type)
        data["address"] = self._from_address(org.legalAddress)
        collection.append(data)

    def _from_address(self, address: Address):
        if address is None:
            return "|||||"
        items = address.lines
        items.append(address.district)
        items.append(address.city)
        items.append(address.state)
        items.append(address.postalCode)
        print(f"ADDRESS: {address}")
        code = address.country.code if address.country else ""
        items.append(code)
        return ("|").join(items)
