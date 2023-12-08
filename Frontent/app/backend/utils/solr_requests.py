import requests 
import logging

logger = logging.getLogger("globalLogger")

solr_url_base = "http://localhost:8983/solr/"

def get_solr_data(core, rest_of_url):
    url = solr_url_base + core + "/select?" + rest_of_url
    logger.info("Sending request to Solr: " + url)

    response1 = requests.get(url)
    logger.info("Response from Solr: " + str(response1))
    response = requests.get(url).json()
    return response

def get_last_query(previous_results, core):
    final_query = ""
    for key in previous_results:
        final_query += key + "=" + previous_results[key]
    

    return True


def get_procedural_queries(gpt_query_json):
    query_properties = "query1"
    core_properties = "core1"
    results = []
    while gpt_query_json[query_properties] != None:
        result = get_solr_data(gpt_query_json[core_properties], gpt_query_json[query_properties])
        results.append(result["response"]["docs"])
        query_properties = "query" + str(int(query_properties[5:]) + 1)
        core_properties = "core" + str(int(core_properties[4:]) + 1)
        if query_properties not in gpt_query_json:
            break
    return results
