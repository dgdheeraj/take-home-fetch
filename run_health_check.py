import sys
import yaml
import json
import time
import signal
import requests
import multiprocessing
from urllib.parse import urlparse

# Made global - When signal handler is invoked, need to wait for any 
# pending child processes 
jobs = []

def signal_handler(sig, frame):
    while jobs:
        process = jobs.pop(0)
        process.join()
    print("Exiting gracefully...")
    exitProgram()

def exitProgram():
        exit()

def getInputFile():
    num_args = len(sys.argv)
    if num_args != 2:
        print("Invalid Format!\
              Please provide filename in the format - python run_health_check.py <path to the file>\n")
        exitProgram()

    filename = sys.argv[1]
    
    try:
        file_descriptor = open(filename, "r")
        return file_descriptor
    except FileNotFoundError:
        print("File Does not exist!\
              Please provide path to a valid file")
        exitProgram()

def getDomainFromUrl(url):
    domain = urlparse(url).netloc
    return domain

def formatEndpoint(endpoint):
    """
    Function to keep only required agruments in endpoint based
    on specifications
    """
    if endpoint.get("method") == None:
        endpoint["method"] = "GET"
    
    name = endpoint["name"]
    endpoint.pop("name")
    if "body" in endpoint:
        endpoint["data"] = json.loads(endpoint["body"])
        endpoint.pop("body")
    
    return name, endpoint

def formatAllEndpoints(endpoints):
    for i,endpoint in enumerate(endpoints):
        name,params = formatEndpoint(endpoint)
        endpoints[i] = {"name": name, "params": params}
    
    return endpoints

def testEndpoint(name, endpoint, mutex, stats_dict):
    """
    Function to test a endpoint
    
    req -> required
    opt -> optional
    Args:
    @name    (req) - Name to describe the endpoint
    
    Wrapped in endpoint dictionary
    @url     (req) - URL of the endpoint
    @method  (opt) - HTTP method of the endpoint (default: GET)
    @headers (opt) - HTTP header to include in the request
    @body    (opt) - HTTP body to include in the request

    @stats_dict - Shared dictionary accross processes to store statistics
                  of all domains
    @mutex      - Lock to serialize updation of statistics dictionary
    """
    domain = getDomainFromUrl(endpoint["url"])

    try:
        response = requests.request(
            **endpoint,
            timeout=500*1000
        )

        mutex.acquire()
        domain_stats = stats_dict[domain] 
        if 200 <= response.status_code <= 299:
            domain_stats["UP"] += 1
        
        domain_stats["TOTAL"] += 1
        stats_dict[domain] = domain_stats
        mutex.release()

    except requests.exceptions.Timeout:
        mutex.acquire()
        domain_stats = stats_dict[domain] 
        domain_stats["TOTAL"] += 1
        stats_dict[domain] = domain_stats
        mutex.release()

def parseFile(file_descriptor):
    endpoints = []
    try:
        endpoints = yaml.safe_load(file_descriptor)
    except yaml.YAMLError as err:
        # print(err)
        ## Will never come here based on specifications
        exitProgram()
    
    return endpoints

def displayStatistics(stats_dict):
    for domain, stats in stats_dict.items():
        percent = round(100 * stats["UP"] / stats["TOTAL"])
        print(f"{domain} has {percent}% availability percentage")

def testAllEndpoints(endpoints, mutex, stats_dict):
    """
    Create new Process for testing every endpoint to avoid
    serializing requests to each endpoint
    Multithreading does not work as expected in Python 
    since it is serialized due Global Interpreter Lock (GIL)
    """
    for endpoint in endpoints:
        name, params = endpoint["name"], endpoint["params"]
        
        domain = getDomainFromUrl(params["url"])
        if stats_dict.get(domain) is None:
                stats_dict[domain] = {"UP":0, "TOTAL":0}

        process = multiprocessing.Process(target=testEndpoint, args=(name, params, mutex, stats_dict)) 
        jobs.append(process)
        process.start()
    
    while jobs:
        process = jobs.pop(0)
        process.join()
    
    displayStatistics(stats_dict)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    manager = multiprocessing.Manager()
    mutex = manager.Lock()
    stats_dict = manager.dict()

    file_descriptor = getInputFile()
    
    endpoints = parseFile(file_descriptor)
    endpoints = formatAllEndpoints(endpoints)

    while True:
        testAllEndpoints(endpoints, mutex, stats_dict)
        time.sleep(15)

if __name__ == "__main__":
    main()