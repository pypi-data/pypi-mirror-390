from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.study_site import StudySite
from usdm4.api.organization import Organization


class SitesSheet(BaseSheet):
    SHEET_NAME = "studyDesignSites"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self.items = []
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                optional=True,
            )
            if self._success:
                for index, row in self._sheet.iterrows():
                    org_name = self._read_cell_by_name(index, ["organization"])
                    site_name = self._read_cell_by_name(index, ["name"])
                    site_description = self._read_cell_by_name(index, ["description"])
                    site_label = self._read_cell_by_name(index, ["label"])
                    country_code = self._builder.iso3166_code_or_decode(
                        self._read_cell_by_name(index, ["country"])
                    )
                    site = self._create(
                        StudySite,
                        {
                            "name": site_name,
                            "description": site_description,
                            "label": site_label,
                            "country": country_code,
                        },
                    )
                    if site:
                        self.items.append(site)
                        if org_name:
                            org: Organization = (
                                self._builder.cross_reference.get_by_name(
                                    Organization, org_name
                                )
                            )
                            if org:
                                org.managedSites.append(site)
                            else:
                                self._errors.error(
                                    f"Failed to find organization with name '{org_name}'"
                                )
                        else:
                            self._errors.error(
                                f"No organization specified for site '{site_name}'"
                            )
        except Exception as e:
            self._sheet_exception(e)
