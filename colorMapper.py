import csv

class ColorMapper():
    # Creates CSV map with Colors and it respectives ids.
    # with memo variable(dict), that stores the RGB values and id.
    def createCSV_withColorsAndIds(self, memo):
        data = []
        for key, value in memo.items():
            infos = []
            infos.append(key)
            infos.append(value)
            data.append(infos)
    
        header = ['color', 'id']
        with open('mapColors.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)

            # write multiple rows
            writer.writerows(data)
    
    # Loads the map from a csv file
    # note that the map.keys() are string values
    # and map.values() are int values
    def loadMapCSV(self, CSVnameFile):
        with open(CSVnameFile, encoding="utf8") as f:
            csv_reader = csv.DictReader(f)
            # skip the header
            next(csv_reader)
            # creating map with all colors
            mapColors = {}
            # show the data
            for line in csv_reader:
                id = line['id']
                # Removing quotes
                id = int(id.replace("'", ""))
                mapColors[line['color']] = id
        return mapColors