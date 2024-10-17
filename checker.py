import re
import sys


class Task:
	def __init__(self, name, duration, machines, resources):
		self.name = name
		self.duration = duration
		self.machines = machines
		self.resources = resources
	
	def __repr__(self):
		return 'Task %r with duration %d, requires machines %s and resources %s' % (self.name, self.duration, ', '.join(self.machines), ', '.join(self.resources))


class Machine:
	def __init__(self, name):
		self.name = name
		self.schedule = []
	
	def add_task(self, task_name, start_time, resources_used, duration):
		self.schedule.append((task_name, start_time, start_time + duration, resources_used))
	
	def get_schedule(self):
		return self.schedule
	
	def __repr__(self):
		schedule_str = ['task %s starting at time %d and end at time %d uses resources %s' % (task[0], task[1], task[2], ', '.join(task[3])) for task in self.schedule]
		return 'Machine %r has schedule: %s' % (self.name, ', '.join(schedule_str))


def parse_input(input_text):
	tasks = {}
	
	# Remove comments and split by lines
	lines = [line.strip() for line in input_text.split('\n') if line.strip() and not line.startswith('%')]
	
	# Parse tasks
	for line in lines:
		parts = line.replace("test(", "").replace(")", "").replace("'", "").replace('’', '').replace(',', '').split()
		task_name = parts[0].strip()
		duration = int(parts[1].strip())
		machines = ['m%d' % int(x) for x in re.sub('m', ',', parts[2].strip('[]')[1:]).split(',')] if parts[2].strip() != "[]" else []
		resources = ['r%d' % int(x) for x in re.sub('r', ',', parts[3].strip('[]')[1:]).split(',')] if parts[3].strip() != "[]" else []
		machines.sort()
		resources.sort()
		tasks[task_name] = Task(task_name, duration, machines, resources)
	
	return tasks


def parse_output(output_text, tasks):
	machines = {}
	makespan = None
	
	# Split by lines
	lines = [line.strip() for line in output_text.split('\n') if line.strip()]
	
	# Extract makespan from the first line
	makespan = int(lines[0].split(':')[-1].strip())
	
	# Extract machine schedules from the rest
	for line in lines[1:]:
		# Clean and split the line into machine name and task info
		parts = line.replace("machine(", "").replace(")])", ")]").replace("'", "").split(',', maxsplit=2)
		machine_name = parts[0].strip()
		
		tasks_data = [x.strip('()') for x in re.split(r"\), *\(", parts[2].strip().strip("[]"))]
		machines[machine_name] = Machine(machine_name)
		if int(parts[1].strip()) > 0:
			for task_data in tasks_data:
				task_data = task_data.replace("[", "").replace("]", "").replace("'", "").replace(' ', '')
				# Split the task info (task_name, start_time, resources if available)
				task_info = task_data.split(',', maxsplit=2)
				task_name = task_info[0].strip()
				
				# Ensure start_time is correctly extracted
				if len(task_info) > 1:
					try:
						start_time = int(task_info[1].strip())
					except ValueError:
						raise ValueError(f"Invalid start time for task {task_name} on machine {machine_name}")
				else:
					raise ValueError(f"Missing start time for task {task_name} on machine {machine_name}")
				
				# Extract resources if they exist
				if len(task_info) > 2:
					resources_used = task_info[2].split(',') if task_info[2].strip() != '' else []
				else:
					resources_used = []
				resources_used.sort()
				
				# Find the task's duration from the input task dictionary
				task_duration = tasks[task_name].duration
				machines[machine_name].add_task(task_name, start_time, resources_used, task_duration)
	
	return makespan, machines


def check_schedule(tasks, machines, given_makespan):
	used_resources = {}
	max_end_time = 0  # This will store the actual makespan
	
	# Check each machine's schedule
	for machine in machines.values():
		# Sort the tasks on each machine by start time
		machine.schedule.sort(key=lambda x: x[1])
		
		# Ensure no tasks on the same machine overlap
		for i in range(len(machine.schedule) - 1):
			current_task = machine.schedule[i]
			next_task = machine.schedule[i + 1]
			
			current_task_name, current_start, current_end, _ = current_task
			next_task_name, next_start, _, _ = next_task
			
			# Check if the current task overlaps with the next task
			if current_end > next_start:
				return False, f"Tasks {current_task_name} and {next_task_name} overlap on machine {machine.name}."
		
		if machine.schedule:
			# The last task in the schedule will have the latest end time
			last_task = machine.schedule[-1]
			task_name, start_time, end_time, resources_used = last_task
			
			# Update the max end time based on the last task's end time
			max_end_time = max(max_end_time, end_time)
		
		# Iterate through each task in the machine's schedule
		for task in machine.schedule:
			task_name, start_time, end_time, resources_used = task
			
			# Check if the task is using the required resources
			if resources_used != tasks[task_name].resources:
				return False, f"Task {task_name} did not use the required resources {tasks[task_name].resources}."
			
			# Check resource overlap with tasks on other machines or this machine
			for resource in resources_used:
				if resource in used_resources:
					# Check for overlapping resource usage across all machines
					for used_task, (used_start, used_end, used_machine) in used_resources[resource]:
						if not (end_time <= used_start or start_time >= used_end):
							return False, f"Resource {resource} is used by {task_name} on machine {machine.name} and overlaps with {used_task} on machine {used_machine}."
				
				# Track resource usage: add (task_name, (start_time, end_time, machine_name)) for this resource
				if resource not in used_resources:
					used_resources[resource] = []
				used_resources[resource].append((task_name, (start_time, end_time, machine.name)))
			
			# Check if the task is assigned to valid machines
			if tasks[task_name].machines and machine.name not in tasks[task_name].machines:
				return False, f"Task {task_name} is assigned to machine {machine.name}, but it is not a valid machine for this task."
	
	# Validate the makespan by comparing it with the actual max end time
	if max_end_time != given_makespan:
		return False, f"Given makespan {given_makespan} does not match the actual makespan {max_end_time}."
	
	return True, "Solution is valid."


def check_solution(input_file, output_file):
	# Read input and output files
	with open(input_file, 'r') as f:
		input_text = f.read()
	
	with open(output_file, 'r') as f:
		output_text = f.read()
	
	# Parse input and output
	tasks = parse_input(input_text)
	makespan, machines = parse_output(output_text, tasks)
	
	# print(tasks, makespan)
	
	# Validate the schedule
	is_valid, message = check_schedule(tasks, machines, makespan)
	print(message)
	
	return is_valid, message


if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Usage: python checker.py <input_file> <output_file>")
		sys.exit(1)
	
	input_file = sys.argv[1]
	output_file = sys.argv[2]
	check_solution(input_file, output_file)
