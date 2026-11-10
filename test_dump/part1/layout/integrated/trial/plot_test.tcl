load cla_trial
select top cell
expand
box values [lindex [box values] 0] [lindex [box values] 1] [lindex [box values] 2] [lindex [box values] 3]
plot pnm plot_test.pnm
quit -noprompt
