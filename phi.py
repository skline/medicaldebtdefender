from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
import hashlib
import base64
import re
# Custom Recognizer for SSN (10 digits)
class SSNRecognizer(PatternRecognizer):
    def __init__(self):
        # Regex pattern to match SSN in the format "123-38-9865" or any nine-digit number
        patterns = [
            Pattern("SSN (dashes)", r"\b\d{3}-\d{2}-\d{4}\b", 0.9),  # SSN with dashes
            Pattern("SSN (no dashes)", r"\b\d{9}\b", 0.8),  # SSN without dashes,
            Pattern("SSN (spaces)", r"\b\d{3} \d{2} \d{4}\b", 0.8),
            Pattern("Passport Number", r"\b[A-Z]{1,3}\d{6,9}\b", 0.8)

        ]
        super().__init__(supported_entity="SSN", patterns=patterns)
class ZipCodeRecognizer(PatternRecognizer):
    def __init__(self):
        # Regex pattern to match US Zip Code in the format "12345" or "12345-6789"
        patterns = [
            Pattern("ZIP (5 digits or ZIP+4)", r"\b\d{5}(-\d{4})?\b", 0.9)
        ]
        super().__init__(supported_entity="ZIP", patterns=patterns)
class StateRecognizer(PatternRecognizer):
    def __init__(self):
        # List of US state names and two-letter abbreviations
        states = [
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
            "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
            "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
            "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
            "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
            "West Virginia", "Wisconsin", "Wyoming", "AL", "AK", "AZ", "AR", "CA",  "CT", "DE", "FL", "GA", "HI", "ID", "IL",
             "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC",
            "ND", "OH", "OK",  "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ]
        # Create a pattern for each state
        patterns = [Pattern(f"State ({state})", rf"(?i)\b{state}\b", 0.9) for state in states]
        super().__init__(supported_entity="STATE", patterns=patterns)
# Custom Recognizer for US Address
class AddressRecognizer(PatternRecognizer):
    def __init__(self):
        street_types = [
    "Alley", "Allee", "Ally", "Aly", "Annex", "Anex", "Annx", "Anx",
    "Arcade", "Arc", "Avenue", "Av", "Ave", "Aven", "Avenu", "Avn", "Avnue",
    "Bayou", "Bayoo", "Byu", "Beach", "Bch", "Bend", "Bnd",
    "Bluff", "Bluf", "Blf", "Bluffs", "Blfs",
    "Bottom", "Bot", "Bottm", "Btm", "Boulevard", "Boul", "Boulv", "Blvd",
    "Branch", "Brnch", "Br", "Bridge", "Brdge", "Brg", "Brook", "Brk",
    "Brooks", "Brks", "Burg", "Bg", "Burgs", "Bgs", "Bypass", "Bypa", "Bypas", "Byps", "Byp",
    "Camp", "Cmp", "Cp", "Canyon", "Canyn", "Cnyn", "Cyn", "Cape", "Cpe",
    "Causeway", "Causwa", "Cswy", "Center", "Cen", "Cent", "Centr", "Centre", "Cnter", "Cntr", "Ctr",
    "Centers", "Ctrs", "Circle", "Circ", "Circl", "Crcl", "Crcle", "Cir", "Circles", "Cirs",
    "Cliff", "Clf", "Cliffs", "Clfs", "Club", "Clb", "Common", "Cmn", "Commons", "Cmns",
    "Corner", "Cor", "Corners", "Cors", "Course", "Crse", "Court", "Ct", "Courts", "Cts",
    "Cove", "Cv", "Coves", "Cvs", "Creek", "Crk", "Crescent", "Crsent", "Crsnt", "Cres", "Crest", "Crst",
    "Crossing", "Crssng", "Xing", "Crossroad", "Xrd", "Curve", "Curv",
    "Dale", "Dl", "Dam", "Dm", "Divide", "Div", "Dvd", "Dv",
    "Drive", "Driv", "Drv", "Dr", "Drives", "Drs",
    "Estate", "Est", "Estates", "Ests", "Expressway", "Exp", "Expr", "Express", "Expw", "Expwy", "Expy",
    "Extension", "Extn", "Extnsn", "Ext", "Extensions", "Exts", "Fall", "Falls", "Fls",
    "Ferry", "Frry", "Fry", "Field", "Fld", "Fields", "Flds", "Flat", "Flt", "Flats", "Flts",
    "Ford", "Frd", "Fords", "Frds", "Forest", "Frst", "Forge", "Forg", "Frg", "Forges", "Frgs",
    "Fork", "Frk", "Forks", "Frks", "Fort", "Frt", "Ft",
    "Freeway", "Freewy", "Frway", "Frwy", "Fwy",
    "Garden", "Gardn", "Grden", "Grdn", "Gdn", "Gardens", "Gdns",
    "Gateway", "Gatewy", "Gatway", "Gtway", "Gtwy", "Glen", "Gln", "Glens", "Glns",
    "Green", "Grn", "Greens", "Grns", "Grove", "Grov", "Grv", "Groves", "Grvs",
    "Harbor", "Harb", "Harbr", "Hrbor", "Hbr", "Harbors", "Hbrs",
    "Haven", "Hvn", "Heights", "Hts", "Highway", "Highwy", "Hiway", "Hiwy", "Hway", "Hwy",
    "Hill", "Hl", "Hills", "Hls", "Hollow", "Hllw", "Holw", "Holws",
    "Inlet", "Inlt", "Island", "Is", "Islands", "Iss", "Isle",
    "Junction", "Jction", "Jctn", "Junctn", "Juncton", "Jct", "Junctions", "Jcts",
    "Key", "Ky", "Keys", "Kys", "Knoll", "Knol", "Knl", "Knolls", "Knls",
    "Lake", "Lk", "Lakes", "Lks", "Land", "Landing", "Lndng", "Lndg", "Lane", "La", "Ln",
    "Light", "Lgt", "Lights", "Lgts", "Loaf", "Lf", "Lock", "Lck", "Locks", "Lcks",
    "Lodge", "Ldge", "Lodg", "Ldg", "Loop", "Lp", "Mall", "Manor", "Mnr", "Manors", "Mnrs",
    "Meadow", "Mdw", "Meadows", "Medows", "Mdws", "Mews", "Mill", "Ml", "Mills", "Mls",
    "Mission", "Msn", "Motorway", "Mtwy", "Mount", "Mt", "Mountain", "Mtn", "Mountains", "Mtns",
    "Neck", "Nck", "Orchard", "Orchrd", "Orch", "Oval", "Ovl", "Overpass", "Opas",
    "Park", "Prk", "Parks", "Parkway", "Parkwy", "Pkway", "Pky", "Pkwy", "Parkways", "Pkwys",
    "Pass", "Passage", "Psge", "Path", "Pike", "Pk", "Pine", "Pne", "Pines", "Pnes",
    "Place", "Pl", "Plain", "Pln", "Plains", "Plns", "Plaza", "Plza", "Plz",
    "Point", "Pt", "Points", "Pts", "Port", "Prt", "Ports", "Prts",
    "Prairie", "Prr", "Pr", "Radial", "Rad", "Radiel", "Radl", "Ramp",
    "Ranch", "Rnch", "Rnchs", "Rapid", "Rpd", "Rapids", "Rpds", "Rest", "Rst",
    "Ridge", "Rdge", "Rdg", "Ridges", "Rdgs", "River", "Rvr", "Rivr", "Riv",
    "Road", "Rd", "Roads", "Rds", "Route", "Rte", "Row", "Rue", "Run",
    "Shoal", "Shl", "Shoals", "Shls", "Shore", "Shr", "Shores", "Shrs",
    "Skyway", "Skwy", "Spring", "Spng", "Sprng", "Spg", "Springs", "Spgs", "Spur",
    "Square", "Sqr", "Sqre", "Squ", "Sq", "Squares", "Sqs", "Station", "Statn", "Stn", "Sta",
    "Strasse", "Stravenue", "Strav", "Straven", "Stravn", "Strvn", "Strvnue", "Stra",
    "Stream", "Streme", "Strm", "Street", "Str", "Strt", "St", "Streets", "Sts",
    "Summit", "Sumit", "Sumitt", "Smt", "Terrace", "Terr", "Ter",
    "Throughway", "Trwy", "Trace", "Trce", "Track", "Trak", "Trk", "Trks",
    "Trafficway", "Trfy", "Trail", "Trl", "Trailer", "Trlr", "Tunnel", "Tunl",
    "Turnpike", "Trnpk", "Turnpk", "Tpke", "Underpass", "Upas", "Union", "Un", "Unions", "Uns",
    "Valley", "Vally", "Vlly", "Vly", "Valleys", "Vlys", "Via", "Viaduct", "Vdct", "Viadct", "Via",
    "View", "Vw", "Views", "Vws", "Village", "Vill", "Well", "Wl", "Wells", "Wls", 'Vista', 'Vist', 'Vst', 'Vsta', 'Vis', 'Walk', 'Wall', 'Way', 'Wy'
        ]
        street_types_pattern = "|".join(street_types)
        pattern = r"(?i)\b\d{1,5}\s(?:[A-Za-z]+\s)*(?:" + street_types_pattern + r")\b"
        super().__init__(supported_entity="ADDRESS", patterns=[Pattern("Address (general)", pattern, 0.85), Pattern("Address (extended)", r"\b(?:[A-Z][a-z]+ )+\d{1,5}(?: [A-Z][a-z]+)*,? (?:Apt|Suite) \d{1,5}\b", 0.8)],)

class PhoneNumberRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern("Phone Number", r"\b\d{3}-\d{3}-\d{4}\b", 0.9),  # Standard US phone number format
            Pattern("Phone Number (intl)", r"\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}\b", 0.8),
            Pattern("Phone Number (dots)", r"\b\d{3}\.\d{3}\.\d{4}\b", 0.8),
            Pattern("Date (intl)", r"\b\d{2}/\d{2}/\d{4}\b", 0.8)
        ]
        super().__init__(supported_entity="PHONE_NUMBER", patterns=patterns)

def anonymize_emails(text, hash_mapping):
    # Enhanced regex pattern to match a broader range of email formats
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,6}\b')
    emails = email_pattern.findall(text)
    for email in emails:
        hashed_email = hash_text(email)  # Using the existing hash_text function
        hash_mapping[f"EMAIL:{hashed_email}"] = email
        text = text.replace(email, f"<EMAIL:{hashed_email}>")
    return text



# Function to hash a given text and return a 15-character hash
def hash_text(text, salt="your_salt_here"):
    hash_object = hashlib.sha256((text + salt).encode())
    # Using base64 to encode the hash to get a shorter representation
    return base64.urlsafe_b64encode(hash_object.digest()).decode()[:15]

# Create an instance of the AnalyzerEngine and add custom recognizers
analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(SSNRecognizer())
analyzer.registry.add_recognizer(AddressRecognizer())
analyzer.registry.add_recognizer(ZipCodeRecognizer())
analyzer.registry.add_recognizer(StateRecognizer())
analyzer.registry.add_recognizer(PhoneNumberRecognizer())

# Create an instance of the AnonymizerEngine
anonymizer = AnonymizerEngine()

# Your clinical note
clinical_notes = [
    "Contact John Doe at 1234 Maple St, Smalltown, CO 80027 or via email at johndoe@example.com. His SSN is 123-45-6789 and phone number is 123-456-7890.",
    "Jane Smith's address is 5678 Oak St, Bigcity, NY 10001, SSN 987-65-4321, and her email is janesmith@email.com. Reach her at 987-654-3210.",
    "Dr. Emily Johnson, residing at 4321 Pine Blvd, Lakeside, CA 92008, can be contacted at emilyj@hospital.org or 456-789-0123. Her SSN is 234-56-7890.",
    "Alex Brown, from 8765 Elm Lane, Riverside, TX 75001, email alexb@provider.com, phone 321-654-0987, SSN 345-67-8901.",
    "Dr. Brian Cox at 1357 Cedar Ave, Mountainview, WA 98001, email: brian.cox@university.edu, phone: 567-890-1234, SSN 456-78-9012.",
    """
Today, I had a consultation with John Doe, born on 01/01/1980. Mr. Doe, reachable at johndoe@gmail.com or by phone at 123-456-7890, came in complaining of severe headaches. His medical record number MRN1234567 shows a history of migraines. He currently resides at 1234 Main St, Smalltown, CO 80027. For our records, he provided his SSN as 123456789. Treatment options were discussed, and a follow-up appointment was scheduled.
"""
    # ... (additional test strings) ...
]
for clinical_note in clinical_notes:
    hash_mapping = {}

    clinical_note = anonymize_emails(clinical_note, hash_mapping)


    # Analyze the text to identify personal information
    analysis_results = analyzer.analyze(text=clinical_note, language='en')

    # Sort results in reverse order to avoid offset issues
    analysis_results = sorted(analysis_results, key=lambda x: x.start, reverse=True)

    # Hash mapping for re-identification

    # Initialize previous end position to avoid overlapping replacements
    previous_end = len(clinical_note)

    # Anonymize each identified entity
    for result in analysis_results:
        # Skip if this entity overlaps with a previously replaced one
        if result.end > previous_end:
            continue

        original_text = clinical_note[result.start:result.end]
        hashed_text = hash_text(original_text)
        entity_hash = f"{result.entity_type.upper()}:{hashed_text}"
        hash_mapping[entity_hash] = original_text
        replacement_text = f"<{entity_hash}>"
        clinical_note = clinical_note[:result.start] + replacement_text + clinical_note[result.end:]

        # Update previous end position
        previous_end = result.start

    # Print the anonymized text
    print(clinical_note)

    # Print the hash mapping
    print("\nHash Mapping:")
    for entity_hash, original_value in hash_mapping.items():
        print(f"{entity_hash}: {original_value}")
    print()