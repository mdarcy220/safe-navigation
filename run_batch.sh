#!/bin/bash
# Robot Simulator

# Try this command line: result_file_prefix="../results/csv/" base_args="--debug-level 1 --robot-speed 10 --radar-resolution 4 --batch-mode --max-steps=5000 --robot-movement-momentum=0.0" num_trials=5 max_processes=6 bash run_batch.sh


num_cores=$(lscpu -p | egrep -v '^#' | sort -u -t, -k 2,4 | wc -l)
[[ -z "$result_file_prefix" ]] && result_file_prefix="."
[[ -z "$base_args" ]] && base_args="--enable-memory --debug-level 1 --robot-speed 6 --radar-resolution 5 --batch-mode --max-steps=500 --robot-movement-momentum=0.0 --robot-memory-sigma=35 --robot-memory-decay=1 --robot-memory-size=500"
[[ -z "$num_trials" ]] && num_trials=5
[[ -z "$max_processes" ]] && max_processes=$num_cores

result_file="$result_file_prefix/$(date +"safenavresults_%y_%m_%d_%H_%M_%S.csv")"
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
	python3 Main.py $arg_set >> "$output_file"

}

# Generate argument sets
printf "Generating argument sets...\n"
all_ped_ids=( 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 20 21 22 23 24 25 26 27 28 29 30 31 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124 125 126 127 128 129 130 131 132 133 134 135 136 137 138 139 140 141 142 143 144 145 146 147 148 149 150 151 152 153 154 155 156 157 159 160 161 162 163 164 166 167 168 169 170 171 172 173 174 175 176 177 178 179 180 181 182 183 184 185 186 187 188 189 190 191 192 193 194 195 196 197 198 199 200 201 202 203 204 205 206 207 208 209 210 211 212 213 214 215 216 217 218 219 220 221 222 223 224 226 227 228 229 230 231 232 233 234 235 236 237 238 239 240 241 242 243 244 245 246 247 248 249 250 251 252 253 254 255 256 257 258 259 260 261 262 263 264 265 266 267 268 269 270 272 273 274 275 276 277 278 279 280 281 282 283 284 285 286 287 288 289 290 291 292 293 294 295 296 297 298 299 300 301 302 303 304 305 306 307 308 309 310 311 312 313 314 315 316 317 318 319 320 321 322 323 324 325 326 327 328 329 330 331 332 333 334 335 336 337 338 339 340 341 342 343 344 345 346 347 348 349 350 351 352 353 354 355 356 357 358 359 360 361 362 363 364 365 366 367 )
for ped_id in "${all_ped_ids[@]}"
do
	arg_sets+=("$base_args --ped-id-to-replace ${ped_id}")
done
#for ((speed = 7; speed <= 10; speed++))
#do
#	for map_modifier in 11 12
#	do
#		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/preset/preset_nothing_mod4.png")
#		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/preset/preset_nothing_mod5.png")
#		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/parallel_walls.png")
#		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/rooms.png")
#		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/empty.png")
#		arg_sets+=("$base_args --map-modifier-num $map_modifier  --speed-mode $speed --map-name Maps/block_columns.png")
#	done
#
#done

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

