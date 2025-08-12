from DictionaryManager import DictionaryManagement

DManager = DictionaryManagement()
DManager.SetFile("Dictionary.json")

all = DManager.GetAllAbbreviations("İlaç her gün sabah PO ve AV ile CHF")
print(all)