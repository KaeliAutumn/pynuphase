import nuphaseroot as nproot
import matplotlib.pyplot as plt
import numpy
import waveform
import nuphaseroot
import detector

class Pulses:
    '''
    Class to do signal processing of a single nuphase event 
    '''  
    def __init__(self, wfms=None, sampling_rate=detector.nuphase_sampling_rate):
        '''
        data can either be loaded here by assigning a list of numpy array wfms, or directly from the ROOT file usind getWaveforms
        '''
        self.wave=[]
        self.wfm_length = 0
        self.sampling_rate = 1./sampling_rate
        self.channels = 0

        if wfms is not None:
            self.wfm_length = len(wfms[0])
            self.channels = len(wfms)
            for i in range(self.channels):
                self.wave.append(waveform.Waveform(wfms[i]-numpy.median(wfms[i]), sampling_rate = self.sampling_rate))
                
    def getWaveforms(self, run, event):
        nproot = nuphaseroot.NUPHASEROOT(run)
        self.wfm_length = nproot.waveform_length
        wfms = nproot.getEvents([event])[0]
        self.channels = len(wfms)

        for i in range(self.channels):
            self.wave.append(waveform.Waveform(wfms[i]-numpy.median(wfms[i]), sampling_rate = self.sampling_rate))

    def fft(self):
        for i in range(self.channels):
            self.wave[i].fft()
            
    def convertToVolts(self):
        for i in range(self.channels):
            self.wave[i].voltage = self.wave[i].voltage * detector.nuphase_mV_per_count * 1.e-3
        self.fft()

    def getBaselineNoise(self, baseline_samples=50):
        pre_rms=[]
        for i in range(self.channels):
            pre_rms.append(numpy.sum(numpy.square(self.wave[i].voltage[0:baseline_samples])))
        return pre_rms

    def nullFiberDelays(self):
        for i in range(self.channels):
            self.wave[i].voltage=numpy.roll(self.wave[i].voltage, -detector.good_ch_fiber_lengths[i]*int(numpy.round(detector.nuphase_fiber_delay/self.wave[i].dt)))
            self.wave[i].fft()

    def upsample(self, upsample_factor):
        for i in range(self.channels):
            self.wave[i].upsampleFreqDomain(upsample_factor)
            #plt.plot(self.wave[i].time, self.wave[i].voltage)
        #plt.show()
        self.wfm_length = len(self.wave[0].voltage)
        self.sampling_rate = self.wave[0].dt

    def getCoherentSum(self, delay, pol='vpol'):
        '''
        simple coherent sum, using all antennas. Can later generalize to all correlation pairs, a la ANITA maps
        fiber delays should be nulled before computing coherent sums
        inputs:
        delay = number of sampling steps to delay nearest antenna pairs
        pol = pick vpol or hpol
        '''
        coh_sum=numpy.zeros(len(self.wave[0].voltage))
        if pol == 'vpol':
            for i in range(detector.nuphase_good_vpol_ch):
                coh_sum += numpy.roll(self.wfms[j].voltage, delay*nuphase_vpol_beamform_codes[i])
            
            return coh_sum, detector.getTheta(delay*self.sampling_rate, detector.nuphase_mean_vpol_baseline)

        elif pol == 'hpol':
            for i in range(detector.nuphase_good_hpol_ch):
                coh_sum += numpy.roll(self.wfms[i+detector.nuphase_good_vpol_ch].voltage, i*delay)

            return coh_sum, detector.getTheta(delay*self.sampling_rate, detector.nuphase_hpol_baselines[0])

        return None
        
    def alignUsingPeak(self, location):
        time=[]
        for i in range(self.channels):
            idx=numpy.argmax(self.wave[i].voltage)
            time.append(self.wave[i].time[idx])
            self.wave[i].voltage = numpy.roll(self.wave[i].voltage, -idx-location)

        return time
            
    def alignUsingThreshold(self, threshold, location):
        time=[]
        for i in range(self.channels):
            above_thresh = numpy.where(self.wave[i].voltage > threshold)[0]

            if len(above_thresh) < 1:
                continue
            #    return None, None

            if location is not None:
                self.wave[i].voltage = numpy.roll(self.wave[i].voltage, -above_thresh[0]-location)

            time.append(self.wave[i].time[above_thresh[0]])
                        
        return time

    def alignUsingCrossCor(self, location, cc_wave, corr_cut=0.5):
        '''
        cc_wave needs to be a list Waveform classes with length = NUPHASE_VPOL_CH 
        '''
        cor = self.crossCorrelate(cc_wave)
        time=[]
        
        for i in range(self.channels):

            if max(cor[i]) < corr_cut:
                return None, None

            idx = numpy.argmax(cor[i])
            
            self.wave[i].voltage = numpy.roll(self.wave[i].voltage, -idx-location)
            time.append(self.wave[i].time[idx])

        return time, cor

    def crossCorrelate(self, cc_wave=None, norm=True):
        '''
        cross correlate vs another instance of the PulseProcess class
        cc_wave=None ==> autocorrelate
        '''
        cor=[]
        for i in range(self.channels):
            if cc_wave is not None:
                if norm:                    
                    cor.append(self.wave[i].crossCorrelate(cc_wave.wave[i]) /
                               math.sqrt(max(self.wave[i].crossCorrelate()) * max(cc_wave.wave[i].crossCorrelate())) )
                else:
                    cor.append(self.wave[i].crossCorrelate(cc_wave.wave[i]))          
            else:
                if norm:
                    cor.append(self.wave[i].crossCorrelate() / 
                               math.sqrt(max(self.wave[i].crossCorrelate()) * max(self.wave[i].crossCorrelate())) )
                else:
                    cor.append(self.wave[i].crossCorrelate())

        return cor


