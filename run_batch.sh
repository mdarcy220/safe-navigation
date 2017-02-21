#!/bin/bash
# Robot Simulator


num_cores=$(lscpu -p | egrep -v '^#' | sort -u -t, -k 2,4 | wc -l)
[[ -z "$result_file_prefix" ]] && result_file_prefix="."
[[ -z "$base_args" ]] && base_args="--enable-memory --debug-level 1 --robot-speed 6 --radar-resolution 5 --batch-mode --max-steps=5000 --robot-movement-momentum=0.0 --robot-memory-sigma=35 --robot-memory-decay=1 --robot-memory-size=500"
[[ -z "$num_trials" ]] && num_trials=5
[[ -z "$max_processes" ]] && max_processes=$num_cores

result_file="$result_file_prefix/$(date +"safenavresults_%y_%m_%d_%H_%M_%S.csv")"
printf "Starting simulation. The results will be stored in: %s\n" "$result_file"
printf "Using base arguments: %s\n" "$base_args"
printf "Running %d trials per argument set\n" "$num_trials"
printf "Using up to %d parallel processes\n" "$max_processes"


arg_sets=()
cur_num_processes=0

run_arg_set() {

	local arg_set="$1"
	local output_file="$2"
	python3 Main.py $arg_set >> "$output_file"

}

# Generate argument sets
printf "Generating argument sets...\n"
for ((speed = 7; speed <= 10; speed++))
do
	for map_modifier in 11 12
	do
		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/preset/preset_nothing_mod4.png")
		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/preset/preset_nothing_mod5.png")
		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/parallel_walls.png")
		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/rooms.png")
		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/empty.png")
		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/easy_maze.png")
	done

done

# Run commands
for arg_set in "${arg_sets[@]}"
do

	printf "Starting arg set: %s\n" "$arg_set"

	for ((i = 0; i < num_trials; i++)); 
	do

		printf "Running trial #%d\n" $((i+1))
		(
			run_arg_set "$arg_set" "$result_file"
		) &

		(( cur_num_processes++ ))
		if (( max_processes <= cur_num_processes ))
		then
			wait -n
			(( cur_num_processes-- ))
		fi

	done

done

wait

printf "All done. Results are in %s\n" "$result_file"

