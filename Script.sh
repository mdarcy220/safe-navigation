#!/bin/bash
# Robot Simulator


ResultFile=$(date +"%y%m%d%H%M%S")
echo "Creating the result file:"
echo $ResultFile
echo "Starting Simulation ..."
Args="--enable-memory --debug-level 1 --robot-speed 6 --radar-resolution 10 --fast-computing"
numberofsimulations=5
echo "Map 1 simulation is starting"
for speed in {1..5}
do  
    echo "Speed mode: $speed"
    for ((i=1; i<=numberofsimulations; i++)); 
    do
        output=$(python3 Main.py $Args --map-modifier-num 0  --map-name Maps/Ground_WithRooms.png --speed-mode $speed)
        echo "Simulation #$i done. The output is:" $output
        echo $output >> $ResultFile
    done
done 


echo "Map 2 simulation is starting"
for speed in {1..5}
do
    echo "Speed mode: $speed"
    for ((i=1; i<=numberofsimulations; i++)); 
    do
        output=$(python3 Main.py $Args --map-modifier-num 2  --map-name Maps/Ground_withParralel_walls.png --speed-mode $speed)
        echo "Simulation #$i done. The output is:" $output
        echo $output >> $ResultFile
    done
done

echo "Map 3 simulation is starting"
for speed in {1..5}
do
    echo "Speed mode: $speed"
    for ((i=1; i<=numberofsimulations; i++)); 
    do
        output=$(python3 Main.py $Args --map-modifier-num 3  --map-name Maps/Ground_WithRooms.png --speed-mode $speed)
        echo "Simulation #$i done. The output is:" $output
        echo $output >> $ResultFile
    done
done

echo "Map 4 simulation is starting"
for speed in {1..5}
do
    echo "Speed mode: $speed"
    for ((i=1; i<=numberofsimulations; i++)); 
    do
        output=$(python3 Main.py $Args --map-modifier-num 1  --map-name Maps/Ground_Nothing.png --speed-mode $speed)
        echo "Simulation #$i done. The output is:" $output
        echo $output >> $ResultFile
    done
done


echo "Map 5 simulation is starting"
for speed in {1..5}
do
    echo "Speed mode: $speed"
    for ((i=1; i<=numberofsimulations; i++)); 
    do
        output=$(python3 Main.py $Args --map-modifier-num 4  --map-name Maps/Ground_Nothing.png --speed-mode $speed)
        echo "Simulation #$i done. The output is:" $output
        echo $output >> $ResultFile
    done
done


echo "Map 6 simulation is starting"
for speed in {1..5}
do
    echo "Speed mode: $speed"
    for ((i=1; i<=numberofsimulations; i++)); 
    do
        output=$(python3 Main.py $Args --map-modifier-num 5 --map-name Maps/Ground_Nothing.png --speed-mode $speed)
        echo "Simulation #$i done. The output is:" $output
        echo $output >> $ResultFile
    done
done


echo "Map 7 simulation is starting"
for speed in {1..5}
do
    echo "Speed mode: $speed"
    for ((i=1; i<=numberofsimulations; i++)); 
    do
        output=$(python3 Main.py $Args --map-modifier-num 7 --map-name Maps/Ground_Nothing.png --speed-mode $speed)
        echo "Simulation #$i done. The output is:" $output
        echo $output >> $ResultFile
    done
done

echo "Map 8 simulation is starting"
for speed in {1..5}
do
    echo "Speed mode: $speed"
    for ((i=1; i<=numberofsimulations; i++)); 
    do
        output=$(python3 Main.py $Args --map-modifier-num 8 --map-name Maps/Ground_Maze.png --speed-mode $speed)
        echo "Simulation #$i done. The output is:" $output
        echo $output >> $ResultFile
    done
done

