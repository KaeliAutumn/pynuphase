#import tools.myplot
import nuphase_pulse
import matplotlib.pyplot as plt
import numpy
import sys
import time
import detector
import waveform as waveform
import signal

NULL_FIBER_DELAY = True
UPSAMPLE_FACTOR = 2 #for nulling fiber delays

def getTimebase(T, sampling_rate_ghz=detector.nuphase_sampling_rate):
    return numpy.arange(T.buffer_length) * 1./sampling_rate_ghz

def makeViewer(num):
    fig = plt.figure(num, figsize=(14,9))
    ax=[]
    for i in range(7):
        if i > 0:
            ax.append(plt.subplot2grid((7,4),(i,0), colspan=2, sharex=ax[0]))
        else:
            ax.append(plt.subplot2grid((7,4),(i,0), colspan=2))

        if i < 6:
            plt.setp(ax[i].get_xticklabels(), visible=False)

    ax.append(plt.subplot2grid((7,4),(0,2), colspan=2))
    ax.append(plt.subplot2grid((7,4),(1,2), colspan=2, sharex=ax[7]))
    plt.setp(ax[7].get_xticklabels(), visible=False)
    fig.subplots_adjust(hspace=0.1, left=0.05, right=0.97, top=0.97, bottom=0.07)
    ax.append(plt.subplot2grid((7,4),(3,2), colspan=2, rowspan=3))

    fig.subplots_adjust(wspace=0.3)
    return fig, ax

def plotViewer(wfms):

    fig, ax = makeViewer(1)

    color=['black','black','black','black','black','black','black','blue', 'blue']
    label_antenna=['V0', 'V1','V2','V3','V4','V5','V6', 'H0', 'H1']
    label_z=['0m', '-1m','-2m ','-3m','-4m','-6m','-8m', '-10m', '-12m']

    waves = nuphase_pulse.Pulses(wfms=wfms)
    waves.convertToVolts()
    waves.fft()
    waves.upsample(UPSAMPLE_FACTOR)
    if NULL_FIBER_DELAY:
        waves.nullFiberDelays()

    for i in range(detector.nuphase_good_channels):

        ax[i].plot(waves.wave[i].time, waves.wave[i].voltage , 'o-', color=color[i], label=label_antenna[i]+' : '+label_z[i], ms=1)
        ax[i].set_xlim([0, waves.wave[i].time[-2]])
        
        if i < 7:
            ax[i].set_ylim([-.35, .35])
        else:
            ax[i].set_ylim([-.35, .35])
        leg = ax[i].legend(loc='upper right', fontsize=10, handlelength=0, handletextpad=0)
        for item in leg.legendHandles:
            item.set_visible(False)
        
        if i==6 or i==8:
            ax[i].set_xlabel('time [ns]')

        ax[9].plot(waves.wave[i].freq, numpy.abs(waves.wave[i].ampl),'--', color=color[i], alpha=0.5)
        ax[9].set_xlabel('Freq [GHz]')
        ax[9].set_xlim([0,0.74])

        ax[9].set_ylabel('|FFT|')
        ax[9].grid(True)

    #flab=filename.split('/')
    #flab=flab[-1].split('.')
    #plt.figtext(0.55, 0.08, 'NuPhase EVENT: ' + str(int(flab[0])-1+event), fontsize=16)

def handle_signal(signum, frame):
    global time_to_stop
    print "Caught deadly signal %d..." % (signum)
    time_to_stop = True

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)  
    
if __name__=="__main__":
    import nuphaseroot
    
    global time_to_stop
    time_to_stop = False

    if len(sys.argv) < 3:
        print "need two or three arguments: run, entry, [entry stop]"
        print "USAGE 1: plot a single event: two arguments: [run, event]"
        print "USAGE 2: cycle through multiple events: three arguments: [run, event_start, event_end]"
        sys.exit()

    run = sys.argv[1]
    event_no = int(sys.argv[2])

    nproot = nuphaseroot.NUPHASEROOT(run)

    if len(sys.argv) == 3:
        wfms = nproot.getEvents([event_no])[0]


        plotViewer(wfms)
        plt.draw()
        plt.pause(0.001)
        raw_input() 
        plt.clf()
        plt.close()
    

    elif len(sys.argv) == 4:
        event_no_end = int(sys.argv[3])

        wfms = nproot.getEvents(range(event_no, event_no_end+1, 1))

        index = 0
        while not time_to_stop and index < len(wfms):
            plotViewer(wfms[index])
            plt.draw()
            #plt.pause(0.5)
            plt.pause(0.001)
            raw_input() 
            plt.clf()
            index=index+1

        plt.close()
