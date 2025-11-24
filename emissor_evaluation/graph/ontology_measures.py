"""
Code originally from
https://gitlab.ifi.uzh.ch/DDIS-Public/chimp-mat/-/blob/master/kbci_py/methods/ontology_measures.py
Credits to Romana Pernischova
"""

import rdflib


def get_number_classes(graph: rdflib.Graph):
    ans = graph.query(
        'PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT DISTINCT ?s WHERE { ?s rdf:type owl:Class. FILTER isURI(?s) }')
    # named classes - N_C (without owl:Thing and owl:Nothing

    return len(ans)


def get_number_properties(graph: rdflib.Graph):
    ans = graph.query(
        'PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT DISTINCT ?prop WHERE {{?prop a owl:DatatypeProperty} UNION {?prop a owl:ObjectProperty}}')
    return len(ans)


def get_number_instances(graph: rdflib.Graph):
    ans = graph.query(
        'PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?type WHERE { ?s rdf:type ?type. ?type rdf:type owl:Class }')
    return len(ans)


def get_number_properties_object(graph: rdflib.Graph):
    ans = graph.query(
        'PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT DISTINCT ?property WHERE { ?property a owl:ObjectProperty}')
    return len(ans)


def get_number_properties_datatype(graph: rdflib.Graph):
    ans = graph.query(
        'PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT DISTINCT ?property WHERE { ?property a owl:DatatypeProperty }')
    return len(ans)


def get_number_properties_equivClass(graph: rdflib.Graph):
    ans = graph.query(
        'PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?s WHERE { ?s owl:equivalentClass ?o }')
    return len(ans)


def get_number_properties_subclass(graph: rdflib.Graph):
    ans = graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?s WHERE { ?s rdfs:subClassOf ?o }')
    return len(ans)


def get_number_entities(graph: rdflib.Graph, num_classes=None, num_instances=None):
    if num_classes == None:
        num_classes = get_number_classes(graph)
    if num_instances == None:
        num_instances = get_number_instances(graph)

    return num_instances + num_classes


def get_number_inverse(graph: rdflib.Graph):
    ans = graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?s WHERE { ?s owl:inverseOf ?o }')
    return len(ans)


def get_ratio_inverse_relations(graph: rdflib.Graph, num_properties_inverse=None, num_properties=None):
    if num_properties == None:
        num_properties = get_number_properties(graph)
    if num_properties_inverse == None:
        num_properties_inverse = get_number_inverse(graph)

    return float(num_properties_inverse) / float(num_properties) if num_properties != 0 else 0


def get_property_class_ratio(graph: rdflib.Graph, num_properties=None, num_classes=None):
    if num_classes == None:
        num_classes = get_number_classes(graph)
    if num_properties == None:
        num_properties = get_number_properties(graph)

    return float(num_properties) / float(num_classes) if num_classes != 0 else 0


def get_class_property_ratio(graph: rdflib.Graph, num_classes=None, num_properties=None):
    if num_classes == None:
        num_classes = get_number_classes(graph)
    if num_properties == None:
        num_properties = get_number_properties(graph)

    return float(num_classes) / float(num_properties) if num_properties != 0 else 0


def get_avg_population(graph: rdflib.Graph, num_instances=None, num_classes=None):
    if num_classes == None:
        num_classes = get_number_classes(graph)
    if num_instances == None:
        num_instances = get_number_instances(graph)

    return float(num_instances) / float(num_classes) if num_classes != 0 else 0


def get_attribute_richness(graph: rdflib.Graph, num_properties_datatype=None, num_properties=None):
    """Same as ratio of datatype properties / properties"""
    if num_properties == None:
        num_properties = get_number_properties(graph)
    if num_properties_datatype == None:
        num_properties_datatype = get_number_properties_datatype(graph)

    return float(num_properties_datatype) / float(num_properties) if num_properties != 0 else 0


def get_inheritance_richness(graph: rdflib.Graph, num_properties_subclass=None, num_properties=None):
    if num_properties == None:
        num_properties = get_number_properties(graph)
    if num_properties_subclass == None:
        num_properties_subclass = get_number_properties_subclass(graph)

    return float(num_properties_subclass) / float(num_properties) if num_properties != 0 else 0


def get_relationship_richness(graph: rdflib.Graph, num_properties=None, num_properties_subclass=None):
    if num_properties == None:
        num_properties = get_number_properties(graph)
    if num_properties_subclass == None:
        num_properties_subclass = get_number_properties_subclass(graph)

    return float(num_properties) / float(num_properties_subclass + num_properties) if num_properties != 0 else 0


def get_ratio_object_properties(graph: rdflib.Graph, num_properties_object=None, num_properties=None):
    if num_properties == None:
        num_properties = get_number_properties(graph)
    if num_properties_object == None:
        num_properties_object = get_number_properties_object(graph)

    return float(num_properties_object) / float(num_properties) if num_properties != 0 else 0


def get_ratio_datatype_properties(graph: rdflib.Graph, num_properties_datatype=None, num_properties=None):
    if num_properties == None:
        num_properties = get_number_properties(graph)
    if num_properties_datatype == None:
        num_properties_datatype = get_number_properties_datatype(graph)

    return float(num_properties_datatype) / float(num_properties) if num_properties != 0 else 0


### Number of Axioms
def get_number_concept_assertions(graph: rdflib.Graph):
    """number of ABox Axioms: concept assertions"""

    ca = len(graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x a ?y. ?y a owl:Class}'))
    ans = ca
    return ans


def get_number_role_assertions(graph: rdflib.Graph):
    """number of ABox Axioms: role assertions"""

    ra = len(
        graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x ?w ?y. ?w a owl:ObjectProperty}'))
    ans = ra
    return ans


def get_number_GCI(graph: rdflib.Graph, mat=None):
    """number of TBox Axioms: general concept inclusions"""

    sco = len(graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x rdfs:subClassOf ?y }'))
    dis = len(graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x owl:disjointWith ?y }'))
    ans = sco + dis

    if mat == None or not mat:
        eq = 2 * len(
            graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x owl:equivalentClass ?y }'))
        ans = sco + eq

    return ans


def get_number_domain_axioms(graph: rdflib.Graph):
    """number of TBox Axioms: domain axioms """

    da = len(graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x rdfs:domain ?y }'))
    ans = da
    return ans


def get_number_range_axioms(graph: rdflib.Graph):
    """number of TBox Axioms: range axioms """

    ra = len(graph.query(
        'PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x rdfs:range ?y; a owl:ObjectProperty }'))
    ans = ra
    return ans


def get_number_role_inclusion(graph: rdflib.Graph, mat=None):
    """number of TBox Axioms: role inclusion"""

    spo = len(graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x rdfs:subPropertyOf ?y }'))
    tp = len(graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?x WHERE { ?x a owl:TransitiveProperty}'))
    rp = len(graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?x WHERE { ?x a owl:ReflexiveProperty}'))
    cp = len(graph.query(
        'PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT DISTINCT ?x WHERE { ?x owl:PropertyChainAxiom ?y}'))
    fp = len(
        graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?x WHERE { ?x a owl:FunctionalDataProperty}'))
    ans = spo + tp + rp + cp + fp

    if mat == None or not mat:
        eq = 2 * len(
            graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x owl:equivalentProperty ?y }'))
        ans = ans + eq

    return ans


def get_number_axioms(graph: rdflib.Graph, mat=None, aBox=None, tBox=None):
    """number of axioms according to OWL EL, calles all methods necessary to calculate axioms."""
    count = 0
    if aBox == None:
        aBox = get_number_aBox_axioms(graph, mat)
    count += aBox

    if tBox == None:
        tBox = get_number_tBox_axioms(graph, mat)
    count += tBox

    return count


def get_number_aBox_axioms(graph: rdflib.Graph, concept_assertions=None, role_assertions=None):
    if concept_assertions == None:
        concept_assertions = get_number_concept_assertions(graph)
    if role_assertions == None:
        role_assertions = get_number_role_assertions(graph)

    return concept_assertions + role_assertions


def get_number_tBox_axioms(graph: rdflib.Graph, mat=None, gci=None, role_inclusion=None, range=None, domain=None):
    count = 0
    if gci == None:
        gci = get_number_GCI(graph, mat)
    count += gci

    if role_inclusion == None:
        role_inclusion = get_number_role_inclusion(graph, mat)
    count += role_inclusion

    if range == None:
        range = get_number_range_axioms(graph)
    count += range

    if domain == None:
        domain = get_number_domain_axioms(graph)
    count += domain

    return count
