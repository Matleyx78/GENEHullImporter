





        keel_point = []
        deck_line_1 = []
        deck_line_2 = []



            keel_point.append(verts[44].Point)
            deck_line_1.append(verts[0].Point)
            deck_line_2.append(verts[1].Point)


        # finish keel
        keel_point.append(verts_of_center_line[18].Point)
        keel_name = 'Keel_Line'
        self.part_creation(keel_name, keel_point)
        # finish deck line
        # print(deck_line_2)
        App.Console.PrintMessage('Indice: ' + str(deck_line_2[0]) + "\n")
        App.Console.PrintMessage('Indice: ' + str(deck_line_2[10]) + "\n")
        App.Console.PrintMessage('Indice: ' + str(len(deck_line_2)) + "\n")
        deck_line_1.append(verts_of_center_line[18].Point)
        for i in range(len(deck_line_2)-1,-1,-1):            
            App.Console.PrintMessage('Indice: ' + str(i) + "\n")
            deck_line_1.append(deck_line_2[i])
        deck_name = 'Deck_Line'
        self.part_creation(deck_name, deck_line_1)