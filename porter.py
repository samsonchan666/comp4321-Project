def updateM(word):
    vowel = 'aeiou'
    structure = []
    structureLength = 0
    m = 0
    for x in word:
        if x in vowel:
            if (len(structure) == 0) or (structure[-1] == 'c'):
                structure.append('v')
        elif (len(structure) == 0) or (structure[-1] == 'v'):
            structure.append('c')
    structureLength = len(structure)

    m = structureLength / 2
    if m > 0:
        if (structure[0] == 'c') and (structure[-1] == 'v'):
            m = m - 1
        elif (structure[0] == 'c') or (structure[-1] == 'v'):
            m = m - 0.5
    return [structure, structureLength, m]


def check_cvcwxy(word):
    vowel = 'aeiou'
    if (len(word) >= 3) and (word[-1] not in (vowel or 'wxy')) and (word[-2] in vowel) and (word[-3] not in vowel):
        return True
    else:
        return False


def Porter(word):
    if (word.isalpha() == False):
        return word
    else:
        vowel = 'aeiou'
        # structure = []
        # structureLength = 0
        # m = 0

        update = updateM(word)

        # For 'fff' case
        if update[1] == 1:
            return word

        # Step 1a
        if word.endswith('sses'):
            word = word.replace('sses', 'ss')
        elif word.endswith('ies'):
            word = word.replace('ies', 'i')
        elif word.endswith('ss'):
            word = word
        elif word.endswith('s'):
            word = word.replace('s', '')

        # Step 1b
        nextStep = False
        temp = word
        if word.endswith('eed'):
            temp = word[0:-3]
            if updateM(temp)[2] > 0:
                word = word.replace('eed', 'ee')
        elif 'v' in update[0][1:-1]:
            if word.endswith('ed'):
                temp = word.replace('ed', '')
            elif word.endswith('ing'):
                temp = word.replace('ing', '')
            if temp != word:
                for x in temp:
                    if x in vowel:
                        word = temp
                        nextStep = True

        update = updateM(word)

        # Step 1b continued
        if nextStep == True:
            if word.endswith('at'):
                word = word.replace('at', 'ate')
            elif word.endswith('bl'):
                word = word.replace('bl', 'ble')
            elif word.endswith('iz'):
                word = word.replace('iz', 'ize')
            elif (word[-1] == word[-2]) and (word[-1] not in 'lsz'):
                word = word[0:-1]
            elif (check_cvcwxy(word) == True) and (update[2] == 1):
                word = word + 'e'

        # Step 1c
        vowelExist = False
        for x in word:
            if x in vowel:
                vowelExist = True
        if (vowelExist == True) and (word.endswith('y') == True):
            word = word.replace('y', 'i')

        # Step 2
        Step2Dict = {'ational': 'ate',
                     'tional': 'tion',
                     'enci': 'ence',
                     'anci': 'ance',
                     'izer': 'ize',
                     'abli': 'able',
                     'alli': 'al',
                     'entli': 'ent',
                     'eli': 'e',
                     'ousli': 'ous',
                     'ization': 'ize',
                     'ation': 'ate',
                     'ator': 'ate',
                     'alism': 'al',
                     'iveness': 'ive',
                     'fulness': 'ful',
                     'ousness': 'ous',
                     'aliti': 'al',
                     'iviti': 'ive',
                     'biliti': 'ble'}
        temp = word
        for x in Step2Dict:
            if temp.endswith(x):
                temp = word.replace(x, '')
                if updateM(temp)[2] > 0:
                    word = word.replace(x, Step2Dict[x])

        # Step 3
        Step3Dict = {'icate': 'ic',
                     'ative': '',
                     'alize': 'al',
                     'iciti': 'ic',
                     'ical': 'ic',
                     'ful': '',
                     'ness': ''}
        temp = word
        for x in Step3Dict:
            if temp.endswith(x):
                temp = word.replace(x, '')
                if updateM(temp)[2] > 0:
                    word = word.replace(x, Step3Dict[x])

        # Step 4
        Step4List = ['al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant', 'ement', 'ment', 'ent',
                     'ion', 'ou', 'ism', 'ate', 'iti', 'ous', 'ive', 'ize']
        for x in Step4List:
            if word.endswith(x):
                temp = word.replace(x, '')
                if x == 'ion':
                    if (temp.endswith('s') == True) or (temp.endswith('t') == True):
                        if updateM(temp)[2] > 1:
                            word = word.replace(x, '')
                else:
                    if updateM(temp)[2] > 1:
                        word = word.replace(x, '')

        # Step 5a
        temp = word
        if temp.endswith('e'):
            temp = word[0:-1]
            m = updateM(temp)[2]
            if m > 1:
                word = temp
            if (m == 1) and (check_cvcwxy(temp) == False):
                word = temp

        # Step 5b
        if (word[-1] == 'l') and (word[-2] == 'l') and (updateM(word)[2] > 1):
            word = word[0:-1]

        return word
