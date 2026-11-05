`timescale 1ns / 1ps

// Shared board helpers for the Boolean Board tops.

// Power-on reset: high for the first 16 clocks after configuration. The board has no
// reset button in the reference pin list, so the design resets itself.
module power_on_reset (
    input  wire clk,
    output wire rst
);
    reg [15:0] sr = 16'hFFFF;
    always @(posedge clk) sr <= {sr[14:0], 1'b0};
    assign rst = sr[15];
endmodule


// Step-rate generator. speed selects how often the test circuit steps:
//   0: 100 MHz / 2^26 = 1.49 Hz   (watch on LEDs and displays)
//   1: 100 MHz / 2^20 = 95.4 Hz
//   2: 100 MHz / 2^14 = 6.10 kHz
//   3: 100 MHz / 2^7  = 781 kHz   (oscilloscope)
// tick is a one-clock pulse at that rate. tclk is a square wave at the same rate for the scope.
// DIV_SHIFT shortens every divider in simulation.
module step_clock #(parameter DIV_SHIFT = 0) (
    input  wire       clk,
    input  wire       rst,
    input  wire [1:0] speed,
    output reg        tick,
    output wire       tclk
);
    reg [25:0] count;
    always @(posedge clk) begin
        if (rst) count <= 26'd0;
        else     count <= count + 1'b1;
    end

    reg [4:0] bit_sel;
    always @(*) begin
        case (speed)
            2'd0: bit_sel = 5'd25 - DIV_SHIFT;
            2'd1: bit_sel = 5'd19 - DIV_SHIFT;
            2'd2: bit_sel = 5'd13 - DIV_SHIFT;
            default: bit_sel = 5'd6 - (DIV_SHIFT > 5 ? 5 : DIV_SHIFT);
        endcase
    end

    // tick on every rising edge of the selected counter bit
    reg prev;
    assign tclk = count[bit_sel];
    always @(posedge clk) begin
        if (rst) begin
            prev <= 1'b0;
            tick <= 1'b0;
        end else begin
            prev <= tclk;
            tick <= tclk & ~prev;
        end
    end
endmodule


// 16-bit Galois LFSR, x^16 + x^14 + x^13 + x^11 + 1, for pseudo-random test vectors.
module lfsr16 (
    input  wire        clk,
    input  wire        rst,
    input  wire        en,
    output reg  [15:0] q
);
    always @(posedge clk) begin
        if (rst)     q <= 16'hACE1;
        else if (en) q <= {1'b0, q[15:1]} ^ (q[0] ? 16'hB400 : 16'h0000);
    end
endmodule


// Two 4-digit hex displays, time-multiplexed, active-low, as in the reference wrapper.
// d0 shows left_val, d1 shows right_val. seg[7] is the decimal point, kept off.
// blank_l / blank_r turn off individual digits (bit 3 = leftmost).
module hex_display2x4 (
    input  wire        clk,
    input  wire        rst,
    input  wire [15:0] left_val,
    input  wire [15:0] right_val,
    input  wire [3:0]  blank_l,
    input  wire [3:0]  blank_r,
    output reg  [3:0]  d0_a,
    output reg  [7:0]  d0_seg,
    output reg  [3:0]  d1_a,
    output reg  [7:0]  d1_seg
);
    reg [17:0] refresh;
    always @(posedge clk) begin
        if (rst) refresh <= 18'd0;
        else     refresh <= refresh + 1'b1;
    end
    wire [1:0] digit = refresh[16:15];   // about 763 Hz per digit

    function [6:0] hex_to_7seg;
        input [3:0] nibble;
        begin
            case (nibble)
                4'h0: hex_to_7seg = 7'b1000000;
                4'h1: hex_to_7seg = 7'b1111001;
                4'h2: hex_to_7seg = 7'b0100100;
                4'h3: hex_to_7seg = 7'b0110000;
                4'h4: hex_to_7seg = 7'b0011001;
                4'h5: hex_to_7seg = 7'b0010010;
                4'h6: hex_to_7seg = 7'b0000010;
                4'h7: hex_to_7seg = 7'b1111000;
                4'h8: hex_to_7seg = 7'b0000000;
                4'h9: hex_to_7seg = 7'b0010000;
                4'hA: hex_to_7seg = 7'b0001000;
                4'hB: hex_to_7seg = 7'b0000011;
                4'hC: hex_to_7seg = 7'b1000110;
                4'hD: hex_to_7seg = 7'b0100001;
                4'hE: hex_to_7seg = 7'b0000110;
                4'hF: hex_to_7seg = 7'b0001110;
                default: hex_to_7seg = 7'b1111111;
            endcase
        end
    endfunction

    reg [3:0] nib_l, nib_r;
    reg [3:0] anode;
    reg       off_l, off_r;
    always @(*) begin
        case (digit)
            2'd0: begin anode = 4'b1110; nib_l = left_val[3:0];   nib_r = right_val[3:0];   off_l = blank_l[0]; off_r = blank_r[0]; end
            2'd1: begin anode = 4'b1101; nib_l = left_val[7:4];   nib_r = right_val[7:4];   off_l = blank_l[1]; off_r = blank_r[1]; end
            2'd2: begin anode = 4'b1011; nib_l = left_val[11:8];  nib_r = right_val[11:8];  off_l = blank_l[2]; off_r = blank_r[2]; end
            default: begin anode = 4'b0111; nib_l = left_val[15:12]; nib_r = right_val[15:12]; off_l = blank_l[3]; off_r = blank_r[3]; end
        endcase
        d0_a   = off_l ? 4'b1111 : anode;
        d1_a   = off_r ? 4'b1111 : anode;
        d0_seg = {1'b1, hex_to_7seg(nib_l)};
        d1_seg = {1'b1, hex_to_7seg(nib_r)};
    end
endmodule
