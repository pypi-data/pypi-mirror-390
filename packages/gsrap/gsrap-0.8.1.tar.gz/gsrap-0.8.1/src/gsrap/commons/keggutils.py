import time
import os
import sys
import pickle


import pandas as pnd
from Bio.KEGG import REST



def download_keggorg(logger, keggorg='lpl', outdir='./', ):


    # check if already downloaded
    outfile = os.path.join(outdir, f'{keggorg}.keggorg')
    if os.path.exists(outfile):
        logger.info(f"Organism code '{keggorg}' already downloaded ('{os.path.join(outdir, f'{keggorg}.keggorg')}').")
        return 0
    
    
    # donwload entire txt:
    logger.info(f"Verifying existence of organism code '{keggorg}' on KEGG...")
    time.sleep(0.5)   # be respectful
    try: response = REST.kegg_list(keggorg).read()
    except: 
        logger.error(f"Organism code '{keggorg}' not found in KEGG database.")
        return 1
    # response is now a string similar to:
    """
    lpl:lp_0026	CDS	31317..32084	hydrolase, HAD superfamily, Cof family
    lpl:lp_0027	CDS	complement(32236..32907)	pgmB1; beta-phosphoglucomutase
    """

    
    # extract the gene IDs list:
    gene_ids = [line.split('\t')[0] for line in response.strip().split('\n')]
    # example of gene_id: "lpl:lp_0005"
    logger.info(f"Respectfully downloading {len(gene_ids)} genes from KEGG...")
    
    
    
    # respectfully download in batch
    # 10 is the max number of elements that can be downloaded
    batch_size = 10
    n_batches = len(gene_ids) // batch_size + (1 if (len(gene_ids) % batch_size) > 0 else 0) 


    n_attempts = 5
    attempts_left = n_attempts
    default_sleep = 0.5
    sleep_time = default_sleep


    completed_batches = 0
    completed_genes = 0
    res_string_list = []
    while completed_batches < n_batches:

        # be respectful
        time.sleep(sleep_time)

        # extract batch 
        start_index = completed_batches *batch_size
        end_index = (completed_batches+1) *batch_size
        if end_index > len(gene_ids): end_index = len(gene_ids)
        curr_batch = gene_ids[start_index: end_index]


        # download batch
        try:
            res_string = REST.kegg_get(curr_batch).read()
            for item in res_string.split("///\n\n"):
                res_string_list.append(item.replace('///\n', ''))
            completed_batches += 1
            completed_genes += len(curr_batch)

            print(f"{completed_genes}/{len(gene_ids)} ({int(completed_genes/len(gene_ids)*100)}%) completed!", end='\r', file=sys.stderr)

            attempts_left = n_attempts
            sleep_time = default_sleep
        except: 
            attempts_left -= 1
            sleep_time = default_sleep *4  # increase sleep time to be more respectful
            logger.warning(f"An error occurred during kegg_get() of batch {curr_batch}. Remaining attempts: {attempts_left}.")

            
            if attempts_left == 0:
                logger.error("No attemps left! Shutting down...")
                return 1


    # hide last progress trace ('sheets_dicts' unused if not in multi-strain mode):
    last_trace = f"{completed_genes}/{len(gene_ids)} ({int(completed_genes/len(gene_ids)*100)}%) completed!"
    whitewash = ''.join([' ' for i in range(len(last_trace))])
    print(whitewash, end='\r', file=sys.stderr)   
    
    
    
    # extract info into a formatted df:
    df = []  # list of dicts, future df
    for entry in res_string_list:

        entry_dict = {}
        curr_header = None

        for line in entry.split('\n'):
            if line == '': continue

            header = line[:12]
            content = line[12:]
            if header != ' '*12:
                curr_header = header

            if curr_header == 'ENTRY       ':
                gid = content.split(' ', 1)[0]
                entry_dict['gid'] = gid

            if curr_header == 'POSITION    ':
                entry_dict['pos'] = content.strip()

            if curr_header == 'ORTHOLOGY   ':
                ko = content.split(' ', 1)[0]
                entry_dict['ko'] = ko

            if curr_header == 'MOTIF       ':
                db, value = content.strip().split(': ', 1)
                entry_dict[db] = value.split(' ')

            if curr_header == 'DBLINKS     ':
                db, value = content.strip().split(': ', 1)
                entry_dict[db] = value.split(' ')

        df.append(entry_dict)
    df = pnd.DataFrame.from_records(df)
    
    
    # save dataframe in the output dir:
    with open(outfile, 'wb') as wb_handler:
        pickle.dump(df, wb_handler)
    logger.info(f"'{outfile}' created!")
        
        
        
    return 0