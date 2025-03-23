import re

def pan_read_data(text):
    name = None
    fname = None
    dob = None
    pan = None
    nameline = []
    dobline = []
    panline = []
    text0 = []
    text1 = []
    text2 = []
    lines = text.split('\n')
    
    for lin in lines:
        s = lin.strip()
        s = lin.replace('\n', '')
        s = s.rstrip()
        s = s.lstrip()
        text1.append(s)
    
    text1 = list(filter(None, text1))
    lineno = 0
    
    for wordline in text1:
        xx = wordline.split('\n')
        if ([w for w in xx if re.search('(INCOMETAXDEPARWENT|INCOME|TAX|GOW|GOVT|GOVERNMENT|OVERNMENT|VERNMENT|DEPARTMENT|EPARTMENT|PARTMENT|ARTMENT|INDIA|NDIA)$', w)]):
            text1 = list(text1)
            lineno = text1.index(wordline)
            break
    
    text0 = text1[lineno+1:]
    
    try:
        # Cleaning first names
        name = text0[0].strip().replace("8", "B").replace("0", "D").replace("6", "G").replace("1", "I")
        name = re.sub('[^a-zA-Z] +', ' ', name)
        
        # Cleaning Father's name
        fname = text0[1].strip().replace("8", "S").replace("0", "O").replace("6", "G").replace("1", "I").replace("\"", "A")
        fname = re.sub('[^a-zA-Z] +', ' ', fname)
        
        # Cleaning DOB
        dob = text0[2][:10].strip().replace('l', '/').replace('L', '/').replace('I', '/').replace('i', '/').replace('|', '/').replace('"', '/1').replace(" ", "")
        
        # Cleaning PAN Card details
        text0 = findword(text1, '(Pormanam|Number|umber|Account|ccount|count|Permanent|ermanent|manent|wumm)$')
        panline = text0[0]
        pan = panline.strip().replace(" ", "").replace("\"", "").replace(";", "").replace("%", "L")
    except:
        pass
    
    data = {
        'Name': name,
        'Father Name': fname,
        'Date of Birth': dob,
        'PAN': pan,
        'ID Type': "PAN"
    }
    
    return data

def findword(textlist, wordstring):
    lineno = -1
    for wordline in textlist:
        xx = wordline.split()
        if ([w for w in xx if re.search(wordstring, w)]):
            lineno = textlist.index(wordline)
            return textlist[lineno+1:]
    return textlist
