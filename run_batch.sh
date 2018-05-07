#!/bin/bash

# Try this command line: result_file_prefix="../results/json/" base_args="--robot-speed 10 --max-steps=5000 --robot-movement-momentum=0.0" num_trials=5 max_processes=6 bash run_batch.sh


num_cores=$(lscpu -p | egrep -v '^#' | sort -u -t, -k 2,4 | wc -l)
[[ -z "$result_file_prefix" ]] && result_file_prefix="."
[[ -z "$base_args" ]] && base_args="--robot-speed 10 --max-steps=1000 --robot-movement-momentum=0.0"
[[ -z "$num_trials" ]] && num_trials=5
[[ -z "$max_processes" ]] && max_processes=$num_cores

result_file="$result_file_prefix/$(date +"safenavresults_%y_%m_%d_%H_%M_%S.json")"
printf "Starting simulation. The results will be stored in: %s\n" "$result_file"
printf "Using base arguments: %s\n" "$base_args"
printf "Running %d trials per argument set\n" "$num_trials"
printf "Using up to %d parallel processes\n" "$max_processes"

ulimit -t 1500

arg_sets=()
cur_num_processes=0

run_arg_set() {

	local arg_set="$1"
	local output_file="$2"
	python3 run_parambased.py $arg_set >> "$output_file"

}

# Generate argument sets
printf "Generating argument sets...\n"

## For humanaware
#all_ped_ids=( $(seq 1 367) )
#bad_peds=( 9 10 26 52 56 115 120 129 171 212 214 216 274 277 282 284 288 290 292 295 296 297 298 334 335 339 367 )
#for ped_id in "${all_ped_ids[@]}"
#do
#	isbad="false"
#	for bad_ped_id in "${bad_peds[@]}" ; do
#		if [[ "$bad_ped_id" == "$ped_id" ]] ; then
#			isbad="true"
#		fi
#	done
#	if [[ "$isbad" == "true" ]] ; then
#		continue
#	fi
#
#	arg_sets+=("$base_args --ped-id-to-replace ${ped_id}")
#done

# For non-humanaware
for ((speed = 7; speed <= 10; speed++))
do
	for map_modifier in 11 12
	do
		#arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/preset/preset_nothing_mod4.svg")
		#arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/preset/preset_nothing_mod5.svg")
		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/parallel_walls.svg")
		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/rooms.svg")
		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/empty.svg")
		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/block_columns.svg")
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

