# USDM4_Excel Package
Library for import and export of USDM Version 4 via MS Excel

## Table of Contents

- [Export](#Export)
- [Import](#Import)
  - [General Sheets](#general-sheets)
    - [Configuration Sheet](#configuration-sheet)
    - [Dictionaries Sheet](#dictionaries-sheet)
    - [Notes Sheet](#notes-sheet)
  - [Study Sheets](#study-sheets)
    - [Study Sheet](#study-sheet)
    - [Study Organizations Sheet](#study-organizations-sheet)
    - [Study Identifiers Sheet](#study-identifiers-sheet)
    - [Documents Sheet](#documents-sheet)
    - [Abbreviation Sheet](#abbreviation-sheet)
    - [Amendment Sheet](#amendment-sheet)
    - [Amendment Changes Sheet](#amendment-changes-sheet)
    - [Amendment Impact Sheet](#amendment-impact-sheet)
    - [Assigned Person Sheet](#assigned-person-sheet)
    - [Document Content Sheet](#document-content-sheet)
    - [Document Template Sheet](#document-template-sheet)
    - [Eligibility Criteria Items Sheet](#eligibility-criteria-items-sheet)
    - [Sites Sheet](#sites-sheet)
  - [Study Design Sheets](#study-design-sheets)
    - [Study Design Arms Sheet](#study-design-arms-sheet)
    - [Study Design Characteristics Sheet](#study-design-characteristics-sheet)
    - [Study Design Devices Sheet](#study-design-devices-sheet)
    - [Study Design Elements Sheet](#study-design-elements-sheet)
    - [Study Design Eligibility Criteria Sheet](#study-design-eligibility-criteria-sheet)
    - [Study Design Encounters Sheet](#study-design-encounters-sheet)
    - [Study Design Epochs Sheet](#study-design-epochs-sheet)
    - [Study Design Estimands Sheet](#study-design-estimands-sheet)
    - [Study Design Indications Sheet](#study-design-indications-sheet)
    - [Study Design Interventions Sheet](#study-design-interventions-sheet)
  - [Data Format Guidelines](#data-format-guidelines)
  - [CDISC CT Code Lists](#cdisc-ct-code-lists)

# Export

A simple export mechanism is in place to export a USDM file to the v4 CDISC Excel format

# Import

## General

This section describes all the columns used within the Excel sheets for USDM4 data import/export, along with the expected formats and values for each column. This format is an updated version of the CDISC v4 Excel format that allows for multiple study designs and a few other improvements.

## General Sheets

### Configuration Sheet

**Sheet Name:** `configuration`

This sheet configures CDISC CT (Controlled Terminology) versions for the import process.

| Column | Format | Description | Example |
|--------|--------|-------------|---------|
| **Name** (Column A) | Text | Configuration parameter name (case-insensitive) | `CT VERSION` |
| **Value** (Column B) | Text | Configuration parameter value | `SDTMCT = 2025-03-28` |

**Supported Configuration Parameters:**
- `CT VERSION`: Specifies CDISC CT version in format `<CT name> = <version>`
  - Valid CT names: `SDTMCT`, `PROTOCOLCT`, `DDFCT`
  - Version format: `YYYY-MM-DD`

**Examples:**
```
CT VERSION | SDTMCT = 2025-03-28
CT VERSION | PROTOCOLCT = 2025-03-28
CT VERSION | DDFCT = 2025-03-28
```

### Dictionaries Sheet

**Sheet Name:** `dictionaries`

This sheet defines syntax template dictionaries for parameterized text.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **name** | Text | Dictionary name | Yes | `Treatment Duration` |
| **description** | Text | Dictionary description | Yes | `Template for treatment duration text` |
| **label** | Text | Dictionary label | Yes | `Duration Template` |
| **key** | Text | Parameter key/tag | Yes | `duration` |
| **class** | Text | API class name for cross-reference | No | `Duration` |
| **xref** | Text | Cross-reference name | No | `Treatment Duration` |
| **attribute** / **path** | Text | Attribute path for cross-reference | No | `quantity.value` |
| **value** | Text | Static value (when not using cross-reference) | No | `12 weeks` |

**Notes:**
- Multiple parameter maps can be defined for the same dictionary
- Either use `class`/`xref`/`attribute` for dynamic references or `value` for static text
- Cross-references link to other API objects created in the system

### Notes Sheet

**Sheet Name:** `notes`

This sheet defines comment annotations that can be referenced by other sheets.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **name** | Text | Note identifier/name | Yes | `Safety Note 1` |
| **text** | Text | Note content/description | Yes | `Monitor for adverse events` |
| **codes** | CDISC CT Codes | Comma-separated list of codes | No | `C49667:Safety Study, C25256:Adverse Event` |

**Code Format:**
- Format: `<code>:<preferred_term>` or `<system>:<code>=<preferred_term>`
- Multiple codes separated by commas
- Example: `C49667:Safety Study, LOINC:LA6115-6=Mild`

## Study Sheets

### Study Sheet

**Sheet Name:** `study`

This sheet defines the main study information using a key-value format (Column A = Parameter Name, Column B = Value).

| Parameter Name | Format | Description | Required | CDISC CT Code List | Example |
|----------------|--------|-------------|----------|-------------------|---------|
| **name** | Text | Study name | Yes | - | `Phase III Efficacy Study` |
| **description** | Text | Study description | Yes | - | `A randomized controlled trial` |
| **label** | Text | Study label | Yes | - | `Study ABC-123` |
| **studyVersion** | Text | Study version identifier | Yes | - | `1.0` |
| **studyAcronym** | Text | Study acronym | No | - | `EFFICACY-III` |
| **studyRationale** | Text | Study rationale | No | - | `To evaluate efficacy and safety` |
| **businessTherapeuticAreas** | CDISC CT Codes | Therapeutic areas (multiple) | No | - | `C3262:Oncology, C3263:Cardiology` |
| **briefTitle** | Text | Brief study title | No | - | `Efficacy Study of Drug X` |
| **officialTitle** | Text | Official study title | No | - | `A Phase III Study of Drug X` |
| **publicTitle** | Text | Public study title | No | - | `Drug X Study for Cancer` |
| **scientificTitle** | Text | Scientific study title | No | - | `Efficacy of Drug X in Advanced Cancer` |
| **studyDesigns** | File References | Study design file names (multiple) | No | - | `design1.xlsx, design2.xlsx` |
| **protocolVersion** | Text | Protocol version | No | - | `2.1` |
| **protocolStatus** | CDISC CT | Protocol status | No | C188723 | `Final` |

**Governance Dates Section:**
After the main parameters, the sheet includes a dates section with the following columns:

| Column | Format | Description | Required | CDISC CT Code List | Example |
|--------|--------|-------------|----------|-------------------|---------|
| **category** | Text | Date category | Yes | - | `study_version`, `protocol_document`, `amendment` |
| **name** | Text | Date name | Yes | - | `Study Start Date` |
| **description** | Text | Date description | Yes | - | `Date when study enrollment begins` |
| **label** | Text | Date label | Yes | - | `Start Date` |
| **type** | CDISC CT | Type of governance date | Yes | C207413 | `Effective Date` |
| **date** | Date | Date value | Yes | - | `2024-01-15` |
| **scopes** | Geographic Scopes | Geographic scopes (future implementation) | No | - | - |

**Valid protocolStatus values (C188723):**
- `Approved` (C25425)
- `Draft` (C85255)
- `Final` (C25508)
- `Obsolete` (C63553)
- `Pending Review` (C188862)

**Valid governance date type values (C207413):**
- `Approval Date` (C71476)
- `Effective Date` (C215663)
- `Issued Date` (C215664)

### Study Organizations Sheet

**Sheet Name:** `studyOrganizations`

Defines organizations involved in the study.

| Column | Format | Description | Required | CDISC CT Code List | Example |
|--------|--------|-------------|----------|-------------------|---------|
| **organisationName** / **organizationName** / **name** | Text | Organization name | Yes | - | `ABC Pharmaceutical` |
| **label** | Text | Organization label | No | - | `ABC Pharma` |
| **organisationType** / **organizationType** / **type** | CDISC CT | Type of organization | Yes | C188724 | `Pharmaceutical Company` |
| **organisationIdentifierScheme** / **organizationIdentifierScheme** / **identifierScheme** | Text | Identifier scheme | Yes | - | `DUNS` |
| **organisationIdentifier** / **organizationIdentifier** / **identifier** | Text | Organization identifier | Yes | - | `123456789` |
| **organisationAddress** / **organizationAddress** / **address** | Address | Organization address | No | - | `123 Main St, City, State, 12345, USA` |

**Valid organizationType values (C188724):**
- `Clinical Study Registry` (C93453)
- `Regulatory Agency` (C188863)
- `Healthcare Facility` (C21541)
- `Pharmaceutical Company` (C54149)
- `Laboratory` (C37984)
- `Contract Research Organization` (C54148)
- `Government Institute` (C199144)
- `Academic Institution` (C18240)
- `Medical Device Company` (C215661)

**Address Format:**
- Format: `<street>, <city>, <state>, <postal_code>, <country>`
- Can also use pipe separator: `<street> | <city> | <state> | <postal_code> | <country>`
- Example: `123 Main Street, Boston, MA, 02101, USA`

### Study Identifiers Sheet

**Sheet Name:** `studyIdentifiers`

Defines study identifiers assigned by different organizations.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **studyIdentifier** / **identifier** | Text | Study identifier value | Yes | `ABC-123-2024` |
| **organization** | Organization Reference | Organization name that assigned the identifier | Yes | `ABC Pharmaceutical` |

**Notes:**
- The organization must exist in the Study Organizations sheet
- Multiple identifiers can be assigned by different organizations

### Documents Sheet

**Sheet Name:** `documents`

Defines study definition documents (protocols, etc.).

| Column | Format | Description | Required | CDISC CT Code List | Example |
|--------|--------|-------------|----------|-------------------|---------|
| **name** | Text | Document name | Yes | - | `Study Protocol v2.1` |
| **label** | Text | Document label | Yes | - | `Protocol` |
| **description** | Text | Document description | Yes | - | `Main study protocol document` |
| **type** | CDISC CT | Type of document | Yes | C215477 | `Protocol` |
| **templateName** | Text | Template name | Yes | - | `Standard Protocol Template` |
| **sheetName** | Text | The sheet name of the sheet holding the document content | Yes | - | `m11Template` |
| **language** | ISO 639 Code | Document language | Yes | - | `en` |
| **notes** | Note References | Comma-separated note names | No | - | `Protocol Note` |

**Valid type values (C215477):**
- `Protocol` (C70817)

### Abbreviation Sheet

**Sheet Name:** `abbreviations`

Defines abbreviations and acronyms used in the study.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **name** | Text | Abbreviation/acronym | Yes | `AE` |
| **description** | Text | Full definition | Yes | `Adverse Event` |
| **notes** | Note References | Comma-separated note names | No | `Definition Note` |

### Amendment Sheet

**Sheet Name:** `amendments`

Defines study amendments.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **name** | Text | Amendment name | Yes | `Amendment 1` |
| **description** | Text | Amendment description | Yes | `Protocol amendment to modify inclusion criteria` |
| **label** | Text | Amendment label | Yes | `Amend-1` |
| **number** | Text | Amendment number | Yes | `01` |
| **summary** | Text | Amendment summary | Yes | `Modified inclusion criteria for better enrollment` |
| **substantialFlag** | Boolean | Substantial amendment flag | Yes | `true` |
| **notes** | Note References | Comma-separated note names | No | `Amendment Note` |

### Amendment Changes Sheet

**Sheet Name:** `amendmentChanges`

Defines specific changes made in amendments.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **name** | Text | Change name | Yes | `Inclusion Criteria Change` |
| **description** | Text | Change description | Yes | `Modified age range from 18-65 to 18-75` |
| **label** | Text | Change label | Yes | `Age Change` |

### Amendment Impact Sheet

**Sheet Name:** `amendmentImpact`

Defines the impact of amendments.

| Column | Format | Description | Required | CDISC CT Code List | Example |
|--------|--------|-------------|----------|-------------------|---------|
| **name** | Text | Impact name | Yes | - | `Safety Impact Assessment` |
| **description** | Text | Impact description | Yes | - | `Assessment of safety implications` |
| **label** | Text | Impact label | Yes | - | `Safety Impact` |
| **type** | CDISC CT | Type of impact | Yes | C215481 | `Study Subject Safety` |
| **notes** | Note References | Comma-separated note names | No | - | `Impact Note` |

**Valid type values (C215481):**
- `Study Subject Safety` (C215665)
- `Study Subject Rights` (C215666)
- `Study Data Reliability` (C215667)
- `Study Data Robustness` (C215668)

### Assigned Person Sheet

**Sheet Name:** `assignedPersons`

Defines persons assigned to study roles.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **name** | Text | Person name | Yes | `Dr. John Smith` |
| **description** | Text | Person description | Yes | `Principal Investigator` |
| **label** | Text | Person label | Yes | `PI Smith` |
| **notes** | Note References | Comma-separated note names | No | `PI Note` |

### Document Content Sheet

**Sheet Name:** `documentContent`

Defines content sections within documents.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **name** | Text | Content section name | Yes | `Inclusion Criteria` |
| **description** | Text | Content description | Yes | `Patient inclusion criteria section` |
| **label** | Text | Content label | Yes | `Inclusion` |
| **text** | HTML/Text | Content text | Yes | `<div>Patients must be 18-75 years old</div>` |
| **notes** | Note References | Comma-separated note names | No | `Content Note` |

**Notes:**
- Text content is automatically wrapped in `<div>` tags if not already HTML
- Supports HTML formatting for rich content

### Document Template Sheet

**Sheet Name:** `documentTemplates`

Defines document templates.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **name** | Text | Template name | Yes | `Standard Protocol Template` |
| **description** | Text | Template description | Yes | `Standard template for clinical protocols` |
| **label** | Text | Template label | Yes | `Std Protocol` |

### Eligibility Criteria Items Sheet

**Sheet Name:** `eligibilityCriteriaItems`

Defines individual eligibility criteria items.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **name** | Text | Criteria item name | Yes | `Age Range` |
| **description** | Text | Criteria description | Yes | `Patient age must be within specified range` |
| **label** | Text | Criteria label | Yes | `Age` |
| **text** | Text | Criteria text | Yes | `Age 18-75 years inclusive` |
| **dictionary** | Dictionary Reference | Dictionary name for parameterized text | No | `Age Template` |

### Sites Sheet

**Sheet Name:** `sites`

Defines study sites.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **name** | Text | Site name | Yes | `Memorial Hospital` |
| **description** | Text | Site description | Yes | `Primary research site` |
| **label** | Text | Site label | Yes | `Site 001` |
| **identifier** | Text | Site identifier | Yes | `SITE-001` |

## Study Design Sheets

### Study Design Arms Sheet

**Sheet Name:** `studyDesignArms`

Defines study arms/groups for the clinical trial.

| Column | Format | Description | Required | CDISC CT Code List | Example |
|--------|--------|-------------|----------|-------------------|---------|
| **studyArmName** / **name** | Text | Study arm name | Yes | - | `Treatment Arm A` |
| **studyArmDescription** / **description** | Text | Study arm description | Yes | - | `Active treatment with Drug X` |
| **label** | Text | Study arm label | No | - | `Arm A` |
| **studyArmType** / **type** | CDISC CT | Type of study arm | Yes | C174222 | `Investigational Arm` |
| **studyArmDataOriginDescription** / **dataOriginDescription** | Text | Data origin description | Yes | - | `Data collected during study` |
| **studyArmDataOriginType** / **dataOriginType** | CDISC CT | Type of data origin | Yes | C188727 | `Data Generated Within Study` |
| **notes** | Note References | Comma-separated note names | No | - | `Safety Note 1, Efficacy Note` |

**Valid studyArmType values (C174222):**
- `Investigational Arm` (C174266)
- `Active Comparator Arm` (C174267)
- `Placebo Control Arm` (C174268)
- `Protocol Treatment Arm` (C15538)
- `Sham Comparator Arm` (C174269)
- `No Intervention Arm` (C174270)
- `Control Arm` (C174226)

**Valid studyArmDataOriginType values (C188727):**
- `Historical Data` (C188864)
- `Data Generated Within Study` (C188866)
- `Real-world Data` (C165830)
- `Synthetic Data` (C176263)
- `Virtual Data` (C188865)

### Study Design Characteristics Sheet

**Sheet Name:** `studyDesignCharacteristics`

Defines study design characteristics.

| Column | Format | Description | Required | Example |
|--------|--------|-------------|----------|---------|
| **name** | Text | Characteristic name | Yes | `Randomization` |
| **description** | Text | Characteristic description | Yes | `Study uses randomization` |
| **label** | Text | Characteristic label | Yes | `Randomized` |
| **text** | Text | Characteristic text/details | Yes | `Subjects randomized 1:1` |
| **dictionary** | Dictionary Reference | Dictionary name for parameterized text | No | `Randomization Template` |
| **notes** | Note References | Comma-separated note names | No | `Randomization Note` |

### Study Design Encounters Sheet

**Sheet Name:** `studyDesignEncounters`

Defines study encounters/visits.

| Column | Format | Description | Required | CDISC CT Code List | Example |
|--------|--------|-------------|----------|-------------------|---------|
| **name** | Text | Encounter name | Yes | - | `Screening Visit` |
| **description** | Text | Encounter description | Yes | - | `Initial screening procedures` |
| **label** | Text | Encounter label | No | - | `Visit 1` |
| **type** | CDISC CT | Type of encounter | Yes | C188728 | `Visit` |
| **environmentalSettings** | CDISC CT | Environmental settings (multiple) | No | C127262 | `Clinic, Hospital` |
| **contactModes** | CDISC CT | Contact modes (multiple) | No | C171445 | `In Person, Telephone Call` |
| **transitionStartRule** | Text | Start transition rule | No | - | `After consent signed` |
| **transitionEndRule** | Text | End transition rule | No | - | `All procedures completed` |
| **notes** | Note References | Comma-separated note names | No | - | `Visit Note` |

**Valid type values (C188728):**
- `Visit` (C25716)

**Valid environmentalSettings values (C127262):**
- `Household Environment` (C102647)
- `Childcare Center` (C127785)
- `Ambulatory Care Facility` (C16281)
- `Hospital` (C16696)
- `Healthcare Facility` (C21541)
- `Clinic` (C211570)
- `Home` (C18002)
- And many more...

**Valid contactModes values (C171445):**
- `Text Message` (C157352)
- `Audio-Videoconferencing` (C171525)
- `In Person` (C175574)
- `E-mail` (C25170)
- `Telephone Call` (C171537)
- And more...

### Study Design Epochs Sheet

**Sheet Name:** `studyDesignEpochs`

Defines study epochs/periods.

| Column | Format | Description | Required | CDISC CT Code List | Example |
|--------|--------|-------------|----------|-------------------|---------|
| **name** | Text | Epoch name | Yes | - | `Treatment Period` |
| **description** | Text | Epoch description | Yes | - | `Active treatment phase` |
| **label** | Text | Epoch label | No | - | `Treatment` |
| **type** | CDISC CT | Type of epoch | Yes | C99079 | `Treatment Epoch` |
| **sequenceInStudy** | Integer | Sequence number | No | - | `2` |
| **previousEpoch** | Epoch Reference | Previous epoch name | No | - | `Screening Period` |
| **nextEpoch** | Epoch Reference | Next epoch name | No | - | `Follow-up Period` |
| **notes** | Note References | Comma-separated note names | No | - | `Treatment Note` |

**Valid type values (C99079):**
- `Open Label Treatment Epoch` (C102256)
- `Product Exposure Epoch` (C210380)
- `Screening Epoch` (C202487)
- `Treatment Epoch` (C101526)
- `Follow-Up Epoch` (C202578)
- `Baseline Epoch` (C125938)
- `Washout Period` (C42872)
- And more...

### Study Design Interventions Sheet

**Sheet Name:** `studyDesignInterventions`

Defines study interventions and their administrations.

| Column | Format | Description | Required | CDISC CT Code List | Example |
|--------|--------|-------------|----------|-------------------|---------|
| **name** | Text | Intervention name | Yes | - | `Drug X Treatment` |
| **description** | Text | Intervention description | No | - | `Active treatment with Drug X` |
| **label** | Text | Intervention label | No | - | `Drug X` |
| **type** | CDISC CT | Type of intervention | Yes | C99078 | `Pharmacologic Substance` |
| **role** | CDISC CT | Role of intervention | No | C207417 | `Experimental Intervention` |
| **codes** | CDISC CT Codes | Additional codes | No | - | `C1909:Pharmacologic Substance` |
| **minimumResponseDuration** | Quantity | Minimum response duration | No | - | `4 weeks` |
| **administrationName** | Text | Administration name | Yes | - | `Daily Oral Dose` |
| **administrationDescription** | Text | Administration description | No | - | `Once daily oral administration` |
| **administrationLabel** | Text | Administration label | No | - | `QD PO` |
| **administrationDose** | Quantity | Administration dose | Yes | - | `10 mg` |
| **administrationRoute** | CDISC CT | Route of administration | Yes | C66729 | `Oral` |
| **administrationFrequency** | CDISC CT | Frequency of administration | Yes | C71113 | `Once Daily` |
| **product** | Product Reference | Product name | No | - | `Drug X Tablet` |
| **administrationDurationDescription** | Text | Duration description | No | - | `Treatment continues for 12 weeks` |
| **administrationDurationWillVary** | Boolean | Duration will vary flag | Yes | - | `false` |
| **administrationDurationWillVaryReason** | Text | Reason duration varies | No | - | `Based on response` |
| **administrationDurationQuantity** | Quantity | Duration quantity | No | - | `12 weeks` |

**Valid type values (C99078):**
- `Gene Therapy` (C15238)
- `Biological Agent` (C307)
- `Radiation Therapy` (C15313)
- `Medical Device` (C16830)
- `Diagnostic Procedure` (C18020)
- `Pharmacologic Substance` (C1909)
- `Combination Product` (C54696)
- `Dietary Supplement` (C1505)
- `Behavioral Intervention` (C15184)
- `Physical Medical Procedure` (C98769)

**Valid role values (C207417):**
- `Additional Required Treatment` (C207614)
- `Background Treatment` (C165822)
- `Challenge Agent` (C158128)
- `Diagnostic` (C18020)
- `Experimental Intervention` (C41161)
- `Placebo` (C753)
- `Rescue Medicine` (C165835)
- `Active Comparator` (C68609)

## Data Format Guidelines

### Text Fields
- Standard text fields accept any string value
- Leading and trailing whitespace is automatically trimmed
- Empty strings are treated as null/missing values

### CDISC CT Fields
- Use **preferred terms** (human-readable text) rather than C-codes
- System automatically looks up corresponding C-codes
- Case-sensitive matching
- Examples: `Investigational Arm`, `Treatment Epoch`, `Oral`

### Multiple Values
- Separate multiple values with commas
- Example: `In Person, Telephone Call`
- Whitespace around commas is automatically trimmed

### Quantity Fields
- Format: `<value> <unit>`
- Examples: `10 mg`, `4 weeks`, `2.5 hours`
- Units must be valid CDISC CT terms from C71620

### Boolean Fields
- Accepted true values: `true`, `TRUE`, `yes`, `YES`, `1`
- Accepted false values: `false`, `FALSE`, `no`, `NO`, `0`
- Empty values default to `false`

### Reference Fields
- Reference other objects by their `name` field
- Must match exactly (case-sensitive)
- Referenced objects must exist in the system

### Note References
- Reference notes defined in the Notes sheet
- Multiple notes separated by commas
- Example: `Safety Note 1, Efficacy Note`

## CDISC CT Code Lists

The following CDISC CT code lists are used throughout the system:

| Code List | Description | Used For |
|-----------|-------------|----------|
| C66726 | CDISC SDTM Dosage Form Terminology | AdministrableProduct.administrableDoseForm |
| C66729 | CDISC SDTM Route of Administration Terminology | Administration.route |
| C66732 | CDISC SDTM Sex of Study Group Terminology | StudyDesignPopulation.plannedSex |
| C66735 | CDISC SDTM Trial Blinding Schema Terminology | InterventionalStudyDesign.blindingSchema |
| C66736 | CDISC SDTM Trial Indication Type Terminology | InterventionalStudyDesign.intentTypes |
| C66737 | CDISC SDTM Trial Phase Terminology | StudyDesign.studyPhase |
| C66739 | CDISC SDTM Trial Type Terminology | InterventionalStudyDesign.subTypes |
| C66797 | CDISC SDTM Category for Inclusion And Or Exclusion Terminology | EligibilityCriteria.category |
| C71113 | CDISC SDTM Frequency Terminology | Administration.frequency |
| C71620 | CDISC SDTM Unit of Measure Terminology | Quantity.unit |
| C99076 | CDISC SDTM Intervention Model Terminology | StudyDesign.interventionModel |
| C99077 | CDISC SDTM Study Type Terminology | StudyDesign.studyType |
| C99078 | CDISC SDTM Intervention Type Terminology | StudyIntervention.type |
| C99079 | CDISC SDTM Epoch Terminology | StudyEpoch.type |
| C127260 | CDISC SDTM Observational Study Sampling Method Terminology | ObservationalStudyDesign.samplingMethod |
| C127261 | CDISC SDTM Observational Study Time Perspective Terminology | ObservationalStudyDesign.timePerspective |
| C127262 | CDISC SDTM Environmental Setting Terminology | Encounter.environmentalSettings |
| C171445 | CDISC SDTM Mode of Subject Contact Terminology | Encounter.contactModes |
| C174222 | CDISC Protocol Study Arm Type Value Set Terminology | StudyArm.type |
| C188723 | CDISC DDF Protocol Status Value Set Terminology | StudyProtocolVersion.protocolStatus |
| C188724 | CDISC DDF Organization Type Value Set Terminology | Organization.type |
| C188725 | CDISC DDF Objective Level Value Set Terminology | Objective.level |
| C188726 | CDISC DDF Endpoint Level Value Set Terminology | Endpoint.level |
| C188727 | CDISC DDF Study Arm Data Origin Type Value Set Terminology | StudyArm.dataOriginType |
| C188728 | CDISC DDF Encounter Type Value Set Terminology | Encounter.type |
| C201264 | CDISC DDF Timing Type Value Set Terminology | Timing.type |
| C201265 | CDISC DDF Timing Relative To From Value Set Terminology | Timing.relativeToFrom |
| C207412 | CDISC DDF Geographic Scope Type Value Set Terminology | GeographicScope.type |
| C207413 | CDISC DDF Governance Date Type Value Set Terminology | GovernanceDate.type |
| C207415 | CDISC DDF Study Amendment Reason Code Value Set Terminology | StudyAmendmentReason.code |
| C207416 | CDISC DDF Study Design Characteristics Value Set Terminology | StudyDesign.characteristics |
| C207417 | CDISC DDF Study Intervention Role Value Set Terminology | StudyIntervention.role |
| C207418 | CDISC DDF Study Intervention Product Designation Value Set Terminology | AdministrableProduct.productDesignation |
| C207419 | CDISC DDF Study Title Type Value Set Terminology | StudyTitle.type |

For complete lists of valid values, refer to the CDISC CT Excel file at `/Users/daveih/Documents/github/infographics/usdm_ct_infographic/ct.xlsx`.

## Notes

1. **Optional vs Required Sheets**: Most sheets are optional. If a sheet is not present, the system will continue processing other sheets.

2. **Error Handling**: The system provides detailed error messages with cell locations when validation fails.

3. **Cross-References**: Many fields reference objects defined in other sheets. Ensure referenced objects are created before they are referenced.

4. **CDISC CT Updates**: CDISC CT versions can be configured in the Configuration sheet. The system will use the specified versions for code validation.

5. **Extensibility**: Most CDISC CT code lists are extensible, meaning custom codes can be added beyond the standard terminology.

6. **Case Sensitivity**: CDISC CT preferred terms are case-sensitive and must match exactly as defined in the terminology.

# Building the Package
Build steps for deployment to pypi.org

- Build with `python3 -m build --sdist --wheel`
- Upload to pypi.org using `twine upload dist/*`
