Scenario QA Test, Case 9, Multiple GSIMs
========================================

gem-tstation:/home/michele/ssd/calc_22553.hdf5 updated Tue May 31 15:36:58 2016

num_sites = 3, sitecol = 831 B

Parameters
----------
============================ ==================
calculation_mode             'scenario'        
number_of_logic_tree_samples 0                 
maximum_distance             {'default': 200}  
investigation_time           None              
ses_per_logic_tree_path      1                 
truncation_level             1.0               
rupture_mesh_spacing         1.0               
complex_fault_mesh_spacing   1.0               
width_of_mfd_bin             None              
area_source_discretization   None              
random_seed                  3                 
master_seed                  0                 
engine_version               '2.0.0-git4fb4450'
============================ ==================

Input files
-----------
=============== ============================================
Name            File                                        
=============== ============================================
gsim_logic_tree `gsim_logic_tree.xml <gsim_logic_tree.xml>`_
job_ini         `job.ini <job.ini>`_                        
rupture_model   `rupture_model.xml <rupture_model.xml>`_    
=============== ============================================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=2, rlzs=2)
  0,LinLee2008SSlab(): ['<0,b_1~b1,w=0.6>']
  0,YoungsEtAl1997SSlab(): ['<1,b_1~b2,w=0.4>']>

Information about the tasks
---------------------------
Not available

Slowest operations
------------------
======================= ========= ========= ======
operation               time_sec  memory_mb counts
======================= ========= ========= ======
filtering sites         0.012     0.0       1     
computing gmfs          0.002     0.0       1     
reading site collection 2.980E-05 0.0       1     
======================= ========= ========= ======