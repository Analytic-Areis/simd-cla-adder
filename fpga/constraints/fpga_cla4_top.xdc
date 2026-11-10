## ==============================================================================
## Vivado constraints for fpga_cla4_top  (registered 4-bit CLA, Part I)
## Board: Real Digital Boolean Board, Xilinx Spartan-7 xc7s50csga324-1
## Pins are copied from the reference project in ../reference_constraints/.
## Every port of fpga_cla4_top is constrained here, including inputs the design ignores.
## ==============================================================================

set_property BITSTREAM.CONFIG.UNUSEDPIN Pullnone [current_design]

## ------------------------------------------------------------------------------
## 1. 100 MHz system clock
## ------------------------------------------------------------------------------
set_property -dict { PACKAGE_PIN F14 IOSTANDARD LVCMOS33 } [get_ports { clk }]                  ; # 100 MHz oscillator
create_clock -period 10.000 -name sys_clk_pin -waveform {0.000 5.000} -add [get_ports clk]

## ------------------------------------------------------------------------------
## 2. Slide switches SW0 to SW15
## ------------------------------------------------------------------------------
set_property -dict { PACKAGE_PIN V2  IOSTANDARD LVCMOS33 } [get_ports { sw[0] }]                ; # SW0: A[0]
set_property -dict { PACKAGE_PIN U2  IOSTANDARD LVCMOS33 } [get_ports { sw[1] }]                ; # SW1: A[1]
set_property -dict { PACKAGE_PIN U1  IOSTANDARD LVCMOS33 } [get_ports { sw[2] }]                ; # SW2: A[2]
set_property -dict { PACKAGE_PIN T2  IOSTANDARD LVCMOS33 } [get_ports { sw[3] }]                ; # SW3: A[3]
set_property -dict { PACKAGE_PIN T1  IOSTANDARD LVCMOS33 } [get_ports { sw[4] }]                ; # SW4: not used (gap)
set_property -dict { PACKAGE_PIN R2  IOSTANDARD LVCMOS33 } [get_ports { sw[5] }]                ; # SW5: B[0]
set_property -dict { PACKAGE_PIN R1  IOSTANDARD LVCMOS33 } [get_ports { sw[6] }]                ; # SW6: B[1]
set_property -dict { PACKAGE_PIN P2  IOSTANDARD LVCMOS33 } [get_ports { sw[7] }]                ; # SW7: B[2]
set_property -dict { PACKAGE_PIN P1  IOSTANDARD LVCMOS33 } [get_ports { sw[8] }]                ; # SW8: B[3]
set_property -dict { PACKAGE_PIN N2  IOSTANDARD LVCMOS33 } [get_ports { sw[9] }]                ; # SW9: not used (gap)
set_property -dict { PACKAGE_PIN N1  IOSTANDARD LVCMOS33 } [get_ports { sw[10] }]               ; # SW10: Cin
set_property -dict { PACKAGE_PIN M2  IOSTANDARD LVCMOS33 } [get_ports { sw[11] }]               ; # SW11: not used
set_property -dict { PACKAGE_PIN M1  IOSTANDARD LVCMOS33 } [get_ports { sw[12] }]               ; # SW12: step rate, low bit
set_property -dict { PACKAGE_PIN L1  IOSTANDARD LVCMOS33 } [get_ports { sw[13] }]               ; # SW13: step rate, high bit
set_property -dict { PACKAGE_PIN K2  IOSTANDARD LVCMOS33 } [get_ports { sw[14] }]               ; # SW14: not used
set_property -dict { PACKAGE_PIN K1  IOSTANDARD LVCMOS33 } [get_ports { sw[15] }]               ; # SW15: 0 = manual, 1 = automatic self-test

## ------------------------------------------------------------------------------
## 3. Left 4-digit display D0: A (left two digits) and B (right two digits), decimal
##    Active-low anodes (digit 0 = rightmost) and active-low cathodes
## ------------------------------------------------------------------------------
set_property -dict { PACKAGE_PIN D5  IOSTANDARD LVCMOS33 } [get_ports { d0_a[0] }]              ; # D0 digit 0 anode
set_property -dict { PACKAGE_PIN C4  IOSTANDARD LVCMOS33 } [get_ports { d0_a[1] }]              ; # D0 digit 1 anode
set_property -dict { PACKAGE_PIN C7  IOSTANDARD LVCMOS33 } [get_ports { d0_a[2] }]              ; # D0 digit 2 anode
set_property -dict { PACKAGE_PIN A8  IOSTANDARD LVCMOS33 } [get_ports { d0_a[3] }]              ; # D0 digit 3 anode
set_property -dict { PACKAGE_PIN D7  IOSTANDARD LVCMOS33 } [get_ports { d0_seg[0] }]            ; # D0 segment a
set_property -dict { PACKAGE_PIN C5  IOSTANDARD LVCMOS33 } [get_ports { d0_seg[1] }]            ; # D0 segment b
set_property -dict { PACKAGE_PIN A5  IOSTANDARD LVCMOS33 } [get_ports { d0_seg[2] }]            ; # D0 segment c
set_property -dict { PACKAGE_PIN B7  IOSTANDARD LVCMOS33 } [get_ports { d0_seg[3] }]            ; # D0 segment d
set_property -dict { PACKAGE_PIN A7  IOSTANDARD LVCMOS33 } [get_ports { d0_seg[4] }]            ; # D0 segment e
set_property -dict { PACKAGE_PIN D6  IOSTANDARD LVCMOS33 } [get_ports { d0_seg[5] }]            ; # D0 segment f
set_property -dict { PACKAGE_PIN B5  IOSTANDARD LVCMOS33 } [get_ports { d0_seg[6] }]            ; # D0 segment g
set_property -dict { PACKAGE_PIN A6  IOSTANDARD LVCMOS33 } [get_ports { d0_seg[7] }]            ; # D0 segment decimal point

## ------------------------------------------------------------------------------
## 4. Right 4-digit display D1: S on the right two digits, decimal
## ------------------------------------------------------------------------------
set_property -dict { PACKAGE_PIN H3  IOSTANDARD LVCMOS33 } [get_ports { d1_a[0] }]              ; # D1 digit 0 anode
set_property -dict { PACKAGE_PIN J4  IOSTANDARD LVCMOS33 } [get_ports { d1_a[1] }]              ; # D1 digit 1 anode
set_property -dict { PACKAGE_PIN F3  IOSTANDARD LVCMOS33 } [get_ports { d1_a[2] }]              ; # D1 digit 2 anode
set_property -dict { PACKAGE_PIN E4  IOSTANDARD LVCMOS33 } [get_ports { d1_a[3] }]              ; # D1 digit 3 anode
set_property -dict { PACKAGE_PIN F4  IOSTANDARD LVCMOS33 } [get_ports { d1_seg[0] }]            ; # D1 segment a
set_property -dict { PACKAGE_PIN J3  IOSTANDARD LVCMOS33 } [get_ports { d1_seg[1] }]            ; # D1 segment b
set_property -dict { PACKAGE_PIN D2  IOSTANDARD LVCMOS33 } [get_ports { d1_seg[2] }]            ; # D1 segment c
set_property -dict { PACKAGE_PIN C2  IOSTANDARD LVCMOS33 } [get_ports { d1_seg[3] }]            ; # D1 segment d
set_property -dict { PACKAGE_PIN B1  IOSTANDARD LVCMOS33 } [get_ports { d1_seg[4] }]            ; # D1 segment e
set_property -dict { PACKAGE_PIN H4  IOSTANDARD LVCMOS33 } [get_ports { d1_seg[5] }]            ; # D1 segment f
set_property -dict { PACKAGE_PIN D1  IOSTANDARD LVCMOS33 } [get_ports { d1_seg[6] }]            ; # D1 segment g
set_property -dict { PACKAGE_PIN C1  IOSTANDARD LVCMOS33 } [get_ports { d1_seg[7] }]            ; # D1 segment decimal point

## ------------------------------------------------------------------------------
## 5. LEDs. LED7 to LED11 are not used: the reference gives no pins for them
## ------------------------------------------------------------------------------
set_property -dict { PACKAGE_PIN A4  IOSTANDARD LVCMOS33 } [get_ports { led[0] }]               ; # LED0: Cin
set_property -dict { PACKAGE_PIN B4  IOSTANDARD LVCMOS33 } [get_ports { led[1] }]               ; # LED1: off
set_property -dict { PACKAGE_PIN A3  IOSTANDARD LVCMOS33 } [get_ports { led[2] }]               ; # LED2: off
set_property -dict { PACKAGE_PIN B3  IOSTANDARD LVCMOS33 } [get_ports { led[3] }]               ; # LED3: Cout (C4)
set_property -dict { PACKAGE_PIN A2  IOSTANDARD LVCMOS33 } [get_ports { led[4] }]               ; # LED4: off
set_property -dict { PACKAGE_PIN E6  IOSTANDARD LVCMOS33 } [get_ports { led[5] }]               ; # LED5: automatic self-test running
set_property -dict { PACKAGE_PIN C3  IOSTANDARD LVCMOS33 } [get_ports { led[6] }]               ; # LED6: self-test error
set_property -dict { PACKAGE_PIN G1  IOSTANDARD LVCMOS33 } [get_ports { led_hi[0] }]            ; # LED12: self-test phase, low bit
set_property -dict { PACKAGE_PIN G2  IOSTANDARD LVCMOS33 } [get_ports { led_hi[1] }]            ; # LED13: self-test phase, high bit
set_property -dict { PACKAGE_PIN F1  IOSTANDARD LVCMOS33 } [get_ports { led_hi[2] }]            ; # LED14: off
set_property -dict { PACKAGE_PIN F2  IOSTANDARD LVCMOS33 } [get_ports { led_hi[3] }]            ; # LED15: off

## ------------------------------------------------------------------------------
## 6. Oscilloscope probes on the GPIO header (the reference project's SPI pins).
##    Check each pin against the header's printed labels before connecting a probe.
## ------------------------------------------------------------------------------
set_property -dict { PACKAGE_PIN B13 IOSTANDARD LVCMOS33 SLEW FAST DRIVE 12 } [get_ports { probe[0] }]; # step clock
set_property -dict { PACKAGE_PIN E12 IOSTANDARD LVCMOS33 SLEW FAST DRIVE 12 } [get_ports { probe[1] }]; # Cin at the adder input
set_property -dict { PACKAGE_PIN A13 IOSTANDARD LVCMOS33 SLEW FAST DRIVE 12 } [get_ports { probe[2] }]; # S3 at the adder output
set_property -dict { PACKAGE_PIN C14 IOSTANDARD LVCMOS33 SLEW FAST DRIVE 12 } [get_ports { probe[3] }]; # C4 at the adder output
set_property -dict { PACKAGE_PIN A14 IOSTANDARD LVCMOS33 SLEW FAST DRIVE 12 } [get_ports { probe[4] }]; # self-test error flag

## ------------------------------------------------------------------------------
## 7. Timing exceptions: switches are slow asynchronous inputs, and LEDs, displays
##    and probes are observed by eye or by the scope, not by another clocked circuit
## ------------------------------------------------------------------------------
set_false_path -from [get_ports { sw[*] }]
set_false_path -to   [get_ports { led[*] led_hi[*] d0_a[*] d0_seg[*] d1_a[*] d1_seg[*] probe[*] }]
