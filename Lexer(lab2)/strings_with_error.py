def arrow_string(text, start_position, end_position):
	result = ''

	start_index = max(text.rfind('\n', 0, start_position.index), 0)
	end_index = text.find('\n', start_index + 1)
	if end_index < 0: 
		end_index = len(text)
	
	line_count = end_position.line - start_position.line + 1
	for i in range(line_count):
		line = text[start_index:end_index]
		if i == 0:
			start_colon = start_position.colon
		else: 
			start_colon = 0
		if i == line_count - 1:
			end_colon = end_position.colon
		else: 
			end_colon = len(line) - 1

		result += line + '\n'
		result += ' ' * start_colon + '^' * (end_colon - start_colon)

		start_index = end_index
		end_index = text.find('\n', start_index + 1)
		if end_index < 0: 
			end_index = len(text)

	return result.replace('\t', '')
