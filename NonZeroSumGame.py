class LAOrg:
    def __init__(self, noOfSpaces, appId):
        self.noOfSpaces = noOfSpaces * 7
        self.applicantsChosen = appId
        self.efficiency = 0
        self.dayWiseEfficiency = [noOfSpaces] * 7

    def noOfApplicantsChosen(self):
        return len(self.applicantsChosen)

    def isSpaceAvailable(self):
        return (self.noOfSpaces - len(self.applicantsChosen)) > 0

    def isDaysAvailable(self, daysNeeded):
        resultingEfficiency = [x - y for x, y in zip(self.dayWiseEfficiency, daysNeeded)]
        return not (sum(n < 0 for n in resultingEfficiency) > 0)

    def updateEfficiency(self, daysNeeded):
        self.dayWiseEfficiency = [x - y for x, y in zip(self.dayWiseEfficiency, daysNeeded)]
        self.efficiency += sum(daysNeeded)

    def undoEfficiency(self, daysNeeded):
        self.dayWiseEfficiency = [x + y for x, y in zip(self.dayWiseEfficiency, daysNeeded)]
        self.efficiency -= sum(daysNeeded)

    def isApplicantAcceptable(self, daysNeeded):
        return self.isSpaceAvailable() and self.isDaysAvailable(daysNeeded)

    def addApplicant(self, appId):
        self.applicantsChosen.append(appId)

    def removeApplicant(self, appId):
        self.applicantsChosen.remove(appId)

    def getTotalEfficiencyAvailable(self):
        return sum(self.dayWiseEfficiency)

class LAHSA(LAOrg):
    def __init__(self, noOfBeds, LAHSA_app_id):
        LAOrg.__init__(self, noOfBeds, LAHSA_app_id)


class SPLA(LAOrg):
    def __init__(self, noOfSpaces, SPLA_app_id):
        LAOrg.__init__(self, noOfSpaces, SPLA_app_id)


class Applicants:
    def __init__(self, appId, daysNeeded, isLAHSACompatible, isSPLACompatible, totalDays):
        self.appId = appId
        self.daysNeeded = daysNeeded

        self.inLAHSA = False
        self.inSPLA = False

        self.isLAHSACompatible = isLAHSACompatible
        self.isSPLACompatible = isSPLACompatible
        self.totalDays = totalDays

class LACity:
    def __init__(self, LAHSA, SPLA, mapOfApplicants):
        self.LAHSA = LAHSA
        self.SPLA = SPLA
        self.mapOfApplicants = mapOfApplicants

    def preProcess(self):

        # Create a list of all applicants
        self.allApplicants = {}
        self.bothCompatibleApplicants = {}

        for appId, appInfo in self.mapOfApplicants.iteritems():
            if appId in self.LAHSA.applicantsChosen:
                appInfo.inLAHSA = True
                self.LAHSA.updateEfficiency(appInfo.daysNeeded)
                pass

            elif appId in self.SPLA.applicantsChosen:
                appInfo.inSPLA = True
                self.SPLA.updateEfficiency(appInfo.daysNeeded)
                pass
            else:
                if appInfo.isLAHSACompatible or appInfo.isSPLACompatible:
                    self.allApplicants[appId] = appInfo
                if appInfo.isLAHSACompatible and appInfo.isSPLACompatible:
                    self.bothCompatibleApplicants[appId] = appInfo


    def getNextPlayer(self):
        return (self.LAHSA.noOfApplicantsChosen() >= self.SPLA.noOfApplicantsChosen())

    def removeApplicantFromList(self, allApplicants, applicantId, applicantInfo, isSPLATurn):
        del allApplicants[applicantId]
        if isSPLATurn:
            self.SPLA.updateEfficiency(applicantInfo.daysNeeded)
            self.SPLA.addApplicant(applicantId)
        else:
            self.LAHSA.updateEfficiency(applicantInfo.daysNeeded)
            self.LAHSA.addApplicant(applicantId)

    def undoApplicantIntoList(self, allApplicants, applicantId, applicantInfo, isSPLATurn):
        allApplicants[applicantId] = applicantInfo
        if isSPLATurn:
            self.SPLA.undoEfficiency(applicantInfo.daysNeeded)
            self.SPLA.removeApplicant(applicantId)
        else:
            self.LAHSA.undoEfficiency(applicantInfo.daysNeeded)
            self.LAHSA.removeApplicant(applicantId)

    # def gamePlay(self, isSPLATurn, allApplicants, hasSPLAPlayed = False, hasLAHSAPlayed = False):
    def gamePlay(self, isSPLATurn, allApplicants, hasSPLAPlayed=False, hasLAHSAPlayed=False, splaCnt=0, lahsaCnt=0):
        if len(allApplicants) == 0:
            return (0, 0, -1)

        best_spla_score, best_lahsa_score = 0, 0
        best_move = -1
        if isSPLATurn:
            hasSPLAPlayed = False
            for applicantId, applicantInfo in allApplicants.iteritems():
                if applicantInfo.isSPLACompatible and self.SPLA.isApplicantAcceptable(applicantInfo.daysNeeded):
                    hasSPLAPlayed = True
                    # Remove applicant from list and update efficiency
                    self.removeApplicantFromList(allApplicants, applicantId, applicantInfo, isSPLATurn)
                    # Recurse back with player changed
                    # spla_score, lahsa_score, _ = self.gamePlay(not isSPLATurn, allApplicants, hasSPLAPlayed, hasLAHSAPlayed)
                    if not hasLAHSAPlayed and lahsaCnt > 1:
                        spla_score, lahsa_score, _ = self.gamePlay(isSPLATurn, allApplicants, hasSPLAPlayed,
                                                                   hasLAHSAPlayed, splaCnt, lahsaCnt)
                    else:
                        spla_score, lahsa_score, _ = self.gamePlay(not isSPLATurn, allApplicants, hasSPLAPlayed,
                                                                   hasLAHSAPlayed, splaCnt, lahsaCnt)

                    # Update the score (check for lahsa if needed)
                    if (spla_score + applicantInfo.totalDays > best_spla_score) or (
                            spla_score + applicantInfo.totalDays == best_spla_score and lahsa_score > best_lahsa_score):
                        best_spla_score = spla_score + applicantInfo.totalDays
                        best_lahsa_score = lahsa_score
                        best_move = applicantId
                    if (spla_score + applicantInfo.totalDays == best_spla_score) and (best_move not in self.bothCompatibleApplicants) and (applicantId in self.bothCompatibleApplicants):
                        best_spla_score = spla_score + applicantInfo.totalDays
                        best_lahsa_score = lahsa_score
                        best_move = applicantId
                    # print "{} SPLA Score: {} LAHSA Score: {} ".format(applicantId, best_spla_score, best_lahsa_score)
                    # Place the player back in the list and reupdate efficiency
                    self.undoApplicantIntoList(allApplicants, applicantId, applicantInfo, isSPLATurn)
                if not hasSPLAPlayed and hasLAHSAPlayed:
                    best_spla_score, best_lahsa_score, best_move = self.gamePlay(not isSPLATurn, allApplicants,
                                                                                 hasSPLAPlayed, hasLAHSAPlayed,
                                                                                 splaCnt + 1, lahsaCnt)
                    # best_spla_score, best_lahsa_score, best_move = self.gamePlay(not isSPLATurn, allApplicants, hasSPLAPlayed, hasLAHSAPlayed)

            return (best_spla_score, best_lahsa_score, best_move)
        else:
            hasLAHSAPlayed = False
            for applicantId, applicantInfo in allApplicants.iteritems():
                if applicantInfo.isLAHSACompatible and self.LAHSA.isApplicantAcceptable(applicantInfo.daysNeeded):
                    hasLAHSAPlayed = True
                    # Remove applicant from list and update efficiency
                    self.removeApplicantFromList(allApplicants, applicantId, applicantInfo, isSPLATurn)
                    # Recurse back with player changed
                    # spla_score, lahsa_score, _ = self.gamePlay(not isSPLATurn, allApplicants, hasSPLAPlayed, hasLAHSAPlayed)
                    if not hasSPLAPlayed and splaCnt > 1:
                        spla_score, lahsa_score, _ = self.gamePlay(isSPLATurn, allApplicants, hasSPLAPlayed,
                                                                   hasLAHSAPlayed, splaCnt, lahsaCnt)
                    else:
                        spla_score, lahsa_score, _ = self.gamePlay(not isSPLATurn, allApplicants, hasSPLAPlayed,
                                                                   hasLAHSAPlayed, splaCnt, lahsaCnt)
                    # Update the score
                    if (lahsa_score + applicantInfo.totalDays > best_lahsa_score) or (
                            lahsa_score + applicantInfo.totalDays == best_lahsa_score and spla_score > best_spla_score):
                        best_lahsa_score = lahsa_score + applicantInfo.totalDays
                        best_spla_score = spla_score
                    # print "{} SPLA Score: {} LAHSA Score: {} ".format(applicantId, best_spla_score, best_lahsa_score)
                    # Place the player back in the list and reupdate efficiency
                    self.undoApplicantIntoList(allApplicants, applicantId, applicantInfo, isSPLATurn)
            if not hasLAHSAPlayed and hasSPLAPlayed:
                best_spla_score, best_lahsa_score, best_move = self.gamePlay(not isSPLATurn, allApplicants,
                                                                             hasSPLAPlayed, hasLAHSAPlayed, splaCnt,
                                                                             lahsaCnt + 1)

                # best_spla_score, best_lahsa_score, best_move = self.gamePlay(not isSPLATurn, allApplicants, hasSPLAPlayed, hasLAHSAPlayed)

            return (best_spla_score, best_lahsa_score, best_move)

    def getBestMove(self):
        isSPLATurn = self.getNextPlayer()
        (maxScoreforSPLA, maxScoreforLAHSA, best_move) = self.gamePlay(isSPLATurn, self.allApplicants)
        y = "%05d" % (best_move,)
        f = open("output.txt","w+")
        f.write(y +"\n")
        f.close()
        return best_move

def isValidApplicantForLAHSA(gender, age, hasPet):
    return (gender == 'F' and age > 17 and not hasPet)


def isValidApplicantForSPLA(hasMedicalCondition, hasCar, hasDL):
    return (not hasMedicalCondition and hasCar and hasDL)


def split(appinfo):
    appId = int(appinfo[:5])
    gender = appinfo[5:6]
    age = int(appinfo[6:9])
    hasPet = True if appinfo[9:10] == "Y" else False
    hasMedicalCondition = True if appinfo[10:11] == "Y" else False
    hasCar = True if appinfo[11:12] == "Y" else False
    hasDL = True if appinfo[12:13] == "Y" else False
    daysNeeded = list(appinfo[13:])
    daysNeeded = [1 if i == '1' else 0 for i in daysNeeded]
    totalDays = daysNeeded.count(1)

    isLAHSACompatible = isValidApplicantForLAHSA(gender, age, hasPet)
    isSPLACompatible = isValidApplicantForSPLA(hasMedicalCondition, hasCar, hasDL)

    applicant = Applicants(appId, daysNeeded, isLAHSACompatible, isSPLACompatible, totalDays)

    return [appId, applicant]

def initialize():
    inputFilePath = "input.txt"

    with open(inputFilePath, "r") as file:
        b = int(file.readline())
        p = int(file.readline())

        l = int(file.readline())
        LAHSA_app_id = []
        for i in range(l):
            LAHSA_app_id.append(int(file.readline()))

        SPLA_app_id = []
        s = int(file.readline())
        for i in range(s):
            SPLA_app_id.append(int(file.readline()))

        lahsa = LAHSA(b, LAHSA_app_id)
        spla = SPLA(p, SPLA_app_id)

        mapOfApplicants = {}

        a = int(file.readline())
        for i in range(a):
            appInf = split(file.readline().rstrip())
            mapOfApplicants[appInf[0]] = appInf[1]

    city = LACity(lahsa, spla, mapOfApplicants)
    city.preProcess()
    return city

def main():
    city = initialize()
    city.getBestMove()

if __name__ =="__main__":
    main()