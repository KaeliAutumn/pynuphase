import numpy

'''
some constants:
'''
n_ice = 1.78
c_light = 0.29929 #m/ns
c_light = c_light / n_ice

nuphase_fiber_delay = 4.950 #ns/m
nuphase_fiber_lengths = [14,12,10,9,8,7,6,5,4,3,2,1]
nuphase_fiber_lengths = nuphase_fiber_lengths[::-1]

nuphase_max_daq_channels = 12
nuphase_good_channels = 9
nuphase_good_vpol_ch = 7
nuphase_good_hpol_ch = 2

nuphase_antenna_name = ['H1','H2','V1','V2','V3','V4','V5','V6','V6','V7','V8','V9','V10']
nuphase_antenna_relative_z = [0,1.98,3.98,5.00,6.02,7.03,8.07,9.09,10.11,11.12,12.135,13.17]  #m
nuphase_antenna_name = nuphase_antenna_name[::-1]
nuphase_antenna_relative_z = nuphase_antenna_relative_z[::-1]

string_depth = 184.77 #m
nuphase_antenna_depth = string_depth - numpy.array(nuphase_antenna_relative_z)
nuphase_good_antenna_depth = numpy.take(nuphase_antenna_depth, [0,1,2,3,4,6,8,10,11])

nuphase_sampling_rate = 1.5 #GHz
nuphase_mV_per_count = 6.8 

nuphase_vpol_baselines = numpy.diff(nuphase_good_antenna_depth[:nuphase_good_vpol_ch])
nuphase_hpol_baselines = numpy.diff(nuphase_good_antenna_depth[nuphase_good_vpol_ch:])

nuphase_vpol_beamform_codes = [4,3,2,1,0,-2,-4] #assuming perfect spacing
nuphase_mean_vpol_baseline = numpy.mean(numpy.abs(nuphase_vpol_baselines / numpy.diff(nuphase_vpol_beamform_codes)))

def getChannelMapping(run):
    '''
    define channel mapping by run number
    nuphase_ch_map = {DAQ channel : 'antenna'}
    '''

    if run < 365:
        nuphase_ch_map = { 0 : 'V9',
                           1 : 'V8',
                           2 : 'V7',
                           3 : 'V6',
                           4 : 'V5',
                           5 : 'V4', #dead
                           6 : 'V3',
                           7 : 'V2', #dead
                           8 : 'H2',
                           9 : 'H1',
                           10: 'V10',  #dead
                           11: 'V1'}
        
    else:
        nuphase_ch_map = { 0 : 'V9',
                           1 : 'V8',
                           2 : 'V7',
                           3 : 'V6',
                           4 : 'V5',
                           5 : 'V4', #dead
                           6 : 'V3',
                           7 : 'V1',
                           8 : 'H2',
                           9 : 'H1',
                           10: 'V10',  #dead
                           11: 'V2'}  #dead
       
    return {a: b for b,a in nuphase_ch_map.iteritems()}

def inverseChannelMap(ch_map):
    return {a: b for b,a in ch_map.iteritems()}

def getTheta(delay, spacing):
    theta= numpy.arcsin( delay * c_light / spacing )
    return theta

good_ch = ['V9', 'V8', 'V7', 'V6', 'V5', 'V3', 'V1', 'H2', 'H1']
good_ch_fiber_lengths=[2,3,4,5,6,8,10,12,14] #m

if __name__=='__main__':
    print nuphase_good_antenna_depth, 'meters'
    print nuphase_vpol_baselines, 'meters'
    print nuphase_hpol_baselines, 'meters'
    print nuphase_mean_vpol_baseline, 'meters'
