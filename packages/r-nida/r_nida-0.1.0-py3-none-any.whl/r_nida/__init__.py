import os
import csv
from typing import Optional, Dict

__all__ = [
    "LocationLookup",
    "NidaParser",
    "NidaService",
    "get_basic_info",
]


class LocationLookup:
    """Locate administrative hierarchy using CSV files in `location_files_code`.
    Usage:
        lookup = LocationLookup()
        data = lookup.get_administrative_hierarchy('35710')
    """

    def __init__(self, csv_dir: Optional[str] = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_dir = csv_dir or os.path.join(base_dir, "location_files_code")

    def _csv_path_for_prefix(self, prefix: str) -> str:
        return os.path.join(self.csv_dir, f"{prefix}.csv")

    def get_administrative_hierarchy(self, ward_id, debug: bool = False) -> Optional[Dict[str, str]]:
        ward_str = str(ward_id).strip()
        if len(ward_str) < 2:
            if debug:
                print("ward_id must have at least 2 characters to select a CSV file")
            return None

        prefix = ward_str[:2]
        csv_filename = self._csv_path_for_prefix(prefix)

        if debug:
            print(f"Looking for CSV file: {csv_filename}")

        if not os.path.exists(csv_filename):
            if debug:
                print(f"CSV file not found: {csv_filename}")
            return None

        try:
            with open(csv_filename, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    matched_key = None
                    # scan all columns for a match (some files use POSTCODE etc)
                    for k, v in row.items():
                        if v is None:
                            continue
                        v_str = str(v).strip()
                        if v_str == ward_str:
                            matched_key = k
                            break
                        else:
                            try:
                                if int(v_str) == int(ward_str):
                                    matched_key = k
                                    break
                            except Exception:
                                pass

                    if matched_key is not None:
                        wardcode_val = (
                            (row.get("WARDCODE") or row.get("PostCode") or row.get("POSTCODE") or row.get("wardcode") or row.get(matched_key) or "")
                            .strip()
                        )

                        result = {
                            "REGION": (row.get("REGION") or row.get("Region") or "").strip(),
                            "REGIONCODE": (row.get("REGIONCODE") or row.get("REGION_CODE") or row.get("POSTCODE") or "").strip(),
                            "DISTRICT": (row.get("DISTRICT") or row.get("District") or "").strip(),
                            "DISTRICTCODE": (row.get("DISTRICTCODE") or row.get("DISTRICT_CODE") or "").strip(),
                            "WARD": (row.get("WARD") or row.get("Ward") or "").strip(),
                            "WARDCODE": wardcode_val,
                            "STREET": (row.get("STREET") or row.get("Street") or "").strip(),
                            "PLACES": (row.get("PLACES") or row.get("Places") or "").strip(),
                        }

                        if debug:
                            print(f"Found row (matched column {matched_key}): {result}")

                        return result

            if debug:
                print(f"No matching ward code {ward_str} found in {csv_filename}")
            return None

        except Exception as e:
            if debug:
                print(f"Error reading CSV: {e}")
            return None


class NidaParser:
    """Parse NIDA / NIN strings into components.

    Supports dashed format YYYYMMDD-LLLLL-SSSSS-XX and compact YYYYMMDDWWWWWSSSSSXX.
    """

    @staticmethod
    def parse(nida_str: str) -> Dict[str, str]:
        s = str(nida_str).strip()
        if '-' in s:
            parts = s.split('-')
            if len(parts) != 4:
                return {"error": "Invalid dashed format: expected 4 segments"}
            raw_date, ward_number, seq_number, unknown = parts
        else:
            if len(s) < 20:
                return {"error": "Invalid compact format: too short"}
            raw_date = s[0:8]
            ward_number = s[8:13]
            seq_number = s[13:18]
            unknown = s[18:20]

        formatted_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"

        return {
            "date": formatted_date,
            "ward_number": ward_number,
            "seq_number": seq_number,
            "unknown": unknown,
        }


class NidaService:
    """High-level service that combines parsing and location lookup.

    Example:
        svc = NidaService()
        svc.get_basic_info('19990504-35710-00001-28')
    """

    def __init__(self, location_lookup: Optional[LocationLookup] = None):
        self.location_lookup = location_lookup or LocationLookup()

    def get_basic_info(self, nida_str: str, debug: bool = False) -> Optional[Dict[str, str]]:
        parse_data = NidaParser.parse(nida_str)
        if parse_data.get("error"):
            if debug:
                print(f"Parse error: {parse_data.get('error')}")
            return None

        ward_id = parse_data.get("ward_number")
        if ward_id is None:
            if debug:
                print("Failed to parse ward number from NIN")
            return None

        location_data = self.location_lookup.get_administrative_hierarchy(ward_id, debug=debug)

        gender = "MALE" if str(parse_data.get("unknown", "")).startswith("2") else "FEMALE"

        result = {"BIRTHDATE": parse_data.get("date"), "GENDER": gender}
        if location_data:
            result.update(location_data)

        return result


def get_basic_info(nin: str, csv_dir: Optional[str] = None, debug: bool = False) -> Optional[Dict[str, str]]:
    """Convenience function: parse and lookup by NIN only.

    Parameters:
        nin: the NIN/NIDA string to parse
        csv_dir: optional path to the CSV directory (overrides default)
        debug: enable debug prints

    Returns:
        dict of basic info or None on failure
    """
    lookup = LocationLookup(csv_dir)
    svc = NidaService(location_lookup=lookup)
    return svc.get_basic_info(nin, debug=debug)


if __name__ == "__main__":
    # Demo: use the convenience function
    nin = "19990504-35710-00001-28"
    info = get_basic_info(nin, debug=False)
    print(info)


