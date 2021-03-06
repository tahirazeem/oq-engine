Classical Hazard-Risk QA test 4
===============================

gem-tstation:/home/michele/ssd/calc_22540.hdf5 updated Tue May 31 15:35:59 2016

num_sites = 6, sitecol = 969 B

Parameters
----------
============================ ===============================
calculation_mode             'classical'                    
number_of_logic_tree_samples 0                              
maximum_distance             {'Active Shallow Crust': 200.0}
investigation_time           50.0                           
ses_per_logic_tree_path      1                              
truncation_level             3.0                            
rupture_mesh_spacing         5.0                            
complex_fault_mesh_spacing   5.0                            
width_of_mfd_bin             0.2                            
area_source_discretization   10.0                           
random_seed                  23                             
master_seed                  0                              
sites_per_tile               10000                          
engine_version               '2.0.0-git4fb4450'             
============================ ===============================

Input files
-----------
======================== ============================================================
Name                     File                                                        
======================== ============================================================
exposure                 `exposure_model.xml <exposure_model.xml>`_                  
gsim_logic_tree          `gmpe_logic_tree.xml <gmpe_logic_tree.xml>`_                
job_ini                  `job_haz.ini <job_haz.ini>`_                                
source                   `source_model.xml <source_model.xml>`_                      
source_model_logic_tree  `source_model_logic_tree.xml <source_model_logic_tree.xml>`_
structural_vulnerability `vulnerability_model.xml <vulnerability_model.xml>`_        
======================== ============================================================

Composite source model
----------------------
========= ====== ====================================== =============== ================
smlt_path weight source_model_file                      gsim_logic_tree num_realizations
========= ====== ====================================== =============== ================
b1        1.000  `source_model.xml <source_model.xml>`_ simple(2)       2/2             
========= ====== ====================================== =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== =================================== =========== ======================= =================
grp_id gsims                               distances   siteparams              ruptparams       
====== =================================== =========== ======================= =================
0      AkkarBommer2010() ChiouYoungs2008() rx rjb rrup vs30measured z1pt0 vs30 ztor mag rake dip
====== =================================== =========== ======================= =================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=2, rlzs=2)
  0,AkkarBommer2010(): ['<0,b1~b1,w=0.4>']
  0,ChiouYoungs2008(): ['<1,b1~b2,w=0.6>']>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== =========== ============ ======
source_model     grp_id trt                  num_sources eff_ruptures weight
================ ====== ==================== =========== ============ ======
source_model.xml 0      Active Shallow Crust 2           6405         160   
================ ====== ==================== =========== ============ ======

Informational data
------------------
======================================== ============
count_eff_ruptures_max_received_per_task 3,197       
count_eff_ruptures_num_tasks             2           
count_eff_ruptures_sent.monitor          5,964       
count_eff_ruptures_sent.rlzs_assoc       1,874       
count_eff_ruptures_sent.sitecol          1,066       
count_eff_ruptures_sent.siteidx          10          
count_eff_ruptures_sent.sources          3,938       
count_eff_ruptures_tot_received          6,394       
hazard.input_weight                      2,276       
hazard.n_imts                            1           
hazard.n_levels                          19          
hazard.n_realizations                    2           
hazard.n_sites                           6           
hazard.n_sources                         0           
hazard.output_weight                     228         
hostname                                 gem-tstation
require_epsilons                         1           
======================================== ============

Exposure model
--------------
=========== =
#assets     6
#taxonomies 2
=========== =

======== ===== ====== === === ========= ==========
taxonomy mean  stddev min max num_sites num_assets
A        1.000 NaN    1   1   1         1         
W        1.000 0.0    1   1   5         5         
*ALL*    1.000 0.0    1   1   6         6         
======== ===== ====== === === ========= ==========

Slowest sources
---------------
============ ========= ============ ====== ========= =========== ========== =========
src_group_id source_id source_class weight split_num filter_time split_time calc_time
============ ========= ============ ====== ========= =========== ========== =========
0            376       AreaSource   55     1         7.389E-04   0.0        0.0      
0            231       AreaSource   104    1         7.000E-04   0.0        0.0      
============ ========= ============ ====== ========= =========== ========== =========

Computation times by source typology
------------------------------------
============ =========== ========== ========= ======
source_class filter_time split_time calc_time counts
============ =========== ========== ========= ======
AreaSource   0.001       0.0        0.0       2     
============ =========== ========== ========= ======

Information about the tasks
---------------------------
Not available

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
reading composite source model 2.203     0.0       1     
managing sources               0.035     0.0       1     
filtering sources              0.031     0.0       39    
store source_info              0.018     0.0       1     
reading exposure               0.005     0.0       1     
total count_eff_ruptures       5.219E-04 0.0       2     
aggregate curves               5.317E-05 0.0       2     
reading site collection        8.821E-06 0.0       1     
============================== ========= ========= ======