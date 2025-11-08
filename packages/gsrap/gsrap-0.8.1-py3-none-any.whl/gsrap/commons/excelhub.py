import pandas as pnd


from .figures import figure_df_C_F1



def write_excel_model(model, filepath, nofigs, df_E, df_B, df_P, df_S, df_C=None):
    
    
    # generate figures
    if nofigs == False:
              
        if df_C is not None:
            df_C_F1 = figure_df_C_F1(df_C)
        
        
    
    # format df_E:  # biomass precursors biosynthesis
    if df_E is not None:
        df_E.insert(0, 'mid', '')  # new columns as first
        df_E['mid'] = df_E.index
        df_E = df_E.reset_index(drop=True)
    
    # format df_B:  # biomass assembly
    if df_B is not None:
        df_B.insert(0, 'mid', '')  # new columns as first
        df_B['mid'] = df_B.index
        df_B = df_B.reset_index(drop=True)
    
    # format df_P:  phenotype screening (Biolog(R))
    if df_P is not None:
        df_P.insert(0, 'plate:well', '')  # new columns as first
        df_P['plate:well'] = df_P.index
        df_P = df_P.reset_index(drop=True)
        
    # format df_S:  metabolite synthesis
    if df_S is not None:
        df_S.insert(0, 'mid', '')  # new columns as first
        df_S['mid'] = df_S.index
        df_S = df_S.reset_index(drop=True)
        
    # format df_C: universal reaction coverage
    if df_C is not None:
        df_C.insert(0, 'kr', '')  # new columns as first
        df_C['kr'] = df_C.index
        df_C = df_C.reset_index(drop=True)
            
        
    
    # define dict-lists, future dataframes
    df_M = []
    df_R = []
    df_T = []
    df_G = []
    df_A = []
    
    for m in model.metabolites: 
        row_dict = {'mid': m.id, 'name': m.name, 'formula': m.formula, 'charge': m.charge,}
        
        for db in m.annotation.keys():
            annots = m.annotation[db]
            if type(annots) == str: annots = [annots]
            annots = '; '.join([i for i in annots])
            row_dict[db] = annots
        df_M.append(row_dict)
        
    for r in model.reactions:
        row_dict = {'rid': r.id, 'name': r.name, 'rstring': r.reaction, 'gpr': "Not applicable", 'bounds': r.bounds}
        
        for db in r.annotation.keys():
            annots = r.annotation[db]
            if type(annots) == str: annots = [annots]
            annots = '; '.join([i for i in annots])
            row_dict[db] = annots
        
        # handle artificial reactions
        if r.id == 'Biomass':
            # commented as the type is inplicit in the ID
            #row_dict['type'] = 'biomass'
            df_A.append(row_dict)
                
        elif len(r.metabolites) == 1:
            # commented as the type is inplicit in the ID
            """
            if len(r.metabolites)==1 and list(r.metabolites)[0].id.rsplit('_',1)[-1] == 'e': 
                row_dict['type'] = 'exchange'
            elif r.lower_bound < 0 and r.upper_bound > 0:
                row_dict['type'] = 'sink'
            elif r.lower_bound == 0 and r.upper_bound > 0:
                row_dict['type'] = 'demand'
            """
            df_A.append(row_dict)
        
        else: # more than 1 metabolite involved
            row_dict['gpr'] = r.gene_reaction_rule
            
            # introduce reaction in the correct table: 
            if len(set([m.id.rsplit('_',1)[-1] for m in r.metabolites])) == 1:
                df_R.append(row_dict)
            else: df_T.append(row_dict)
            
    for g in model.genes:
        row_dict = {'gid': g.id, 'involved_in': '; '.join([r.id for r in g.reactions])}
        
        for db in g.annotation.keys():
            annots = g.annotation[db]
            if type(annots) == str: annots = [annots]
            annots = '; '.join([i for i in annots])
            row_dict[db] = annots
        df_G.append(row_dict)
    
    # create dataframes from dict-lists
    df_M = pnd.DataFrame.from_records(df_M)
    df_R = pnd.DataFrame.from_records(df_R)
    df_T = pnd.DataFrame.from_records(df_T)
    df_A = pnd.DataFrame.from_records(df_A)
    df_G = pnd.DataFrame.from_records(df_G)
    
    # sort columns
    df_M_first_cols = ['mid', 'name', 'formula', 'charge']
    df_M = df_M[df_M_first_cols + sorted([c for c in df_M.columns if c not in df_M_first_cols])]
    df_R_first_cols = ['rid', 'name', 'rstring', 'gpr', 'bounds']
    df_R = df_R[df_R_first_cols + sorted([c for c in df_R.columns if c not in df_R_first_cols])]
    df_T = df_T[df_R_first_cols + sorted([c for c in df_T.columns if c not in df_R_first_cols])]
    df_A = df_A[df_R_first_cols + sorted([c for c in df_A.columns if c not in df_R_first_cols])]
    df_G_first_cols = ['gid', 'involved_in']
    df_G = df_G[df_G_first_cols + sorted([c for c in df_G.columns if c not in df_G_first_cols])]
    
    
    
    with pnd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        df_M.to_excel(writer, sheet_name='Metabolites', index=False)
        df_R.to_excel(writer, sheet_name='Reactions', index=False)
        df_T.to_excel(writer, sheet_name='Transporters', index=False)
        df_G.to_excel(writer, sheet_name='Genes', index=False)
        df_A.to_excel(writer, sheet_name='Artificials', index=False)
        if df_E is not None and len(df_E)!=0: df_E.to_excel(writer, sheet_name='Precursors', index=False)
        if df_B is not None: df_B.to_excel(writer, sheet_name='Biomass', index=False)
        if df_P is not None and len(df_P)!=0: df_P.to_excel(writer, sheet_name='Biolog®', index=False)
        if df_S is not None and len(df_S.columns)>2: df_S.to_excel(writer, sheet_name='Biosynth', index=False) 
        if df_C is not None: 
            df_C.to_excel(writer, sheet_name='Coverage', index=False) 
            if nofigs == False:
                worksheet = writer.sheets['Coverage']
                worksheet.insert_image('E3', 'df_C_F1.png', {'image_data': df_C_F1})
            
        
    sheets_dict = {
        'model_id': model.id,
        'Metabolites': df_M,
        'Reactions': df_R,
        'Transporters': df_T,
        'Artificials': df_A,
        'Precursors': df_E,
        'Biomass': df_B,
        'Biolog': df_P,
        'Biosynth': df_S,
        'Coverage': df_C,
    }
    return sheets_dict



def comparative_table(logger, outdir, sheets_dicts):
    
    
    # create topology table (reaction presence / absence matrix): 
    df_topology = pnd.DataFrame()
    for sheets_dict in sheets_dicts:
        for index, row in sheets_dict['Reactions'].iterrows():
            if row['rid'] not in df_topology.index:
                df_topology.loc[row['rid'], 'rid'] = row['rid']
                for key, value in row.to_dict().items():
                    # force string to avoid errors with bounds
                    df_topology.loc[row['rid'], key] = '' if pnd.isna(value) else str(value)   
            df_topology.loc[row['rid'], sheets_dict['model_id']] = 1
    for sheets_dict in sheets_dicts:  # replace missing values:
        df_topology = df_topology.fillna({sheets_dict['model_id']: 0})
        
        
    # create GPR table (reaction presence / absence matrix): 
    df_gprs = pnd.DataFrame()
    for sheets_dict in sheets_dicts:
        for index, row in sheets_dict['Reactions'].iterrows():
            if row['rid'] not in df_gprs.index:
                df_gprs.loc[row['rid'], 'rid'] = row['rid']
                for key, value in row.to_dict().items():
                    # force string to avoid errors with bounds
                    df_gprs.loc[row['rid'], key] = '' if pnd.isna(value) else str(value)   
            df_gprs.loc[row['rid'], sheets_dict['model_id']] = row['gpr']
    for sheets_dict in sheets_dicts:  # replace missing values:
        df_gprs = df_gprs.fillna({sheets_dict['model_id']: 'missing'})
        
    
    with pnd.ExcelWriter(f"{outdir}/comparison.mkmodel.xlsx") as writer:
        df_topology.to_excel(writer, sheet_name='Topology', index=False)
        df_gprs.to_excel(writer, sheet_name='GPRs', index=False)
    logger.info(f"'{outdir}/comparison.mkmodel.xlsx' created!")
        
    