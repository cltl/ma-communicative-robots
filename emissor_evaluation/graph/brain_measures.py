import rdflib


def get_number_triples(graph: rdflib.Graph):
    ans = graph.query('SELECT (COUNT(*) as ?triples) WHERE {?s ?p ?o .}')
    ans = [row for row in ans]
    return float(ans[0].triples)


# Claims
def get_number_statements(graph: rdflib.Graph):
    ans = graph.query('PREFIX gaf: <http://groundedannotationframework.org/gaf#> '
                      'SELECT DISTINCT ?statement WHERE {?statement a gaf:Assertion .}')
    return len(ans)


def get_number_grasp_instances(graph: rdflib.Graph):
    ans = graph.query('PREFIX gaf: <http://groundedannotationframework.org/gaf#> '
                      'SELECT DISTINCT ?instance WHERE {?instance a gaf:Instance .}')
    return len(ans)


# Perspectives
def get_number_perspectives(graph: rdflib.Graph):
    ans = graph.query('PREFIX grasp: <http://groundedannotationframework.org/grasp#> '
                      'SELECT DISTINCT ?perspective WHERE {?perspective a grasp:Attribution .}')
    return len(ans)


def get_number_mentions(graph: rdflib.Graph):
    ans = graph.query('PREFIX gaf: <http://groundedannotationframework.org/gaf#> '
                      'SELECT DISTINCT ?mention WHERE {?mention a gaf:Mention .}')
    return len(ans)


# Interactions
def get_number_chats(graph: rdflib.Graph):
    ans = graph.query('PREFIX gaf: <http://groundedannotationframework.org/gaf#> '
                      'SELECT DISTINCT ?chat WHERE {?chat a gaf:Chat .}')
    return len(ans)


def get_number_utterances(graph: rdflib.Graph):
    ans = graph.query('PREFIX grasp: <http://groundedannotationframework.org/grasp#> '
                      'SELECT DISTINCT ?utt WHERE {?utt a grasp:Utterance .}')
    return len(ans)


def get_number_sources(graph: rdflib.Graph):
    ans = graph.query('PREFIX grasp: <http://groundedannotationframework.org/grasp#> '
                      'SELECT DISTINCT ?source WHERE {?source a grasp:Source .}')
    return len(ans)


# Conflicts
def get_number_negation_conflicts(graph: rdflib.Graph):
    sparql_query = """
        PREFIX gaf: <http://groundedannotationframework.org/gaf#>
        PREFIX grasp: <http://groundedannotationframework.org/grasp#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX graspf: <http://groundedannotationframework.org/grasp/factuality#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
        
        SELECT ?g (COUNT(DISTINCT ?authorPos) as ?numPos) (COUNT(DISTINCT ?authorNeg) as ?numNeg)
        
        WHERE {
            ?g gaf:denotedBy ?mPos .
            ?mPos grasp:hasAttribution ?attPos .
            ?attPos rdf:value graspf:POSITIVE .
            ?attPos rdf:value / rdf:type graspf:PolarityValue .
            ?mPos prov:wasDerivedFrom ?uttPos .
            ?uttPos rdf:type grasp:Utterance .
            ?contPos sem:hasEvent / sem:hasSubEvent ?uttPos .
            ?contPos ?time_predPos ?datePos .
            VALUES (?time_predPos) { (sem:hasTime) (sem:hasBeginTimeStamp) } .
            ?mPos grasp:wasAttributedTo ?authorPos .
        
            ?g gaf:denotedBy ?mNeg .
            ?mNeg grasp:hasAttribution ?attNeg .
            ?attNeg rdf:value graspf:NEGATIVE .
            ?attNeg rdf:value / rdf:type graspf:PolarityValue .
            ?mNeg prov:wasDerivedFrom ?uttNeg .
            ?uttNeg rdf:type grasp:Utterance .
            ?contNeg sem:hasEvent / sem:hasSubEvent ?uttNeg .
            ?contNeg ?time_predNeg ?dateNeg .
            VALUES (?time_predNeg) { (sem:hasTime) (sem:hasBeginTimeStamp) } .
            ?mNeg grasp:wasAttributedTo ?authorNeg .
        
        
            FILTER (STRSTARTS(STR(?authorPos), "http://cltl.nl/leolani/friends/")
                    && STRSTARTS(STR(?authorNeg), "http://cltl.nl/leolani/friends/")
            ) .
        
        }
        GROUP BY ?g
    """

    ans = graph.query(sparql_query)
    ans = [row for row in ans]
    return len(ans)


# Gaps

# Density
def get_average_mentions_per_factoid(graph: rdflib.Graph):
    # How often we talk about the same things
    sparql_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX gaf: <http://groundedannotationframework.org/gaf#>
        PREFIX grasp: <http://groundedannotationframework.org/grasp#>

        SELECT (AVG(?numMentions) AS ?avgMentions) WHERE {
          {
            SELECT DISTINCT ?statement (COUNT(DISTINCT ?mention) AS ?numMentions) WHERE {
              ?statement rdf:type gaf:Assertion;
                gaf:denotedBy ?mention.
            }
            GROUP BY ?statement
          }
        }
    """

    ans = graph.query(sparql_query)
    ans = [row for row in ans]
    return float(ans[0].avgMentions)


def get_average_views_per_factoid(graph: rdflib.Graph):
    # How diverse opinions about the things we know
    sparql_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX gaf: <http://groundedannotationframework.org/gaf#>
        PREFIX grasp: <http://groundedannotationframework.org/grasp#>
        
        SELECT (AVG(?numAttributions) AS ?avgViews) WHERE {
          {
            SELECT DISTINCT ?statement (COUNT(DISTINCT ?attribution) AS ?numAttributions) WHERE {
              ?statement rdf:type gaf:Assertion;
                gaf:denotedBy ?mention.
              ?mention grasp:hasAttribution ?attribution.
            }
            GROUP BY ?statement
          }
        }
    """

    ans = graph.query(sparql_query)
    ans = [row for row in ans]
    return float(ans[0].avgViews)


def get_average_turns_per_interaction(graph: rdflib.Graph):
    # How long are the interactions
    sparql_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX grasp: <http://groundedannotationframework.org/grasp#>
        PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
        
        SELECT (AVG(?numUtterances) AS ?avgUtterances) WHERE {
          {
            SELECT DISTINCT ?chat (COUNT(DISTINCT ?utterance) AS ?numUtterances) WHERE {
              ?chat rdf:type grasp:Chat;
                sem:hasSubEvent ?utterance.
            }
            GROUP BY ?chat
          }
        }
    """

    ans = graph.query(sparql_query)
    ans = [row for row in ans]
    return float(ans[0].avgUtterances)


def get_average_factoids_per_source(graph: rdflib.Graph):
    # How much knowledge per source
    sparql_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX grasp: <http://groundedannotationframework.org/grasp#>
        PREFIX gaf: <http://groundedannotationframework.org/gaf#>
        
        SELECT (AVG(?numStatements) AS ?avgStatements) WHERE {
          {
            SELECT DISTINCT ?author (COUNT(DISTINCT ?statement) AS ?numStatements) WHERE {
              ?author rdf:type grasp:Source.
              ?statement gaf:denotedBy / grasp:wasAttributedTo ?author.
            }
            GROUP BY ?author
          }
        }
    """

    ans = graph.query(sparql_query)
    ans = [row for row in ans]
    return float(ans[0].avgStatements)


def get_average_views_per_source(graph: rdflib.Graph):
    # How many opinions per source
    sparql_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX grasp: <http://groundedannotationframework.org/grasp#>

        SELECT (AVG(?numAttributions) AS ?avgAttributions) WHERE {
          {
            SELECT DISTINCT ?author (COUNT(DISTINCT ?attribution) AS ?numAttributions) WHERE {
              ?author rdf:type grasp:Source.
              ?mention grasp:wasAttributedTo ?author;
                grasp:hasAttribution ?attribution.
            }
            GROUP BY ?author
          }
        }
    """

    ans = graph.query(sparql_query)
    ans = [row for row in ans]
    return float(ans[0].avgAttributions)
