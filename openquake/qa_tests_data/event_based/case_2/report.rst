Event-Based Hazard QA Test, Case 2
==================================

gem-tstation:/home/michele/ssd/calc_22607.hdf5 updated Tue May 31 15:38:28 2016

num_sites = 1, sitecol = 739 B

Parameters
----------
============================ ===============================
calculation_mode             'event_based'                  
number_of_logic_tree_samples 0                              
maximum_distance             {'active shallow crust': 200.0}
investigation_time           1.0                            
ses_per_logic_tree_path      600                            
truncation_level             0.0                            
rupture_mesh_spacing         1.0                            
complex_fault_mesh_spacing   1.0                            
width_of_mfd_bin             0.001                          
area_source_discretization   10.0                           
random_seed                  1066                           
master_seed                  0                              
engine_version               '2.0.0-git4fb4450'             
============================ ===============================

Input files
-----------
======================= ============================================================
Name                    File                                                        
======================= ============================================================
gsim_logic_tree         `gsim_logic_tree.xml <gsim_logic_tree.xml>`_                
job_ini                 `job.ini <job.ini>`_                                        
source                  `source_model.xml <source_model.xml>`_                      
source_model_logic_tree `source_model_logic_tree.xml <source_model_logic_tree.xml>`_
======================= ============================================================

Composite source model
----------------------
========= ====== ====================================== =============== ================
smlt_path weight source_model_file                      gsim_logic_tree num_realizations
========= ====== ====================================== =============== ================
b1        1.000  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
========= ====== ====================================== =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== ================ ========= ========== ==========
grp_id gsims            distances siteparams ruptparams
====== ================ ========= ========== ==========
0      SadighEtAl1997() rrup      vs30       rake mag  
====== ================ ========= ========== ==========

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=1)
  0,SadighEtAl1997(): ['<0,b1~b1,w=1.0>']>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== =========== ============ ======
source_model     grp_id trt                  num_sources eff_ruptures weight
================ ====== ==================== =========== ============ ======
source_model.xml 0      Active Shallow Crust 1           3            75    
================ ====== ==================== =========== ============ ======

Informational data
------------------
======== ============
hostname gem-tstation
======== ============

Specific information for event based
------------------------------------
======================== =====
Total number of ruptures 3    
Total number of events   3    
Rupture multiplicity     1.000
======================== =====

Slowest sources
---------------
============ ========= ============ ====== ========= =========== ========== =========
src_group_id source_id source_class weight split_num filter_time split_time calc_time
============ ========= ============ ====== ========= =========== ========== =========
0            1         PointSource  75     1         0.004       1.812E-05  2.088    
============ ========= ============ ====== ========= =========== ========== =========

Computation times by source typology
------------------------------------
============ =========== ========== ========= ======
source_class filter_time split_time calc_time counts
============ =========== ========== ========= ======
PointSource  0.004       1.812E-05  2.088     1     
============ =========== ========== ========= ======

Information about the tasks
---------------------------
================================= ===== ========= ===== ===== =========
measurement                       mean  stddev    min   max   num_tasks
compute_ruptures.time_sec         2.088 NaN       2.088 2.088 1        
compute_ruptures.memory_mb        0.0   NaN       0.0   0.0   1        
compute_gmfs_and_curves.time_sec  0.001 4.216E-04 0.001 0.002 3        
compute_gmfs_and_curves.memory_mb 0.0   0.0       0.0   0.0   3        
================================= ===== ========= ===== ===== =========

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
total compute_ruptures         2.088     0.0       1     
reading composite source model 0.008     0.0       1     
managing sources               0.006     0.0       1     
store source_info              0.005     0.0       1     
total compute_gmfs_and_curves  0.004     0.0       3     
filtering sources              0.004     0.0       1     
saving ruptures                0.003     0.0       1     
make contexts                  0.002     0.0       3     
aggregating hcurves            0.002     0.0       3     
saving gmfs                    0.001     0.0       3     
aggregate curves               9.668E-04 0.0       4     
filtering ruptures             6.232E-04 0.0       3     
bulding hazard curves          5.271E-04 0.0       3     
compute poes                   4.883E-04 0.0       3     
reading site collection        2.599E-05 0.0       1     
splitting sources              1.812E-05 0.0       1     
============================== ========= ========= ======