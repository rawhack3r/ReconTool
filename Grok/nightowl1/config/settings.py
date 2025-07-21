import os

SETTINGS = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "MAX_THREADS": 50,
    "MAX_PROCESSES": 8,
    "OUTPUT_DIR": "output",
    "REPORT_DIR": "output/reports",
    "WORDLISTS": {
        "subdomains": "data/wordlists/subdomains.txt",
        "directories": "data/wordlists/directories.txt",
        "fuzz_params": "data/wordlists/fuzz_params.txt"
    }
}