import yaml
import logging
import argparse
import os
import pprint
import re
import copy

from CRABClient.UserUtilities import config, ClientException, getUsername
from CRABAPI.RawCommand import crabCommand
from httplib import HTTPException
import string
import random
import hashlib

username = getUsername()

def submit(config):
    try:
        crabCommand('submit', config = config)
    except HTTPException as hte:
        print('Cannot execute command')
        print(hte.headers)
    
def rnd_str(N, seedstr='test'):
    # Seed with dataset name hash to be reproducible
    random.seed(int(hashlib.sha512(seedstr).hexdigest(), 16))
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(N))

def to_request_name(dataset_name):
    if len(dataset_name) < 85:
        request_name = dataset_name
    else:
        request_name = dataset_name[:80] + rnd_str(8, dataset_name)
    return request_name + username

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(description='Run analysis on baconbits files using processor coffea files')
    parser.add_argument('-w', '--workdir', dest='workdir', required=True, help='Crab working directory. Must be outside of $CMSSW_BASE lest your tarballs balloon in size and crab complains.')
    parser.add_argument('-c', '--card', '--yaml', dest='card', required=True, help='Crab yaml card')
    parser.add_argument('--make', action='store_true', help="Make crab configs according to the spec.")
    parser.add_argument('--submit', action='store_true', help="Submit configs created by ``--make``.")
    parser.add_argument('--status', action='store_true', help="Run `crab submit` but filter for only status info. Creates a list of DAS names.")
    parser.add_argument("--test", type=str2bool, default='False', choices={True, False}, help="Test submit - only 1 file, don't publish.")
    args = parser.parse_args()

    with open(args.card, 'r') as f:
        card = yaml.safe_load(f)

    work_area = args.workdir
    abs_work_area = os.path.abspath(work_area)
    if os.path.isdir(args.workdir):
        if args.submit or args.make:
            if raw_input("``workArea: {}`` already exists. Continue? (y/n)".format(args.workdir)) != "y":
                exit()
    else:
        os.mkdir(work_area)
        os.mkdir(work_area+"/"+"submit_scripts")
    abs_work_area = os.path.abspath(work_area)

    defaults = card['defaults']
    groups, group_cfgs = [], []
    if isinstance(card['samples'], list):  # Plain list of samples
        raise NotImplementedError("Not implemented")
        sys.exit()
    elif isinstance(card['samples'], dict):  # Dict of samples
        for group, cfg in card['samples'].items():
            if 'datasets' not in cfg:
                raise ValueError("`datasets` not found in {cfg}".format(cfg))
            group_cfg = copy.deepcopy(defaults)
            for key in cfg.keys():
                if key != 'datasets':
                    group_cfg[key] = cfg[key]
            group_cfgs.append(group_cfg)
            if isinstance(cfg['datasets'], dict):
                groups.append(list(cfg['datasets'].values()))
            elif isinstance(cfg['datasets'], list):
                groups.append(cfg['datasets'])
            else:
                raise ValueError("`datasets` not understood in {cfg}".format(cfg))
    else:
        raise NotImplementedError("`samples` format not understood")
      

    if args.make:
        for datasets, cfg in zip(groups, group_cfgs):
            if(cfg['tag_mod'] is not None) and (cfg['tag_extension'] is not None):
                print("Can't specify both ``campaign: tag_mod`` and ``campaign: tag_extension``. Leave one empty.")
                exit()

            with open(cfg['crab_template'], 'r') as template_file:
                base_crab_config = template_file.read()

            print("Making configs in {}:".format(abs_work_area))
            for dataset in datasets:
                print("   ==> "+ dataset)
                crab_config = copy.deepcopy(base_crab_config)
                dataset_name = dataset.lstrip("/").replace("/", "_")

                tag = dataset.split("/")[2]
                if cfg['tag_mod'] is not None:
                    tag = re.sub(r'MiniAOD[v]?[0-9]?', cfg['tag_mod'], tag) if tag.startswith('RunII') else tag + '_' + cfg['tag_mod']
                elif cfg['tag_extension'] is not None:
                    tag = tag + '_' + cfg['tag_extension']
                else:
                    raise ValueError("Either ``campaign: tag_mod`` or ``campaign: tag_extension`` need to be specified")

                request_name = to_request_name(dataset_name)

                verbatim_lines = []
                card_info = {
                    '_requestName_': request_name,
                    '_workArea_': os.path.join(abs_work_area, "workdirs"),
                    '_psetName_': os.path.expandvars(cfg.get("config", None)),
                    '_inputDataset_': dataset,
                    '_outLFNDirBase_': cfg['outLFNDirBase'].format(username=username),
                    '_storageSite_': cfg['storageSite'],
                    '_publication_': str(cfg['publication']),
                    '_splitting_': 'LumiBased' if cfg['data'] else "Automatic",
                    '_outputDatasetTag_': tag, 
                    '_isMC_': str(not bool(cfg['data'])), 
                    '_globaltag_': cfg['globaltag'],
                }
                
                if args.test:
                    verbatim_lines.append("config.Data.totalUnits = 1")
                    # card_info['_publication_'] = 'False'

                if cfg['data']:
                    verbatim_lines.append("config.Data.unitsPerJob = 50")
                    verbatim_lines.append("config.JobType.maxJobRuntimeMin = 2750")
                if cfg['data'] and cfg.get('lumimask') is not None:
                    verbatim_lines.append("config.Data.lumiMask = '{}'".format(cfg['lumimask']))
                if cfg.get('voGroup', None) is not None:
                        verbatim_lines.append("config.User.voGroup = '{}'".format(cfg['voGroup']))
                
                for line in verbatim_lines:
                    crab_config += "\n" + line
                crab_config += "\n"

                for key in card_info:
                    crab_config = crab_config.replace(key, card_info[key])

                cfg_filename = os.path.join(abs_work_area, "submit_scripts" , 'submit_{}.py'.format(dataset_name))
                with open(cfg_filename, 'w') as cfg_file:
                    cfg_file.write(crab_config)


    if args.submit:
        from multiprocessing import Process
        import imp

        for datasets, cfg in zip(groups, group_cfgs):
            print("Submitting configs:")
            for dataset in datasets:
                print("   ==> "+dataset)
                dataset_name = dataset.lstrip("/").replace("/", "_")
                cfg_filename = os.path.join(abs_work_area, "submit_scripts" , 'submit_{}.py'.format(dataset_name))
                config_file = imp.load_source('config', cfg_filename)
                p = Process(target=submit, args=(config_file.config,))
                p.start()
                p.join()

    if args.status:
        das_names = []
        for datasets, cfg in zip(groups, group_cfgs):
            for dataset in datasets:
                dataset_name = dataset.lstrip("/").replace("/", "_")
                request_name = to_request_name(dataset_name)
                cfg_dir = os.path.join(abs_work_area , "workdirs", 'crab_'+request_name)
                o = os.popen('crab status '+cfg_dir).read().split("\n")
                for i, line in enumerate(o):
                    if line.startswith("CRAB project directory:"): print line
                    if line.startswith("Status on the scheduler:"): print line
                    if line.startswith("Jobs status"):
                        for j in range(5):
                            if len(o[i+j]) < 2:
                                continue
                            if  any(s in o[i+j] for s in ['unsubmitted', 'idle', 'finished','running','transferred', 'transferring', 'failed']):
                                print(o[i+j])
                    
                    if "Output dataset:" in line:
                        das_names.append(line.split()[-1])

        das_names_file = 'outputs_{}.txt'.format(args.card.split("/")[-1].split(".")[0])
        print("Writing output dataset DAS names to: {}".format(das_names_file))
        with open(das_names_file, 'w') as das_file:
            das_file.write("\n".join(das_names))
