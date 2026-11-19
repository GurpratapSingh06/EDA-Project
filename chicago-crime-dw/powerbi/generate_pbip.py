import json
import os

base_dir = r"M:\Third Year\PEC Exploratory Data Analytics LAB\EDA Project\chicago-crime-dw"
export_dir = os.path.join(base_dir, "outputs", "powerbi_exports").replace("\\", "/")
target_root = os.path.join(base_dir, "powerbi")

os.makedirs(os.path.join(target_root, "ChicagoCrimeAnalytics.Report"), exist_ok=True)
os.makedirs(os.path.join(target_root, "ChicagoCrimeAnalytics.SemanticModel"), exist_ok=True)

# 1. PBIP file
pbip_path = os.path.join(target_root, "ChicagoCrimeAnalytics.pbip")
with open(pbip_path, "w", encoding="utf-8") as f:
    json.dump({
        "version": "1.0",
        "artifacts": [
            {"report": {"path": "ChicagoCrimeAnalytics.Report"}}
        ],
        "settings": {"enableAutoAuth": True}
    }, f, indent=2)

# 2. PBIR file
pbir_path = os.path.join(target_root, "ChicagoCrimeAnalytics.Report", "definition.pbir")
with open(pbir_path, "w", encoding="utf-8") as f:
    json.dump({
        "version": "1.0",
        "datasetReference": {
            "byPath": {"path": "../ChicagoCrimeAnalytics.SemanticModel"},
            "byConnection": None
        }
    }, f, indent=2)

# 3. PBISM file
pbism_path = os.path.join(target_root, "ChicagoCrimeAnalytics.SemanticModel", "definition.pbism")
with open(pbism_path, "w", encoding="utf-8") as f:
    json.dump({"version": "1.0"}, f, indent=2)

# 4. model.bim
model = {
    "name": "ChicagoCrimeDW",
    "compatibilityLevel": 1550,
    "model": {
        "culture": "en-US",
        "dataAccessOptions": {
            "legacyRedirects": True,
            "returnErrorValuesAsNull": True
        },
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "sourceQueryCulture": "en-US",
        "tables": [
            {
                "name": "dim_date",
                "columns": [
                    {"name": "datekey", "dataType": "int64", "sourceColumn": "datekey", "isKey": True, "summarizeBy": "none"},
                    {"name": "fulldate", "dataType": "dateTime", "sourceColumn": "fulldate"},
                    {"name": "day", "dataType": "int64", "sourceColumn": "day", "summarizeBy": "none"},
                    {"name": "dayname", "dataType": "string", "sourceColumn": "dayname"},
                    {"name": "dayofweek", "dataType": "int64", "sourceColumn": "dayofweek", "summarizeBy": "none"},
                    {"name": "week", "dataType": "int64", "sourceColumn": "week", "summarizeBy": "none"},
                    {"name": "month", "dataType": "int64", "sourceColumn": "month", "summarizeBy": "none"},
                    {"name": "monthname", "dataType": "string", "sourceColumn": "monthname"},
                    {"name": "quarter", "dataType": "int64", "sourceColumn": "quarter", "summarizeBy": "none"},
                    {"name": "year", "dataType": "int64", "sourceColumn": "year", "summarizeBy": "none"},
                    {"name": "isweekend", "dataType": "boolean", "sourceColumn": "isweekend"}
                ],
                "partitions": [{
                    "name": "dim_date-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            f'    Source = Csv.Document(File.Contents("{export_dir}/dim_date.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                            '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                            '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"datekey", Int64.Type}, {"fulldate", type date}, {"day", Int64.Type}, {"dayname", type text}, {"dayofweek", Int64.Type}, {"week", Int64.Type}, {"month", Int64.Type}, {"monthname", type text}, {"quarter", Int64.Type}, {"year", Int64.Type}, {"isweekend", type logical}})',
                            "in",
                            '    #"Changed Type"'
                        ]
                    }
                }]
            },
            {
                "name": "dim_time",
                "columns": [
                    {"name": "timekey", "dataType": "int64", "sourceColumn": "timekey", "isKey": True, "summarizeBy": "none"},
                    {"name": "hour", "dataType": "int64", "sourceColumn": "hour", "summarizeBy": "none"},
                    {"name": "minute", "dataType": "int64", "sourceColumn": "minute", "summarizeBy": "none"},
                    {"name": "timeband", "dataType": "string", "sourceColumn": "timeband"}
                ],
                "partitions": [{
                    "name": "dim_time-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            f'    Source = Csv.Document(File.Contents("{export_dir}/dim_time.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                            '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                            '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"timekey", Int64.Type}, {"hour", Int64.Type}, {"minute", Int64.Type}, {"timeband", type text}})',
                            "in",
                            '    #"Changed Type"'
                        ]
                    }
                }]
            },
            {
                "name": "dim_crime_type",
                "columns": [
                    {"name": "crimetypekey", "dataType": "int64", "sourceColumn": "crimetypekey", "isKey": True, "summarizeBy": "none"},
                    {"name": "iucr", "dataType": "string", "sourceColumn": "iucr"},
                    {"name": "primarytype", "dataType": "string", "sourceColumn": "primarytype"},
                    {"name": "description", "dataType": "string", "sourceColumn": "description"},
                    {"name": "fbicode", "dataType": "string", "sourceColumn": "fbicode"},
                    {"name": "crimecategorygroup", "dataType": "string", "sourceColumn": "crimecategorygroup"}
                ],
                "partitions": [{
                    "name": "dim_crime_type-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            f'    Source = Csv.Document(File.Contents("{export_dir}/dim_crime_type.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                            '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                            '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"crimetypekey", Int64.Type}, {"iucr", type text}, {"primarytype", type text}, {"description", type text}, {"fbicode", type text}, {"crimecategorygroup", type text}})',
                            "in",
                            '    #"Changed Type"'
                        ]
                    }
                }]
            },
            {
                "name": "dim_location",
                "columns": [
                    {"name": "locationkey", "dataType": "int64", "sourceColumn": "locationkey", "isKey": True, "summarizeBy": "none"},
                    {"name": "district", "dataType": "int64", "sourceColumn": "district", "summarizeBy": "none"},
                    {"name": "beat", "dataType": "int64", "sourceColumn": "beat", "summarizeBy": "none"},
                    {"name": "ward", "dataType": "int64", "sourceColumn": "ward", "summarizeBy": "none"},
                    {"name": "communityarea", "dataType": "int64", "sourceColumn": "communityarea", "summarizeBy": "none"},
                    {"name": "locationdescription", "dataType": "string", "sourceColumn": "locationdescription"},
                    {"name": "locationgroup", "dataType": "string", "sourceColumn": "locationgroup"},
                    {"name": "latitudeband", "dataType": "string", "sourceColumn": "latitudeband"},
                    {"name": "longitudeband", "dataType": "string", "sourceColumn": "longitudeband"}
                ],
                "partitions": [{
                    "name": "dim_location-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            f'    Source = Csv.Document(File.Contents("{export_dir}/dim_location.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                            '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                            '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"locationkey", Int64.Type}, {"district", Int64.Type}, {"beat", Int64.Type}, {"ward", Int64.Type}, {"communityarea", Int64.Type}, {"locationdescription", type text}, {"locationgroup", type text}, {"latitudeband", type text}, {"longitudeband", type text}})',
                            "in",
                            '    #"Changed Type"'
                        ]
                    }
                }]
            },
            {
                "name": "fact_crime_incident_summary",
                "columns": [
                    {"name": "datekey", "dataType": "int64", "sourceColumn": "datekey", "summarizeBy": "none"},
                    {"name": "timekey", "dataType": "int64", "sourceColumn": "timekey", "summarizeBy": "none"},
                    {"name": "crimetypekey", "dataType": "int64", "sourceColumn": "crimetypekey", "summarizeBy": "none"},
                    {"name": "locationkey", "dataType": "int64", "sourceColumn": "locationkey", "summarizeBy": "none"},
                    {"name": "contextkey", "dataType": "int64", "sourceColumn": "contextkey", "summarizeBy": "none"},
                    {"name": "incidentcount", "dataType": "int64", "sourceColumn": "incidentcount"},
                    {"name": "arrestcount", "dataType": "int64", "sourceColumn": "arrestcount"},
                    {"name": "domesticcount", "dataType": "int64", "sourceColumn": "domesticcount"},
                    {"name": "nightcount", "dataType": "int64", "sourceColumn": "nightcount"}
                ],
                "measures": [
                    {"name": "Total Incidents", "expression": "SUM(fact_crime_incident_summary[incidentcount])", "formatString": "#,0"},
                    {"name": "Total Arrests", "expression": "SUM(fact_crime_incident_summary[arrestcount])", "formatString": "#,0"},
                    {"name": "Arrest Rate", "expression": "DIVIDE([Total Arrests], [Total Incidents], 0) * 100", "formatString": "0.00\"%\""},
                    {"name": "Domestic Incidents", "expression": "SUM(fact_crime_incident_summary[domesticcount])", "formatString": "#,0"},
                    {"name": "Domestic Rate", "expression": "DIVIDE([Domestic Incidents], [Total Incidents], 0) * 100", "formatString": "0.00\"%\""},
                    {"name": "Night Incidents", "expression": "SUM(fact_crime_incident_summary[nightcount])", "formatString": "#,0"},
                    {"name": "Night Incident Pct", "expression": "DIVIDE([Night Incidents], [Total Incidents], 0) * 100", "formatString": "0.00\"%\""},
                    {"name": "Distinct Crime Types", "expression": "DISTINCTCOUNT(fact_crime_incident_summary[crimetypekey])", "formatString": "#,0"}
                ],
                "partitions": [{
                    "name": "fact_crime_incident_summary-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            f'    Source = Csv.Document(File.Contents("{export_dir}/fact_crime_incident_summary.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                            '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                            '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"datekey", Int64.Type}, {"timekey", Int64.Type}, {"crimetypekey", Int64.Type}, {"locationkey", Int64.Type}, {"contextkey", Int64.Type}, {"incidentcount", Int64.Type}, {"arrestcount", Int64.Type}, {"domesticcount", Int64.Type}, {"nightcount", Int64.Type}})',
                            "in",
                            '    #"Changed Type"'
                        ]
                    }
                }]
            },
            {
                "name": "fact_area_daily",
                "columns": [
                    {"name": "areadailykey", "dataType": "int64", "sourceColumn": "areadailykey", "summarizeBy": "none"},
                    {"name": "datekey", "dataType": "int64", "sourceColumn": "datekey", "summarizeBy": "none"},
                    {"name": "communityarea", "dataType": "int64", "sourceColumn": "communityarea", "summarizeBy": "none"},
                    {"name": "totalincidentcount", "dataType": "int64", "sourceColumn": "totalincidentcount"},
                    {"name": "totalarrestcount", "dataType": "int64", "sourceColumn": "totalarrestcount"},
                    {"name": "totaldomesticcount", "dataType": "int64", "sourceColumn": "totaldomesticcount"},
                    {"name": "totalnightcount", "dataType": "int64", "sourceColumn": "totalnightcount"},
                    {"name": "distinctcrimetypes", "dataType": "int64", "sourceColumn": "distinctcrimetypes"},
                    {"name": "arrestrate", "dataType": "double", "sourceColumn": "arrestrate"},
                    {"name": "domesticrate", "dataType": "double", "sourceColumn": "domesticrate"}
                ],
                "partitions": [{
                    "name": "fact_area_daily-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            f'    Source = Csv.Document(File.Contents("{export_dir}/fact_area_daily.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                            '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                            '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"areadailykey", Int64.Type}, {"datekey", Int64.Type}, {"communityarea", Int64.Type}, {"totalincidentcount", Int64.Type}, {"totalarrestcount", Int64.Type}, {"totaldomesticcount", Int64.Type}, {"totalnightcount", Int64.Type}, {"distinctcrimetypes", Int64.Type}, {"arrestrate", type number}, {"domesticrate", type number}})',
                            "in",
                            '    #"Changed Type"'
                        ]
                    }
                }]
            }
        ],
        "relationships": [
            {
                "name": "rel_date_fact_crime",
                "fromTable": "fact_crime_incident_summary",
                "fromColumn": "datekey",
                "toTable": "dim_date",
                "toColumn": "datekey"
            },
            {
                "name": "rel_time_fact_crime",
                "fromTable": "fact_crime_incident_summary",
                "fromColumn": "timekey",
                "toTable": "dim_time",
                "toColumn": "timekey"
            },
            {
                "name": "rel_crime_type_fact_crime",
                "fromTable": "fact_crime_incident_summary",
                "fromColumn": "crimetypekey",
                "toTable": "dim_crime_type",
                "toColumn": "crimetypekey"
            },
            {
                "name": "rel_location_fact_crime",
                "fromTable": "fact_crime_incident_summary",
                "fromColumn": "locationkey",
                "toTable": "dim_location",
                "toColumn": "locationkey"
            },
            {
                "name": "rel_date_fact_area",
                "fromTable": "fact_area_daily",
                "fromColumn": "datekey",
                "toTable": "dim_date",
                "toColumn": "datekey"
            }
        ]
    }
}

target_bim = os.path.join(target_root, "ChicagoCrimeAnalytics.SemanticModel", "model.bim")
with open(target_bim, "w", encoding="utf-8") as f:
    json.dump(model, f, indent=2)

print("Generated PBIP project files successfully.")
