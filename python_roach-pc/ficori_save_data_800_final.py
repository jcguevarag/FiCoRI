#!/usr/bin/env python
'''
This script save data for the First Colombian Radio Interferometer and it is based on the script use for CASPER workshop Tutorial 4 written by Jason Manley, August 2009
\n\n 
Author: Juan C. Guevara Gomez, January 2016.
'''

#TODO: add support for coarse delay change
#TODO: add support for ADC histogram plotting.
#TODO: add support for determining ADC input level 
from __future__ import print_function
import corr,time,numpy,struct,sys,logging,pylab
import datetime
from datetime import timedelta


katcp_port=7147
UTadd=timedelta(hours=5)
def exit_fail():
    print('FAILURE DETECTED. Log entries:\n',lh.printMessages())
    try:
        fpga.stop()
    except: pass
    raise
    exit()

def exit_clean():
    try:
        fpga.stop()
    except: pass
    exit()

def get_data(baseline):

    #acc_n = fpga.read_uint('acc_num')
    #print('Grabbing integration number %i'%acc_n)
    #get the data...   
    a_0=struct.unpack('>256l',fpga.read('dir_x0_aa_real',1024,0))
    a_1=struct.unpack('>256l',fpga.read('dir_x1_aa_real',1024,0))
    a_2=struct.unpack('>256l',fpga.read('dir_x2_aa_real',1024,0))
    a_3=struct.unpack('>256l',fpga.read('dir_x3_aa_real',1024,0))
    b_0=struct.unpack('>256l',fpga.read('dir_x0_bb_real',1024,0))
    b_1=struct.unpack('>256l',fpga.read('dir_x1_bb_real',1024,0))
    b_2=struct.unpack('>256l',fpga.read('dir_x2_bb_real',1024,0))
    b_3=struct.unpack('>256l',fpga.read('dir_x3_bb_real',1024,0))

    x0_i=struct.unpack('>256l',fpga.read('dir_x0_%s_imag'%baseline,1024,0))
    x0_r=struct.unpack('>256l',fpga.read('dir_x0_%s_real'%baseline,1024,0))
    x1_i=struct.unpack('>256l',fpga.read('dir_x1_%s_imag'%baseline,1024,0))
    x1_r=struct.unpack('>256l',fpga.read('dir_x1_%s_real'%baseline,1024,0))
    x2_i=struct.unpack('>256l',fpga.read('dir_x2_%s_imag'%baseline,1024,0))
    x2_r=struct.unpack('>256l',fpga.read('dir_x2_%s_real'%baseline,1024,0))
    x3_i=struct.unpack('>256l',fpga.read('dir_x3_%s_imag'%baseline,1024,0))
    x3_r=struct.unpack('>256l',fpga.read('dir_x3_%s_real'%baseline,1024,0))

    cross_corr=[]
    auto_corr_a=[]
    auto_corr_b=[]

    for i in range(256):
        cross_corr.append(complex(x0_i[i], x0_r[i]))
        cross_corr.append(complex(x1_i[i], x1_r[i]))
        cross_corr.append(complex(x2_i[i], x2_r[i]))
        cross_corr.append(complex(x3_i[i], x3_r[i]))
        auto_corr_a.append(a_0[i])
        auto_corr_a.append(a_1[i])
        auto_corr_a.append(a_2[i])
        auto_corr_a.append(a_3[i])
        auto_corr_b.append(b_0[i])
        auto_corr_b.append(b_1[i])
        auto_corr_b.append(b_2[i])
        auto_corr_b.append(b_3[i])

    #alpha=numpy.average(auto_corr_b)-numpy.average(auto_corr_a)
    #auto_corr_a=auto_corr_a+alpha    

    return auto_corr_a,auto_corr_b,cross_corr



#START OF MAIN:

if __name__ == '__main__':
    from optparse import OptionParser

    p = OptionParser()
    p.set_usage('correlator_plot_cross.py <ROACH_HOSTNAME_or_IP> [options]')
    p.set_description(__doc__)
    p.add_option('-c', '--cross', dest='cross', type='str',default='ab',
        help='Plot this cross correlation magnitude and phase. default: ab')
    p.add_option('-C','--channel',dest='ch',action='store_true',
        help='Set plot with channel number or frequency.')
    p.add_option('-f','--frequency',dest='fr',type='float',default=800.0,
        help='Set plot max frequency.(If -c sets to False)')
    opts, args = p.parse_args(sys.argv[1:])

    if args==[]:
        print('Please specify a ROACH board. \nExiting.')
        exit()
    else:
        roach = args[0]

    if opts.ch !=None:
        ifch = opts.ch
    else:
        ifch = False

    if ifch == False:
        if opts.fr != '':
            maxfr = opts.fr
        else:
            maxfr = 800.0
        xaxis = numpy.arange(0.0, maxfr, maxfr*1./1024)

    baseline=opts.cross

try:
    loggers = []
    lh=corr.log_handlers.DebugLogHandler()
    logger = logging.getLogger(roach)
    logger.addHandler(lh)
    logger.setLevel(10)

    print('Connecting to server %s on port %i... '%(roach,katcp_port))
    fpga = corr.katcp_wrapper.FpgaClient(roach, katcp_port, timeout=10,logger=logger)
    time.sleep(1)

    if fpga.is_connected():
        print('ok\n')
    else:
        print('ERROR connecting to server %s on port %i.\n'%(roach,katcp_port))
        exit_fail()


    # set up the figure with a subplot for each polarisation to be plotted
    #fig = matplotlib.pyplot.figure()
    #ax = fig.add_subplot(2,1,1)

    # start the process
    #fig.canvas.manager.window.after(100, drawDataCallback,baseline)
    #drawDataCallback(baseline)
    print('Creating files with data')
    print('Clock FPGA',fpga.est_brd_clk())
    #acc_n = fpga.read_uint('acc_num')
    counter=fpga.read_uint('acc_num')
    time_init=datetime.datetime.now()
    dma_start = datetime.datetime(time_init.year,time_init.month,time_init.day,time_init.hour,time_init.minute,0)
    
    fab = open('/home/juan/Documentos/Ficori/Data_v2/Data_Cross_phase_Ant_AB_%s.dat'%(datetime.datetime.now()).strftime('%Y%m%d-%H:%M'),'w')
    fa = open('/home/juan/Documentos/Ficori/Data_v2/Data_Auto_Ant_A_%s.dat'%(datetime.datetime.now()).strftime('%Y%m%d-%H:%M'),'w')
    fb = open('/home/juan/Documentos/Ficori/Data_v2/Data_Auto_Ant_B_%s.dat'%(datetime.datetime.now()).strftime('%Y%m%d-%H:%M'),'w')
    
    DT = timedelta(minutes=5)
    while counter > 0:
		time_init=datetime.datetime.now()
		dma_start = datetime.datetime(time_init.year,time_init.month,time_init.day,time_init.hour,time_init.minute,0) 
		if dma_now-dma_start < DT: 
			if fpga.read_uint('acc_num') == counter+1:
				auto_corr_a,auto_corr_b,cross_corr = get_data(baseline)
				print(str(datetime.datetime.now()+UTadd),*auto_corr_a,sep=' ',file=fa)
				print(str(datetime.datetime.now()+UTadd),*auto_corr_b,sep=' ',file=fb)
				print(str(datetime.datetime.now()+UTadd),*cross_corr,sep=' ',file=fab)
				counter = counter+1
		else:
			fa.close()
			fb.close()
			fab.close()
			dma_start = dma_now
			fab = open('/home/juan/Documentos/Ficori/Data_v2/Data_Cross_phase_Ant_AB_%s.dat'%(datetime.datetime.now()).strftime('%Y%m%d-%H:%M'),'w')
			fa = open('/home/juan/Documentos/Ficori/Data_v2/Data_Auto_Ant_A_%s.dat'%(datetime.datetime.now()).strftime('%Y%m%d-%H:%M'),'w')
			fb = open('/home/juan/Documentos/Ficori/Data_v2/Data_Auto_Ant_B_%s.dat'%(datetime.datetime.now()).strftime('%Y%m%d-%H:%M'),'w')
		print('Integration number %d'%counter)
    print('Saving complete. Exiting...')
except AttributeError:
    pass
except KeyboardInterrupt:
    exit_clean()
except:
    exit_fail()

exit_clean()

