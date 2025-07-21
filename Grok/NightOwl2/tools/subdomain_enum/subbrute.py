
import dns.resolver
import itertools

def run_subbrute(target, wordlist="data/wordlists/subdomains.txt", output_file="output/subdomains/subbrute.txt"):
    subdomains = []
    try:
        with open(wordlist, "r") as f:
            words = [line.strip() for line in f if line.strip()]
        resolver = dns.resolver.Resolver()
        for word in words:
            subdomain = f"{word}.{target}"
            try:
                resolver.resolve(subdomain, "A")
                subdomains.append(subdomain)
            except:
                pass
        with open(output_file, "w") as f:
            f.write("\n".join(subdomains))
        return subdomains, ""
    except Exception as e:
        return [], str(e)