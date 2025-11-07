

import json
import re
import uuid
from elasticsearch import Elasticsearch
#from elasticsearch.client import IndicesClient
import pandas as pd
from . import heb_tokenizer


class elasticE():
    def __init__(self,elastic_obj,debug=False):
        self.Debug = debug
        self.es = elastic_obj

    def DeleteIndex(self,index_name):
        ret = -1
        if self.es.indices.exists(index=index_name):
            ret = self.es.indices.delete(index=index_name, ignore=[400, 404])
        return ret


    def CreateIndex(self,index_name,settings = None):
        if settings:
            ret = self.es.indices.create(index=index_name, ignore=400, body=settings)
        else:
            ret = self.es.indices.create(index=index_name, ignore=400)
        return ret


    def DeleteAllDocuments(self,index, document_type):
        return self.es.delete_by_query(index=index, doc_type=document_type, body={"query": {"match_all": {}}})


    def LoadIndex(self,df, index, doc_type, fields=[], conversions=[], limit=0):
        if fields == []:
            fields = list(df.columns.values)
        counter = 1
        for i in range(len(df)):
            new_doc = {}
            for field in fields:
                if 'FloatToInt' in conversions and type(df[field].iloc[i]) == float:
                    new_doc[field] = str(int(df[field].iloc[i]))
                else:
                    new_doc[field] = str(df[field].iloc[i])
            self.es.create(index=index, id=i, doc_type=doc_type, body=new_doc)
            counter += 1
            if limit > 0 and counter > limit:
                break
        return self.es.count(index=index, doc_type=doc_type, body={"query": {"match_all": {}}})

    def AddDocument(self,index, doc_type,doc_id,new_doc):
        self.es.create(index=index, id=doc_id  ,doc_type=doc_type, body=new_doc)

def load_synonyms(path):
    synonyms = {"vocabulary": {}, "lexicons": {}, "conversion":{}}
    if path is None:
        return synonyms
    # '/usr/local/etc/elasticsearch-8.12.2/config/analysis/biblical_synonym.txt'
    try:
        with open(path , 'r', encoding='utf-8') as file:
            lines = [line.rstrip() for line in file if line.strip().lstrip() != ""]
        #print(lines)
        for line in lines:
            if line != "":
                conversion = re.split("=>",line)
                items = conversion[0].split(",")
                lexicon_counter = len(synonyms["lexicons"])
                tmp = {x.strip().lstrip(): lexicon_counter for x in items}
                synonyms["vocabulary"] = {**synonyms["vocabulary"], **tmp}

                if len(conversion)> 1:
                    synonyms["conversion"][lexicon_counter] = conversion[1].strip().lstrip()
                synonyms["lexicons"][lexicon_counter] = [x.strip().lstrip() for x in items]
    except Exception as e:
        raise ValueError(e)

    return synonyms

def write_synonyms(file_name, synonyms):
    conversionTo = "=>"
    f = open(file_name, "w")
    for s in synonyms["lexicons"]:
        line = ",".join(synonyms["lexicons"][s])
        symbol = synonyms["conversion"].get(s, None)
        if symbol is not None:
            line += conversionTo + symbol
        line += "\n"
        #print(line)
        f.write(line)
    f.close()

def get_index_records(es_params):
    les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))


def get_es_analyze_text(index, analyzer, text, es_params=None, les=None):
    '''
    Use the Elasticsearch Analyse request to detect synonyms
    '''
    if les is None:
        if es_params is None:
            return -1

        les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))

    response = les.indices.analyze(
        index=index,
        body={
            "analyzer": analyzer,
            "text": text
        }
    )
    return response


def get_es_records_by_field(field,value, es_params, les= None, default_result = False, all_records = False):
    '''

    :param field: The field to fetch the data from Elasticsearch. If None, fetch all records for the INDEX
    :param value:  The field value
    :param es_params: Connection string
    :param les: Valid connection
    :param default_result:
    :param all_records: True to iterate over the elastic results
    :return:
    '''

    def collect_records(ret, results,default_result):
        for idx, hit in enumerate(results):
            if default_result:
                ret[len(ret)] = hit
            else:
                segment = 0
                if "segment" in hit['_source']: segment = int(hit['_source']['segment'])
                if "external_comments" in hit['_source']:
                    comment = hit['_source']['external_comments']
                else:
                    comment = None
                ret[len(ret)] = {"target_name": hit['_source']['location'],
                                   "target_segment": segment,
                                   "score": hit['_score'],
                                   "id": hit['_id'],
                                   "content":hit['_source'],
                                   "comment": comment}
        return ret


    if les is None:
        les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))
    if field:
        if type(value) == list:
            tmp = [{"match": {field: x}} for x in value]
            q = { "query": { "bool": { "must": tmp } } }
        else:
            q = json.dumps({"query": {"match": {field: value }}})
    else:
        q = json.dumps({"query": {"match_all": {}}})
    if all_records:
        result = les.search(index=es_params['index'], body=q,scroll = '2s')
    else:
        result = les.search(index=es_params['index'], body=q)
    #print(q)
    ret ={}
    if result.get('hits') is not None and len(result['hits']['hits']):
        ret = collect_records(ret, result['hits']['hits'], default_result)
    if all_records and len(result['hits']['hits']):
        old_scroll_id = result['_scroll_id']
        while len(result['hits']['hits']):
            result = les.scroll(
                scroll_id=old_scroll_id,
                scroll='2s'  # length of time to keep search context
            )
            old_scroll_id = result['_scroll_id']
            if result.get('hits') is not None and len(result['hits']['hits']):
                ret = collect_records(ret, result['hits']['hits'], default_result)

    # if result.get('hits') is not None and result['hits'].get('hits') != []:

        # if default_result:
        #     return result['hits']['hits']
        # for idx,hit in enumerate(result['hits']['hits']):
        #
        #     ret[idx] = {"target_name": hit['_source']['location'],
        #                 "target_segment": int(hit['_source']['segment']),
        #                 "score": hit['_score'],
        #                 "id": hit['_id'],
        #                 "content":hit['_source']}

    # ret = collect_records(ret, result['hits']['hits'], default_result)

    return ret

def get_record_by_id(rec_id,params, les=None):
    if les is None:
        les = Elasticsearch(params['ehost'], http_auth=params.get('auth', None))
    rec = les.get(index=params['index'], id=rec_id)
    return rec

def get_es_source_by_field(field,value, es_params, les= None):
    if les is None:
        les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))
    if type(value)==list:
        q = '{"query": {"terms": {"'+field+'": '+str(value)+'}}}'
    else:
        q = '{"query": {"match": {"' + field + '": "' + str(value) + '"}}}'
    result = les.search(index=es_params['index'], body=q)
    ret = pd.DataFrame()
    if result.get('hits') is not None and result['hits'].get('hits') != []:
        # print(f"Total results: {len(result['hits']['hits'])}, Best Score: {result['hits']['max_score']}, Max Score to fetch: {result['hits']['max_score']*0.9}")

        for hit in result['hits']['hits']:

            ret = ret.append({"target_name": hit['_source']['location'],
                              "target_segment": int(hit['_source']['segment']),
                              "score": hit['_score'],
                              "id": hit['_id'],
                              "text": hit['_source']['sentence'],
                              "references": hit['_source']["references"]}, ignore_index=True)
    return ret

def get_es_sentence_from_source(location,les,index,mlog = None):
    sentence = sentence_tokens = None
    try:
        location = location.replace('"',"'")
        q = '''{"query": {"match": {"location": "'''+ location+ '''" }}}'''
        result = les.search(index=index, body=q)
        if len(result['hits']['hits']) > 0:
            sentence = result['hits']['hits'][0]['_source']['sentence']
        # sentence = text_reuse.clean_text(sentence)
        # sentence_tokens= text_reuse.ftokens(sentence)
    except Exception as e:
        if mlog is not None:
            mlog.log(f"Error: Get ES Location From Source, Params: location: {location}, index: {index}\nquery: {q}\n{str(e)}")
        pass
    #return sentence, sentence_tokens
    return sentence


def get_es_scored_source_by_field(field, value, es_params, les=None, size=20):
    if les is None:
        les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))
    q = {
        "size": size,
        "query": {
            "script_score": {
                "query": {
                    "match": {
                        field: value
                    }
                },
                "script": {
                    "source": """ return params['_source']['score']; """
                }
            }
        }
    }

    result = les.search(index=es_params['index'], body=q)

    return result

def get_sentence_count(sentence, fields, es_params,efilter=None, les=None):
    q = query_builder(query_type="match_phrase",
                        text=sentence,
                        fields=fields,
                        size=0,
                        slop=2,
                        filter=efilter,
                        token_spliter=None)



    #print(json.dumps(q,ensure_ascii=False))

    if les is None:
        les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))


    result = les.search(index=es_params['index'], body=q)

    return result

def delete_es_record(doc_id, es_params, les= None):
    try:
        if les is None:
            les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))
        ret = (les.delete(index=es_params['index'],  id=doc_id), "")
    except Exception as e:
        ret = (None, e)
    return ret

def delete_by_query(query, es_params, les= None):
    try:
        if les is None:
            les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))
        ret = les.delete_by_query(index=es_params['index'], body=query)
    except Exception as e:
        ret = (None, e)
    return ret


def post_es_record(doc, es_params, les=None):
    try:
        if les is None:
            les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))
        ret = (les.index(index=es_params['index'], document=doc), "")
    except Exception as e:
        ret = (None, e)
    return ret


def bulk_store(records, es_params, bulk_size=5000, les=None):
    if les is None:
        les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))

    bulk_data = []

    for i in records:
        # print(record[i]['_source'])

        bulk_data.append({"index": {"_index": es_params["index"], }})
        bulk_data.append(records[i]['_source'])

        if len(bulk_data) > bulk_size:
            les.bulk(index=es_params["index"], body=bulk_data, refresh=True)
            bulk_data = []

    if len(bulk_data) > 0:
        les.bulk(index=es_params["index"], body=bulk_data, refresh=True)
        # print("complete")


def copy_records_between_hosts(source_params, target_params, clear_data=False):
    '''

    :param source_params: Parameters to the source host and index {"ehost": '194.195.244.68:9876', "index": "movies4000"}
    :param target_params:Parameters to the traget host
    :param clear_data: To delete the tata from the target index
    :return:
    '''
    if clear_data:
        query = {"query": {"match_all": {}}}
        delete_by_query(query=query, es_params=target_params)

    records = get_es_records_by_field(None, None, es_params=source_params, default_result=True,
                                                        all_records=True)

    bulk_store(records, target_params)


def get_parasha(location_name,es_params={"host": 'http://localhost:9200', "index": "rabbinic2"},
                full_results = False):
    '''

    :param location_name:  like "Midrash_Aggadic Midrash_Midrash Tanchuma Buber__Vayikra_1_1"
    :param es_params:  the elasticsearch host and port
    :param full_results: if True return dataframe with all the document's fields, otherwise retrun the text only
    :return:
    '''

    def _get_parasha(source_name):
        tmp = source_name.split("__")[1].split("_")
        if len(tmp) > 1:
            return " ".join(tmp[:-1])
        else:
            return tmp[0]

    es = Elasticsearch(es_params['host'], http_auth=es_params.get('auth', None))
    parasha = _get_parasha(location_name)
    tmp = get_es_source_by_field("location", location_name,
                                 es_params=es_params,
                                 les=es)
    full_df = tmp[tmp['target_name'] == location_name].copy()
    if len(full_df) == 0:
        if full_results:
            return pd.DataFrame()
        return None
    # print(tmp)
    ret = full_df['text'].iloc[0]
    # tokens = text_reuse.ftokens(tmp['text'].iloc[0])
    current_segment = full_df['target_segment'].iloc[0]
    #         print(current_segment, tmp['text'].iloc[0])
    more_segments = True
    while more_segments:
        tmp = get_es_source_by_field("segment", [current_segment + 1],
                                     es_params={"index": "rabbinic2"}, les=es)
        if len(tmp) > 0 and parasha == _get_parasha(tmp['target_name'].iloc[0]):
            #                 print("Get next segment {}, {}".format(current_segment+1,
            #                                                        tmp['target_name'].iloc[0]))
            full_df = pd.concat([full_df,tmp])
            ret += tmp['text'].iloc[0]
            current_segment += 1
        else:
            more_segments = False
    if full_results:
        return full_df
    return ret



def update_by_id(doc_id, doc, index, es_params, les=None):
    try:
        if les is None:
            les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))
        ret = les.update(index=index, id=doc_id, doc=doc)

    except Exception as e:
        ret = (None, e)
    return ret


def update_by_location(location, doc, index, es_params, les=None):
    try:
        if les is None:
            les = Elasticsearch(es_params['ehost'], http_auth=es_params.get('auth', None))
        record = get_es_records_by_field("location",
                                         location,
                                         es_params=es_params,
                                         les=les)
        record_id = record[0]['id']
        ret = les.update(index=index,
                              id=record_id,
                              body=doc)

    except Exception as e:
        ret = (None, e)
    return ret

def es_tokenizer(txt):
    return txt.split(" ")


def tokens2expresions(suspect_t, index, analyzer, es_params):
    def tokensPositions(tokens):
        '''
        Convert a list oftokens to a dictionary with keys the offset of each token as if
        they were joined by " ".join(tokens)
        '''
        pos2token = {}
        start = 0
        for idx, t in enumerate(tokens):
            pos2token[(start, start + len(t))] = {"token": t, "seq": idx}
            start += len(t) + 1

        return pos2token

    # Use Elasticsearch to find Synonyms (individual experssion)

    # Store the position of each token in the token list
    pos2token = tokensPositions(suspect_t)

    text = " ".join(suspect_t)
    result = get_es_analyze_text(index=index, analyzer=analyzer, text=text, es_params=es_params)

    multitokens = []
    for x in result['tokens']:
        if x['type'] == 'SYNONYM':
            tokens = [pos2token[y]['seq'] for y in pos2token if x['start_offset'] <= y[0] and x['end_offset'] >= y[1]]
            if len(tokens) > 1:
                multitokens.append(tokens)

    # Convert the tokens list to dictionary
    dtokens = {idx: token for idx, token in enumerate(suspect_t)}

    # Filter mltiple tokens syninyms
    for s in multitokens:
        new_value = " ".join([x for idx, x in enumerate(suspect_t) if idx in s])
        dtokens[s[0]] = new_value
        for d in s[1:]:
            del dtokens[d]

    return [dtokens[x] for x in dtokens]


def ftokens(text, spliter=None, lang=None):
    """
    Tokenize text into words based on language and splitter
    
    Args:
        text (str): The text to tokenize
        spliter (str, optional): Custom splitter character
        lang (list, optional): List of language codes to filter tokens by
        
    Returns:
        list: List of tokens
    """
    supported_languages = ["HEB", "LAT", "ARA", "EL"]
    if spliter:
        ret = [x for x in text.split(spliter) if x != '']
    else:
        if lang:
            # Return tokens only for specified languages
            ret = [x[1] for x in heb_tokenizer.tokenize(text) if x[0] in lang]
        else:
            ret = [x[1] for x in heb_tokenizer.tokenize(text) if x[0] in supported_languages]
    return ret


def _clean_special_chars(src):
    '''
    copied from text reuse module
    :param src:
    :return:
    '''
    if src:
        src = src.replace("׳", "'")
        src = src.replace('״','"')
        for sym in ['־' , ":" , "׃"]:
            src = src.replace(sym, " ")
        for sym in ['(' , ")" , "{", "}", "\u200e", "?", ">", "<", "%", "$", "@", "!", "\n", "/", "˙","[","]"]:
            src = src.replace(sym, "")
    return src

def clean_query_text(txt):
    txt = _clean_special_chars(txt)
    sym = [("'", ""), ('"', ""), ("[", " "), ("]", " "), ("}", " "), ("{", " ")]
    for k, v in sym:
        txt = txt.replace(k, v)
    return txt


# def elastic_stemmer(text, index, analyzer, host):
#     client = Elasticsearch(host)
#     indices_client = IndicesClient(client)
#
#     body = {"analyzer": analyzer, "text": text}
#
#     analysis_result = indices_client.analyze(index=index, body=body)
#
#     new_text = ""
#     last_start = 0
#     for token in analysis_result['tokens']:
#         new_text += text[last_start:token['start_offset']] + token['token']
#         last_start = token['end_offset']
#     new_text = re.sub(r'\s+', ' ', new_text)
#     return new_text

def query_builder(text, fields=["sentence"], fuzziness=0, exact_match=True, size=20, slop=0,
                  query_type="span",
                  operator="AND",
                  filter= None,
                  synonyms= False,
                  minimum_tokens = None,
                  token_spliter = None,
                  token_filter = None,
                  highlight=False, win=3, slide=1,filter_field="categories", stop_words=None):
    '''

    :param text: query
    :param fields: a list of fields to search in
    :param fuzziness: the fuzziness of each token
    :param exact_match: whether the order of the tokens is important
    :param size: The size of the resultset
    :param slop: is exact match, whther to allow few insertions
    :param query_type:
    :param operator: And, Or between the tokens
    :param filter: Filter categories: Only documents from certain category, exclude specific categories.
    :param synonyms: Expand the query text with additionl tokens from the disctionary
    :param minimum_tokens: Minimum number/percantage of the query tokens must appear in the text.
    :param tokenizer: a Function to tokenize text
    :return:
    '''

    if query_type == 'query_string':
        q = text
        if fuzziness != 0:
            fuzz = "~" + str(fuzziness) + " "
            arr = ftokens(text, spliter=token_spliter, lang=token_filter)
            if stop_words:
                arr = [x for x in arr if x not in stop_words]
            q = fuzz.join(arr) + fuzz

        tmp = {"query_string": {"fields": fields,
                                  "default_operator": operator,
                                  "query": q}}
        query = {"bool": {"must": tmp } }
    elif query_type == 'match':
        # query = {"query": {"match": {fields[0]: {"query": text,
        #                                          "fuzziness": fuzziness,
        #                                          "operator": operator}}}}
        tmp = {"match": {fields[0]: {"query": text,
                                     "fuzziness": fuzziness,
                                     "operator": operator}}}
        if minimum_tokens:
            tmp["match"][fields[0]]["minimum_should_match"] = minimum_tokens
        query = {"bool": {"must": tmp}}
    elif query_type == "multimatch":
        # "fields": ["sentence^10"],
        # "minimum_should_match": "100%"
        fuzziness_transposition = True
        if fuzziness == 0:
            fuzziness_transposition = False
        tmp = {"multi_match": { "query": text,
                                "fields": fields,
                                "operator": operator,
                                #"tie_breaker": 0.3,
                                "fuzziness": fuzziness,
                                "fuzzy_transpositions": fuzziness_transposition,
                                "auto_generate_synonyms_phrase_query": synonyms
                                }}
        if minimum_tokens:
            tmp["multi_match"]["minimum_should_match"] = minimum_tokens
        query = {"bool": {"must": tmp}}
    elif query_type == "match_phrase":
        tmp = {"match_phrase": {
                  fields[0]: {"query":text, "slop": slop}
                }}
        query = {"bool": {"must": tmp}}

    elif query_type == "match_phrase_windows":
        wf = []
        arr = ftokens(text)
        if stop_words:
            arr = [x for x in arr if x not in stop_words]

        if win==0: win==3

        windows = [arr[i:i+win] for i in range(0,len(arr)-win+1,slide)]
        if len(windows) == 0: return None
        for i in windows:
            tmp= {
                "match_phrase": {
                    fields[0]: {
                        "query": " ".join(i),
                        "slop": slop
                    }
                }
            }
            wf.append(tmp)
        query = {"bool": {"should": wf,  "minimum_should_match": minimum_tokens},

                 } # minimum windows should be matched

    else:
        arr = ftokens(text, spliter=token_spliter, lang=token_filter)
        if stop_words:
            arr = [x for x in arr if x not in stop_words]
        clauses = [{"span_multi":
                        {"match":
                             {"fuzzy": {fields[0]:
                                            {"fuzziness": fuzziness,
                                             "value": term}}}}} for term in arr]
        query = {"bool": {"must": {"span_near": {"clauses": clauses, "slop": slop, "in_order": exact_match}} } }
    if filter and type(filter) == dict:
        if 'must' in filter:
            filterq = [{"match": {filter_field: x}} for x in filter['must']]
            query['bool']['filter'] = {"bool": {"should" :filterq}}
        if 'must_not' in filter:
            filterq = [{"match": {filter_field: x}} for x in filter['must_not']]
            query['bool']['must_not'] = filterq

    ret = {"size": size, "query": query}
    if highlight:
        ret["highlight"] = {
            "pre_tags": ["<text style=color:green;font-weight: bold;>"],
            "post_tags": ["</text>"],
            "fields": {fields[0]: {"type": "plain"}}
        }
        # ret["highlight"] =  {"fields": {fields[0]: {"type": "plain"}}}
    # print("Query Builder\n{} ".format(json.dumps(ret, ensure_ascii=False)))
    return ret


def hebSentence2record(in_path, out_path):

    '''

    :param in_path:
    :param out_path:
    :return: Convert JSON files prepared for the load directory program which are missing the heb_sentence field
            This function copy the "sentence" field to the "heb_sentence" field
    '''
    def stream_read_json(path):
        with open(path, 'r', encoding="utf-8") as f:
            for jsonObj in f:
                obj = json.loads(jsonObj)
                # print(obj)
                yield obj
        return

    def add_record(local_file, rec):
        if not os.path.exists(local_file):
            f = open(local_file, 'w')
            f.close()
        with open(local_file, "a") as fp:
            json.dump(rec, fp, ensure_ascii=False)
            fp.write("\r\n")

    for f in os.listdir(in_path):
        if f.endswith('.json'):
            sj = stream_read_json(in_path + f)
            for r in sj:
                r['heb_sentence'] = r['sentence']
                add_record(out_path + f, r)
            del (sj)

        break



def searchBQsequences(suspect_sequence,params, min_match=6, categories=None):
    es = Elasticsearch(params['ehost'], http_auth=params.get('auth', None))

    #min_match = 6

    # Query to fetch min_match terms of the suspect in the source. 
    # If multiple quotation appear in the source it will be count
    #------------------------------------------------------------
    # should = [{ "term": { "citation_seq.keyword": x }} for x in set(suspect_sequence)]
    # query = { "bool": { "should": should, "minimum_should_match": min_match } }
    # tmp = es.search(index="rabbinic2_citations",
    #                 query=query,
    #                 _source=["location", "citation_seq", "book_chapter_seq", "nodes", "edges","gt_clean_text"], size=20 )


    # Query to fetch min_match terms of the suspect in the source. 
    # It must be unique quotation (Different verse)
    #------------------------------------------------------------
    
    qfilter = {
                        "terms": {
                            "citation_seq.keyword": list(set(suspect_sequence))
                        }
                    }
    
    if categories and type(categories)==list:
        qfilter.append({ "terms": { "categories.keyword": categories } })

    unique_query = {
        "script_score": {
            "query": {
                "bool": {
                    "filter": qfilter
                }
            },
            "script": {
                "source": """
                    int count = 0;
                    Set matched = new HashSet();
                    for (term in params['terms']) {
                        if (doc['citation_seq.keyword'].contains(term)) {
                            matched.add(term);
                        }
                    }
                    return matched.size()
                """,
                "params": {
                    "terms": list(set(suspect_sequence))
                    
                }
            }
        }
    }
    tmp = es.search(index=params['index'],
                    query=unique_query, min_score=min_match,
                    _source=["location", "citation_seq", "book_chapter_seq", "nodes", "edges","gt_clean_text"], 
                    size=30 )
    #print(json.dumps(unique_query, ensure_ascii=False))

    results = []
    #print(f"search4sequences --> index\tScore\tLocation")
    if 'hits' in tmp:
        results = [{"score": x['_score'], "source":x['_source']} for x in  tmp['hits']['hits']]

        # Print results
        # for idx,i in enumerate(tmp['hits']['hits']):
        #     print(f"{idx}\t{i['_score']}\t{i['_source']['location']}")

    return results

