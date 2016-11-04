#!/bin/bash
# Robot Simulator


ResultFile=$(date +"safenavresults_%y_%m_%d_%H_%M_%S.csv")
printf "Starting Simulation. The results will be stored in: %s\n" "$ResultFile"
base_args_1="--enable-memory --debug-level 1 --robot-speed 6 --radar-resolution 10 --batch-mode"
numberofsimulations=5
arg_sets=()
max_processes=8
cur_num_processes=0

run_arg_set() {

    local arg_set="$1"
    local output_file="$2"
    python3 Main.py $arg_set >> "$output_file"

}

# Generate argument sets
printf "Generating argument sets...\n"
for ((speed = 1; speed <= 5; speed++))
do

    arg_sets+=("$base_args_1 --map-modifier-num 0  --map-name Maps/Ground_WithRooms.png                 --speed-mode $speed")
    arg_sets+=("$base_args_1 --map-modifier-num 1  --map-name Maps/Ground_Nothing.png                   --speed-mode $speed")
    arg_sets+=("$base_args_1 --map-modifier-num 10 --map-name Maps/Ground_withParralel_walls.png        --speed-mode $speed")
    arg_sets+=("$base_args_1 --map-modifier-num 10 --map-name Maps/Ground_WithRooms.png                 --speed-mode $speed")
    arg_sets+=("$base_args_1 --map-modifier-num 10 --map-name Maps/Ground_Nothing.png                   --speed-mode $speed")
    arg_sets+=("$base_args_1 --map-modifier-num 4  --map-name Maps/Ground_Nothing.png                   --speed-mode $speed")
    arg_sets+=("$base_args_1 --map-modifier-num 5  --map-name Maps/Ground_Nothing.png                   --speed-mode $speed")
    arg_sets+=("$base_args_1 --map-modifier-num 7  --map-name Maps/Ground_Nothing.png                   --speed-mode $speed")
    arg_sets+=("$base_args_1 --map-modifier-num 9  --map-name Maps/Ground_Maze.png                      --speed-mode $speed")

done

# Run commands
for arg_set in "${arg_sets[@]}"
do

    printf "Starting arg set: %s\n" "$arg_set"

    for ((i = 0; i < numberofsimulations; i++)); 
    do

        printf "Running trial #%d\n" $((i+1))
        (
            run_arg_set "$arg_set" "$ResultFile"
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

printf "All done. Results are in %s\n" "$ResultFile"

