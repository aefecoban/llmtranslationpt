import re
import json

class DictionaryManagement:

    def __init__(self):
        self.Dictionary = {}
    
    def FindAbbreviations(self, text):
        # (?=[A-Z0-9]*[A-Z])
        # İfadenin devamında sıfır veya daha fazla "büyük harf ve rakam" ve ardından en az bir büyük harf olmalıdır.
        #
        # [A-Z0-9]{2,}
        # En az bir büyük harf ve rakamdan oluşan, en az 2 karakterlik veri
        #
        # Kombinasyonlu ifade de bu ifadelerin arasına "/" karakteri gelirse de kabul ediyor.
        # DM2, PCRE, DM2/A (kombinasyonlu)
        abbreviation_pattern = r'\b(?=[A-Z0-9]*[A-Z])[A-Z0-9]{2,6}\b'
        combined_pattern = r'\b(?=[A-Z0-9]*[A-Z])[A-Z0-9]{2,6}/(?=[A-Z0-9]*[A-Z])[A-Z0-9]{1,5}\b'
    
        tokens = re.findall(abbreviation_pattern, text)
        tokens.extend(re.findall(combined_pattern, text))
    
        abbreviations = {token for token in tokens if re.search(r'[A-Z]', token) and not token[0].isdigit()}
    
        return sorted(abbreviations)

    def FilterAbbreviationsWithTreshold(self, allAbbreviations, threshold):
        # Çok fazla kısaltma bulunurken, bunların bazıları yanlış olabilir.
        # Az sayıda tekrar eden veri varsa bunları sileceğiz, belirli bir eşik değerin üstündeki
        # tekrar sayıları o verinin potansiyel kısaltma olduğunu ifade edeceğini kabul ediyoruz.
        abbreviationsCount = {}
    
        for abbreviation in allAbbreviations:
            abbreviationsCount[abbreviation] = abbreviationsCount.get(abbreviation, 0) + 1
    
        return [abbr for abbr, count in abbreviationsCount.items() if count > threshold]

    def SetFile(self, fileLocation):
        with open(file=fileLocation, mode='r', encoding='utf-8') as f:
            self.SetDictionary(json.load(f))

    def SetDictionary(self, di):
        self.Dictionary = di

    def GetAllAbbreviations(self, text):
        arr = list(set(self.FindAbbreviations(text)))
        result = {}
        for key in arr:
            if key in self.Dictionary:
                result[key] = self.Dictionary[key][:3]
        return result
