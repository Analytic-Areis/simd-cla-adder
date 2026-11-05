`timescale 1ns / 1ps

// Testbench for the 4-bit CLA.
//   TEST 1: all 512 input combinations against a + b + cin
//   TEST 2: hint vector A = 1111, B = 0000, Cin 0 -> 1 -> 0 (longest carry path)
//   TEST 3: directed corner cases
// Waveform: sim/tb_cla4.vcd (TEST 2 and TEST 3 are spaced 10 ns apart for reading).
module tb_cla4;

    reg  [3:0] a, b;
    reg        cin;
    wire [3:0] s;
    wire       cout;

    cla4 dut (.a(a), .b(b), .cin(cin), .s(s), .cout(cout));

    integer i, errors, checks;

    task check;
        input [255:0] label;
        begin
            #1;
            checks = checks + 1;
            if ({cout, s} !== a + b + cin) begin
                errors = errors + 1;
                $display("  FAIL %0s: A=%b B=%b Cin=%b -> C4=%b S=%b, expected %b",
                         label, a, b, cin, cout, s, a + b + cin);
            end
        end
    endtask

    task show;
        input [255:0] label;
        begin
            #9;
            $display("  %-34s A=%b B=%b Cin=%b | C4=%b S=%b (%0d + %0d + %0d = %0d)",
                     label, a, b, cin, cout, s, a, b, cin, {cout, s});
            if ({cout, s} !== a + b + cin) begin
                errors = errors + 1;
                $display("  FAIL: expected %0d", a + b + cin);
            end
            checks = checks + 1;
        end
    endtask

    initial begin
        $dumpfile("tb_cla4.vcd");
        $dumpvars(0, tb_cla4);
        $dumpoff;   // the exhaustive sweep is checked, not dumped
        errors = 0;
        checks = 0;

        $display("\n--- TEST 1: all 512 input combinations ---");
        for (i = 0; i < 512; i = i + 1) begin
            {cin, b, a} = i;
            check("exhaustive");
        end
        $display("  >> %0d vectors checked, %0d errors", checks, errors);

        $display("\n--- TEST 2: hint vector, carry ripples through all bits ---");
        $dumpon;
        a = 4'b1111; b = 4'b0000; cin = 0; show("A=15, B=0, Cin=0");
        cin = 1;                           show("Cin rises: carry out, S=0000");
        cin = 0;                           show("Cin falls: back to 1111");
        cin = 1;                           show("Cin rises again");

        $display("\n--- TEST 3: corner cases ---");
        a = 4'h0; b = 4'h0; cin = 0; show("zero");
        a = 4'hF; b = 4'hF; cin = 1; show("all ones, largest sum 31");
        a = 4'hF; b = 4'h1; cin = 0; show("generate at bit 0, propagate up");
        a = 4'h8; b = 4'h8; cin = 0; show("generate at bit 3 only");
        a = 4'h5; b = 4'hA; cin = 1; show("all propagate, Cin decides");
        a = 4'h5; b = 4'hA; cin = 0; show("all propagate, no carry");
        a = 4'h7; b = 4'h1; cin = 0; show("7 + 1");
        a = 4'h3; b = 4'h6; cin = 1; show("3 + 6 + 1");

        $display("\n--- RESULT: %0d checks, %0d errors: %0s ---", checks, errors, errors ? "FAIL" : "PASS");
        $finish;
    end

endmodule
