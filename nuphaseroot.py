import numpy
import ROOT as root
import setup
import detector
import os

class NUPHASEROOT:
    '''
    Python Class wrapper for nuphaseroot package
    1) returns numpy waveforms for a single run
    2) returns status dictionaries for a single or chronological set of runs
    2) returns header dictionaries for a single or chronological set of runs
    
    define nuphaseroot install (build) directory and data location in setup.py
    '''
    
    root_data_prefix = setup.nuphase_root_data_prefix
    
    def __init__(self, run=0):
        self.loadSharedLibrary()
        self.run = int(run)
        self.waveform_length = 0

        #header dictionary
        self.header = {}
        self.header['readout_time'] = []
        self.header['deadtime'] = []
        self.header['buffer_number'] = []
        self.header['trig_time'] = []
        self.header['beam_power'] = []
        self.header['gate_flag'] = []
        self.header['event_number'] = []
        self.header['trig_number'] = []
        self.header['trig_beam'] = []
        self.header['trig_type'] = []

        #status dictionary
        self.status = {}
        self.status['trig_thresholds'] = []
        self.status['latched_pps_time'] = []
        self.status['readout_time'] = []
        self.status['global_scalers'] = []
        self.status['beam_scalers'] = [] 
        self.status['deadtime'] = [] 

    def loadSharedLibrary(self):
        root.gROOT.Reset()
        root.gSystem.Load(setup.nuphase_root_library)

    def clearDicts(self):

        for key in self.status:
            self.status[key] = []
        for key in self.header:
            self.header[key] = []
            
    def setRun(self, run):
        self.run = run
        self.clearDicts()

    def getHeaderData(self, filtered=False):
        '''
        get header data
        if filtered=True, use filtered header files which are matched, event-by-event, to the event files
        '''
        if filtered:
            header_filename = self.root_data_prefix + 'run'+str(self.run)+'/header.filtered.root'
        else:
            header_filename = self.root_data_prefix + 'run'+str(self.run)+'/header.root'

        if not os.path.isfile(header_filename):
            print 'No headerfile found for specified run'
            return self.header
        
        f = root.TFile(header_filename)
        t_hd = f.Get('header')
        
        header = root.nuphase.Header()
        t_hd.SetBranchAddress("header", header)
        
        for ev in range(t_hd.GetEntries()):
            t_hd.GetEntry(ev)

            self.header['readout_time'].append(header.readout_time[0] + header.readout_time_ns[0]*1.e-9)
            self.header['deadtime'].append(header.deadtime[0])
            self.header['buffer_number'].append(header.buffer_number)
            self.header['trig_time'].append(numpy.array(header.trig_time).tolist())
            self.header['beam_power'].append(numpy.array(header.beam_power).tolist())
            self.header['gate_flag'].append(ord(header.gate_flag))
            self.header['event_number'].append(header.event_number)
            self.header['trig_number'].append(header.trig_number)
            self.header['trig_beam'].append(header.triggered_beams)
            self.header['trig_type'].append(header.trigger_type)

        return self.header

    def getHeaderFromMultiple(self, runs, filtered=False):

        combined_header=self.header.copy()
        
        #clear dict
        for key in combined_header:
            combined_status[key] = []

        for run in runs:
            self.setRun(run)
            self.getHeaderData(filtered)

            for key in combined_header:
                combined_header[key].extend(self.header[key])

        return combined_header

    def getStatusData(self):
        status_filename = self.root_data_prefix + 'run'+str(self.run)+'/status.root'

        if not os.path.isfile(status_filename):
            print 'No statusfile found for specified run'
            return self.status

        t_st = f.Get('status')

        status = root.nuphase.Status()
        try:
            t_st.SetBranchAddress("status", status)
        except:
            return self.status

        for st in range(t_st.GetEntries()):
            t_st.GetEntry(st)

            self.status['readout_time'].append(status.readout_time + status.readout_time_ns*1.e-9)
            self.status['trig_thresholds'].append(numpy.array(status.trigger_thresholds).tolist())
            self.status['global_scalers'].append(numpy.array(status.global_scalers).tolist())
            self.status['beam_scalers'].append(numpy.array(status.beam_scalers).tolist())
            self.status['latched_pps_time'].append(status.latched_pps_time)
            self.status['deadtime'].append(status.deadtime)

        return self.status

    def getStatusFromMultiple(self, runs, decimation=1):

        combined_status=self.status.copy()
        
        #clear dict
        for key in combined_status:
            combined_status[key] = []

        for run in runs:
            self.setRun(run)
            self.getStatusData()

            for key in combined_status:
                combined_status[key].extend(self.status[key])

        return combined_status

    def getEventTree(self):
        event_filename = self.root_data_prefix + 'run'+str(self.run)+'/event.root'

        if not os.path.isfile(event_filename):
            print 'No eventfile found for specified run'
            return 1

        f = root.TFile(event_filename)
        t = f.Get('event')
        event = root.nuphase.Event()
        t.SetBranchAddress("event", event)
        return t, event
        
    
    def getEvents(self, get_events='all'):
        '''
        dump entire event waveforms to event list of numpy arrays
        returns only waveforms from the known good channels in the array, in descending order in the string
        get_events = list of Tree entries, or 'all'
        '''
        
        event_filename = self.root_data_prefix + 'run'+str(self.run)+'/event.root'

        if not os.path.isfile(event_filename):
            print 'No eventfile found for specified run'
            return 1

        f = root.TFile(event_filename)        
        t = f.Get('event')

        event = root.nuphase.Event()
        t.SetBranchAddress("event", event)
        
        #t, event = self.getEventTree()
        wave = []

        #get number of saved channels
        digitized_channels = numpy.zeros(detector.nuphase_max_daq_channels)
        t.GetEntry(0)
        self.waveform_length = event.getBufferLength()

        ch_map = detector.getChannelMapping(self.run)
        event_map=[]
        for ant in detector.good_ch:
            event_map.append(ch_map[ant])

        if get_events == 'all':
            event_loop = range(t.GetEntries())
        else:
            event_loop = get_events

        for j in event_loop:
            t.GetEntry(j)

            _wave = numpy.zeros((detector.nuphase_good_channels, self.waveform_length))

            for i in range(detector.nuphase_good_channels):
                _wave[i] = self.dumpEvent(event, event_map[i])
                
            wave.append(_wave)
        
        return wave 

    def dumpEvent(self, event, channel):
        long_buffer = event.getRawData(channel)
        long_buffer.SetSize(event.getBufferLength())
        return numpy.frombuffer(long_buffer, numpy.ubyte) 


    
#if __name__=='__main__':
#    nproot = NUPHASEROOT(360)
#    nproot.getEvents([1,2,3])
    
    
