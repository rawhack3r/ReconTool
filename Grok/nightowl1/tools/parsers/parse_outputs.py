
import json
import xml.etree.ElementTree as ET
import re
from nightowl.core.error_handler import ErrorHandler

class ParseOutputs:
    @staticmethod
    def parse_subfinder_output(file_path):
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            ErrorHandler.log_error(f"Error parsing subfinder output: {e}")
            return []

    @staticmethod
    def parse_assetfinder_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_findomain_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_amass_output(file_path):
        try:
            with open(file_path, 'r') as f:
                return [json.loads(line)['name'] for line in f if line.strip()]
        except Exception as e:
            ErrorHandler.log_error(f"Error parsing amass output: {e}")
            return []

    @staticmethod
    def parse_sublist3r_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_gotator_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_puredns_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_subdomainfinder_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_crt_sh_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_dnsrecon_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_certspotter_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_dnsgen_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_trufflehog_output(file_path):
        try:
            with open(file_path, 'r') as f:
                return [json.loads(line)['Raw'] for line in f if line.strip()]
        except Exception as e:
            ErrorHandler.log_error(f"Error parsing trufflehog output: {e}")
            return []

    @staticmethod
    def parse_gitleaks_output(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return [finding['Secret'] for finding in data]
        except Exception as e:
            ErrorHandler.log_error(f"Error parsing gitleaks output: {e}")
            return []

    @staticmethod
    def parse_secretfinder_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_gf_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_hunter_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_theharvester_output(file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            results = []
            for elem in root.findall(".//email"):
                results.append(elem.text)
            for elem in root.findall(".//host"):
                results.append(elem.text)
            return results
        except Exception as e:
            ErrorHandler.log_error(f"Error parsing theHarvester output: {e}")
            return []

    @staticmethod
    def parse_katana_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_ffuf_output(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return [result['url'] for result in data.get('results', [])]
        except Exception as e:
            ErrorHandler.log_error(f"Error parsing ffuf output: {e}")
            return []

    @staticmethod
    def parse_gau_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_waybackurls_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_dnsdumpster_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_shodan_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_nuclei_output(file_path):
        try:
            with open(file_path, 'r') as f:
                return [json.loads(line)['info']['name'] for line in f if line.strip()]
        except Exception as e:
            ErrorHandler.log_error(f"Error parsing nuclei output: {e}")
            return []

    @staticmethod
    def parse_zap_output(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return [alert['alert'] for alert in data.get('alerts', [])]
        except Exception as e:
            ErrorHandler.log_error(f"Error parsing zap output: {e}")
            return []

    @staticmethod
    def parse_metasploit_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_cloudenum_output(file_path):
        return ParseOutputs.parse_subfinder_output(file_path)

    @staticmethod
    def parse_httpx_output(file_path):
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            ErrorHandler.log_error(f"Error parsing httpx output: {e}")
            return []