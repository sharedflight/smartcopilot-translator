smartcopilot_cfg_filepath = 'smartcopilot.cfg'

# Python implementation to check whether the array 
# contains a set of contiguous integers 
# Function to check whether the array  
# contains a set of contiguous integers 
# This code is contributed by 'Ansu Kumari' 
# Source: https://www.geeksforgeeks.org/check-array-contains-contiguous-integers-duplicates-allowed/
def dataref_indices_are_contiguous(arr): 
    # Storing elements of 'arr[]' in a hash table 'us'  
    us = set() 
    for i in arr: us.add(i) 
  
    # As arr[0] is present in 'us' 
    count = 1
  
    # Starting with previous smaller element of arr[0] 
    curr_ele = arr[0] - 1
  
    # If 'curr_ele' is present in 'us' 
    while curr_ele in us: 
  
        # Increment count 
        count += 1
  
        # Update 'curr_ele" 
        curr_ele -= 1
  
    # Starting with next greater element of arr[0] 
    curr_ele = arr[0] + 1
  
    # If 'curr_ele' is present in 'us' 
    while curr_ele in us: 
  
        # Increment count 
        count += 1
  
        # Update 'curr_ele" 
        curr_ele += 1
  
    # Returns true if array contains a set of 
    # contiguous integers else returns false 
    return (count == len(us)) 


##### CORE FUNCTION TO READ A LINE IN A GIVEN SECTION #####

def parse_smartcopilot_line(line, current_section):

	success = True
	line_type = 'UNKNOWN';
	sync_modifiers = [];
	dataref = "????";
	right_side_value = 0;
	holdvalues = [];
	override_modifiers = [];
	array_index = -1;

	if line[0] == '#':
		line_type = "#";

	if line[0] == '[':
		line_type = "#SECTION";
		right_bracket_pos = line.find(']');
		current_section = line[1:right_bracket_pos].lower();

	if line_type == "UNKNOWN":

		if current_section == "triggers":
			line_type = "Trigger";
		elif current_section == "commands":
			line_type = "Command";
		elif current_section == "continued":
			line_type = "Trigger";
			sync_modifiers.append("SYS_MASTER_ONLY");
		elif current_section == "send_back":
			line_type = "Trigger";
			sync_modifiers.append("PILOT_FLYING_ONLY");
		elif current_section == "override":
			line_type = "Override";
		elif current_section == "transponder":
			line_type = "Trigger";
			sync_modifiers.append("SYNC_TRANS");
		elif current_section == "weather":
			line_type = "Trigger";
			sync_modifiers.append("SYNC_WX");
		elif current_section == "slow":
			line_type = "Trigger";
			sync_modifiers.append("SYNC_SLOW");
		elif current_section == "setup":
			line_type = "#Setup";
		elif current_section == "info":
			line_type = "#Info";
		else:
			success = False;
	
		if success == True and current_section != "info":
			line_split_on_spaces = line.split(" ");
			dataref = line_split_on_spaces[0];

			position_of_fixed_index = dataref.find("_FIXED_INDEX_");
			position_of_left_brace = dataref.find("[");
			position_of_right_brace = dataref.find("]");

			if position_of_fixed_index > 0:
				dataref = dataref[0:position_of_fixed_index];
				sync_modifiers.append("FAKEARRAY");
			elif position_of_left_brace > 0 and position_of_right_brace > position_of_left_brace:
				array_index = int(dataref[position_of_left_brace+1:position_of_right_brace]);
				dataref = dataref[0:position_of_left_brace];
				
			right_side_value = line_split_on_spaces[2];

			if len(line_split_on_spaces) != 3:
				success = False;

			if current_section == "override":
				
				
				if int(right_side_value) == 10:
					override_modifiers.append("NON_PILOT_FLYING");
				elif int(right_side_value) == 12:
					override_modifiers.append("NON_SYSTEM_MASTER");
				elif int(right_side_value) == 31:
					override_modifiers.append("OVERRIDE_ALL");
				else:
					if int(right_side_value) >= 16:
						right_side_value -= 16;
						print("Don't know what NOT_DEFINED override type is.");
						success = False;
					if int(right_side_value) >= 8:
						right_side_value -= 8;
						print("Don't know what to do here...");
						success = False;

				#MASTER_CONTROL = 1
				#MASTER_NO_CONTROL = 2
				#SLAVE_CONTROL = 4
				#SLAVE_NO_CONTROL = 8
				#NOT_DEFINED = 16

				right_side_value = 0;

			elif float(right_side_value) != 0:
				if float(right_side_value).is_integer() == True:
					holdvalues.append(int(float(right_side_value)));
				else:
					holdvalues.append(float(right_side_value));

	array_index_array = []

	if array_index != -1:
		array_index_array = [array_index];

	parsed_line = {"type" : line_type, "dataref" : dataref, "array_index" : array_index_array, "rhs" : right_side_value, "holdvalues" : holdvalues, "override_modifiers": override_modifiers, "sync_modifiers" : sync_modifiers, "scp_line" : line, "scp_section": current_section};



	
	return parsed_line, current_section, success



current_section = '';

parsed_line_infos = [];

with open(smartcopilot_cfg_filepath) as fp:
	line = fp.readline();
	cnt = 1;
	while line:
		line = line.strip()

		if len(line) == 0:
			cnt += 1;
			line = fp.readline();
			continue

		parsed_line, current_section, success = parse_smartcopilot_line(line, current_section);

		if (success == False):
			print("We died on this line in secion {}:".format(current_section));
			print(line);
			exit();

		parsed_line["scp_line_number"] = cnt;

		parsed_line["sf_line_number"] = len(parsed_line_infos) + 1;

		parsed_line_infos.append(parsed_line);

		print("{} {} @ {} : {}".format(parsed_line["type"], parsed_line["dataref"], ",".join(parsed_line["sync_modifiers"]), parsed_line["scp_line"]));
		

		cnt += 1;
		line = fp.readline();

config_file_lines = [];

datarefs_that_appear = {};
# Lets loop over and look for 
# datarefs that appear more than once...
for parsed_line in parsed_line_infos:
	dataref = parsed_line["dataref"];
	
	if dataref == "????":
		continue;

	if dataref in datarefs_that_appear:
		print("Alread have seen this dataref {}".format(dataref));
		print(datarefs_that_appear[dataref]);
		print("New parsed_line was:");
		print(parsed_line);
		
		its_ok = False;

		for previous_parsed_line in datarefs_that_appear[dataref]:
			if previous_parsed_line["scp_line"] == parsed_line["scp_line"]:
				print("WARNING: EXACT DUPLICATE OF SCP LINE {} FOUND AGAIN ON SCP LINE {}".format(previous_parsed_line["scp_line_number"], parsed_line["scp_line_number"]));
				parsed_line["skip"] = previous_parsed_line;
				its_ok = True;

		# Set its_ok to true and then if find difference
		# will set to false again...
		if its_ok == False:
			its_ok = True;
			
			for idx, previous_parsed_line in enumerate(datarefs_that_appear[dataref]):
				if previous_parsed_line['type'] ==  parsed_line['type']:
					for key in previous_parsed_line:
						if key != "scp_line_number" and key != "scp_line" and key != "array_index" and key != "skip"  and key != "sf_line_number": 
							if previous_parsed_line[key] != parsed_line[key]:
								its_ok = False;

					if its_ok == True:
						print("THIS SHOULD BE OK SINCE JUST ARRAY INDEX DIFFERS");
						print("ADDING ADDITIONAL ARRAY INDEX. NEW LINE IS:")
						datarefs_that_appear[dataref][idx]["array_index"].extend(parsed_line["array_index"]);
						parsed_line["skip"] = datarefs_that_appear[dataref][idx];
						# NOTE: Python objects are passed by reference, so this will modify the original
						# parsed_line in our parsed_line_infos.
						# WE WILL MARK THE LATEST LINE TO SKIP.
						print("REVISED PARSED LINE IS:");
						print(datarefs_that_appear[dataref][idx]);
				else:
					print("WE NEED TO DECIDE IF THIS SHOULD BE OK??? Sync type doesn't match a previous parsed line");
					its_ok = False;


		if its_ok == False:
			print("THIS IS NOT OK!");
			exit();
				


	else:
		datarefs_that_appear[parsed_line["dataref"]] = [parsed_line];

still_in_comment_header = True;

for parsed_line in parsed_line_infos:

	config_file_line = "";

	parsed_line["sf_line_number"] = len(config_file_lines) + 1;

	if "skip" in parsed_line:
		config_file_line = "#SKIPPED (EITHER DUPLICATE OR MERGE WITH LINE " + str(parsed_line["skip"]["sf_line_number"]) + ") -- " + parsed_line["scp_line"];

	elif parsed_line["type"] == "#":
		if parsed_line["scp_line"].find("##") >= 0 and still_in_comment_header == False:
			config_file_lines.append("");
		config_file_line = parsed_line["scp_line"];
		config_file_lines.append(config_file_line);
		continue;
	elif parsed_line["type"] == "#SECTION":
		config_file_line = parsed_line["type"] + " " + parsed_line["scp_line"];
		config_file_lines.append("");
		config_file_lines.append(config_file_line);
		config_file_lines.append("");
		continue;
	elif parsed_line["type"] == "Trigger":
		
		hold_and_sync_modifiers_joined = '';
		dataref_string = parsed_line['dataref'];

		if len(parsed_line["holdvalues"]) > 0:
			print("Found a trigger line with hold values!");
			print(parsed_line);
			hold_values_joined = "[" + ",".join(map(str, parsed_line["holdvalues"])) + "]";
			parsed_line['sync_modifiers'].append("HOLDVALUES");
			sync_modifiers_joined = ",".join(parsed_line['sync_modifiers']);
			
			hold_and_sync_modifiers_joined = hold_values_joined + " " + sync_modifiers_joined;
			print(hold_and_sync_modifiers_joined);
		else:
			sync_modifiers_joined = ",".join(parsed_line['sync_modifiers']);
			hold_and_sync_modifiers_joined = sync_modifiers_joined;

		if len(parsed_line["array_index"]) > 0:
			print("Found a trigger array");
			indices_contiguous = dataref_indices_are_contiguous(parsed_line["array_index"]);
			if indices_contiguous == True:
				print("Found the indices are contiguous.");
				start_index = min(parsed_line["array_index"]);
				stop_index = max(parsed_line["array_index"]);
				if start_index ==  stop_index:
					config_file_line = "Trigger " + parsed_line["dataref"] + "[" + str(start_index) + "] @ 0 " + hold_and_sync_modifiers_joined;
				else:
					config_file_line = "Trigger " + parsed_line["dataref"] + "[" + str(start_index) + ":" + str(stop_index) + "] @ 0 " + hold_and_sync_modifiers_joined;
				print(config_file_line);
			else:
				print("WARNING: Found indices of trigger dataref {} are not contiguous. Will produce individual lines.");
				config_file_lines.append("# WARNING: The indices for this dataref were not contiguous?");
				for a_index in parsed_line["array_index"]:
					config_file_line = "Trigger " + parsed_line["dataref"] + "[" + str(a_index)+ "] @ 0 " + hold_and_sync_modifiers_joined;
					config_file_lines.append(config_file_line);
				continue



		else:
			print("Found trigger parsed_line:")
			print(parsed_line);
			config_file_line = "Trigger " + parsed_line["dataref"] + " @ 0 " + hold_and_sync_modifiers_joined;

	elif parsed_line["type"] == "Command":
		config_file_line = "Command " + parsed_line["dataref"];

	elif parsed_line["type"] == "Override":
		
		if len(parsed_line["array_index"]) > 0:
			print("ERROR: DO NOT KNOW HOW TO HANDLE ARRAY DATAREF OVERIDES YET!?!?");
			print("Original SCP line {}: {}".format(parsed_line["scp_line_number"] , parsed_line["scp_line"]))
			print("Parsed line data:");
			exit();

		if len(parsed_line["override_modifiers"]) > 1:
			print("WARNING: We are splitting override into multiple overrides ?!?!?");
			print("Original SCP line {}: {}".format(parsed_line["scp_line_number"] , parsed_line["scp_line"]))
			config_file_lines.append("# WARNING: We are splitting override into multiple overrides ?!?!?");
			config_file_lines.append("Original SCP line {}: {}".format(parsed_line["scp_line_number"] , parsed_line["scp_line"]));
			
			print("Parsed line data:");
			print(parsed_line);

			for override_modifier in parsed_line["override_modifiers"]:
				config_file_line = "Override " + parsed_line["dataref"] + " @ 1 " + override_modifier;
				config_file_lines.append(config_file_line);
			continue

		else:

			config_file_line = "Override " + parsed_line["dataref"] + " @ 1 " + parsed_line["override_modifiers"][0]

	elif parsed_line["type"] == "#Setup":

		config_file_line = "#[SETUP] Section Line: " + parsed_line["scp_line"];

	elif parsed_line["type"] == "#Info":

		config_file_line = "#[INFO] Section Line: " + parsed_line["scp_line"];

	else:
		print("We died on this parsed_line:")
		print(parsed_line);
		exit();

	still_in_comment_header = False;

	config_file_lines.append(config_file_line);

with open("Shared Flight Config File.txt", 'w') as f:
    f.write('\n'.join(config_file_lines))
		