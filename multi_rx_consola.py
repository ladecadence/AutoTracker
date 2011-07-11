#!/usr/bin/env python
# -*- coding: utf-8 -*-

##################################################
# Gnuradio Automatic satellite tracker
# Title: Auto-RX
# Author: EA1IDZ
# Description: Automatic tracker using the Funcube Dongle
# Generated: Tue Jul  5 14:12:25 2011
##################################################

# This code is Free Software released under the GNU/GPL License.
# See LICENSE for information.

from gnuradio import audio
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import blks2
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from optparse import OptionParser
import fcd
from liblo import *
import threading
import curses
import time
import atexit


# satellite and frequency list
sat_data = [
	#{'name':'AO-7', 'freq':145977500, 'mode':'cw'},
	{'name':'AO-7', 'freq':435106000, 'mode':'cw'},
	{'name':'AO-27', 'freq':436795000, 'mode':'fm'},
	{'name':'CO-55', 'freq':436837500, 'mode':'cw'},
	{'name':'CO-58', 'freq':437425000, 'mode':'cw'},
	{'name':'CO-57', 'freq':436847500, 'mode':'cw'},
	{'name':'COMPASS-1', 'freq':435790000, 'mode':'cw'},
        {'name':'HO-68', 'freq':437275000, 'mode':'cw'},
        {'name':'VO-52', 'freq':145936000, 'mode':'cw'},
        {'name':'SEEDS_II_(CO-66)', 'freq':437485000, 'mode':'cw'},
        {'name':'DELFI-C3_(DO-64)', 'freq':145870000, 'mode':'cw'},
	{'name':'SO-67', 'freq':435300000, 'mode':'fm'},
	{'name':'UWE-2', 'freq':437385000, 'mode':'fm'},
        {'name':'SO-50', 'freq':436795000, 'mode':'fm'},
	{'name':'SWISSCUBE', 'freq':437505000, 'mode':'cw'},
	{'name':'ITUPSAT_1', 'freq':437325000, 'mode':'cw'},
	{'name':'BEESAT', 'freq':436000000, 'mode':'cw'},
	{'name':'FO-29', 'freq':435795000, 'mode':'cw'},
	{'name':'ISS', 'freq':145825000, 'mode':'cw'},
	{'name':'PRISM', 'freq':437250000, 'mode':'cw'},
	{'name':'AAU_CUBESAT', 'freq':437900000, 'mode':'cw'},
	{'name':'STARS', 'freq':437305000, 'mode':'cw'},
	{'name':'KKS-1', 'freq':437385000, 'mode':'cw'},
	{'name':'CUTE-1.7+APD_II_(CO-65)', 'freq':437275000, 'mode':'cw'},
]


# fm receiver, created using gnuradio-companion
class fm_rx(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "FM Receiver")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 96000
		self.xlate_filter_taps = xlate_filter_taps = firdes.low_pass(1, samp_rate, 48000, 5000, firdes.WIN_HAMMING, 6.76)
		self.sql_lev = sql_lev = -100
		self.rf_gain = rf_gain = 20
		self.freq = freq = 144800000
		self.af_gain = af_gain = 2

		##################################################
		# Blocks
		##################################################
		self.xlating_fir_filter = gr.freq_xlating_fir_filter_ccc(1, (xlate_filter_taps), 0, samp_rate)
		self.nbfm_normal = blks2.nbfm_rx(
			audio_rate=48000,
			quad_rate=96000,
			tau=75e-6,
			max_dev=5e3,
		)
		self.low_pass_filter = gr.fir_filter_ccf(1, firdes.low_pass(
			1, samp_rate, 12500, 1500, firdes.WIN_HAMMING, 6.76))
		self.gr_simple_squelch_cc_0 = gr.simple_squelch_cc(sql_lev, 1)
		self.gr_multiply_const_vxx_1 = gr.multiply_const_vff((af_gain, ))
		self.fcd_source_c_1 = fcd.source_c("hw:1")
		self.fcd_source_c_1.set_freq(freq)
		self.fcd_source_c_1.set_freq_corr(-32)
		    
		self.audio_sink = audio.sink(48000, "", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.xlating_fir_filter, 0), (self.low_pass_filter, 0))
		self.connect((self.low_pass_filter, 0), (self.gr_simple_squelch_cc_0, 0))
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.audio_sink, 1))
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.audio_sink, 0))
		self.connect((self.gr_simple_squelch_cc_0, 0), (self.nbfm_normal, 0))
		self.connect((self.nbfm_normal, 0), (self.gr_multiply_const_vxx_1, 0))
		self.connect((self.fcd_source_c_1, 0), (self.xlating_fir_filter, 0))

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.set_xlate_filter_taps(firdes.low_pass(1, self.samp_rate, 48000, 5000, firdes.WIN_HAMMING, 6.76))
		self.low_pass_filter.set_taps(firdes.low_pass(1, self.samp_rate, 12500, 1500, firdes.WIN_HAMMING, 6.76))

	def get_xlate_filter_taps(self):
		return self.xlate_filter_taps

	def set_xlate_filter_taps(self, xlate_filter_taps):
		self.xlate_filter_taps = xlate_filter_taps
		self.xlating_fir_filter.set_taps((self.xlate_filter_taps))

	def get_sql_lev(self):
		return self.sql_lev

	def set_sql_lev(self, sql_lev):
		self.sql_lev = sql_lev
		self.gr_simple_squelch_cc_0.set_threshold(self.sql_lev)

	def get_rf_gain(self):
		return self.rf_gain

	def set_rf_gain(self, rf_gain):
		self.rf_gain = rf_gain
		self.fcd_source_c_1.set_lna_gain(self.rf_gain)

	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq
		self.fcd_source_c_1.set_freq(self.freq)

	def get_af_gain(self):
		return self.af_gain

	def set_af_gain(self, af_gain):
		self.af_gain = af_gain
		self.gr_multiply_const_vxx_1.set_k((self.af_gain, ))

# cw / ssb receiver (just change bandpass filter values), created using gnuradio-companion
class cw_rx(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self, "CW/SSB Receiver")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 96000
		self.xlate_filter_taps = xlate_filter_taps = firdes.low_pass(1, samp_rate, 48000, 5000, firdes.WIN_HAMMING, 6.76)
		self.sql_lev = sql_lev = -100
		self.rf_gain = rf_gain = 20
		self.pass_trans = pass_trans = 600
		self.pass_low = pass_low = 300
		self.pass_high = pass_high = 1200
		self.freq = freq = 144800000
		self.af_gain = af_gain = 5

		##################################################
		# Blocks
		##################################################
		self.xlating_fir_filter = gr.freq_xlating_fir_filter_ccc(1, (xlate_filter_taps), 0, samp_rate)
		self.gr_simple_squelch_cc_0 = gr.simple_squelch_cc(sql_lev, 1)
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vff((af_gain, ))
		self.gr_complex_to_real_0 = gr.complex_to_real(1)
		self.gr_agc2_xx_0 = gr.agc2_cc(1e-1, 20.8e-6, 0.3, 1.0, 0.0)
		self.fcd_source_c_1 = fcd.source_c("hw:1")
		self.fcd_source_c_1.set_freq(freq)
		self.fcd_source_c_1.set_freq_corr(-10)
		    
		self.band_pass_filter_0 = gr.fir_filter_ccf(2, firdes.band_pass(
			1, samp_rate, pass_low, pass_high, pass_trans, firdes.WIN_HAMMING, 6.76))
		self.audio_sink = audio.sink(48000, "", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.fcd_source_c_1, 0), (self.xlating_fir_filter, 0))
		self.connect((self.xlating_fir_filter, 0), (self.gr_simple_squelch_cc_0, 0))
		self.connect((self.band_pass_filter_0, 0), (self.gr_agc2_xx_0, 0))
		self.connect((self.gr_complex_to_real_0, 0), (self.gr_multiply_const_vxx_0, 0))
		self.connect((self.gr_agc2_xx_0, 0), (self.gr_complex_to_real_0, 0))
		self.connect((self.gr_simple_squelch_cc_0, 0), (self.band_pass_filter_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.audio_sink, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.audio_sink, 1))

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.set_xlate_filter_taps(firdes.low_pass(1, self.samp_rate, 48000, 5000, firdes.WIN_HAMMING, 6.76))
		self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, self.pass_low, self.pass_high, self.pass_trans, firdes.WIN_HAMMING, 6.76))

	def get_xlate_filter_taps(self):
		return self.xlate_filter_taps

	def set_xlate_filter_taps(self, xlate_filter_taps):
		self.xlate_filter_taps = xlate_filter_taps
		self.xlating_fir_filter.set_taps((self.xlate_filter_taps))

	def get_sql_lev(self):
		return self.sql_lev

	def set_sql_lev(self, sql_lev):
		self.sql_lev = sql_lev
		self.gr_simple_squelch_cc_0.set_threshold(self.sql_lev)

	def get_rf_gain(self):
		return self.rf_gain

	def set_rf_gain(self, rf_gain):
		self.rf_gain = rf_gain
		self.fcd_source_c_1.set_lna_gain(self.rf_gain)

	def get_pass_trans(self):
		return self.pass_trans

	def set_pass_trans(self, pass_trans):
		self.pass_trans = pass_trans
		self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, self.pass_low, self.pass_high, self.pass_trans, firdes.WIN_HAMMING, 6.76))

	def get_pass_low(self):
		return self.pass_low

	def set_pass_low(self, pass_low):
		self.pass_low = pass_low
		self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, self.pass_low, self.pass_high, self.pass_trans, firdes.WIN_HAMMING, 6.76))

	def get_pass_high(self):
		return self.pass_high

	def set_pass_high(self, pass_high):
		self.pass_high = pass_high
		self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, self.pass_low, self.pass_high, self.pass_trans, firdes.WIN_HAMMING, 6.76))

	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq
		self.fcd_source_c_1.set_freq(self.freq)

	def get_af_gain(self):
		return self.af_gain

	def set_af_gain(self, af_gain):
		self.af_gain = af_gain
		self.gr_multiply_const_vxx_0.set_k((self.af_gain, ))


# Automatic tracker, uses liblo and gnuradio objects
class multi_recv(ServerThread):
	tracking = False 	# not traking any sat
	tracked = "" 		# name of tracked sat
	fr = 0 			# tx frequency
	fr_rx = 0		# rx requency
	mode = 'cw'		# mode
	rx = None		# receiver
	stdscr = None		# main window
	title_win = None	# title
	trk_win = None		# tracking window
	freq_win = None		# frequency window
		
	# creates objects and windows
	def __init__(self):
        	ServerThread.__init__(self, 7770)
		self.stdscr = curses.initscr()
		curses.noecho()
		curses.cbreak()
		curses.curs_set(0)
		self.stdscr.keypad(1)
		self.trk_win = curses.newwin(10, 40, 5, 1)
		self.freq_win = curses.newwin(9, 30,5,45)
		self.title_win = curses.newwin(4,80,1,1)
		self.trk_win.box(0,0)
		self.freq_win.box(0,0)		
		#self.trk_win.leaveok(1)
		#self.freq_win.leaveok(1)
		curses.start_color()
		curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		

	def draw_base(self):
		# draws windows and basic texts
		self.title_win.box(0,0)
		self.title_win.addstr(1,1, "Automatic Satellite Radio Tracker", curses.color_pair(1))
		self.title_win.addstr(2,1, "David Pello 2011 - PlataformaCero")
		self.freq_win.box(0,0)
                self.freq_win.addstr(1,1, "FRECUENCIA", curses.color_pair(2))
                self.freq_win.addstr(2,1, "----------")
		self.trk_win.box(0,0)
                self.trk_win.addstr(1,1, "SATELITE", curses.color_pair(3))
                self.trk_win.addstr(2,1, "--------")
		
		self.trk_win.refresh()
		self.freq_win.refresh()
		self.title_win.refresh()
	
	# starts OSC server and satellite tracking
	def go(self):
		self.start()
		self.draw_base()
		self.trk_win.addstr(4,1, "Esperando al siguiente satélite...", curses.A_BOLD)
		self.trk_win.refresh()
	
	# creates callback for OSC message with five floats and a string
    	@make_method(None, 'fffffs')
    	def sat_callback(self, path, args):
        	a, e, h, s, d, idesg = args

		#get name
		name = path.split("/")[len(path.split("/")) -1]	
	
		# need to track it?
		if float(e) >=0 and (self.tracking==False):
			self.tracking = True
			self.tracked = name
			# search data
			for i in sat_data:
				if i['name'] == name:
					self.fr = i['freq']
					self.mode = i['mode']
			self.freq_win.erase()
			self.freq_win.addstr(3,1, "Frecuencia TX: " + str(self.fr)+" Hz")
			self.freq_win.addstr(4,1, "Doppler: " + str(int(d))+" Hz")
			self.freq_win.addstr(5,1, "Frecuencia RX:" + str(self.fr+int(d))+" Hz")
			self.freq_win.addstr(6,1, "Modo: "+self.mode)
			
			# select rx mode
			if self.mode == 'cw': # FIXME
				self.rx = cw_rx()
			if self.mode == 'fm':
				self.rx = fm_rx()
			
			# start receiver
			d = (d * self.fr) / 100000000 # calculate real Doppler (we get doppler @ 100MHz)
			self.fr_rx = self.fr + (int(d/10)*10)
			self.rx.set_freq(self.fr_rx)
			self.rx.start()
			
			self.stdscr.erase()
			self.stdscr.refresh()
			
			self.trk_win.erase()
			self.trk_win.addstr(3,1, "Escuchando satelite: " + self.tracked)
			self.trk_win.addstr(4,1, "International Designator: " + idesg)
			self.draw_base()

		# need update?
		if self.tracking and name == self.tracked:
			d = (d * self.fr) / 100000000 # calculate real Doppler (we get doppler @ 100MHz)
			self.freq_win.erase()
			self.freq_win.addstr(3,1, "Frecuencia TX: " + str(self.fr) + " Hz")
			self.freq_win.addstr(4,1, "Doppler:" + str(int(d)) + " Hz")
			self.freq_win.addstr(5,1, "Frecuencia RX: " + str(self.fr_rx) + " Hz")
                        self.freq_win.addstr(6,1, "Modo: "+self.mode)
			
			# Update frequency, just in 10Hz jumps
			if abs((self.fr_rx+d)-(self.fr-d)) >= 10:
				self.fr_rx = self.fr+(int(d/10)*10)
				self.rx.set_freq(self.fr_rx)

			self.trk_win.erase()
			self.trk_win.addstr(3,1, "Escuchando satelite: " + self.tracked, curses.A_BOLD)
			self.trk_win.addstr(4,1, "International Designator: " + idesg)
			self.trk_win.addstr(5,1, "Altitud: " + "%.3f" % h + " Km")
			self.trk_win.addstr(6,1, "Velocidad: " + "%.3f" % s + " Km/s.")
			self.trk_win.addstr(7,1, "Azimuth: " + "%3d" % int(a) + " º")
			self.trk_win.addstr(8,1, "Elevacion: " + "%3d" % int(e) + " º")
			self.draw_base()
	
		# finish tracking?	
		if self.tracking and name == self.tracked and float(e)<0:
			# stop receiver
			self.tracking = False
			self.rx.stop()
			del self.rx
			# update windows 
			self.trk_win.erase()
			self.trk_win.addstr(3,1, "Fin del paso de: " + self.tracked)
			self.trk_win.addstr(5,1, "Esperando al siguiente satélite...", curses.A_BOLD)
			self.draw_base()
			#pause for gnuradio to stop
			time.sleep(1)

	# bad OSC message
    	@make_method(None, None)
    	def fallback(self, path, args):
        	self.stdscr.addstr(20,1, "received unknown message: " + path)
		self.stdscr.refresh()
# closes curses
def clear():
	curses.nocbreak()
	recv.stdscr.keypad(0)
	curses.echo()
	curses.endwin()

################
##### MAIN #####
################
if __name__ == '__main__':
	atexit.register(clear)
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	recv = multi_recv()
	recv.go()
	
	#end curses
	clear()


