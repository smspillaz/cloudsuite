################################################################################
#                               Xeon E5-2680                                   #
################################################################################
TDP_xeon        = 120       # watts
die_xeon        = 306.18    # mm2
cores_xeon      = 14
clk_base_xeon   = 2.4       # GHz
clk_turbo_xeon  = 3.3       # GHz
RPS_max_xeon     = 115000
freq_scaling_xeon = clk_base_xeon/clk_turbo_xeon

################################################################################
#                        ThunderX2 CN9975 - Cavium                             #
################################################################################
TDP_cavium        = 180       # watts
die_cavium        = 420       # mm2
cores_cavium      = 28
clk_base_cavium   = 1.8       # GHz
clk_turbo_cavium  = 2.4       # GHz
RPS_max_cavium    = 159000
freq_scaling_cavium = clk_base_cavium/clk_turbo_cavium