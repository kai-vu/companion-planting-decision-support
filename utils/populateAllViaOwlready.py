import pandas as pd
from owlready2 import *
import types
import requests


def toPascalCase(s):
    return ''.join(x for x in s.title() if not (x.isspace() or x == '.'))


import numpy as np

# create the links to the java gateway and parse the ontology

iri = 'http://www.semanticweb.org/kai/ontologies/2024/companion-planting#'
# partof = get_ontology('http://www.ontologydesignpatterns.org/cp/owl/partof.owl#')
# onto = get_ontology('../owl/companion-planting-base0.2.rdf').load()
onto = get_ontology('../owl/companion-planting-base0.2.rdf')
onto.base_iri = iri
darwin = get_ontology('http://rs.tdwg.org/dwc/terms/')

with darwin:
    class scientificName(AnnotationProperty):
        pass
onto.imported_ontologies.append(darwin)

'''
####################
CREATE BASE ONTOLOGY
####################
'''

# questions:
# 1. are attractorOf and visitedBy the same?
# 2. do we need to rename the companion properties?
# 3. increasedLevelInteraction == protectiveShelter?

# Object properties and property chains
with onto:
    # species class
    speciesParentClass = types.new_class('Species', (Thing,))
    # classes
    Garden = types.new_class("Garden", (Thing,))
    Flora = types.new_class("Flora", (speciesParentClass,))
    Fauna = types.new_class("Fauna", (speciesParentClass,))
    BadGarden = types.new_class("BadGarden", (Garden,))
    CompanionGarden = types.new_class("CompanionGarden", (Garden,))
    ThreeCompanionGarden = types.new_class("3CompanionGarden", (Garden,))
    ThreeTripleCompanionGarden = types.new_class("3TripleCompanionGarden", (Garden,))
    BadlyPlacedFlora = types.new_class("BadlyPlacedFlora", (Flora,))
    PlantWithCompanion = types.new_class("PlantWithCompanion", (Flora,))
    PlantWith2Companions = types.new_class("PlantWith2Companions", (Flora,))
    PlantWith3Companions = types.new_class("PlantWith3Companions", (Flora,))
    Fruit = types.new_class("Fruit", (Flora,))
    Predator = types.new_class("Predator", (Fauna,))
    Pollinator = types.new_class("Pollinator", (Fauna,))

    # companion properties (do we need all of these?)
    anticompanionWith = types.new_class("anticompanionWith", (ObjectProperty,))
    companionWith = types.new_class("companionWith", (ObjectProperty,))
    positiveHostingFor = types.new_class("positiveHostingFor", (companionWith,))
    recruitsPollinatorsFor = types.new_class("recruitsPollinatorsFor", (positiveHostingFor,))
    recruitsPredatorsFor = types.new_class("recruitsPredatorsFor", (positiveHostingFor,))
    trapCropFor = types.new_class("trapCropFor", (companionWith,))

    providesNutrientsFor = types.new_class("providesNutrientsFor", (companionWith,))
    providesNitrogenFor = types.new_class("providesNitrogenFor", (providesNutrientsFor,))
    providesCalcium = types.new_class("providesCalcium", (providesNutrientsFor,))
    providesPhosphorus = types.new_class("providesPhosphorus", (providesNutrientsFor,))
    providesPotassium = types.new_class("providesPotassium", (providesNutrientsFor,))
    providesWaterFor = types.new_class("providesWaterFor", (providesNutrientsFor,))
    physicalSupportFor = types.new_class("physicalSupportFor", (companionWith,))
    providesShadeFor = types.new_class("providesShadeFor", (physicalSupportFor,))
    providesWindProtectionFor = types.new_class("providesWindProtectionFor", (physicalSupportFor,))

    companionNeighbour = types.new_class("companionNeighbour", (ObjectProperty,))
    neighbour = types.new_class("neighbour", (ObjectProperty, SymmetricProperty))
    incompatibleNeighbour = types.new_class("incompatibleNeighbour", (ObjectProperty,))
    containsFlora = types.new_class("containsFlora", (ObjectProperty,))

    # interaction properties (globi)
    interactsWith = types.new_class("interactsWith", (ObjectProperty,))
    visitedBy = types.new_class("visitedBy", (interactsWith,))
    _visitedBy = types.new_class("_visitedBy", (interactsWith,))
    hasParasite = types.new_class("hasParasite", (interactsWith,))
    parasiteOf = types.new_class("parasiteOf", (interactsWith,))
    hostOf = types.new_class("hostOf", (interactsWith,))
    hasHost = types.new_class("hasHost", (interactsWith,))
    pollinatedBy = types.new_class("pollinatedBy", (interactsWith,))
    _pollinatedBy = types.new_class("_pollinatedBy", (interactsWith,))
    hasPathogen = types.new_class("hasPathogen", (interactsWith,))
    _hasPathogen = types.new_class("_hasPathogen", (interactsWith,))
    eatenBy = types.new_class("eatenBy", (interactsWith,))
    _eatenBy = types.new_class("_eatenBy", (interactsWith,))
    mutualistOf = types.new_class("mutualistOf", (interactsWith,))
    _mutualistOf = types.new_class("_mutualistOf", (interactsWith,))
    flowersVisitedBy = types.new_class("flowersVisitedBy", (interactsWith,))
    _flowersVisitedBy = types.new_class("_flowersVisitedBy", (interactsWith,))

    # other interaction properties
    repellerOf = types.new_class("repellerOf", (interactsWith,))
    isRepelledBy = types.new_class("isRepelledBy", (interactsWith,))

    # plant property predicates
    belongsToLayer = types.new_class("belongsToLayer", (ObjectProperty,))
    hasPart = types.new_class("hasPart", (ObjectProperty,))

    # property chains
    recruitsPredatorsFor.property_chain.append(PropertyChain([visitedBy, _eatenBy, parasiteOf]))
    recruitsPollinatorsFor.property_chain.append(PropertyChain([visitedBy, _pollinatedBy]))
    recruitsPollinatorsFor.property_chain.append(PropertyChain([flowersVisitedBy, _pollinatedBy]))
    repellerOf.property_chain.append(PropertyChain([hasPart, repellerOf]))

    # other axioms
    BadGarden.equivalent_to = [Garden & containsFlora.some(BadlyPlacedFlora)]
    CompanionGarden.equivalent_to = [Garden & containsFlora.some(PlantWithCompanion)]
    PlantWithCompanion.equivalent_to = [Flora & companionNeighbour.some(Flora)]
    PlantWith2Companions.equivalent_to = [Flora & companionNeighbour.min(2)]
    PlantWith3Companions.equivalent_to = [Flora & companionNeighbour.min(3)]
    ThreeCompanionGarden.equivalent_to = [Garden & containsFlora.min(3, PlantWithCompanion)]
    ThreeTripleCompanionGarden.equivalent_to = [Garden & containsFlora.min(3, PlantWith3Companions)]

'''
####################
ADD COMPANION AXIOMS
####################
'''
# load the companion planting dataset/table
df = pd.read_csv('../datasets/Processed/companion_plants_including_taxon.csv')

# load the names-taxon-products dataframe: idx, taxon,plantCommonName,plantWikidata,productCommonName,productWikidata
ntp = pd.read_csv('../datasets/Processed/names-taxon-products.csv')
ntp['plantWikidata'] = ntp['plantWikidata'].apply(lambda x: x.replace('q', 'Q') if 'q' in x else x)
# adding the various plants from the companion plant table
plants = pd.concat([df[['v1', 'taxon_v1']].rename(columns={'v1': 'v', 'taxon_v1': 'taxon'}),
                    df[['v2', 'taxon_v2']].rename(columns={'v2': 'v', 'taxon_v2': 'taxon'})]).drop_duplicates().values

with onto:
    Flora = types.new_class("Flora", (Thing,))
    # potatoClass = types.new_class("PotatoButInLatin", (Flora,))
    allPlantConcepts = dict()
    for p in plants:
        if (not pd.isna(p[1])):
            plant = types.new_class(toPascalCase(p[1]), (Flora,))  # class and IRI
            allPlantConcepts[p[1]] = plant
            plant.label = [locstr(p[0].title(), lang="en")]  # english label
            # plant. = [p[1].title()] #find how to add custom annotations
            # darwin.scientificName
            plant.scientificName = [p[1].title()]
            row = ntp[ntp.taxon == p[1]]
            if not row.empty:
                plant.seeAlso = [row.iloc[0].plantWikidata]

            # neighbouring axioms
            gca = GeneralClassAxiom(onto.companionWith.some(plant) &
                                    onto.neighbour.some(plant))  # lhs
            gca.is_a.append(onto.companionNeighbour.some(plant))

            gca = GeneralClassAxiom(onto.anticompanionWith.some(plant) &
                                    onto.neighbour.some(plant))  # lhs
            gca.is_a.append(onto.incompatibleNeighbour.some(plant))

    AllDisjoint(list(allPlantConcepts.values()))

    df = df[~((df.v1 == 'tomato') & (df.v2.isin(['beet','rue','tansy','thyme'])) & (df.rel == 'companion'))]

    for _, row in df.iterrows():
        if not (pd.isna(row.taxon_v1) or pd.isna(row.taxon_v2)):
            v1 = allPlantConcepts[row.taxon_v1]
            v2 = allPlantConcepts[row.taxon_v2]

            if row['rel'] == 'companion':
                if len(v1.companionWith) == 0:
                    v1.companionWith = [v2]
                    #AnnotatedRelation(v1, companionWith, v2).comment = ['Companion planting chart']

                else:
                    b=v1.companionWith.append(v2)
                    #AnnotatedRelation(v1, companionWith, v2).comment = ['Companion planting chart']

            if row['rel'] == 'antagonistic':
                if len(v1.anticompanionWith) == 0:
                    v1.anticompanionWith = [v2]
                    #AnnotatedRelation(v1, anticompanionWith, v2).comment = ['Companion planting chart']

                else:
                    v1.anticompanionWith.append(v2)
                    #AnnotatedRelation(v1, anticompanionWith, v2).comment = ['Companion planting chart']

# onto.save(file='../owl/companion_planting_v5.owl')
'''
##############################
ADD SPECIES INTERACTION AXIOMS
##############################
'''

#

taxon_names = list(pd.concat([df['taxon_v1'], df['taxon_v2']]).drop_duplicates().dropna().values)
interaction_data = []

for taxon_name in taxon_names:
    taxon_name = taxon_name.replace(" ", "%20")
    URL = "https://api.globalbioticinteractions.org/taxon/" + taxon_name + "/interactsWith"
    try:
        interaction_data.append(requests.get(URL).json()['data'])
    except:
        pass

# Add class axioms based on GLOBI interaction data
with onto:
    for row in interaction_data:

        try:
            if row[0][1] not in ['interactsWith']:
                species = toPascalCase(row[0][0])
                predicate = row[0][1]
                if species.startswith(tuple(['UCSC', 'CLEMS', 'SBMNH', 'CUP'])):
                    pass
                else:
                    species_class = types.new_class(species, (
                    onto.Species,))  # thing should be more specific, plant or other animal
                    # species_class.scientificName = row[0][0]
                    interaction_predicate = types.new_class(predicate, (ObjectProperty,))
                    interaction_predicate_inverse = types.new_class("_" + predicate, (ObjectProperty,))

                for interacting_species in row[0][2]:
                    if interacting_species.startswith(tuple(['UCSC', 'CLEMS', 'SBMNH', 'CUP'])):
                        pass
                    else:
                        interacting_species_ln = interacting_species
                        interacting_species = toPascalCase(interacting_species)

                        interacting_species_class = types.new_class(interacting_species, (onto.Species,))
                        interacting_species_class.scientificName = interacting_species_ln
                        species_class.is_a.append(interaction_predicate.some(interacting_species_class))
                        interacting_species_class.is_a.append(interaction_predicate_inverse.some(species_class))
        except:
            pass

onto.save(file='../owl/companion_planting_v6.owl')

'''
##############################
'''

