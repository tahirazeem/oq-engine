Scenario Damage
===============

gem-tstation:/home/michele/ssd/calc_22544.hdf5 updated Tue May 31 15:36:57 2016

num_sites = 7, sitecol = 697 B

Parameters
----------
============================ ==================
calculation_mode             'scenario_damage' 
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
==================== ============================================
Name                 File                                        
==================== ============================================
exposure             `exposure_model.xml <exposure_model.xml>`_  
job_ini              `job.ini <job.ini>`_                        
rupture_model        `rupture_model.xml <rupture_model.xml>`_    
sites                `sites.csv <sites.csv>`_                    
structural_fragility `fragility_model.xml <fragility_model.xml>`_
==================== ============================================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=1)
  0,BooreAtkinson2008(): ['<0,b_1~b1,w=1.0>']>

Exposure model
--------------
=========== =
#assets     1
#taxonomies 1
=========== =

======== ===== ====== === === ========= ==========
taxonomy mean  stddev min max num_sites num_assets
Wood     1.000 NaN    1   1   1         1         
======== ===== ====== === === ========= ==========

Information about the tasks
---------------------------
========================= ===== ====== ===== ===== =========
measurement               mean  stddev min   max   num_tasks
scenario_damage.time_sec  0.011 NaN    0.011 0.011 1        
scenario_damage.memory_mb 0.0   NaN    0.0   0.0   1        
========================= ===== ====== ===== ===== =========

Slowest operations
------------------
======================= ========= ========= ======
operation               time_sec  memory_mb counts
======================= ========= ========= ======
total scenario_damage   0.011     0.0       1     
computing riskmodel     0.011     0.0       1     
filtering sites         0.007     0.0       1     
reading exposure        0.003     0.0       1     
computing gmfs          0.002     0.0       1     
saving gmfs             0.001     0.0       1     
assoc_assets_sites      6.092E-04 0.0       1     
building riskinputs     1.152E-04 0.0       1     
reading site collection 1.051E-04 0.0       1     
building hazard         6.914E-05 0.0       1     
======================= ========= ========= ======