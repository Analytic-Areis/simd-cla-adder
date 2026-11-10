`timescale 1ns / 1ps

// Testbench for the two Boolean Board tops, with the step dividers shortened.
//   TEST 1: CLA4 board, automatic self-test through all four phases: error flag must stay low
//   TEST 2: CLA4 board, manual switches: 7 + 1 + 1
//   TEST 3: SIMD8 board, automatic self-test through all four phases
//   TEST 4: SIMD8 board, manual entry of A and B with sw[14], both modes
//   TEST 5: self-check catches a fault: the expected value is corrupted on purpose
// Waveform: sim/tb_fpga_tops.vcd
module tb_fpga_tops;

    reg clk = 0;
    always #5 clk = ~clk;   // 100 MHz

    reg  [15:0] sw_c, sw_m;
    wire [6:0]  led_c, led_m;
    wire [3:0]  hi_c, hi_m;
    wire [4:0]  probe_c, probe_m;

    // DIV_SHIFT = 5 makes the fastest rate one step every 4 clocks
    fpga_cla4_top  #(.DIV_SHIFT(5)) board_c (.clk(clk), .sw(sw_c), .d0_a(), .d0_seg(), .d1_a(), .d1_seg(),
                                             .led(led_c), .led_hi(hi_c), .probe(probe_c));
    fpga_simd8_top #(.DIV_SHIFT(5)) board_m (.clk(clk), .sw(sw_m), .d0_a(), .d0_seg(), .d1_a(), .d1_seg(),
                                             .led(led_m), .led_hi(hi_m), .probe(probe_m));

    integer errors = 0;
    reg [3:0] phases_c, phases_m;

    always @(posedge clk) begin
        if (sw_c[15]) phases_c = phases_c | (4'b1 << board_c.phase);
        if (sw_m[15]) phases_m = phases_m | (4'b1 << board_m.phase);
    end

    task expect;
        input [255:0] label;
        input [15:0]  got, want;
        begin
            if (got !== want) begin
                errors = errors + 1;
                $display("  FAIL %0s: got %h, expected %h", label, got, want);
            end else
                $display("  ok   %0s: %h", label, got);
        end
    endtask

    initial begin
        $dumpfile("tb_fpga_tops.vcd");
        $dumpvars(1, tb_fpga_tops);
        $dumpvars(1, board_c.dut);
        $dumpvars(1, board_m.dut);
        phases_c = 0; phases_m = 0;
        sw_c = 16'h0000; sw_m = 16'h0000;
        repeat (40) @(posedge clk);

        $display("\n--- TEST 1: CLA4 board, automatic self-test ---");
        sw_c = 16'b1011_0000_0000_0000;            // auto, fastest rate
        wait (board_c.step == 11'd2047);
        repeat (20) @(posedge clk);
        expect("phases visited (1111)", phases_c, 4'b1111);
        expect("error LED6 stays off", led_c[6], 1'b0);
        sw_c = 16'b0011_0000_0000_0000;            // manual

        $display("\n--- TEST 2: CLA4 board, manual: A on sw[3:0], B on sw[8:5], Cin on sw[10] ---");
        sw_c = 16'b0011_0100_0010_0111;            // Cin=1, B=1, A=7
        repeat (40) @(posedge clk);
        expect("7 + 1 + 1: registered {C4,S} = 9", {board_c.q_cout, board_c.q_s}, 5'd9);
        expect("left display A=07 B=01", board_c.disp.left_val, 16'h0701);
        expect("right display S=09", board_c.disp.right_val, 16'h0009);
        expect("LED0 Cin on", led_c[0], 1'b1);
        expect("LED3 Cout off", led_c[3], 1'b0);
        sw_c = 16'b0011_1011_1111_1111;            // unused sw[4], sw[9] set, Cin=0, B=15, A=15
        repeat (40) @(posedge clk);
        expect("15 + 15: registered {C4,S} = 30", {board_c.q_cout, board_c.q_s}, 5'd30);
        expect("left display A=15 B=15", board_c.disp.left_val, 16'h1515);
        expect("right display S=14", board_c.disp.right_val, 16'h0014);
        expect("LED0 Cin off", led_c[0], 1'b0);
        expect("LED3 Cout on", led_c[3], 1'b1);

        $display("\n--- TEST 3: SIMD8 board, automatic self-test ---");
        sw_m = 16'b1011_0000_0000_0000;
        wait (board_m.step == 10'd1023);
        repeat (20) @(posedge clk);
        expect("phases visited (1111)", phases_m, 4'b1111);
        expect("error LED6 stays off", led_m[6], 1'b0);
        sw_m = 16'b0011_0000_0000_0000;

        $display("\n--- TEST 4: SIMD8 board, manual A=0x37, B=0x59, Cin=1 ---");
        sw_m = 16'b0011_0000_0011_0111;            // sw14=0: A = 0x37
        repeat (5) @(posedge clk);
        sw_m = 16'b0111_0001_0101_1001;            // sw14=1: B = 0x59, Cin=1, mode 0
        repeat (40) @(posedge clk);
        expect("8-bit: {Cout,S} = 0x091", {board_m.q_cout, board_m.q_s}, 9'h091);
        sw_m = 16'b0111_0011_0101_1001;            // mode 1
        repeat (40) @(posedge clk);
        expect("dual: {Cout,CoutLo,S} = 0x181", {board_m.q_cout, board_m.q_cout_lo, board_m.q_s}, 10'h181);
        expect("gated carry LED3 off", led_m[3], 1'b0);

        $display("\n--- TEST 5: self-check catches a fault ---");
        sw_m = 16'b1011_0000_0000_0000;
        repeat (60) @(posedge clk);
        force board_m.expect_q = 10'h3FF;
        repeat (20) @(posedge clk);
        release board_m.expect_q;
        expect("error LED6 lights", led_m[6], 1'b1);
        sw_m = 16'b0011_0000_0000_0000;
        repeat (5) @(posedge clk);
        expect("error clears in manual mode", led_m[6], 1'b0);

        $display("\n--- RESULT: %0d errors: %0s ---", errors, errors ? "FAIL" : "PASS");
        $finish;
    end

endmodule
