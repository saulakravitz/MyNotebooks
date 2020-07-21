# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %% [markdown]
# ## Create FHIR R4 CapStatement Resource
# 
# ### Outline:
# 
# - Source excel with requirements
# - pandas to convert in python Ordered Dict
# - build json
# - generate narrative using Jinja2 templates
# 
# ### Prerequisites:
# 
# - Python 3.6 or greater
# %% [markdown]
# ### Import FHIRClient and other libraries

# %%
get_ipython().run_line_magic('config', 'IPCompleter.greedy=True')


# %%
from fhirclient.r4models.fhirabstractbase import FHIRValidationError
from fhirclient.r4models import searchparameter as SP
from fhirclient.r4models import capabilitystatement as CS
from fhirclient.r4models import bundle as B
from fhirclient.r4models import narrative as N
import fhirclient.models.identifier as I
import fhirclient.r4models.identifier as I
import fhirclient.r4models.coding as C
import fhirclient.r4models.codeableconcept as CC
import fhirclient.r4models.fhirdate as D
import fhirclient.r4models.extension as X
import fhirclient.r4models.contactdetail as CD
import fhirclient.r4models.fhirreference as FR
from json import dumps, loads, load
from requests import get, post, put
import os
from pathlib import Path
from csv import reader as csvreader
from IPython.display import display as Display, HTML, Markdown
from pprint import pprint
from collections import namedtuple
from pandas import *
from datetime import datetime, date
from jinja2 import Environment, FileSystemLoader, select_autoescape
from stringcase import snakecase, titlecase
from itertools import zip_longest
from openpyxl import load_workbook
from commonmark import commonmark
from lxml import etree

# %% [markdown]
# ####  Assign Global Variables
# 
# 
# Here is where we assign all the global variables for this example such as the canonical base and project information

# %%
#******************** Need to update when changing IGs *************************************************
fhir_base_url = 'http://hl7.org/fhir/'
#pre = "US-Core"
pre = "Da Vinci"
#canon = "http://hl7.org/fhir/us/core/"  # don't forget the slash  - fix using os.join or path
canon = "http://hl7.org/fhir/us/davinci-notifications/"  # don't forget the slash  - fix using os.join or path
#canon = "http://hl7.org/fhir/us/davinci-deqm/"  # don't forget the slash  - fix using os.join or path
#ig_folder = 'US-Core'
#ig_folder = 'Davinci-Notifications'
#ig_folder = 'Davinci-DEQM'
#publisher = 'HL7 International - US Realm Steering Committee'
#publisher = 'HL7 International - Clinical Decision Support Work Group'
publisher = 'HL7 International - Infrastructure and Messaging Work Group'
'''
publisher_endpoint = dict(
                        system = 'url',
                        value = 'http://www.hl7.org/Special/committees/usrealm/index.cfm'
                        )
'''
'''publisher_endpoint = dict(
                        system = 'url',
                        value = 'http://www.hl7.org/Special/committees/cds/index.cfm'
                        )
'''
publisher_endpoint = dict(
                        system = 'url',
                        value = 'http://www.hl7.org/Special/committees/inm/index.cfm'
                        )


#ig_package_tar_path =  "//ERICS-AIR-2/ehaas/Documents/FHIR/US-Core-R4/output"  # !! Change back to US-Core
#ig_package_path =  "//ERICS-AIR-2/ehaas/.fhir/packages/hl7.fhir.us.core.argo#dev" # !! Change back to r4
ig_package_tar_path =  "//ERICS-AIR-2/ehaas/Documents/FHIR/Davinci-Notifications/output"
ig_package_path =  "//ERICS-AIR-2/ehaas/.fhir/packages/hl7.fhir.us.davinci-alerts#dev/package"
#ig_package_tar_path =  "//ERICS-AIR-2/ehaas/Documents/FHIR/Davinci-DEQM/output"
#ig_package_path =  "//ERICS-AIR-2/ehaas/.fhir/packages/hl7.fhir.us.davinci-deqm#dev"
#ig_package_path = "C:/Users/Administrator/Downloads/"
#ig_source_path = "//ERICS-AIR-2/ehaas/Documents/FHIR/US-Core-R4/source/" # !! Change back to US-Core
#ig_source_path = "//ERICS-AIR-2/ehaas/Documents/FHIR/Davinci-DEQM/source/"
ig_source_path = "//ERICS-AIR-2/ehaas/Documents/FHIR/Davinci-Notifications/source/"
#ig_source_path = "/Users/ehaas/Documents/FHIR/US-Core-R4/source/"
#ig_source_path = ''

# spreadsheet source
#in_path = '/Users/ehaas/Documents/FHIR/pyfhir/test/'
#in_path = "//ERICS-AIR-2/ehaas/Documents/FHIR/US-Core-R4/source/source_spreadsheets/"  # !! Change back to US-Core
#in_file ="uscore-server"
#in_file ="uscore-client"
in_path = "//ERICS-AIR-2/ehaas/Documents/FHIR/Davinci-Notifications/source/resources/source-data/capstatements-spreadsheets/"
in_file ="alert-initiator"
#in_file ="alert-receiver"
#in_file ="query-responder"
#in_file ="query-requester"
#in_path = "//ERICS-AIR-2/ehaas/Documents/FHIR/Davinci-DEQM/source/resources/source-data/"
#in_file = "DEQM_Capability_Statement_Consumer_Client"
#in_file = "DEQM_Capability_Statement_Reporter_Client"
#in_file = "DEQM_Capability_Statement_Consumer_Server"
#in_file = "DEQM_Capability_Statement_Producer_Client"
#in_file = "DEQM_Capability_Statement_Producer_Server"
#in_file = "DEQM_Capability_Statement_Receiver_Server"
#"\\ERICS-AIR-2\ehaas\Documents\FHIR\Davinci-Alerts\source\resources\source-data\alert-sender.xlsx"
#'//ERICS-AIR-2/ehaas/Documents/FHIR/Davinci-Alerts/source/resources/source_data/alert-sender.xlsx'
#******************** Need to update when changing IGs *************************************************

f_jurisdiction =  CC.CodeableConcept({
      "coding" : [
        {
          "system" : "urn:iso:std:iso:3166",
          "code" : "US"
        }
      ]
    })

conf_url = 'http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation'
combo_url = 'http://hl7.org/fhir/StructureDefinition/capabilitystatement-search-parameter-combination'

sp_specials = {'us-core-includeprovenance':'http://hl7.org/fhir/us/core/SearchParameter/us-core-includeprovenance'}  # dict to for SP to get right canonicals, may use spreadsheet or package file in future.

none_list = ['', ' ', 'none', 'n/a', 'N/A', 'N', 'False']

sep_list = (',', ';', ' ', ', ', '; ')

f_now = D.FHIRDate(str(date.today()))
f_now.as_json()

# %% [markdown]
# #### Conformance Extension

# %%
def get_conf(conf='MAY',as_dict=False):
    if as_dict:
        return [X.Extension(dict(
            url = conf_url,
            valueCode = conf
            )).as_json()]
    else:
        return [X.Extension(dict(
            url = conf_url,
            valueCode = conf
            ))]
        

# %% [markdown]
# ### validate

# %%
# *********************** validate Resource ********************************

def validate(r):

    fhir_test_server = 'http://test.fhir.org/r4'

    headers = {
    'Accept':'application/fhir+json',
    'Content-Type':'application/fhir+json'
    }

    # profile = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' # The official URL for this profile is: http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient
 
    params = dict(
      # profile = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' # The official URL for this profile is: http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient
        )
    
    #   r = requests.post('https://httpbin.org/post', data = {'key':'value'})
    r = post(f'{fhir_test_server}/Questionnaire/$validate', params = params, headers = headers, data = dumps(r.as_json()))
    # return r.status_code
    # view  output
    # return (r.json()["text"]["div"])
    return r

# %% [markdown]
# ### Get Cap Statement input data
# %% [markdown]
# #### first the meta sheet

# %%
xls = ExcelFile(f'{in_path}{in_file}.xlsx')
df = read_excel(xls,'meta',na_filter = False)

df

# %% [markdown]
# #### Create NamedTuple from df to use dot notation

# %%
d = dict(zip(df.Element, df.Value))
meta = namedtuple("Meta", d.keys())(*d.values())      
         
meta.id

# %% [markdown]
# 
# ### Create CS instance

# %%

def get_sys_op():
    op_list = []
    df_op = read_excel(xls,'ops',na_filter = False)
    for i in df_op.itertuples(index=True):
        if i.type == 'system':
            op = CS.CapabilityStatementRestResourceOperation()
            op.name = i.name 
            op.definition = i.definition
            op.extension = get_conf(i.conf) 
            op_list.append(op.as_json())
    return op_list


def get_rest_ints():
    ri_list = []
    df_ri = read_excel(xls,'rest_interactions',na_filter = False)
    for i in df_ri.itertuples(index=True):
        ri = CS.CapabilityStatementRestInteraction()
        ri.code = i.code 
        ri.documentation = i.doc if i.doc not in none_list else None
        ri.extension = get_conf(i.conf)
        print(ri.as_json())
        ri_list.append(ri.as_json())
    return ri_list

def get_igs():
    ig_list = []
    df_igs = read_excel(xls,'igs',na_filter = False)
    for ig in df_igs.itertuples(index=True):
        ig_list.append(ig.uri)
    return ig_list # TODO add conformance to this

def kebab_to_pascal(word):
    return ''.join(x.capitalize() for x in word.split('-'))

cs = CS.CapabilityStatement()
cs.id = meta.id
cs.url = f'{canon}CapabilityStatement/{meta.id}'
cs.version = meta.version
cs.name = f'{kebab_to_pascal(meta.id)}{cs.resource_type}'
cs.title = f'{titlecase(meta.id).replace("Us ", "US ")} {cs.resource_type}'
cs.status = 'active'

cs.experimental = False
cs.date = f_now  # as FHIRDate
cs.publisher = publisher
cs.contact = [CD.ContactDetail( {"telecom" : [ publisher_endpoint ] })]
cs.description = meta.description
cs.jurisdiction = [f_jurisdiction]
cs.kind = 'requirements'
cs.fhirVersion = meta.fhirVersion
cs.acceptUnknown = 'both'
cs.format = [
    "xml",
    "json"
  ]
cs.patchFormat = [
    "application/json-patch+json",
  ]
cs.implementationGuide = meta.ig.split(",") + get_igs()
rest = CS.CapabilityStatementRest(dict(
    mode = meta.mode,
    documentation = meta.documentation,
    security = dict(
        description = meta.security
        ) if meta.security else None,
    interaction = get_rest_ints(),
    operation = get_sys_op()
    ))
cs.rest = [rest]


cs.as_json()

# %% [markdown]
# #### Then the list of IG profiles

# %%
xls = ExcelFile(f'{in_path}{in_file}.xlsx')
df = read_excel(xls,'profiles',na_filter = False)

df

# %% [markdown]
# #### add Resources
# 
# - read sheets for resource attributes, interaction attributes,  search attributes, profiles, and combo search parameters

# %%
df_resources = read_excel(xls,'resources',na_filter = False)
df_profiles = read_excel(xls,'profiles',na_filter = False)
df_i = read_excel(xls,'interactions',na_filter = False)
df_sp = read_excel(xls,'sps',na_filter = False)
df_combos = read_excel(xls,'sp_combos',na_filter = False)
df_op = read_excel(xls,'ops',na_filter = False)


def get_i(type):
    int_list = []
    for i in df_i.itertuples(index=True):
        #print(i.code, getattr(i,f'conf_{type}'))
        if getattr(i,f'conf_{type}') not in none_list:
            int  = CS.CapabilityStatementRestResourceInteraction()
            int.code = i.code
            try:
                int.documentation = getattr(i,f'doc_{type}') if getattr(i,f'doc_{type}') not in none_list else None
            except AttributeError:
                pass
            int.extension = get_conf(getattr(i,f'conf_{type}'))    
            int_list.append(int.as_json())
        
    return int_list


def get_sp(r_type):
    sp_list = []
    for i in df_sp.itertuples(index=True):
        if i.base == r_type:
            sp  = CS.CapabilityStatementRestResourceSearchParam()
            sp.name = i.code
            
            # TODO need to fix this to reference the package file to reconcile definition to names
            if i.code in sp_specials: #special case temp fix for us-core
                sp.definition = sp_specials[i.code]
            elif i.update == 'Y' or i.exists =='N':
                sp.definition = (f'{canon}SearchParameter/{pre.lower()}-{i.base.lower()}-{i.code.split("_")[-1]}')                  
            else:  # use base definition
                sp.definition = f'{fhir_base_url}SearchParameter/{i.base}-{i.code.split("_")[-1]}'  # removes the '_' for things like _id
                                 
            # print(sp.definition)
                                 
            sp.type = i.type
            sp.extension = get_conf(i.base_conf)
            #print(sp.as_json())                
            sp_list.append(sp.as_json())
                             
    return sp_list


def get_combo_ext(r_type,combos):
    x_list = []
    for combo in combos:
        # convert to extension
        combo_ext = X.Extension()
        combo_ext.url = combo_url
        combo_conf_ext = get_conf(combo[1])
        combo_ext.extension=combo_conf_ext
        for param in combo[0].split(','):
            req_combo = X.Extension(
                dict (
                    url = 'required',
                    valueString = param   #http://hl7.org/fhir/us/core/SearchParameter/us-core-patient-family
                    )
                )
            combo_ext.extension.append(req_combo)
        x_list.append(combo_ext)
        # print(x_list)
    return x_list
                             
def get_op(r_type):
    op_list = []
    for i in df_op.itertuples(index=True):
         if i.type == r_type:
            op = CS.CapabilityStatementRestResourceOperation()
            op.name = i.name 
            op.definition = i.definition
            op.documentation = i.documentation if i.documentation not in none_list else None
            op.extension = get_conf(i.conf) 
            op_list.append(op.as_json())
                           
    return op_list 

rest.resource =  []
for r in df_resources.itertuples(index=True):
    if not r.type.startswith('!'):
        # print(r.type, r.conformance, r.readHistory)
        supported_profile = [p.Profile for p in df_profiles.itertuples(index=True) if p.Type == r.type]
        #pprint(supported_profile)                         
        res = CS.CapabilityStatementRestResource(
        dict(
            type = r.type,
            documentation = r.documentation if r.documentation not in none_list else None,
            versioning = r.versioning if r.versioning not in none_list else None,
            readHistory = r.readHistory if r.readHistory not in none_list else None,
            updateCreate = r.updateCreate if r.updateCreate not in none_list else None,
            conditionalCreate = r.conditionalCreate if r.conditionalCreate not in none_list else None,
            conditionalRead = r.conditionalRead if r.conditionalRead not in none_list else None,
            conditionalUpdate = r.conditionalUpdate if r.conditionalUpdate not in none_list else None,
            conditionalDelete = r.conditionalDelete if r.conditionalDelete not in none_list else None,
            referencePolicy = [x for x in r.referencePolicy.split(",") if x],
            searchInclude =  [x for x in r.shall_include.split(",") + r.should_include.split(",") if x],
            searchRevInclude =  [x for x in r.shall_revinclude.split(",") + r.should_revinclude.split(",") if x],
            interaction = get_i(r.type),
            searchParam = get_sp(r.type),
            operation = get_op(r.type),
            #profile = f'{fhir_base_url}StructureDefinition/{r.type}',
            supportedProfile = supported_profile,
            )
        )
        res.extension = get_conf(r.conformance)
        combos = {(i.combo,i.combo_conf) for i in df_combos.itertuples(index=True) if i.base == r.type}
        res.extension = res.extension + get_combo_ext(r.type,combos) # convert list to  lst of combo extension
                            
                                 
        '''
        #TODO add in conformance expectations for primitives 
        #need to convert to dict since model can't handle primitive extensions

        resttype_dict = res.as_json()

        for i in ['Include','RevInclude']:
            element = f'_search{i}'

            resttype_dict[element] = []
            print(element)
            for expectation in ['should', 'shall']: # list all should includes first
                sp_attr = f'{expectation}_{i.lower()}'
                print(sp_attr) 
                includes = getattr(r,sp_attr).split(',')
                print(includes)

                for include in includes:
                    if include not in none_list:             
                        print(include)
                        conf = get_conf(expectation.upper(),as_dict=True)
                        print(conf)
                        conf = conf
                        print(conf)        
                        resttype_dict[element].append(conf)

            if not resttype_dict[element]:
                    del(resttype_dict[element])

        print(dumps(resttype_dict, indent = 4))
        res = CS.CapabilityStatementRestResource(resttype_dict, strict = False)
        print('++++++++++++++++RES.__dict__+++++++++++++++++++')
        print(dumps(res._searchRevInclude, indent = 4))
        '''                               
                                 
        rest.resource.append(res)

rest.resource =  sorted(rest.resource,key = lambda x: x.type)  # sort resources                         
cs.rest = [rest]
    
print(dumps(cs.as_json(),indent=3))    
        
        

# %% [markdown]
# ### Convert model to dict and add extensions to primitives **Deactivated ( marked a raw block ) since will need to use dict in subsuquent steps.

#add in conformance expectations for primitives 
#convert to dict since model can't handle primitive extensions

resttype_dict = res.as_json()

for i in ['Include','RevInclude']:
    element = f'_search{i}'

    resttype_dict[element] = []
    print(element)
    for expectation in ['should', 'shall']: # list all should includes first
        sp_attr = f'{expectation}_{i.lower()}'
        print(sp_attr) 
        includes = getattr(r,sp_attr).split(',')
        print(includes)

        for include in includes:
            if include not in none_list:             
                print(include)
                conf = get_conf(expectation.upper(),as_dict=True)
                print(conf)
                conf = conf
                print(conf)        
                resttype_dict[element].append(conf)

    if not resttype_dict[element]:
            del(resttype_dict[element])

print(resttype_dict)

print(dumps(cs.as_json(),indent=3))    # %% [markdown]
# ### Validate

# %%
#validate and write to file

print('...validating')
r = validate(cs)
display(HTML(f'<h1>Validation output</h1><h3>Status Code = {r.status_code}</h3> {r.json()["text"]["div"]}'))

# %% [markdown]
# ### Create Narrative
# 
# - Using Jinja2 Template create xhtml for narrative
# %% [markdown]
# #### First: Get spec_internal from package.tgz a json file which includes canonical to local relative page links
# 
# Note for this to work you have to have a working build that already contains all the needed artifacts.

# %%
import tarfile
def get_si(path):
    with tarfile.open(f'{path}/package.tgz', mode='r') as tf:
        #pprint(tf.getnames())
        f = tf.extractfile('other/spec.internals')
        r = f.read()
        return(loads(r))

def get_si2(path):
    with open(f'{path}/other/spec.internals', 'r', encoding='utf-8-sig') as f:
        r = f.read()
        return(loads(r, encoding = 'utf-8'))

'''
try:      
    si = get_si(ig_package_tar_path)
except FileNotFoundError:
    
'''  
si = get_si2(ig_package_path) # get from package (json) file in local .fhir directory
path_map = si['paths']
path_map

# %% [markdown]
# #### Then Use Jinja2 template to create narrative

# %%
in_path = ''
in_file = 'R4capabilitystatement-server.j2'

def markdown(text, *args, **kwargs):
    return commonmark(text, *args, **kwargs)



env = Environment(
    loader=FileSystemLoader(searchpath = in_path),
    autoescape=select_autoescape(['html','xml','xhtml','j2','md'])
    )

env.filters['markdown'] = markdown


template = env.get_template(in_file)

sp_map = {sp.code:sp.type for sp in df_sp.itertuples(index=True)}
pname_map = {p.Profile:p.Name for p in df_profiles.itertuples(index=True)}
pprint(pname_map)

rendered = template.render(cs=cs, path_map=path_map, pname_map = pname_map, sp_map =sp_map )

display(HTML(rendered))


parser = etree.XMLParser(remove_blank_text=True)
root = etree.fromstring(rendered, parser=parser)

div = (etree.tostring(root[1][0], encoding='unicode', method='html'))
narr = N.Narrative()
narr.status = 'generated'
narr.div = div
cs.text = narr


#print(dumps(cs.as_json(),indent=3))

# %% [markdown]
# ### validate again

# %%
print('...validating')
r = validate(cs)
display(HTML(f'<h1>Validation output</h1><h3>Status Code = {r.status_code}</h3> {r.json()["text"]["div"]}'))

# %% [markdown]
# ### Write to folder

# %%
# save to file
print('...........saving to file............')
#save in ig_source folder
path = Path.cwd() / ig_source_path / 'resources' / f'capabilitystatement-{cs.id.lower()}.json'
path.write_text(dumps(cs.as_json(), indent=4))


# %%


