`timescale 1ns / 1ps

// Testbench for the registered circuits, cla4_reg and simd8_reg.
//   TEST 1: 2000 random vectors with the clock enable held high: each result must appear
//           one clock after its inputs are captured, as in the Part I timing
//   TEST 2: clock enable pulsed every third clock: outputs must hold between enables
//   TEST 3: hint vector through the registers, both designs, both SIMD modes
// Waveform: sim/tb_registered.vcd
module tb_registered;

    reg clk = 0;
    always #5 clk = ~clk;

    reg        rst, en;
    reg  [7:0] d_a, d_b;
    reg        d_cin, d_mode;

    wire [3:0] c_q_s;
    wire       c_q_cout;
    cla4_reg cla (.clk(clk), .rst(rst), .en(en), .d_a(d_a[3:0]), .d_b(d_b[3:0]), .d_cin(d_cin),
                  .q_s(c_q_s), .q_cout(c_q_cout), .a(), .b(), .cin(), .s(), .cout());

    wire [7:0] m_q_s;
    wire       m_q_cout, m_q_cout_lo;
    simd8_reg simd (.clk(clk), .rst(rst), .en(en), .d_a(d_a), .d_b(d_b), .d_cin(d_cin), .d_mode(d_mode),
                    .q_s(m_q_s), .q_cout(m_q_cout), .q_cout_lo(m_q_cout_lo),
                    .a(), .b(), .cin(), .simd_mode(), .s(), .cout(), .cout_lo(), .cin_hi());

    // expected values, two enabled clocks behind the inputs
    reg [4:0] exp_c  [0:1];
    reg [9:0] exp_m  [0:1];
    reg [1:0] filled;
    integer   i, errors, checks;

    function [9:0] simd_model;
        input [7:0] a, b;
        input cin, mode;
        reg [4:0] lo, hi;
        begin
            lo = a[3:0] + b[3:0] + cin;
            hi = a[7:4] + b[7:4] + (mode ? 1'b0 : lo[4]);
            simd_model = {hi[4], lo[4], hi[3:0], lo[3:0]};
        end
    endfunction

    // the model shifts on every enabled edge, like the circuit
    always @(posedge clk) begin
        if (rst) begin
            filled <= 0;
        end else if (en) begin
            exp_c[1] <= exp_c[0];
            exp_m[1] <= exp_m[0];
            exp_c[0] <= d_a[3:0] + d_b[3:0] + d_cin;
            exp_m[0] <= simd_model(d_a, d_b, d_cin, d_mode);
            filled   <= {filled[0], 1'b1};
        end
    end

    // compare just before every rising edge
    always @(negedge clk) begin
        if (!rst && filled[1]) begin
            checks = checks + 1;
            if ({c_q_cout, c_q_s} !== exp_c[1] || {m_q_cout, m_q_cout_lo, m_q_s} !== exp_m[1]) begin
                errors = errors + 1;
                if (errors < 10)
                    $display("  FAIL t=%0t: cla4 %b%h (exp %h), simd8 %b%b%h (exp %h)", $time,
                             c_q_cout, c_q_s, exp_c[1], m_q_cout, m_q_cout_lo, m_q_s, exp_m[1]);
            end
        end
    end

    task apply;
        input [7:0] a, b;
        input cin, mode;
        begin
            @(posedge clk); #1;
            {d_a, d_b, d_cin, d_mode} = {a, b, cin, mode};
        end
    endtask

    initial begin
        $dumpfile("tb_registered.vcd");
        $dumpvars(0, tb_registered);
        errors = 0; checks = 0;
        rst = 1; en = 0; {d_a, d_b, d_cin, d_mode} = 0;
        repeat (3) @(posedge clk);
        #1 rst = 0;

        $display("\n--- TEST 1: 2000 random vectors, enable always on ---");
        en = 1;
        for (i = 0; i < 2000; i = i + 1)
            apply($random, $random, $random, $random);
        $display("  >> %0d checks, %0d errors", checks, errors);

        $display("\n--- TEST 2: enable every third clock ---");
        for (i = 0; i < 600; i = i + 1) begin
            @(posedge clk); #1;
            en = (i % 3 == 0);
            {d_a, d_b, d_cin, d_mode} = {$random, $random, $random, $random};
        end
        en = 1;
        $display("  >> %0d checks, %0d errors", checks, errors);

        $display("\n--- TEST 3: hint vector through the registers ---");
        for (i = 0; i < 8; i = i + 1)
            apply(8'hFF, 8'h00, i[0], i[2]);
        repeat (3) @(posedge clk);
        $display("  >> %0d checks, %0d errors", checks, errors);

        $display("\n--- RESULT: %0d checks, %0d errors: %0s ---", checks, errors, errors ? "FAIL" : "PASS");
        $finish;
    end

endmodule
