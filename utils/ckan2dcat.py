"""

NOTE on uploading existing data from CKAN to dcatd:

$ python dumpckan.py
$ python ckan2dcat.py https://api.data.amsterdam.nl/dcatd/
$ python resources2distributions.py [UPLOADURL] [JWT]
$ cd dcatdata
$ for d in *.json; do curl -XPOST --header "Authorization: Bearer [JWT]" [DCATDURL]/datasets -d @${d} & done

"""
import argparse
import json
import os
import pathlib

from pyld import jsonld

from datacatalog.plugins import dcat_ap_ams

CKANDIR = 'ckandata'
DCATDIR = 'dcatdata'


def load_packages():
    retval = []
    for filename in pathlib.Path(CKANDIR).glob('*.json'):
        with open(filename) as fh:
            retval.append(json.load(fh))
    return retval


def dump_datasets(datasets, context):
    os.makedirs(DCATDIR, exist_ok=True)
    for dataset in datasets:
        try:
            expanded = jsonld.expand(dataset)
            compacted = jsonld.compact(expanded, context)
        except:
            print(json.dumps(dataset, indent=2, sort_keys=True))
            raise
        with open(f"{DCATDIR}/{compacted['ams:ckan_name']}.json", 'w') as fh:
            json.dump(compacted, fh, indent=2, sort_keys=True)


def ckan2dcat(ckan, context):
    # context = dict(context)  # dict() because we mutate the context
    # context['@vocab'] = 'https://ckan.org/terms/'
    retval = dcat_ap_ams.DATASET.from_ckan(ckan)
    retval['@context'] = context
    retval['@id'] = f"ams-dcatd:{retval['dct:identifier']}"
    retval['ams:ckan_name'] = ckan['name']
    for distribution in retval['dcat:distribution']:
        if 'dct:modified' not in distribution['foaf:isPrimaryTopicOf']:
            distribution['foaf:isPrimaryTopicOf']['dct:modified'] = \
                distribution['foaf:isPrimaryTopicOf']['dct:issued']
    try:
        dcat_ap_ams.DATASET.validate(retval)
    except Exception:
        print(json.dumps(retval, indent=2, sort_keys=True))
        raise
    return retval


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CKAN 2 DCAT.')
    parser.add_argument(
        'baseurl',
        nargs=1,
        metavar='URL',
        help='baseurl of the dcatd instance'
    )
    args = parser.parse_args()
    ctx = dcat_ap_ams.context(args.baseurl[0])
    dump_datasets((ckan2dcat(x, ctx) for x in load_packages()), ctx)
