import warnings 
import os
import logging


import cobra
import gempipe


from ..commons import fba_no_warnings
from ..commons import get_optthr



def verify_egc(logger, model, mid, outdir): 

    
    # changes as not permament: 
    found_egc = False
    with model: 
        
        # close (0; 0) all the exchange reactions: 
        gempipe.close_boundaries(model)
        
                
        # create a dissipation reaction: 
        dissip = cobra.Reaction(f'__dissip__{mid}')
        model.add_reactions([dissip])
        dissip = model.reactions.get_by_id(f'__dissip__{mid}')
        
        
        # define the dissipation reaction:
        modeled_mids = [m.id for m in model.metabolites]
        if   mid == 'atp':
            dissip_string = 'atp_c + h2o_c --> adp_c + pi_c + h_c'
        elif mid == 'ctp':
            dissip_string = 'ctp_c + h2o_c --> cdp_c + pi_c + h_c'
        elif mid == 'gtp':
            dissip_string = 'gtp_c + h2o_c --> gdp_c + pi_c + h_c'
        elif mid == 'utp':
            dissip_string = 'utp_c + h2o_c --> udp_c + pi_c + h_c'
        elif mid == 'itp':
            dissip_string = 'itp_c + h2o_c --> idp_c + pi_c + h_c'
        elif mid == 'nadh':
            dissip_string = 'nadh_c --> nad_c + h_c'
        elif mid == 'nadph':
            dissip_string = 'nadph_c --> nadp_c + h_c'
        elif mid == 'fadh2':
            dissip_string = 'fadh2_c --> fad_c + 2.0 h_c'
        elif mid == 'accoa':
            dissip_string = 'accoa_c + h2o_c --> ac_c + coa_c + h_c'
        elif mid == 'glu__L':
            dissip_string = 'glu__L_c + h2o_c --> akg_c + nh4_c + 2.0 h_c'
        elif mid == 'q8h2':
            dissip_string = 'q8h2_c --> q8_c + 2.0 h_c'
        dissip.build_reaction_from_string(dissip_string)
        
        
        # set the objective and optimize: 
        model.objective = f'__dissip__{mid}'
        res, obj_value, status = fba_no_warnings(model)
        
        
        # apply the threshold:
        obj_value = res.objective_value
        status = res.status
        if status == 'optimal' and obj_value >= get_optthr():
            found_egc = True
                

            # get suspect !=0 fluxes 
            fluxes = res.fluxes
            # get interesting fluxes (get_optthr() tries to take into account the approximation in glpk and cplex solvers)
            fluxes_interesting = fluxes[(fluxes > get_optthr()) | (fluxes < -get_optthr())]
            

            # create a model for escher, remove Rs not beloning to the cycle
            model_copy = model.copy()
            all_rids = [r.id for r in model_copy.reactions]
            to_delete = set(all_rids) - set(fluxes_interesting.index)


            # trick to avoid the WARNING "cobra/core/group.py:147: UserWarning: need to pass in a list" 
            # triggered when trying to remove reactions that are included in groups. 
            with warnings.catch_warnings():  # temporarily suppress warnings for this block
                warnings.simplefilter("ignore")  # ignore all warnings
                cobra_logger = logging.getLogger("cobra.util.solver")
                old_level = cobra_logger.level
                cobra_logger.setLevel(logging.ERROR)   
                
                # triggering code
                model_copy.remove_reactions(to_delete)  # should work also with IDs

                # restore original behaviour: 
                cobra_logger.setLevel(old_level) 
                
                
            # save JSON to direct import in Escher:
            outfile = os.path.join(outdir, f'EGC_{mid}.json')
            cobra.io.save_json_model(model_copy, outfile)


            # log some messages
            rid_labels = []
            for rid, flux in fluxes_interesting.to_dict().items():
                rid_label = "'" + rid + "'" 
                # mark reversible reactions composing the cycle:
                r = model.reactions.get_by_id(rid)
                if r.lower_bound < 0 and r.upper_bound > 0:
                    rid_label = rid_label + '(<=>)'
                rid_labels.append(rid_label)
            logger.warning(f"Found erroneous EGC (N={len(model_copy.reactions)}) for '{mid}' (f={obj_value}): [{', '.join(rid_labels)}]. EGC saved to '{outfile}' to be inspected with Escher-FBA.")
            
            
    return found_egc



def verify_egc_all(logger, model, outdir='./', mids_to_check=['atp','ctp','gtp','utp','itp','nadh','nadph','fadh2','accoa','glu__L','q8h2']):

    
    all_results = []
    for mid in mids_to_check:
        all_results.append(verify_egc(logger, model, mid, outdir))
    if any(all_results)==False:
        logger.info("Found 0 erroneous energy-generating cycles (EGCs).")
        
        
