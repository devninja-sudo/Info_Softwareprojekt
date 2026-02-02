def getPossibleTurnFields(self, Field:Feld, boardFields:list[dict], ignoreChecksOrAnxiety:bool=False)->list[Feld]:        # Geht sicher, dass nicht doch irgendwie Ein Feld außerhalb des Brettes ist arbeitet noch Relative
    PossibleTurnFields = []
    relativePossibleTurnFields = self.__getPossibleRelativeFieldsFromFigurOnField(Field, boardFields, ignoreChecksOrAnxiety)
    for relativeField in relativePossibleTurnFields:
        field = self.getRelativeField(Field.getLabel(), relativeField)
        if type(field) != Feld:
            continue
        PossibleTurnFields.append(field)
    return PossibleTurnFields

def __getPossibleRelativeFieldsFromFigurOnField(self, startingPointField:Feld, boardFields:list[dict], ignoreChecksOrAnxiety:bool=False)->list[tuple]:
    figure:None|Springer|Turm|Bauer|Laeufer|Dame|Koenig = startingPointField.getFigure()
    if figure == None:
        return []       # Ein Feld ohne Figur kann seine Figur nirgendwo hinsetzen
    
    startFieldLabel:str = startingPointField.getLabel()
    canJump:bool = figure.getCanJump()
    canKillMates:bool = figure.getCanKillMates()
    relativeMaybePossibleTurnsData:list[dict] = figure.getMaybePossibleTurns(startFieldLabel)                           # Diese sollten eig. nicht Links zu nicht existenten Feldern haben
    relativeMaybePossibleTurnsData:list[dict] = self.__getOnlyTurnDataWithValidFields(relativeMaybePossibleTurnsData)   # Das ist jetzt trotzdem nochmal Sichergestellt, wer weiß oder so...
    if not(canJump):
        relativeMaybePossibleTurnsData:list[dict] = self.__getTurnDataWithoutWalkThroughFigures(relativeMaybePossibleTurnsData, startingPointField)
    if not(canKillMates):
        relativeMaybePossibleTurnsData:list[dict] = self.__getTurnsNotKillingMatesFromTurnData(relativeMaybePossibleTurnsData, figure.getTeam())
    possibleRelativeFields = []                                                                                             
    for relativeMaybePossibleTurnData in relativeMaybePossibleTurnsData:                                                                        # Für jeden Punkt prüfen, welche der zusätzlichen Eigenschaften den Zuges erfüllt sein müssen um den Zug auszuführen und wenn diese nicht erfüllt ist ihn aussortieren
        if type(relativeMaybePossibleTurnData) != dict:
            raise Exception("Unexpectet Type error in Brett: Line 309")
        if relativeMaybePossibleTurnData["onlyOnKill"] or not(relativeMaybePossibleTurnData["canKill"]) or relativeMaybePossibleTurnData["hasAnxiety"]:
            print(relativeMaybePossibleTurnData["hasAnxiety"], ignoreChecksOrAnxiety)
            targetFieldOfTurn:Feld = boardFields[relativeMaybePossibleTurnData["fieldLabel"]]
            if self.__CheckIfIsNotAFeldInstance(targetFieldOfTurn):
                continue
            if targetFieldOfTurn.getFigure() == None and relativeMaybePossibleTurnData["onlyOnKill"]:
                continue
            if targetFieldOfTurn.getFigure() != None and not(relativeMaybePossibleTurnData["canKill"]):
                continue
            if not(ignoreChecksOrAnxiety):
                print("checkt Anxiety:")
                if relativeMaybePossibleTurnData["hasAnxiety"]:
                    if len(self.__getDangerFieldsForField(targetFieldOfTurn, figure.getTeam())) != 0:
                        for i in self.__getDangerFieldsForField(targetFieldOfTurn, figure.getTeam()):
                            print(i.getLabel())
                        print(targetFieldOfTurn, " wird bedroht und ", startingPointField.getFigure(), " hat Angst!")
                        continue
        possibleRelativeFields.append(relativeMaybePossibleTurnData["point"])  
    return possibleRelativeFields
    