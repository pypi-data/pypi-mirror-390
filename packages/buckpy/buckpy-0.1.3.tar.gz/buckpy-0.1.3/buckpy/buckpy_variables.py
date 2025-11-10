"""
This module contains the definition of the indices of the variables used in BuckPy.
The indices of the variables listed in this module are global variables.
"""

# Index of the variables of the np_prob_var and np_case NumPy arrays
MUAX     = 0
MULAT_HT = 1
MULAT_OP = 2
HOOS     = 3

# Index of the variables of the np_case NumPy array
CBF_HT        = 4
CBF_OP        = 5
LFF_INST      = 6
LFF_HT        = 7
LFF_OP        = 8
RFF_INST      = 9
RFF_HT        = 10
RFF_OP        = 11
EAF_INST      = 12
EAF_HT        = 13
EAF_P_OP      = 14
EAF_OP        = 15
EAF_OP_UNBUCK = 16
LDELTAF_HT    = 17
RDELTAF_HT    = 18
LDELTAF_OP    = 19
RDELTAF_OP    = 20

# Index of the variables of the np_scen NumPy array
KP            = 0
LENGTH        = 1
ROUTE_TYPE    = 2
BEND_RADIUS   = 3
SW_INST       = 4
SW_HT         = 5
SW_OP         = 6
SCHAR_HT      = 7
SCHAR_OP      = 8
SV_HT         = 9
SV_OP         = 10
CBF_RCM       = 11
RLT           = 12
FRF_HT        = 13
FRF_P_OP      = 14
FRF_T_OP      = 15
FRF_OP        = 16
L_BUCKLE_HT   = 17
EAF_BUCKLE_HT = 18
L_BUCKLE_OP   = 19
EAF_BUCKLE_OP = 20
SECTION_ID    = 21
SECTION_KP    = 22
SECTION_REF   = 23
MUAX_MEAN     = 24
MULAT_HT_MEAN = 25
MULAT_OP_MEAN = 26
HOOS_MEAN     = 27

# Index of the variables of the np_distr NumPy array
MUAX_ARRAY         = 0
MUAX_CDF_ARRAY     = 1
MULAT_ARRAY_HT     = 2
MULAT_CDF_ARRAY_HT = 3
MULAT_ARRAY_OP     = 4
MULAT_CDF_ARRAY_OP = 5
HOOS_ARRAY         = 6
HOOS_CDF_ARRAY     = 7

# Index of the variables of the np_ends NumPy array
ROUTE_TYPE_BC = 0
KP_FROM       = 1
KP_TO         = 2
REAC_INST     = 3
REAC_HT       = 4
REAC_OP       = 5

# Index of the variables of the np_pp_buckle NumPy array
SIM_PP        = 0
KP_PP         = 1
ROUTE_TYPE_PP = 2
MUAX_PP       = 3
MULAT_OP_PP   = 4
HOOS_PP       = 5
CBF_OP_PP     = 6
VAS_PP        = 7

# Index of the variables of the np_pp_plot NumPy array
P_KP            = 0
P_CBF_HT        = 1
P_CBF_OP        = 2
P_EAF_INST      = 3
P_EAF_HT        = 4
P_EAF_P_OP      = 5
P_EAF_OP        = 6
P_BETA2         = 7
P_EAF_OP_UNBUCK = 8
