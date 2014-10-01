def getNodeNameDictionary():
	nodes = []
	
	nodes.append(("Input", [
		"IntegerInputNode",
		"FloatInputNode",
		"StringInputNode",
		"ObjectInputNode",
		"TimeInfoNode",
		"ObjectInfoNode",
		"RandomNumberNode",
		"RandomStringNode",
		"CharactersNode" ] ))
		
	nodes.append(("Output", [
		"TextOutputNode",
		"ObjectOutputNode",
		"AttributeOutputNode",
		"DebugOutputNode",
		"ModifierOutputNode" ] ))
		
	nodes.append(("Strings", [
		"CombineStringsNode",
		"ReplicateStringsNode",
		"SubstringNode",
		"StringAnalyzeNode" ] ))

	nodes.append(("Convert", [
		"ToStringConversion",
		"ToFloatConversion",
		"ToIntegerConversion",
		"CombineVector",
		"SeparateVector" ] ))
	
	nodes.append(("Math", [
		"FloatMathNode",
		"VectorLengthNode" ] ))
		
	nodes.append(("Script", [
		"ExpressionNode" ] ))
	
	return nodes