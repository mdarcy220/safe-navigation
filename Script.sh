#!/bin/bash
# Robot Simulator


num_cores=$(lscpu -p | egrep -v '^#' | sort -u -t, -k 2,4 | wc -l)
[[ -z "$result_file_prefix" ]] && result_file_prefix="."
[[ -z "$base_args" ]] && base_args="--enable-memory --debug-level 1 --robot-speed 6 --radar-resolution 10 --batch-mode --robot-movement-momentum=0.2"
[[ -z "$num_trials" ]] && num_trials=5
[[ -z "$max_processes" ]] && max_processes=$num_cores

result_file="$result_file_prefix/$(date +"safenavresults_%y_%m_%d_%H_%M_%S.csv")"
printf "Starting Simulation. The results will be stored in: %s\n" "$result_file"
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
for ((speed = 1; speed <= 6; speed++))
do

    arg_sets+=("$base_args --map-modifier-num 1  --map-name Maps/preset/preset_nothing_mod1.png       --speed-mode $speed")
    arg_sets+=("$base_args --map-modifier-num 4  --map-name Maps/preset/preset_nothing_mod4.png       --speed-mode $speed")
    arg_sets+=("$base_args --map-modifier-num 5  --map-name Maps/preset/preset_nothing_mod5.png       --speed-mode $speed")
    arg_sets+=("$base_args --map-modifier-num 0  --map-name Maps/Ground_WithRooms.png                 --speed-mode $speed")
    #arg_sets+=("$base_args --map-modifier-num 0  --map-name Maps/rooms_roundedcorners.png                 --speed-mode $speed")
    arg_sets+=("$base_args --map-modifier-num 10 --map-name Maps/Ground_withParralel_walls.png        --speed-mode $speed")
    arg_sets+=("$base_args --map-modifier-num 10 --map-name Maps/Ground_WithRooms.png                 --speed-mode $speed")
    arg_sets+=("$base_args --map-modifier-num 10 --map-name Maps/Ground_Nothing.png                   --speed-mode $speed")
    arg_sets+=("$base_args --map-modifier-num 7  --map-name Maps/Ground_Nothing.png                   --speed-mode $speed")
    arg_sets+=("$base_args --map-modifier-num 9  --map-name Maps/Ground_Maze.png                      --speed-mode $speed")

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

