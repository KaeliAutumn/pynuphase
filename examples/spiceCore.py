import nuphaseroot as nproot
import waveform 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import time
import numpy
import sys
import matplotlib.cm as cm
import nuphase_pulse

RUN = 360
pulse_threshold = .140 #V
channel_to_threshold = 0

nuphase = nproot.NUPHASEROOT()
nuphase.setRun(RUN)
wave = nuphase.getEvents()
header=nuphase.getHeaderData(filtered=False)

plt.plot(header['readout_time'])
plt.figure()
times=[]
hit=[]
all_times = []
for j in xrange(len(wave)):

    all_times.append(header['readout_time'][j])

    pulse = nuphase_pulse.Pulses(wfms=wave[j])
    pulse.convertToVolts()

    if numpy.max(pulse.wave[channel_to_threshold].voltage) > pulse_threshold:
        times.append(header['readout_time'][j])
        hit.append(1)
    else:
        hit.append(0)



all_times_zulu = mdates.epoch2num(numpy.array(all_times))
hit_times = mdates.epoch2num(numpy.array(times))

fig, ax = plt.subplots(1,1)
plt.setp(ax.get_xticklabels(), rotation=30)

#ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%S'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

#ax.xaxis.set_minor_locator(mdates.MinuteLocator())

#plt.plot(all_times_zulu, hit, 'o', ms=4, color='green')
plt.hist(hit_times, bins=100, color='green', alpha=0.7)# normed=True)

#plt.ylim([-1,2])
#plt.grid(True)

#plt.ylim(['01:30':'03:50'])


hi=45
lo=-2
txt=-4
#s="01/08/2018 2:15:00"
s="01/07/2018 20:15:00"
w=['50 m']
q= mdates.epoch2num(time.mktime(datetime.datetime.strptime(s, "%m/%d/%Y %H:%M:%S").timetuple()))
plt.plot([q,q],[lo,hi], '--', c='black', alpha=0.7)
plt.text(q, txt, w[0], rotation=90)
s="01/08/2018 2:28:00"
s="01/07/2018 20:28:00"

w=['200 m']
q=mdates.epoch2num(time.mktime(datetime.datetime.strptime(s, "%m/%d/%Y %H:%M:%S").timetuple()))
plt.plot([q,q],[lo,hi], '--', c='black', alpha=0.7)
plt.text(q, txt, w[0], rotation=90)


s="01/08/2018 2:45:00"
s="01/07/2018 20:45:00"

w=['400 m']
q=mdates.epoch2num(time.mktime(datetime.datetime.strptime(s, "%m/%d/%Y %H:%M:%S").timetuple()))
plt.plot([q,q],[lo,hi], '--', c='black', alpha=0.7)
plt.text(q, txt, w[0], rotation=90)

s="01/08/2018 3:05:00"
s="01/07/2018 21:05:00"

w=['600 m']
q=mdates.epoch2num(time.mktime(datetime.datetime.strptime(s, "%m/%d/%Y %H:%M:%S").timetuple()))
plt.plot([q,q],[lo,hi], '--', c='black', alpha=0.7)
plt.text(q, txt, w[0], rotation=90)

s="01/08/2018 3:22:00"
s="01/07/2018 21:22:00"
w=['800 m']
q= mdates.epoch2num(time.mktime(datetime.datetime.strptime(s, "%m/%d/%Y %H:%M:%S").timetuple()))
plt.plot([q,q],[lo,hi], '--', c='black', alpha=0.7)
plt.text(q, txt, w[0], rotation=90)


s="01/08/2018 3:42:00"
s="01/07/2018 21:42:00"
w=['1000 m']
q= mdates.epoch2num(time.mktime(datetime.datetime.strptime(s, "%m/%d/%Y %H:%M:%S").timetuple()))
plt.plot([q,q],[lo,hi], '--', c='black', alpha=0.7)
plt.text(q, txt, w[0], rotation=90)
#plt.plot('01:30', 02:15:00
#

#s1="01/08/2018 02:15:00"
s1="01/07/2018 19:00:00"
s2="01/07/2018 22:00:00"
q1= mdates.epoch2num(time.mktime(datetime.datetime.strptime(s1, "%m/%d/%Y %H:%M:%S").timetuple()))
q2= mdates.epoch2num(time.mktime(datetime.datetime.strptime(s2, "%m/%d/%Y %H:%M:%S").timetuple()))
#plt.ylim([q1,q2])

#plt.ylabel('Pulse exceeding 4.5$\sigma$ pk2pk amplitude == 1.0')
plt.ylabel('Number of events with signal pk2pk > 4.5$\sigma$')
plt.xlabel('Time Zulu [Hour:minute on 8-Jan 2018]')
plt.title('nuphase preliminary: run '+str(RUN)+' SpiceCore drop')

plt.show()
