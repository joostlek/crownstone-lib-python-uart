#!/bin/bash

# Set location of plantuml
#plantuml=/opt/plantuml/plantuml.jar
plantuml=~/progs/plantuml/plantuml.1.2020.0.jar

if [ ! -f "$plantuml" ]; then
	echo "No such file: $f"
	echo "Set plantuml in this script"
	exit 1
fi

for f in *.txt; do
	echo "Generating $f"
	java -jar "$plantuml" -tpng "$f"
	java -jar "$plantuml" -tsvg "$f"
done

echo "Done"
