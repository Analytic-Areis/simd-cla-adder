`timescale 1ns / 1ps

// Testbench for the SIMD-reconfigurable 8-bit adder.
//   TEST 1: 8-bit mode,      all 2^17 combinations of A, B, Cin, against A + B + Cin
//   TEST 2: dual 4-bit mode, all 2^17 combinations, against two independent 4-bit sums
//   TEST 3: worst carry path A = 0xFF, B = 0x00, Cin toggling, in both modes
//   TEST 4: same operands, mode switched: the carry is passed in mode 0 and blocked in mode 1
//   TEST 5: the gating cell on its own, all four combinations of lower carry and mode
// Waveform: sim/tb_simd8.vcd (TEST 3 to TEST 5 are spaced 10 ns apart for reading).
module tb_simd8;

    reg  [7:0] a, b;
    reg        cin, simd_mode;
    wire [7:0] s;
    wire       cout, cout_lo, cin_hi;

    simd8 dut (.a(a), .b(b), .cin(cin), .simd_mode(simd_mode),
               .s(s), .cout(cout), .cout_lo(cout_lo), .cin_hi(cin_hi));

    // behavioural model written with '+'
    wire [4:0] lo = a[3:0] + b[3:0] + cin;
    wire [4:0] hi = a[7:4] + b[7:4] + (simd_mode ? 1'b0 : lo[4]);
    wire [9:0] model = {hi[4], lo[4], hi[3:0], lo[3:0]};

    integer i, errors, checks;

    task check;
        begin
            #1;
            checks = checks + 1;
            if ({cout, cout_lo, s} !== model || cin_hi !== (lo[4] & ~simd_mode)) begin
                errors = errors + 1;
                if (errors < 10)
                    $display("  FAIL: mode=%b A=%h B=%h Cin=%b -> Cout=%b CoutLo=%b S=%h CinHi=%b, expected Cout=%b CoutLo=%b S=%h",
                             simd_mode, a, b, cin, cout, cout_lo, s, cin_hi, model[9], model[8], model[7:0]);
            end
        end
    endtask

    task show;
        input [319:0] label;
        begin
            #9;
            $display("  %-40s mode=%b A=%h B=%h Cin=%b | CoutLo=%b CinHi=%b Cout=%b S=%h",
                     label, simd_mode, a, b, cin, cout_lo, cin_hi, cout, s);
            checks = checks + 1;
            if ({cout, cout_lo, s} !== model || cin_hi !== (lo[4] & ~simd_mode)) begin
                errors = errors + 1;
                $display("  FAIL: expected Cout=%b CoutLo=%b S=%h", model[9], model[8], model[7:0]);
            end
        end
    endtask

    initial begin
        $dumpfile("tb_simd8.vcd");
        $dumpvars(0, tb_simd8);
        $dumpoff;   // the exhaustive sweeps are checked, not dumped
        errors = 0;
        checks = 0;
        a = 0; b = 0; cin = 0; simd_mode = 0;

        $display("\n--- TEST 1: 8-bit mode, all 131072 combinations ---");
        simd_mode = 0;
        for (i = 0; i < 131072; i = i + 1) begin
            {cin, b, a} = i;
            check;
        end
        $display("  >> %0d vectors checked so far, %0d errors", checks, errors);

        $display("\n--- TEST 2: dual 4-bit mode, all 131072 combinations ---");
        simd_mode = 1;
        for (i = 0; i < 131072; i = i + 1) begin
            {cin, b, a} = i;
            check;
        end
        $display("  >> %0d vectors checked so far, %0d errors", checks, errors);

        $display("\n--- TEST 3: worst carry path, A=FF B=00, Cin toggling ---");
        $dumpon;
        a = 8'hFF; b = 8'h00;
        simd_mode = 0; cin = 0; show("8-bit, Cin=0: FF");
        cin = 1;                show("8-bit, Cin rises: carry reaches Cout");
        cin = 0;                show("8-bit, Cin falls");
        simd_mode = 1; cin = 0; show("dual, Cin=0: F and F");
        cin = 1;                show("dual, Cin rises: carry stops at bit 4");
        cin = 0;                show("dual, Cin falls");

        $display("\n--- TEST 4: same operands, mode switched ---");
        a = 8'h0F; b = 8'h01; cin = 0;
        simd_mode = 0; show("8-bit: 0x0F + 0x01 = 0x10");
        simd_mode = 1; show("dual: F+1 = 0 carry 1, 0+0 = 0");
        a = 8'h37; b = 8'h59; cin = 1;
        simd_mode = 0; show("8-bit: 0x37 + 0x59 + 1 = 0x91");
        simd_mode = 1; show("dual: 7+9+1 = 0x1, 3+5 = 0x8");
        a = 8'hF8; b = 8'h18; cin = 0;
        simd_mode = 0; show("8-bit: 0xF8 + 0x18, Cout = 1");
        simd_mode = 1; show("dual: 8+8 = 0 carry 1, F+1 = 0 carry 1");

        $display("\n--- TEST 5: carry-gating cell ---");
        a = 8'h0F; b = 8'h00;
        cin = 0; simd_mode = 0; show("lower carry 0, mode 0: CinHi = 0");
        cin = 1; simd_mode = 0; show("lower carry 1, mode 0: CinHi = 1");
        cin = 0; simd_mode = 1; show("lower carry 0, mode 1: CinHi = 0");
        cin = 1; simd_mode = 1; show("lower carry 1, mode 1: CinHi = 0");

        $display("\n--- RESULT: %0d checks, %0d errors: %0s ---", checks, errors, errors ? "FAIL" : "PASS");
        $finish;
    end

endmodule
