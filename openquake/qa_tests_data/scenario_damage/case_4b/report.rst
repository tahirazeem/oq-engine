scenario hazard
===============

gem-tstation:/home/michele/ssd/calc_22550.hdf5 updated Tue May 31 15:36:58 2016

num_sites = 7, sitecol = 1015 B

Parameters
----------
============================ ==================
calculation_mode             'scenario'        
number_of_logic_tree_samples 0                 
maximum_distance             {'default': 200.0}
investigation_time           None              
ses_per_logic_tree_path      1                 
truncation_level             3.0               
rupture_mesh_spacing         2.0               
complex_fault_mesh_spacing   2.0               
width_of_mfd_bin             None              
area_source_discretization   None              
random_seed                  42                
master_seed                  0                 
engine_version               '2.0.0-git4fb4450'
============================ ==================

Input files
-----------
=============== ============================================
Name            File                                        
=============== ============================================
exposure        `exposure_model.xml <exposure_model.xml>`_  
gsim_logic_tree `gsim_logic_tree.xml <gsim_logic_tree.xml>`_
job_ini         `job_haz.ini <job_haz.ini>`_                
rupture_model   `rupture_model.xml <rupture_model.xml>`_    
=============== ============================================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=2, rlzs=2)
  0,BooreAtkinson2008(): ['<0,b_1~b1,w=0.75>']
  0,ChiouYoungs2008(): ['<1,b_1~b2,w=0.25>']>

Exposure model
--------------
=========== =
#assets     7
#taxonomies 3
=========== =

======== ===== ====== === === ========= ==========
taxonomy mean  stddev min max num_sites num_assets
tax1     1.000 0.0    1   1   4         4         
tax2     1.000 0.0    1   1   2         2         
tax3     1.000 NaN    1   1   1         1         
*ALL*    1.000 0.0    1   1   7         7         
======== ===== ====== === === ========= ==========

Information about the tasks
---------------------------
Not available

Slowest operations
------------------
======================= ========= ========= ======
operation               time_sec  memory_mb counts
======================= ========= ========= ======
filtering sites         0.008     0.0       1     
reading exposure        0.007     0.0       1     
computing gmfs          0.005     0.0       1     
reading site collection 5.960E-06 0.0       1     
======================= ========= ========= ======